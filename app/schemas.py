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


class RoomType(str, Enum):
    single = "single"
    double = "double"
    triple = "triple"
    quad = "quad"
    ensuite = "ensuite"


class ApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class MaintenanceStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.student


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RoomApplicationCreate(BaseModel):
    room_id: int
    notes: str | None = Field(default=None, max_length=1000)


class RoomCreate(BaseModel):
    number: str = Field(..., max_length=32)
    room_type: RoomType
    capacity: int = Field(..., gt=0)
    is_available: bool = True
    description: str | None = Field(default=None, max_length=2000)


class RoomUpdate(BaseModel):
    number: str | None = Field(default=None, max_length=32)
    room_type: RoomType | None = None
    capacity: int | None = Field(default=None, gt=0)
    is_available: bool | None = None
    description: str | None = Field(default=None, max_length=2000)


class RoomBase(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    number: str
    room_type: str
    capacity: int
    is_available: bool
    description: str | None


class RoomOut(RoomBase):
    occupied_beds: int
    available_beds: int


class MaintenanceRequestCreate(BaseModel):
    title: str = Field(..., max_length=128)
    description: str = Field(..., min_length=5)


class MaintenanceRequestStatusUpdate(BaseModel):
    status: MaintenanceStatus


class MaintenanceRequestOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: str
    status: MaintenanceStatus
    created_at: datetime


class PaymentInitiate(BaseModel):
    amount: Decimal
    phone_number: str = Field(..., max_length=32)


class PaymentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    phone_number: str
    created_at: datetime


class RoomApplicationOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    room_id: int
    student_id: int
    status: ApplicationStatus
    notes: str | None
    created_at: datetime


class AdminApplicationUpdate(BaseModel):
    status: ApplicationStatus
    notes: str | None = Field(default=None, max_length=1000)


class OccupancyReport(BaseModel):
    total_rooms: int
    total_capacity: int
    occupied_beds: int
    available_beds: int
    occupancy_rate: float
    unavailable_rooms: int


class PaymentReport(BaseModel):
    total_payments: int
    completed_payments: int
    pending_payments: int
    failed_payments: int
    total_collected: Decimal
    pending_amount: Decimal


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
