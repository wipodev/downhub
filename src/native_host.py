import sys
import json
import struct
import subprocess
import os
import logging
import time
from pathlib import Path

# -----------------------------
# Protocol Configuration (Synced with config.js)
# -----------------------------
MESSAGES = {
    "PROGRESS": "NATIVE_PROGRESS",
    "DONE": "NATIVE_DONE",
    "ERROR": "NATIVE_ERROR"
}

# Global variable to cancel the subprocess from the main thread
current_process = None

# -----------------------------
# Paths and Directories
# -----------------------------
BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
LOG_FILE = BASE_DIR / "debug_native.log"
UPDATE_STAMP_FILE = BASE_DIR / "bin" / ".last_ytdlp_update"

YTDLP_PATH = BASE_DIR / "bin" / "yt-dlp.exe"
FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg.exe"

# Configure logging in the executable directory
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="w"
)

logging.info("--- Starting Native Host ---")

# -----------------------------
# Native Messaging Helpers
# -----------------------------

def read_message():
    """Read a length-prefixed JSON message from Chrome via stdin."""
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            logging.warning("No message length received (possible disconnection)")
            return None
        message_length = struct.unpack("<I", raw_length)[0]
        logging.debug(f"Received length: {message_length} bytes")
        message = sys.stdin.buffer.read(message_length).decode("utf-8")
        return json.loads(message)
    except Exception as e:
        logging.error(f"Error reading message: {e}")
        return None

def send_message(message):
    """Send a length-prefixed JSON message back to Chrome via stdout."""
    try:
        encoded = json.dumps(message).encode("utf-8")
        sys.stdout.buffer.write(struct.pack("<I", len(encoded)))
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return True
    except (IOError, BrokenPipeError):
        logging.error("Connection lost with Chrome (Cancellation detected)")
        return False

def get_downloads_folder():
    """Return the current Windows user's Downloads directory."""
    return Path(os.environ["USERPROFILE"]) / "Downloads"

# -----------------------------
# yt-dlp Auto-Update Logic
# -----------------------------

def ensure_ytdlp_updated(force=False):
    """Update yt-dlp.exe if more than 24 hours have passed since the last check, or if forced."""
    if not YTDLP_PATH.exists():
        return

    now = time.time()
    update_interval = 86400  # 24 hours in seconds

    if not force and UPDATE_STAMP_FILE.exists():
        try:
            last_check = float(UPDATE_STAMP_FILE.read_text().strip())
            if (now - last_check) < update_interval:
                return
        except ValueError:
            pass

    logging.info("Checking for yt-dlp updates...")
    send_message({
        "type": MESSAGES["PROGRESS"],
        "percent": 0,
        "status": "Verificando actualizaciones de motor..."
    })

    try:
        result = subprocess.run(
            [str(YTDLP_PATH), "-U"],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        output = (result.stdout or "") + (result.stderr or "")
        logging.info(f"yt-dlp update output: {output.strip()}")
        UPDATE_STAMP_FILE.write_text(str(now))
    except Exception as e:
        logging.warning(f"Could not auto-update yt-dlp: {e}")

# -----------------------------
# Download Logic
# -----------------------------

def download_video(url, filename):
    """Execute yt-dlp as a subprocess and stream progress back to the extension."""
    logging.info(f"Download started for: {url}")
    global current_process
    output_template = str(get_downloads_folder() / filename)
    
    if not YTDLP_PATH.exists():
        send_message({"type": MESSAGES["ERROR"], "message": f"Falta yt-dlp.exe en {BASE_DIR}"})
        os._exit(1)

    # Check daily update before starting the download
    ensure_ytdlp_updated(force=False)

    cmd = [
        str(YTDLP_PATH),
        url,
        "-o", output_template,
        "--ffmpeg-location", str(FFMPEG_PATH),
        "--merge-output-format", "mp4",
        "--newline",
        "--progress",
        "--no-playlist"
    ]

    last_error = "Error en el proceso de descarga"

    try:
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logging.info(f"yt-dlp subprocess launched (PID: {current_process.pid})")

        for line in current_process.stdout:
            line = line.strip()

            if "ERROR:" in line:
                logging.error(f"YT-DLP DETAIL: {line}")
                last_error = line.replace("ERROR:", "").strip()
            
            if "[download]" in line and "%" in line:
                try:
                    parts = line.split()
                    for p in parts:
                        if "%" in p:
                            percent_val = float(p.replace("%", ""))
                            if not send_message({
                                "type": MESSAGES["PROGRESS"],
                                "percent": percent_val,
                                "status": "Descargando video..."
                            }):
                                cancel_download(output_template)
                            break
                except Exception:
                    pass

            elif "[Merger]" in line or "[VideoConvertor]" in line:
                send_message({
                    "type": MESSAGES["PROGRESS"],
                    "percent": 99,
                    "status": "Finalizando archivo (FFmpeg)..."
                })
            
            elif "WARNING:" in line:
                logging.warning(f"YT-DLP WARNING: {line}")

        current_process.wait()
        logging.info(f"Download finished with return code: {current_process.returncode}")

        if current_process.returncode == 0:
            send_message({"type": MESSAGES["DONE"]})
            os._exit(0)
        else:
            if current_process.returncode < 0:
                send_message({"type": MESSAGES["ERROR"], "message": "Descarga cancelada."})
                logging.error("Download cancelled.")
            else:
                # If YouTube returned 403 Forbidden, force an immediate yt-dlp update for the next retry
                if "403" in last_error or "Forbidden" in last_error:
                    ensure_ytdlp_updated(force=True)
                    last_error = "YouTube bloqueó la descarga (403). Motor actualizado: intenta de nuevo."
                send_message({"type": MESSAGES["ERROR"], "message": last_error})
                logging.error(f"Download failed: {last_error}")
            os._exit(1)

    except Exception as e:
        send_message({"type": MESSAGES["ERROR"], "message": str(e)})
        logging.error(f"Exception in download thread: {e}")
        os._exit(1)

# -----------------------------
# Cancellation & Cleanup
# -----------------------------

def cancel_download(file):
    """Kill yt-dlp and child FFmpeg processes and remove partial files."""
    if hasattr(cancel_download, "_running"):
        return
    cancel_download._running = True

    logging.info("--- Starting cleanup process ---")
    
    global current_process
    if current_process:
        logging.info(f"Terminating process tree for PID: {current_process.pid}")
        try:
            subprocess.run(
                ['taskkill', '/F', '/T', '/PID', str(current_process.pid)], 
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except Exception as e:
            logging.error(f"Error using taskkill: {e}")
            current_process.kill()

    time.sleep(2.0) 

    folder = Path(file).parent
    base_name = Path(file).stem

    logging.info(f"Looking for temp files in: {folder}")
    
    for attempt in range(5):
        all_cleared = True
        for temp_file in folder.glob("*"):
            if base_name in temp_file.name and (temp_file.suffix in ['.part', '.temp', '.ykv', '.yka'] or ".part" in temp_file.name):
                try:
                    if temp_file.exists():
                        os.remove(temp_file)
                        logging.info(f"Removed on attempt {attempt+1}: {temp_file.name}")
                except OSError:
                    all_cleared = False
                    logging.warning(f"File still locked: {temp_file.name} (retrying...)")
        
        if all_cleared:
            break
        time.sleep(1.0)

    logging.info("Cleanup finished. Exiting.")
    os._exit(0)

# -----------------------------
# Main Entrypoint
# -----------------------------

def main():
    """Main entry point invoked by Chrome Native Messaging."""
    if sys.stdin is None:
        logging.warning("Manual execution detected (no stdin). This binary must be invoked by Chrome.")
        sys.exit(0)

    logging.info("=== DownHub Started (Main Thread) ===")
    msg = read_message()
    
    if msg and msg.get("type") == "download_task":
        url = msg.get("url")
        filename = msg.get("filename", "video.mp4")
        logging.info(f"Starting download in Main Thread: {filename}")
        download_video(url, filename) 
    
    logging.info("Main Thread finished. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except EOFError:
        sys.exit(0)