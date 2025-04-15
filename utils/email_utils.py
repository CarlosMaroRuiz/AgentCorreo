# utils/email_utils.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_USERNAME, EMAIL_PASSWORD

def send_email(to: str, subject: str, body: str, is_html: bool = False,
               smtp_server: str = None, smtp_port: int = None, 
               username: str = None, password: str = None) -> str:
    """Envía un correo electrónico usando SMTP.
    
    Args:
        to (str): Dirección de correo del destinatario
        subject (str): Asunto del correo
        body (str): Contenido del correo
        is_html (bool): Indica si el contenido es HTML
        smtp_server (str, opcional): Servidor SMTP
        smtp_port (int, opcional): Puerto SMTP
        username (str, opcional): Usuario del correo
        password (str, opcional): Contraseña del correo
        
    Returns:
        str: Mensaje de resultado
    """
    # Usar variables de entorno si no se proporcionan parámetros
    smtp_server = smtp_server or EMAIL_SMTP_SERVER
    smtp_port = smtp_port or EMAIL_SMTP_PORT
    username = username or EMAIL_USERNAME
    password = password or EMAIL_PASSWORD
    
    if not all([smtp_server, smtp_port, username, password]):
        return "Error: Faltan credenciales de correo en el entorno"
    
    # Crear un mensaje multipart para soportar tanto texto como HTML
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = to
    
    # Adjuntar la versión de texto plano (como respaldo)
    plain_text = body
    if is_html:
        # Si es HTML, intentar extraer texto plano básico
        import re
        plain_text = re.sub('<.*?>', ' ', body)
        plain_text = re.sub('\\s+', ' ', plain_text).strip()
    
    msg.attach(MIMEText(plain_text, 'plain', 'utf-8'))
    
    # Si es HTML, adjuntar la versión HTML
    if is_html:
        msg.attach(MIMEText(body, 'html', 'utf-8'))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, [to], msg.as_string())
        return "Correo enviado exitosamente."
    except Exception as e:
        return f"Error al enviar el correo: {str(e)}"