import subprocess
import sys
import os
import time

api_path = os.path.join("api", "main.py")
api_process = subprocess.Popen([sys.executable, api_path])
time.sleep(2)

try:
    import api.gui
except Exception as e:
    print(f"Error ejecutando la GUI: {e}")
finally:
    api_process.terminate()
