import smtplib
from email.message import EmailMessage
from app.core.config import settings


class EmailNotConfigured(Exception):
    """Raised when SMTP settings are missing."""


def send_email(to_email: str, subject: str, body: str):
    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    sender = settings.SMTP_FROM or username

    if not all([host, port, sender]):
        raise EmailNotConfigured("SMTP settings are not configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_email
    message.set_content(body)

    port = int(port)
    use_ssl = port == 465
    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port) as server:
                if username and password:
                    server.login(username, password)
                server.send_message(message)
        else:
            with smtplib.SMTP(host, port) as server:
                server.ehlo()
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(message)
    except Exception as exc:
        raise RuntimeError(f"Failed to send email: {exc}") from exc
