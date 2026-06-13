from enum import Enum
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str | None = None


class UserRole(str, Enum):
    student = "student"
    admin = "admin"


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.student


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RoomApplicationCreate(BaseModel):
    room_id: int
    notes: str | None = None


class RoomCreate(BaseModel):
    number: str = Field(..., max_length=32)
    room_type: str
    capacity: int = Field(..., gt=0)
    description: str | None = None


class RoomBase(BaseModel):
    id: int
    number: str
    room_type: str
    capacity: int
    is_available: bool
    description: str | None

    class Config:
        from_attributes = True


class MaintenanceRequestCreate(BaseModel):
    title: str = Field(..., max_length=128)
    description: str


class MaintenanceRequestOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentInitiate(BaseModel):
    amount: Decimal
    phone_number: str = Field(..., max_length=32)


class PaymentOut(BaseModel):
    id: int
    amount: Decimal
    currency: str
    status: str
    phone_number: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoomApplicationOut(BaseModel):
    id: int
    room_id: int
    student_id: int
    status: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminApplicationUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|approved|rejected)$")
    notes: str | None = None


class MpesaCallbackMetaField(BaseModel):
    Name: str
    Value: str | int


class MpesaCallbackData(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: int
    ResultDesc: str
    CallbackMetadata: dict | None = None


class MpesaCallbackBody(BaseModel):
    stkCallback: MpesaCallbackData


class MpesaCallback(BaseModel):
    Body: MpesaCallbackBody
