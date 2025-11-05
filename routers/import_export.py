from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd, io, csv
from database import get_db
import models

router = APIRouter(prefix="/import-export", tags=["Import/Export"])

@router.post("/invoices/upload")
async def import_invoices(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, f"Failed to read file: {e}")

    required = {"project_id","amount","issued_date","due_date","paid_status"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(400, f"Missing required columns. Found: {df.columns.tolist()}")

    inserted = 0
    for _, row in df.iterrows():
        inv = models.Invoice(
            project_id=row["project_id"],
            amount=row["amount"],
            issued_date=row["issued_date"],
            due_date=row["due_date"],
            paid_status=row["paid_status"]
        )
        db.add(inv)
        inserted += 1
    db.commit()
    return {"message": f"Imported {inserted} invoices"}

@router.get("/invoices/export")
def export_invoices(db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id","project_id","amount","issued_date","due_date","paid_status"])
    for i in invoices:
        writer.writerow([i.id, i.project_id, i.amount, i.issued_date, i.due_date, i.paid_status])
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="text/csv",
                             headers={"Content-Disposition":"attachment; filename=invoices.csv"})