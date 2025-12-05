import smtplib
from email.message import EmailMessage
from typing import Optional
import requests
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
    # Provider 1: SendGrid (HTTPS)
    sg_key = settings.SENDGRID_API_KEY
    sg_from = settings.SENDGRID_FROM or settings.SMTP_FROM
    if sg_key and sg_from:
        try:
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {sg_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [{"to": [{"email": to_email}]}],
                    "from": {"email": sg_from},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}],
                },
                timeout=10,
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"SendGrid API error: {resp.status_code} {resp.text}")
            return
        except Exception as exc:
            raise RuntimeError(f"Failed to send email via SendGrid: {exc}") from exc

    # Provider 2: Resend (HTTPS)
    api_key = settings.RESEND_API_KEY
    api_from = settings.RESEND_FROM or settings.SMTP_FROM
    if api_key and api_from:
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "from": api_from,
                    "to": [to_email],
                    "subject": subject,
                    "text": body,
                },
                timeout=10,
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"Resend API error: {resp.status_code} {resp.text}")
            return
        except Exception as exc:
            raise RuntimeError(f"Failed to send email via Resend: {exc}") from exc

    # Provider 3: Mailtrap Send API (HTTPS)
    mt_token = settings.MAILTRAP_API_TOKEN
    mt_from = settings.MAILTRAP_FROM or settings.SMTP_FROM
    if mt_token and mt_from:
        try:
            resp = requests.post(
                "https://send.api.mailtrap.io/api/send",
                headers={
                    "Authorization": f"Bearer {mt_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": {"email": mt_from},
                    "to": [{"email": to_email}],
                    "subject": subject,
                    "text": body,
                },
                timeout=10,
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"Mailtrap API error: {resp.status_code} {resp.text}")
            return
        except Exception as exc:
            raise RuntimeError(f"Failed to send email via Mailtrap: {exc}") from exc

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
