import os
import sys
import time
import logging
import subprocess
from pathlib import Path

from config import (
    APP_VERSION,
    BASE_DIR,
    YTDLP_PATH,
    FFMPEG_PATH,
    DENO_PATH,
    get_downloads_folder,
    setup_logging,
)
from messaging import read_message, send_progress, send_done, send_error
from app_updater import ensure_ytdlp_updated, run_background_app_update

setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"--- Starting DownHub Native Host v{APP_VERSION} ---")

current_process = None


def download_video(url: str, filename: str) -> None:
    """Execute yt-dlp as a subprocess and stream progress back to the extension."""
    global current_process
    logger.info(f"Download started for: {url}")
    output_template = str(get_downloads_folder() / filename)

    if not YTDLP_PATH.exists():
        send_error(f"Falta yt-dlp.exe en {BASE_DIR}")
        os._exit(1)

    ensure_ytdlp_updated(force=False)

    cmd = [
        str(YTDLP_PATH),
        url,
        "-o", output_template,
        "--ffmpeg-location", str(FFMPEG_PATH),
        "--merge-output-format", "mp4",
        "--newline",
        "--progress",
        "--no-playlist",
    ]

    if DENO_PATH.exists():
        cmd.extend(["--js-runtimes", f"deno:{DENO_PATH}"])

    last_error = "Error en el proceso de descarga"

    try:
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        logger.info(f"yt-dlp subprocess launched (PID: {current_process.pid})")

        for line in current_process.stdout:
            line = line.strip()

            if "ERROR:" in line:
                logger.error(f"YT-DLP DETAIL: {line}")
                last_error = line.replace("ERROR:", "").strip()

            if "[download]" in line and "%" in line:
                try:
                    for part in line.split():
                        if "%" in part:
                            percent_val = float(part.replace("%", ""))
                            if not send_progress(percent_val, "Descargando video..."):
                                cancel_download(output_template)
                            break
                except Exception:
                    pass

            elif "[Merger]" in line or "[VideoConvertor]" in line:
                send_progress(99, "Finalizando archivo (FFmpeg)...")

            elif "WARNING:" in line:
                logger.warning(f"YT-DLP WARNING: {line}")

        current_process.wait()
        logger.info(f"Download finished with return code: {current_process.returncode}")

        if current_process.returncode == 0:
            send_done()
            run_background_app_update()
            os._exit(0)
        else:
            if current_process.returncode < 0:
                send_error("Descarga cancelada.")
                logger.error("Download cancelled.")
            else:
                if "403" in last_error or "Forbidden" in last_error:
                    ensure_ytdlp_updated(force=True)
                    last_error = "YouTube bloqueó la descarga (403). Motor actualizado: intenta de nuevo."
                send_error(last_error)
                logger.error(f"Download failed: {last_error}")
                run_background_app_update()
            os._exit(1)

    except Exception as e:
        send_error(str(e))
        logger.error(f"Exception in download thread: {e}")
        os._exit(1)


def cancel_download(file_path: str) -> None:
    """Kill yt-dlp and child FFmpeg processes and remove partial files."""
    if hasattr(cancel_download, "_running"):
        return
    cancel_download._running = True

    logger.info("--- Starting cleanup process ---")

    global current_process
    if current_process:
        logger.info(f"Terminating process tree for PID: {current_process.pid}")
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(current_process.pid)],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:
            logger.error(f"Error using taskkill: {e}")
            current_process.kill()

    time.sleep(2.0)

    folder = Path(file_path).parent
    base_name = Path(file_path).stem

    for attempt in range(5):
        all_cleared = True
        for temp_file in folder.glob("*"):
            if base_name in temp_file.name and (
                temp_file.suffix in [".part", ".temp", ".ykv", ".yka"] or ".part" in temp_file.name
            ):
                try:
                    if temp_file.exists():
                        os.remove(temp_file)
                        logger.info(f"Removed on attempt {attempt + 1}: {temp_file.name}")
                except OSError:
                    all_cleared = False
        if all_cleared:
            break
        time.sleep(1.0)

    logger.info("Cleanup finished. Exiting.")
    os._exit(0)


def main() -> None:
    """Main entry point invoked by Chrome Native Messaging."""
    if sys.stdin is None:
        logger.warning("Manual execution detected (no stdin). This binary must be invoked by Chrome.")
        sys.exit(0)

    logger.info("=== DownHub Started (Main Thread) ===")
    msg = read_message()

    if msg and msg.get("type") == "download_task":
        url = msg.get("url")
        filename = msg.get("filename", "video.mp4")
        download_video(url, filename)

    logger.info("Main Thread finished. Exiting.")


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        sys.exit(0)