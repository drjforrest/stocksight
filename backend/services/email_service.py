import smtplib
import os
from email.message import EmailMessage
from typing import Optional

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

class EmailError(Exception):
    """Custom exception for email-related errors"""
    pass

def send_report(recipient_email: str, pdf_path: str) -> None:
    """Sends the generated PDF report via email
    
    Args:
        recipient_email: Email address to send the report to
        pdf_path: Path to the PDF file to send
        
    Raises:
        EmailError: If email credentials are missing or sending fails
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise EmailError("Missing email credentials. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables.")

    msg = EmailMessage()
    msg["Subject"] = "Your StockSight Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    msg.set_content("Attached is your StockSight competitor analysis report.")

    with open(pdf_path, "rb") as pdf_file:
        msg.add_attachment(pdf_file.read(), maintype="application", subtype="pdf", filename="StockSight_Report.pdf")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # type checker now knows these are str
            server.send_message(msg)
    except smtplib.SMTPException as e:
        raise EmailError(f"Failed to send email: {str(e)}")