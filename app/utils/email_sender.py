import smtplib
from email.message import EmailMessage
from app.core.config import settings


class EmailNotConfigured(Exception):
    """Raised when SMTP settings are missing."""


def _send_with_settings(host, port, username, password, sender, message, use_ssl: bool):
    if use_ssl:
        with smtplib.SMTP_SSL(host, port, timeout=10) as server:
            if username and password:
                server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(message)


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

    port_int = int(port)
    use_ssl = port_int == 465
    try:
        _send_with_settings(host, port_int, username, password, sender, message, use_ssl)
        return
    except Exception as exc:
        # Fallback to SSL on 465 if initial attempt fails and not already SSL
        if not use_ssl and port_int != 465:
            try:
                _send_with_settings(host, 465, username, password, sender, message, True)
                return
            except Exception:
                pass
        raise RuntimeError(f"Failed to send email: {exc}") from exc
