import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

try:
    from config import LocalDevelopmentConfig
    SMTP_SERVER_HOST = getattr(LocalDevelopmentConfig, 'SMTP_SERVER', 'localhost')
    SMTP_SERVER_PORT = getattr(LocalDevelopmentConfig, 'SMTP_PORT', 1025)
    SENDER_ADDRESS = getattr(LocalDevelopmentConfig, 'SENDER_EMAIL', 'noreply@trekkingapp.com')
except Exception:
    SMTP_SERVER_HOST = "localhost"
    SMTP_SERVER_PORT = 1025 
    SENDER_ADDRESS = "noreply@trekkingapp.com"


def send_email(to_address, subject, message, content="html", attachment_file=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = subject

        if content == "html":
            msg.attach(MIMEText(message, "html"))
        else:
            msg.attach(MIMEText(message, "plain"))

        if attachment_file:
            with open(attachment_file, 'rb') as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename = {attachment_file}")
            msg.attach(part)

        s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT, timeout=5)
        s.send_message(msg)
        s.quit()
        print(f"Email sent successfully to {to_address}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_address}: {str(e)}")
        return False
