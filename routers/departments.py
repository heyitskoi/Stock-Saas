from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Department, User
from auth import require_role
from schemas import DepartmentCreate, DepartmentResponse

router = APIRouter(prefix="/api/departments")

admin_or_manager = require_role(["admin", "manager"])


@router.get("/public", response_model=list[DepartmentResponse])
def public_list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()


@router.post("/", response_model=DepartmentResponse)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    if db.query(Department).filter(Department.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Department already exists")
    dept = Department(name=payload.name, icon=payload.icon)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/", response_model=list[DepartmentResponse])
def list_departments(
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    return db.query(Department).all()


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    dept.name = payload.name
    dept.icon = payload.icon
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(admin_or_manager),
):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(dept)
    db.commit()
    return {"detail": "Department deleted"}
