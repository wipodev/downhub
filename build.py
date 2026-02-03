import os, sys
import subprocess
import shutil
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS ---
APPDATA = os.environ.get('LOCALAPPDATA')
INNO_SETUP_EXE = Path(APPDATA) / "Programs/Inno Setup 6/ISCC.exe"
BASE_DIR = Path(__file__).parent
SPEC_FILE = BASE_DIR / "native_host.spec"
ISS_FILE = BASE_DIR / "setup.iss"

def run_command(command, app):
    """Execute a command on the system"""
    try:
        subprocess.check_call(command, shell=True)
        print(f"[+] {app} generado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error executing {app}: {e}")
        exit(1)

def clean_folders():
    """Elimina carpetas de compilaciones anteriores para evitar basura."""
    folders = [BASE_DIR / "dist", BASE_DIR / "build"]
    for folder in folders:
        if folder.exists():
            print(f"[*] Limpiando {folder.name}...")
            shutil.rmtree(folder)

def run_inno_setup():
    """Ejecuta el compilador de Inno Setup."""
    print("[*] Iniciando Inno Setup...")
    if not INNO_SETUP_EXE.exists():
        print(f"[-] Error: No se encontró ISCC.exe en {INNO_SETUP_EXE}")
        exit(1)
    run_command(f'"{str(INNO_SETUP_EXE)}" {str(ISS_FILE)}', "Instalador")

def main():
    print("--- INICIANDO PROCESO DE BUILD ---")
    clean_folders()

    args = [a.lower() for a in sys.argv[1:]]
    if "--keys" in args or "keys" in args or "-k" in args:
        print("Generating extension key and updating files...")
        run_command("python extension_key.py", "key")

    print("[*] Iniciando PyInstaller...")
    run_command(f"pyinstaller {str(SPEC_FILE)}", "Ejecutable")

    args = [a.lower() for a in sys.argv[1:]]
    if "--inno" in args or "inno" in args or "-i" in args:
        run_inno_setup()
    print("--- PROCESO FINALIZADO ---")

if __name__ == "__main__":
    main()