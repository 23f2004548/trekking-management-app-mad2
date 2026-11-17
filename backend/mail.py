import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER_HOST = os.getenv("SMTP_SERVER_HOST", "localhost")
SMTP_SERVER_PORT = int(os.getenv("SMTP_SERVER_PORT", 1025))
SENDER_ADDRESS = "noreply@trekflow.com"


def send_email(to_address, subject, message, content="html", attachment_file=None):
    """
    Sends an email using standard SMTP.
    If local SMTP server (e.g. MailHog) is not running, gracefully logs the email
    to prevent Celery jobs from breaking.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = subject

        if content == "html":
            msg.attach(MIMEText(message, "html"))
        else:
            msg.attach(MIMEText(message, "plain"))

        if attachment_file and os.path.exists(attachment_file):
            with open(attachment_file, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_file)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT, timeout=3)
        s.send_message(msg)
        s.quit()
        print(f"[MAIL] Sent email to {to_address} with subject '{subject}'")
        return True
    except Exception as e:
        # Graceful fallback: log to dispatched mail log
        log_dir = os.path.join(os.getcwd(), "instance", "mail_logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "sent_emails.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- [MAIL TO: {to_address} | SUBJECT: {subject}] ---\n{message}\n")
        print(f"[MAIL FALLBACK] Saved email to {log_file} (SMTP not running: {e})")
        return True
