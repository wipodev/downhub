import subprocess

def run_command(command):
    """Execute a command on the system"""
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        exit(1)

def main():
    print("Compiling API...")
    run_command("python setup_api.py build")
    
    print("Packaging extension...")
    run_command("python setup_ext.py")
    
    print("Creating installer...")
    run_command('"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_installer.iss')
    
    print("Construction process completed.")

if __name__ == "__main__":
    main()
