from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum


class ProjectStatus(enum.Enum):
    planned = "planned"
    ongoing = "ongoing"
    completed = "completed"
    on_hold = "on_hold"


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(String(250))
    company_name = Column(String(100))

    projects = relationship("Project", back_populates="client", cascade="all, delete")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.planned)
    budget = Column(Float)

    client = relationship("Client", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete")
    invoices = relationship("Invoice", back_populates="project", cascade="all, delete")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    title = Column(String(150), nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    completed = Column(Boolean, default=False)

    project = relationship("Project", back_populates="tasks")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    amount = Column(Float, nullable=False)
    issued_date = Column(Date)
    due_date = Column(Date)
    paid_status = Column(String(20))  # paid / unpaid / overdue

    project = relationship("Project", back_populates="invoices")