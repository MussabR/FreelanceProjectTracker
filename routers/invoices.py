from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from fastapi.responses import StreamingResponse
from utils.pdf_generator import generate_invoice_pdf
import models, schemas
from database import get_db

router = APIRouter(prefix="/invoices", tags=["Invoices"])


# -------------------------------------------------------------
# POST /invoices/create
# -------------------------------------------------------------
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    try:
        project = db.query(models.Project).filter(models.Project.id == invoice.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        new_invoice = models.Invoice(**invoice.model_dump())
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

        return {
            "status": "success",
            "message": "Invoice created successfully",
            "data": {
                "id": new_invoice.id,
                "project_id": new_invoice.project_id,
                "amount": new_invoice.amount,
                "issued_date": str(new_invoice.issued_date),
                "due_date": str(new_invoice.due_date),
                "paid_status": new_invoice.paid_status,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# GET /invoices/list
# -------------------------------------------------------------
@router.get("/list", status_code=status.HTTP_200_OK)
def get_all_invoices(db: Session = Depends(get_db)):
    try:
        invoices = db.query(models.Invoice).all()
        data = [
            {
                "id": inv.id,
                "project_id": inv.project_id,
                "amount": inv.amount,
                "issued_date": str(inv.issued_date),
                "due_date": str(inv.due_date),
                "paid_status": inv.paid_status,
            }
            for inv in invoices
        ]

        return {
            "status": "success",
            "message": "Invoices retrieved successfully",
            "count": len(data),
            "data": data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# GET /invoices/by-project/{project_id}
# -------------------------------------------------------------
@router.get("/by-project/{project_id}", status_code=status.HTTP_200_OK)
def get_invoices_by_project(project_id: int, db: Session = Depends(get_db)):
    try:
        invoices = db.query(models.Invoice).filter(models.Invoice.project_id == project_id).all()
        if not invoices:
            raise HTTPException(status_code=404, detail="No invoices found for this project")

        data = [
            {
                "id": inv.id,
                "amount": inv.amount,
                "issued_date": str(inv.issued_date),
                "due_date": str(inv.due_date),
                "paid_status": inv.paid_status,
            }
            for inv in invoices
        ]

        return {
            "status": "success",
            "message": f"Invoices for Project ID {project_id} retrieved successfully",
            "count": len(data),
            "data": data,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# PUT /invoices/update/{id}
# -------------------------------------------------------------
@router.put("/update/{id}", status_code=status.HTTP_200_OK)
def update_invoice(id: int, updated_data: schemas.InvoiceUpdate, db: Session = Depends(get_db)):
    try:
        invoice = db.query(models.Invoice).filter(models.Invoice.id == id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(invoice, key, value)

        db.commit()
        db.refresh(invoice)

        return {
            "status": "success",
            "message": "Invoice updated successfully",
            "data": {
                "id": invoice.id,
                "project_id": invoice.project_id,
                "amount": invoice.amount,
                "issued_date": str(invoice.issued_date),
                "due_date": str(invoice.due_date),
                "paid_status": invoice.paid_status,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# DELETE /invoices/delete/{id}
# -------------------------------------------------------------
@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_invoice(id: int, db: Session = Depends(get_db)):
    try:
        invoice = db.query(models.Invoice).filter(models.Invoice.id == id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        db.delete(invoice)
        db.commit()

        return {"status": "success", "message": f"Invoice {id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# GET /invoices/summary
# -------------------------------------------------------------
@router.get("/summary", status_code=status.HTTP_200_OK)
def get_invoice_summary(db: Session = Depends(get_db)):
    try:
        total_billed = db.query(func.sum(models.Invoice.amount)).scalar() or 0
        total_paid = db.query(func.sum(models.Invoice.amount)).filter(models.Invoice.paid_status == "paid").scalar() or 0
        total_unpaid = db.query(func.sum(models.Invoice.amount)).filter(models.Invoice.paid_status == "unpaid").scalar() or 0

        return {
            "status": "success",
            "message": "Invoice summary retrieved successfully",
            "summary": {
                "total_billed": total_billed,
                "total_paid": total_paid,
                "total_unpaid": total_unpaid,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# GET /invoices/overdue
# -------------------------------------------------------------
@router.get("/overdue", status_code=status.HTTP_200_OK)
def get_overdue_invoices(db: Session = Depends(get_db)):
    try:
        today = date.today()
        overdue = db.query(models.Invoice).filter(
            models.Invoice.due_date < today,
            models.Invoice.paid_status != "paid"
        ).all()

        data = [
            {
                "id": inv.id,
                "project_id": inv.project_id,
                "amount": inv.amount,
                "issued_date": str(inv.issued_date),
                "due_date": str(inv.due_date),
                "paid_status": inv.paid_status,
            }
            for inv in overdue
        ]

        return {
            "status": "success",
            "message": "Overdue invoices retrieved successfully",
            "count": len(data),
            "data": data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# -------------------------------------------------------------
# GET /invoices/pdf/{id}
# -------------------------------------------------------------
@router.get("/pdf/{id}", status_code=status.HTTP_200_OK)
def get_invoice_pdf(id: int, db: Session = Depends(get_db)):
    try:
        inv = db.query(models.Invoice).filter(models.Invoice.id == id).first()
        if not inv:
            raise HTTPException(status_code=404, detail="Invoice not found")

        pdf = generate_invoice_pdf(inv)
        return StreamingResponse(
            pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoice_{id}.pdf"},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating invoice PDF: {e}")