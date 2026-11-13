import io
import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from web import schemas   
from web.dependencies import get_db, get_current_user
from database.models import Employee, Attendance
from face_recognition.detector import YuNetDetector
from face_recognition.recognizer import ArcFaceRecognizer
import config

router = APIRouter(prefix="/employees", tags=["Employees"])

detector = YuNetDetector(config.YUNET_MODEL_PATH)
recognizer = ArcFaceRecognizer()

def get_embedding_from_image(image_bytes: bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    bboxes = detector.detect(img)
    if len(bboxes) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    x, y, w, h = bboxes[0]
    face_crop = img[y:y+h, x:x+w]
    if face_crop.size == 0:
        raise HTTPException(status_code=400, detail="Failed to crop face")
    embedding = recognizer.get_embedding(face_crop)
    return embedding

# ---------- GET список сотрудников ----------
@router.get("", response_model=List[schemas.EmployeeResponse])
@router.get("/", response_model=List[schemas.EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    employees = db.query(Employee).all()
    return employees

# ---------- POST создать сотрудника ----------
@router.post("", response_model=schemas.EmployeeResponse)
@router.post("/", response_model=schemas.EmployeeResponse)
def create_employee(
    name: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    existing = db.query(Employee).filter(Employee.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Employee with this name already exists")
    image_bytes = photo.file.read()
    embedding = get_embedding_from_image(image_bytes)
    new_employee = Employee(name=name, face_embedding=embedding)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

# ---------- PUT обновить сотрудника ----------
@router.put("/{employee_id}", response_model=schemas.EmployeeResponse)
def update_employee(
    employee_id: int,
    name: Optional[str] = None,
    photo: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if name:
        existing = db.query(Employee).filter(Employee.name == name, Employee.id != employee_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Name already taken by another employee")
        employee.name = name
    if photo:
        image_bytes = photo.file.read()
        embedding = get_embedding_from_image(image_bytes)
        employee.face_embedding = embedding
    db.commit()
    db.refresh(employee)
    return employee

# ---------- DELETE удалить сотрудника ----------
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"detail": "Employee deleted"}

# ---------- GET посещаемость сотрудника ----------
@router.get("/{employee_id}/attendance", response_model=List[schemas.AttendanceResponse])
def get_employee_attendance(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    records = db.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.date.desc()).all()
    return records