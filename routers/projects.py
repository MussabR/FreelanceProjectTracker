from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import models, schemas
from database import get_db

router = APIRouter(prefix="/projects", tags=["Projects"])

# ✅ CREATE PROJECT
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == project.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_project = models.Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "status": "success",
        "message": "Project created successfully",
        "data": {
            "id": new_project.id,
            "title": new_project.title,
            "description": new_project.description,
            "status": new_project.status,
            "budget": new_project.budget,
        },
    }

# ✅ LIST ALL PROJECTS
@router.get("/list", status_code=status.HTTP_200_OK)
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).options(joinedload(models.Project.client)).all()
    data = [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "status": p.status,
            "budget": p.budget,
            "client": {
                "id": p.client.id if p.client else None,
                "name": p.client.name if p.client else None,
            },
        }
        for p in projects
    ]
    return {
        "status": "success",
        "message": "Projects retrieved successfully",
        "count": len(data),
        "data": data,
    }

# ✅ GET PROJECT BY ID
@router.get("/get/{id}", status_code=status.HTTP_200_OK)
def get_project(id: int, db: Session = Depends(get_db)):
    project = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.client),
            joinedload(models.Project.tasks),
            joinedload(models.Project.invoices),
        )
        .filter(models.Project.id == id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "status": "success",
        "data": {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "status": project.status,
            "budget": project.budget,
            "client": {
                "id": project.client.id,
                "name": project.client.name,
            } if project.client else None,
            "tasks": [{"id": t.id, "title": t.title, "completed": t.completed} for t in project.tasks],
            "invoices": [{"id": i.id, "amount": i.amount, "paid_status": i.paid_status} for i in project.invoices],
        },
    }

# ✅ PROJECTS BY CLIENT (for client-info page)
@router.get("/client-info/{client_id}", status_code=status.HTTP_200_OK)
def get_client_info_with_projects(client_id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    projects = db.query(models.Project).filter(models.Project.client_id == client_id).all()

    return {
        "status": "success",
        "message": "Client info and related projects retrieved successfully",
        "client": client
    }

# ✅ UPDATE PROJECT
@router.put("/update/{id}", status_code=status.HTTP_200_OK)
def update_project(id: int, project_data: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return {"status": "success", "message": "Project updated successfully"}

# ✅ DELETE PROJECT
@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_project(id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"status": "success", "message": f"Project {id} deleted successfully"}

# ✅ PROJECT SUMMARY
@router.get("/summary", status_code=status.HTTP_200_OK)
def project_summary(db: Session = Depends(get_db)):
    total_projects = db.query(models.Project).count()
    total_budget = db.query(func.sum(models.Project.budget)).scalar() or 0
    ongoing = db.query(models.Project).filter(models.Project.status == "ongoing").count()
    completed = db.query(models.Project).filter(models.Project.status == "completed").count()
    return {
        "status": "success",
        "summary": {
            "total_projects": total_projects,
            "ongoing": ongoing,
            "completed": completed,
            "total_budget": total_budget,
        },
    }