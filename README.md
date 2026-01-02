                                                    
# LinuxKeylogger

**LinuxKeylogger** es una herramienta de demostración desarrollada en **Python**, diseñada con fines de **investigación y formación en ciberseguridad**.  
Su objetivo es mostrar cómo operan los *keyloggers* a nivel técnico, permitiendo a los profesionales y estudiantes del área **comprender sus mecanismos**, **detectar comportamientos maliciosos** y **diseñar contramedidas efectivas**.

> ⚠️ **Advertencia de Uso Ético**
>
> Esta herramienta ha sido desarrollada **exclusivamente con fines educativos y de investigación en ciberseguridad**.
> El uso de este software para **monitorizar o registrar la actividad de un dispositivo sin el consentimiento explícito de su propietario** es **ilegal** y **éticamente inaceptable**.  
> 
> Los desarrolladores **no se responsabilizan del uso indebido** de esta herramienta.  
> Úsala únicamente bajo tu propia responsabilidad, en **entornos controlados** y **siempre conforme a la legislación vigente** y a los principios éticos de la ciberseguridad.

---

## Características

- **Registro de pulsaciones** - Captura de todo tipo de teclas (letras, números y teclas especiales como Shift, Ctrl, Alt, Enter, Espacio, etc.) para análisis forense y detección de comportamiento malicioso.  
- **Ejecución en segundo plano** - Modo silencioso pensado únicamente para pruebas en entornos controlados y con consentimiento explícito.  
- **Salida ordenada a fichero** - Guarda los registros en un archivo `keylog.txt` en el directorio del proyecto, con marcas de tiempo y metadatos para facilitar el análisis.  
- **Configuración sencilla** - Parámetros personalizables mediante `config.ini` para ajustar el alcance, formato de logs y modos de operación.  
- **Compatibilidad con Linux** - Implementado y probado en sistemas Linux.  
- **Captura del portapapeles** - Registro opcional del contenido del portapapeles para análisis de fugas de datos en pruebas controladas.  
- **Envío de registros por correo (opcional y configurable)** - Mecanismo opcional para enviar informes a una cuenta autorizada; deshabilitado por defecto y requiere credenciales y consentimiento.
> 📎 [**Ver _anexo 1_ para configuración de SMTPServer**](#anexo-1-Configuración-SMTP-Server)
---

##  Instalación

Para poner en marcha la herramienta, necesitarás tener **Python 3** instalado en tu sistema.

1. **Clona el repositorio:**
    ```bash
    git clone https://github.com/Sote19/Linux_Keylogger
    cd Linux_Keylogger
    ```

2. **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    
3. **Dale permisos de ejecución al script (Linux/macOS):**
   ```bash
   chmod +x keylogger.py
   chmod +x run_keylogger.py
   chmod +x cleanup.sh
   ```
   
4. **Configura el archivo de parámetros:**
    En el archivo `config.ini` puedes modificar todas las líneas **no comentadas** (`;` al inicio) para personalizar el comportamiento de la herramienta, como la ruta del archivo de registro, el modo de ejecución o las opciones de envío por correo.

---

## Uso Básico

Para ejecutar la herramienta, simplemente inicia el script principal desde la terminal:

```bash
python3 run_keylogger.py
```
El programa se ejecutará en segundo plano y comenzará a registrar las pulsaciones de teclado según la configuración definida en ```config.ini```.

Para detener el programa de manera manual, habrá que hacer la siguiente combinación de teclas: ```ctrl + shift + esc```

## Estructura del proyecto
```bash
ENTI_keylogger/
│
├── keylogger.py       # Script principal
├── run_keylogger.py   # Script que pone en marcha el Keylogger
├── cleanup.sh         # Script que elimina el rastro
├── config.ini         # Archivo de configuración (editable)
├── keylog.txt         # Archivo de registro generado (automático, definido en config.ini)
├── requirements.txt   # Dependencias necesarias
└── README.md          # Documentación del proyecto
```
# Anexos
## Anexo 1 (Configuración SMTP Server)
<details>
  <summary>Ver anexo 🔽</summary>
  
  Para poder recibir los reportes por correo, es necesario utilizar una **Contraseña de aplicación** en lugar de la contraseña habitual de Gmail.  
  Esto se debe a que Gmail bloquea el acceso SMTP directo por motivos de seguridad.

  ### Pasos para generarla
  
  1. Accede a la **configuración de tu cuenta de Google** (https://myaccount.google.com/).
  2. En el menú lateral, ve al apartado **Seguridad**.
  3. Activa la **verificación en dos pasos** (2FA).  
     ⚠️ *Durante este proceso, será necesario añadir un número de teléfono.*
  4. Una vez activado el 2FA, vuelve a la configuración y busca **“Contraseñas de aplicación”** en el buscador superior.
  5. Crea una nueva contraseña de aplicación y asigna un nombre identificativo (por ejemplo, *SMTP Script*).
  6. Google te mostrará una contraseña con este formato: xxxx xxxx xxxx xxxx

  Guarda esa contraseña, ya que será la que uses en el archivo `config.ini` para el parámetro `password`.
  
</details>

---
