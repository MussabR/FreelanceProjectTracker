from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import engine, Base
from routers import (
    clients, projects, tasks, invoices, frontend, dashboard,
    import_export, auth, frontend_dashboard
)

# Create all tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freelance Project Tracker")

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(clients.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(invoices.router)
app.include_router(frontend.router)
app.include_router(dashboard.router)
app.include_router(import_export.router)
# app.include_router(auth.router)
app.include_router(frontend_dashboard.router)

# Default route (Dashboard)
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})