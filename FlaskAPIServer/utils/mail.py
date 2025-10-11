import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .. import config
from . import logger

logger = logger.setup(config.DEBUG, "MAIL", config.LOG_PATH)

def send_email(to_email, subject, text_body, html_body=None):
    msg = MIMEMultipart()
    msg['From'] = config.FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(text_body, 'plain'))

    if html_body:
        msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки email: {e}")
        return False