from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str) -> None:
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT') or '587')
    user = os.getenv('SMTP_USERNAME')
    password = os.getenv('SMTP_PASSWORD')
    sender = os.getenv('SMTP_FROM') or 'no-reply@lucy.world'
    if not host or not user or not password:
        # Fallback: print to logs
        print(f"[EMAIL] To: {to_email}\nSubject: {subject}\n\n{body}")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
