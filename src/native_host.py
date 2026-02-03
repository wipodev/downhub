import sys
import json
import struct
import subprocess
import os
import logging
import time
from pathlib import Path

# -----------------------------
# Configuración de Protocolo (Sincronizado con config.js)
# -----------------------------
MESSAGES = {
    "PROGRESS": "NATIVE_PROGRESS",
    "DONE": "NATIVE_DONE",
    "ERROR": "NATIVE_ERROR"
}

# Variable global para poder cancelar el proceso desde el hilo principal
current_process = None

# Configurar logs en la misma carpeta del script
LOG_FILE = Path(sys.executable).parent / "debug_native.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filemode="w" # 'w' para que se limpie en cada inicio
)

logging.info("--- Iniciando Host Nativo ---")

# -----------------------------
# Native Messaging helpers
# -----------------------------

def read_message():
    try:
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length:
            logging.warning("No se recibió longitud del mensaje (posible desconexión)")
            return None
        message_length = struct.unpack("<I", raw_length)[0]
        logging.debug(f"Longitud recibida: {message_length} bytes")
        message = sys.stdin.buffer.read(message_length).decode("utf-8")
        return json.loads(message)
    except Exception as e:
        logging.error(f"Error leyendo mensaje: {e}")
        return None

def send_message(message):
    try:
        encoded = json.dumps(message).encode("utf-8")
        sys.stdout.buffer.write(struct.pack("<I", len(encoded)))
        sys.stdout.buffer.write(encoded)
        sys.stdout.buffer.flush()
        return True
    except (IOError, BrokenPipeError):
        # ¡AQUÍ ES DONDE SE ENTERA!
        logging.error("Conexión perdida con Chrome (Cancelación detectada)")
        return False

# -----------------------------
# Rutas y Directorios
# -----------------------------

BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent

YTDLP_PATH = BASE_DIR / "bin" / "yt-dlp.exe"
FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg.exe"

def get_downloads_folder():
    """Retorna la carpeta de descargas del usuario en Windows."""
    return Path(os.environ["USERPROFILE"]) / "Downloads"

# -----------------------------
# Lógica de Descarga
# -----------------------------

def download_video(url, filename):
    logging.info(f"Hilo de descarga iniciado para: {url}")
    global current_process
    output_template = str(get_downloads_folder() / filename)
    
    if not YTDLP_PATH.exists():
        send_message({"type": MESSAGES["ERROR"], "message": f"Falta yt-dlp.exe en {BASE_DIR}"})
        os._exit(1)

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

    try:
        current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logging.info(f"Subproceso yt-dlp lanzado (PID: {current_process.pid})")

        for line in current_process.stdout:
            line = line.strip()
            
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
                except: pass

            elif "[Merger]" in line or "[VideoConvertor]" in line:
                send_message({
                    "type": MESSAGES["PROGRESS"],
                    "percent": 99,
                    "status": "Finalizando archivo (FFmpeg)..."
                })

        current_process.wait()
        logging.info(f"Descarga finalizada con código: {current_process.returncode}")

        if current_process.returncode == 0:
            send_message({"type": MESSAGES["DONE"]})
            os._exit(0)
        else:
            # Si el código es menor a 0, significa que fue terminado (cancelado)
            if current_process.returncode < 0:
                send_message({"type": MESSAGES["ERROR"], "message": "Descarga cancelada."})
                logging.error(f"Descarga cancelada.")
            else:
                send_message({"type": MESSAGES["ERROR"], "message": "Error en el proceso de descarga"})
                logging.error(f"Error en el proceso de descarga")
            os._exit(1)

    except Exception as e:
        send_message({"type": MESSAGES["ERROR"], "message": str(e)})
        logging.error(f"Excepción en hilo de descarga: {e}")
        os._exit(1)

# -----------------------------
# Cancelacion
# -----------------------------

def cancel_download(file):
    if hasattr(cancel_download, "_running"): return
    cancel_download._running = True

    logging.info("--- Iniciando proceso de limpieza ---")
    
    global current_process
    if current_process:
        logging.info(f"Terminando árbol de procesos del PID: {current_process.pid}")
        # Intentamos matar a yt-dlp y a TODOS sus hijos (como ffmpeg)
        try:
            # Comando de Windows para matar un proceso y sus hijos (/T) de forma forzada (/F)
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(current_process.pid)], 
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            logging.error(f"Error usando taskkill: {e}")
            current_process.kill() # Plan B

    # Esperamos un poco más para que Windows registre el cierre de los descriptores
    time.sleep(2.0) 

    folder = Path(file).parent
    # Usamos el nombre base pero con cuidado con los caracteres especiales
    base_name = Path(file).stem

    logging.info(f"Buscando temporales en: {folder}")
    
    # Intentamos la limpieza hasta 5 veces con pausas entre medio
    for intento in range(5):
        all_cleared = True
        # Buscamos archivos que contengan el nombre base y terminen en extensiones de yt-dlp
        for temp_file in folder.glob("*"):
            # Si el nombre del archivo contiene el base_name y es un temporal...
            if base_name in temp_file.name and (temp_file.suffix in ['.part', '.temp', '.ykv', '.yka'] or ".part" in temp_file.name):
                try:
                    if temp_file.exists():
                        os.remove(temp_file)
                        logging.info(f"Eliminado en intento {intento+1}: {temp_file.name}")
                except OSError:
                    all_cleared = False
                    logging.warning(f"Archivo bloqueado aún: {temp_file.name} (reintentando...)")
        
        if all_cleared:
            break
        time.sleep(1.0) # Esperar un segundo antes del siguiente intento de borrado

    logging.info("Limpieza finalizada. Saliendo.")
    os._exit(0)

# -----------------------------
# Bucle Principal
# -----------------------------

def main():
    global current_process
    logging.info("=== DownHub Iniciado (Hilo Principal) ===")
    
    msg = read_message()
    
    if msg and msg.get("type") == "download_task":
        url = msg.get("url")
        filename = msg.get("filename", "video.mp4")
        logging.info(f"Iniciando descarga en Hilo Principal: {filename}")
        download_video(url, filename) 
    
    logging.info("Hilo Principal finalizado. Saliendo.")

if __name__ == "__main__":
    try:
        main()
    except EOFError:
        sys.exit(0)