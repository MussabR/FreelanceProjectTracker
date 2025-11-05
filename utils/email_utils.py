import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from datetime import date
import models

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

def send_overdue_notifications(db):
    today = date.today()
    overdue = db.query(models.Invoice).filter(
        models.Invoice.due_date < today,
        models.Invoice.paid_status != "paid"
    ).all()

    for inv in overdue:
        client_email = inv.project.client.email
        subject = f"Invoice #{inv.id} Overdue"
        body = f"Dear Client,\n\nInvoice #{inv.id} was due on {inv.due_date}.\nPlease make the payment of {inv.amount}."
        send_email(client_email, subject, body)