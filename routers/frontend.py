from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter(
    prefix="/web",
    tags=["Web Pages"]
)

templates = Jinja2Templates(directory="templates")

# ✅ Clients Page
# ------------------------------------------------
@router.get("/clients", response_class=HTMLResponse)
def show_clients(request: Request, db: Session = Depends(get_db)):
    clients = db.query(models.Client).all()
    return templates.TemplateResponse(
        "clients.html",
        {"request": request, "clients": clients}
    )


# ✅ Projects Page
# ------------------------------------------------
@router.get("/projects", response_class=HTMLResponse)
def show_projects(request: Request, db: Session = Depends(get_db)):
    projects = (
        db.query(models.Project)
        .join(models.Client, models.Client.id == models.Project.client_id)
        .add_columns(
            models.Project.id,
            models.Project.title,
            models.Project.status,
            models.Project.budget,
            models.Client.name.label("client_name"),
            models.Client.id.label("client_id")
        )
        .all()
    )
    return templates.TemplateResponse(
        "projects.html",
        {"request": request, "projects": projects}
    )


# ✅ Client Info Page (Single Client + Related Projects)
# ------------------------------------------------
@router.get("/clients/{id}", response_class=HTMLResponse)
def show_client_info(request: Request, id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        return templates.TemplateResponse(
            "404.html", {"request": request, "message": "Client not found"}
        )

    projects = db.query(models.Project).filter(models.Project.client_id == id).all()

    return templates.TemplateResponse(
        "client-info.html",
        {
            "request": request,
            "client": client,
            "projects": projects
        }
    )