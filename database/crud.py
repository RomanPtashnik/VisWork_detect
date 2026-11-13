import datetime
import numpy as np
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256
from .models import User, Employee, Attendance

def authenticate_admin(session: Session, username: str, password: str) -> bool:
    user = session.query(User).filter(User.username == username).first()
    if user and pbkdf2_sha256.verify(password, user.password_hash):
        return True
    return False

def cosine_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_employee_by_embedding(session: Session, embedding, threshold=0.6):
    employees = session.query(Employee).all()
    if not employees:
        return None
    best_match = None
    best_dist = float('inf')
    for emp in employees:
        dist = cosine_distance(embedding, emp.face_embedding)
        if dist < best_dist:
            best_dist = dist
            best_match = emp
    if best_dist < threshold:
        return best_match
    return None

def record_attendance(session: Session, employee_id: int, lunch_break_minutes: int = 60):
    today = datetime.date.today()
    now = datetime.datetime.now()
    attendance = session.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date == today
    ).first()

    if not attendance:
        attendance = Attendance(employee_id=employee_id, date=today, check_in=now)
        session.add(attendance)
        session.commit()
        return "check_in", now, None
    else:
        if attendance.check_in and not attendance.check_out:
            attendance.check_out = now
            delta = now - attendance.check_in
            total_hours = delta.total_seconds() / 3600
            worked = total_hours - (lunch_break_minutes / 60)
            if worked < 0:
                worked = 0
            attendance.worked_hours = worked
            session.commit()
            return "check_out", now, worked
        else:
            return "already_closed", None, None