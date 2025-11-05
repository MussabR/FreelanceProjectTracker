from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

def generate_invoice_pdf(invoice):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, 800, f"Invoice #{invoice.id}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 760, f"Project ID: {invoice.project_id}")
    c.drawString(50, 740, f"Amount: {invoice.amount}")
    c.drawString(50, 720, f"Issued: {invoice.issued_date}")
    c.drawString(50, 700, f"Due: {invoice.due_date}")
    c.drawString(50, 680, f"Status: {invoice.paid_status}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer