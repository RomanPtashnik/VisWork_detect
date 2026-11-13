from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ----- Auth -----
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ----- Employee -----
class EmployeeBase(BaseModel):
    name: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ----- Attendance -----
class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: datetime
    check_in: Optional[datetime]
    check_out: Optional[datetime]
    worked_hours: Optional[float]

    class Config:
        from_attributes = True