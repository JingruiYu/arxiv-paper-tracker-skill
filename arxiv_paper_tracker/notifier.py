"""Optional notification backends."""

from __future__ import annotations

import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from arxiv_paper_tracker.config import EmailConfig


def maybe_send_email(markdown_text: str, email_config: EmailConfig) -> bool:
    """Send digest by email when enabled in config.

    Credentials are read only from the user-provided config file. Email is disabled
    by default so public users can run the tracker without configuring SMTP.
    """
    if not email_config.enabled:
        return False
    _validate_email_config(email_config)

    message = MIMEMultipart("alternative")
    message["Subject"] = email_config.subject
    message["From"] = email_config.sender or email_config.username
    message["To"] = ", ".join(email_config.receivers)
    message.attach(MIMEText(markdown_text, "plain", "utf-8"))
    message.attach(MIMEText(_markdown_to_simple_html(markdown_text), "html", "utf-8"))

    if email_config.use_ssl:
        with smtplib.SMTP_SSL(email_config.smtp_host, email_config.smtp_port) as server:
            server.login(email_config.username, email_config.password)
            server.sendmail(message["From"], email_config.receivers, message.as_string())
    else:
        with smtplib.SMTP(email_config.smtp_host, email_config.smtp_port) as server:
            server.starttls()
            server.login(email_config.username, email_config.password)
            server.sendmail(message["From"], email_config.receivers, message.as_string())
    return True


def _validate_email_config(email_config: EmailConfig) -> None:
    required_fields = {
        "smtp_host": email_config.smtp_host,
        "username": email_config.username,
        "password": email_config.password,
        "receivers": email_config.receivers,
    }
    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        raise ValueError(f"email.enabled=true but missing fields: {', '.join(missing_fields)}")


def _markdown_to_simple_html(markdown_text: str) -> str:
    lines = []
    for line in markdown_text.splitlines():
        escaped = html.escape(line)
        if escaped.startswith("# "):
            lines.append(f"<h1>{escaped[2:]}</h1>")
        elif escaped.startswith("## "):
            lines.append(f"<h2>{escaped[3:]}</h2>")
        elif escaped.startswith("- "):
            lines.append(f"<p>{escaped}</p>")
        elif not escaped.strip():
            lines.append("<br>")
        else:
            lines.append(f"<p>{escaped}</p>")
    return "<html><body>" + "\n".join(lines) + "</body></html>"
