from pydantic import BaseModel, EmailStr, ConfigDict


class StudentCreate(BaseModel):
    roll_number: str
    full_name: str
    email: EmailStr
    department: str
    semester: int


class StudentResponse(BaseModel):
    id: int
    roll_number: str
    full_name: str
    email: EmailStr
    department: str
    semester: int
    attendance_percentage: float

    model_config = ConfigDict(from_attributes=True)