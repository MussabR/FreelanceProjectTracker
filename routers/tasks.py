from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# CREATE
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "status": "success",
        "message": "Task created successfully",
        "data": {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "due_date": str(new_task.due_date),
            "completed": new_task.completed,
            "project_id": new_task.project_id
        }
    }


# LIST ALL
@router.get("/list", status_code=status.HTTP_200_OK)
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "due_date": str(t.due_date) if t.due_date else None,
            "completed": t.completed,
            "project_id": t.project_id
        }
        for t in tasks
    ]
    return {"status": "success", "count": len(data), "data": data}


# BY PROJECT
@router.get("/by-project/{project_id}", status_code=status.HTTP_200_OK)
def get_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = db.query(models.Task).filter(models.Task.project_id == project_id).all()
    data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "due_date": str(t.due_date) if t.due_date else None,
            "completed": t.completed
        }
        for t in tasks
    ]
    return {"status": "success", "project": project.title, "count": len(data), "data": data}


# UPDATE
@router.put("/update/{id}", status_code=status.HTTP_200_OK)
def update_task(id: int, updated_data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return {"status": "success", "message": "Task updated successfully"}


# DELETE
@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"status": "success", "message": f"Task ID {id} deleted successfully"}


# SUMMARY
@router.get("/summary/{project_id}", status_code=status.HTTP_200_OK)
def get_task_summary(project_id: int, db: Session = Depends(get_db)):
    total = db.query(models.Task).filter(models.Task.project_id == project_id).count()
    if total == 0:
        raise HTTPException(status_code=404, detail="No tasks found for this project")

    completed = db.query(models.Task).filter(
        models.Task.project_id == project_id, models.Task.completed == True
    ).count()

    percentage = round((completed / total) * 100, 2)
    return {
        "status": "success",
        "summary": {
            "project_id": project_id,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_percentage": f"{percentage}%"
        }
    }