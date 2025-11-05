from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


# ------------------- CLIENT SCHEMAS -------------------
class ClientBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    company_name: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company_name: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ------------------- PROJECT SCHEMAS -------------------
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    client_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "planned"
    budget: Optional[float] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    budget: Optional[float] = None


class ProjectResponse(ProjectBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ------------------- TASK SCHEMAS -------------------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    due_date: Optional[date] = None
    completed: Optional[bool] = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ------------------- INVOICE SCHEMAS -------------------

class InvoiceBase(BaseModel):
    project_id: int
    amount: float
    issued_date: Optional[date] = None
    due_date: Optional[date] = None
    paid_status: Optional[str] = "unpaid"


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    amount: Optional[float] = None
    issued_date: Optional[date] = None
    due_date: Optional[date] = None
    paid_status: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    # class Config:
    #     from_attributes = True