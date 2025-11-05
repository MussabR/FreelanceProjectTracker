from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total_clients = db.query(models.Client).count()
    total_projects = db.query(models.Project).count()
    total_tasks = db.query(models.Task).count()
    total_invoices = db.query(models.Invoice).count()

    total_billed = db.query(func.sum(models.Invoice.amount)).scalar() or 0
    total_paid = db.query(func.sum(models.Invoice.amount)).filter(models.Invoice.paid_status == "paid").scalar() or 0

    completion_rate = db.query(func.count()).filter(models.Task.completed == True).scalar() or 0

    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "total_invoices": total_invoices,
        "total_billed": float(total_billed),
        "total_paid": float(total_paid),
        "outstanding": float(total_billed - total_paid),
        "completion_rate": completion_rate
    }