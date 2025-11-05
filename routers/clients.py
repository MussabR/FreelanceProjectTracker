from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
import models, schemas
from database import get_db

router = APIRouter(prefix="/clients", tags=["Clients"])

# ✅ CREATE CLIENT
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Client).filter(models.Client.email == client.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Client already exists")

    new_client = models.Client(**client.model_dump())
    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return {
        "status": "success",
        "message": "Client created successfully",
        "data": {
            "id": new_client.id,
            "name": new_client.name,
            "email": new_client.email,
            "phone": new_client.phone,
            "company": new_client.company_name

        }
    }


# ✅ LIST ALL CLIENTS
@router.get("/list", status_code=status.HTTP_200_OK)
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(models.Client).all()
    data = [
        {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone,"company_name": c.company_name}
        for c in clients
    ]
    return {"status": "success", "count": len(data), "data": data}


# ✅ GET CLIENT BY ID
@router.get("/get/{id}", status_code=status.HTTP_200_OK)
def get_client(id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "status": "success",
        "data": {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "company_name": client.company_name
        }
    }


# ✅ NEW: CLIENT INFO WITH RELATED PROJECTS
@router.get("/info/{id}", status_code=status.HTTP_200_OK)
def get_client_with_projects(id: int, db: Session = Depends(get_db)):
    client = (
        db.query(models.Client)
        .options(joinedload(models.Client.projects))
        .filter(models.Client.id == id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "status": "success",
        "message": "Client info with related projects retrieved successfully",
        "client": {
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "company":client.company_name
        },
        "projects": [
            {
                "id": p.id,
                "title": p.title,
                "status": p.status,
                "budget": p.budget,
                "description": p.description,
            }
            for p in client.projects
        ],
    }


# ✅ UPDATE CLIENT
@router.put("/update/{id}", status_code=status.HTTP_200_OK)
def update_client(id: int, update_data: schemas.ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(client, key, value)

    db.commit()
    db.refresh(client)
    return {"status": "success", "message": "Client updated successfully"}


# ✅ DELETE CLIENT
@router.delete("/delete/{id}", status_code=status.HTTP_200_OK)
def delete_client(id: int, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()
    return {"status": "success", "message": f"Client ID {id} deleted successfully"}