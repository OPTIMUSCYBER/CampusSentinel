from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.lab import Lab
from app.schemas.lab import LabCreate, LabRead

router = APIRouter()

@router.post("", response_model=LabRead)
def create_lab(payload: LabCreate, db: Session = Depends(get_db)):
    existing = db.query(Lab).filter(Lab.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lab name already exists")
    
    lab = Lab(name=payload.name, location=payload.location)
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab

@router.get("", response_model=List[LabRead])
def list_labs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    labs = db.query(Lab).offset(skip).limit(limit).all()
    return labs
