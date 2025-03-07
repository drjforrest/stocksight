import smtplib
import os
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_report(recipient_email, pdf_path):
    """Sends the generated PDF report via email"""
    msg = EmailMessage()
    msg["Subject"] = "Your StockSight Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    msg.set_content("Attached is your StockSight competitor analysis report.")

    with open(pdf_path, "rb") as pdf_file:
        msg.add_attachment(pdf_file.read(), maintype="application", subtype="pdf", filename="StockSight_Report.pdf")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)