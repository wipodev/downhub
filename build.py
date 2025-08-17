import subprocess
import os

def run_command(command):
    """Execute a command on the system"""
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        exit(1)

def main():
    local_appdata = os.environ["LOCALAPPDATA"]

    print("Generating extension key and updating files...")
    run_command("python setup_ext.py")

    print("Compiling API...")
    run_command("python setup_api.py build")
    
    print("Creating installer...")
    inno_path = os.path.join(local_appdata, r"Programs\Inno Setup 6\ISCC.exe")
    run_command(f'"{inno_path}" setup_installer.iss')
    
    print("Construction process completed.")

if __name__ == "__main__":
    main()
