#!/bin/bash
# Cleanup silencioso para el KeyLogger desde dentro de la carpeta

# Detener keylogger.py
pid=$(pgrep -f keylogger.py)
[ -n "$pid" ] && kill $pid 2>/dev/null

# Desinstalar librerías de requirements.txt (si el archivo existía)
[ -f ENTI_keylogger/requirements.txt ] && pip uninstall -r ENTI_keylogger/requirements.txt -y 2>/dev/null

# Subir al directorio padre
cd .. 2>/dev/null

# Eliminar carpeta del proyecto (incluyendo este script)
rm -rf ENTI_keylogger 2>/dev/null