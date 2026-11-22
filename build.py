import os
import sys
import re
import json
import shutil
import zipfile
import subprocess
from pathlib import Path

# --- PATH CONFIGURATION ---
APPDATA = os.environ.get('LOCALAPPDATA')
LOCAL_ISCC = Path(APPDATA) / "Programs/Inno Setup 6/ISCC.exe"
SYSTEM_ISCC = Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe")
INNO_SETUP_EXE = LOCAL_ISCC if LOCAL_ISCC.exists() else SYSTEM_ISCC
BASE_DIR = Path(__file__).parent

VERSION_FILE = BASE_DIR / "VERSION"
CONFIG_FILE = BASE_DIR / "src" / "config.py"
MANIFEST_FILE = BASE_DIR / "extension" / "manifest.json"
ENTRY_POINT = BASE_DIR / "src" / "native_host.py"
ISS_FILE = BASE_DIR / "setup.iss"
DIST_DIR = BASE_DIR / "dist"
ICON_FILE = BASE_DIR / "assets" / "icon_service.ico"


def get_service_version():
    """Read and validate the native service version from the root VERSION file."""
    if not VERSION_FILE.exists():
        print("[-] Error: VERSION file not found in project root.")
        sys.exit(1)
    version = VERSION_FILE.read_text(encoding="utf-8").strip().lstrip("vV")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print(f"[-] Error: Invalid service version format '{version}'. Expected X.Y.Z.")
        sys.exit(1)
    return version


def get_extension_version():
    """Read the independent extension version directly from extension/manifest.json."""
    if not MANIFEST_FILE.exists():
        return "unknown"
    data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    return data.get("version", "unknown")


def sync_service_version(version):
    """Propagate the service version across Python source and Inno Setup."""
    version_4_str = f"{version}.0"

    print(f"[*] Synchronizing Service version {version} across native files...")

    # 1. Update APP_VERSION in src/config.py
    nh_text = CONFIG_FILE.read_text(encoding="utf-8")
    nh_text = re.sub(r'APP_VERSION\s*=\s*["\'][^"\']+["\']', f'APP_VERSION = "{version}"', nh_text)
    CONFIG_FILE.write_text(nh_text, encoding="utf-8")

    # 2. Update setup.iss for Inno Setup installer metadata
    if ISS_FILE.exists():
        iss_text = ISS_FILE.read_text(encoding="utf-8")
        iss_text = re.sub(r"^AppVersion=.*$", f"AppVersion={version}", iss_text, flags=re.MULTILINE)
        iss_text = re.sub(r"^VersionInfoProductVersion=.*$", f"VersionInfoProductVersion={version_4_str}", iss_text, flags=re.MULTILINE)
        iss_text = re.sub(r"^VersionInfoTextVersion=.*$", f"VersionInfoTextVersion={version_4_str}", iss_text, flags=re.MULTILINE)
        iss_text = re.sub(r"^VersionInfoVersion=.*$", f"VersionInfoVersion={version_4_str}", iss_text, flags=re.MULTILINE)
        ISS_FILE.write_text(iss_text, encoding="utf-8")

    print(f"[+] Native service files synced to v{version}.")


def run_command(command, app):
    """Execute a system command and exit on failure."""
    try:
        subprocess.check_call(command, shell=True)
        print(f"[+] {app} generado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error executing {app}: {e}")
        sys.exit(1)


def clean_folders():
    """Remove previous build directories to avoid stale artifacts."""
    for folder in [DIST_DIR, BASE_DIR / "build"]:
        if folder.exists():
            print(f"[*] Limpiando {folder.name}...")
            shutil.rmtree(folder)


def compile_nuitka(version):
    """Compile native_host.py into a standalone Windows executable using Nuitka."""
    version_4_str = f"{version}.0"
    print(f"[*] Iniciando Nuitka (v{version})...")
    icon_flag = f'--windows-icon-from-ico="{str(ICON_FILE)}" ' if ICON_FILE.exists() else ""
    cmd = (
        f'"{sys.executable}" -m nuitka '
        '--standalone '
        '--onefile '
        '--remove-output '
        '--windows-console-mode=disable '
        '--include-windows-runtime-dlls=yes '
        '--include-package=updater '
        f'{icon_flag}'
        '--company-name="WipoDev" '
        '--product-name="DownHub" '
        '--file-description="DownHub Native Messaging Host" '
        '--copyright="Copyright (c) 2026 WipoDev" '
        f'--file-version="{version_4_str}" '
        f'--product-version="{version_4_str}" '
        f'--output-dir="{str(DIST_DIR)}" '
        '--output-filename="DownHubService.exe" '
        f'"{str(ENTRY_POINT)}"'
    )
    run_command(cmd, "Ejecutable Nuitka")


def package_extension_zip(ext_version):
    """Package the extension folder contents into dist/extension.zip for GitHub Releases."""
    ext_dir = BASE_DIR / "extension"
    zip_path = DIST_DIR / "extension.zip"
    if not ext_dir.exists():
        return
    print(f"[*] Empaquetando dist/extension.zip (Extensión v{ext_version})...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in ext_dir.rglob("*"):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(ext_dir))
    print("[+] dist/extension.zip generado con éxito.")


def run_inno_setup():
    """Run the Inno Setup compiler."""
    print("[*] Iniciando Inno Setup...")
    if not INNO_SETUP_EXE.exists():
        print(f"[-] Error: No se encontró ISCC.exe en {INNO_SETUP_EXE}")
        sys.exit(1)
    run_command(f'"{str(INNO_SETUP_EXE)}" "{str(ISS_FILE)}"', "Instalador")


def main():
    print("--- INICIANDO PROCESO DE BUILD ---")
    service_version = get_service_version()
    ext_version = get_extension_version()
    args = [a.lower() for a in sys.argv[1:]]

    clean_folders()
    sync_service_version(service_version)

    if "--keys" in args or "keys" in args or "-k" in args:
        print("Generating extension key and updating files...")
        run_command("python extension_key.py", "key")

    compile_nuitka(service_version)

    if "--ext" in args or "ext" in args or "-e" in args:
        package_extension_zip(ext_version)

    if "--inno" in args or "inno" in args or "-i" in args:
        run_inno_setup()

    print(f"--- PROCESO FINALIZADO (Service: v{service_version} | Extension: v{ext_version}) ---")


if __name__ == "__main__":
    main()