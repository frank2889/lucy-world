from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {'1', 'true', 'yes', 'on'}


def send_email(to_email: str, subject: str, body: str) -> None:
    host = (os.getenv('SMTP_HOST') or '').strip()
    port = int(os.getenv('SMTP_PORT') or '587')
    user = (os.getenv('SMTP_USERNAME') or '').strip() or None
    password = (os.getenv('SMTP_PASSWORD') or '').strip() or None
    sender = (os.getenv('SMTP_FROM') or 'no-reply@lucy.world').strip()
    reply_to = (os.getenv('SMTP_REPLY_TO') or '').strip() or None
    use_ssl = _env_flag('SMTP_USE_SSL', default=False)
    use_tls = _env_flag('SMTP_USE_TLS', default=not use_ssl)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    if reply_to:
        msg['Reply-To'] = reply_to
    msg.set_content(body)

    if not host:
        logger.warning('SMTP_HOST is not configured; logging email instead of sending')
        print(f"[EMAIL:MISSING_CONFIG] To: {to_email}\nSubject: {subject}\n\n{body}")
        return

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=10) as server:
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=10) as server:
                if use_tls:
                    server.starttls()
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        logger.info('Sent email to %s via SMTP server %s:%s', to_email, host, port)
    except Exception as exc:  # pragma: no cover - network dependent
        logger.exception('Failed to deliver email to %s via SMTP', to_email)
        print(f"[EMAIL:FAILED:{exc}] To: {to_email}\nSubject: {subject}\n\n{body}")
