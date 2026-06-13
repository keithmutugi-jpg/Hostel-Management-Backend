from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, Text, Enum as SQLAEnum
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, Enum):
    student = "student"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(length=128), nullable=False)
    email = Column(String(length=256), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=256), nullable=False)
    role = Column(SQLAEnum(UserRole), default=UserRole.student, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    room_applications = relationship("RoomApplication", back_populates="student")
    payments = relationship("Payment", back_populates="user")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="student")


class RoomType(str, Enum):
    single = "single"
    double = "double"
    triple = "triple"
    quad = "quad"
    ensuite = "ensuite"


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(length=32), unique=True, index=True, nullable=False)
    room_type = Column(SQLAEnum(RoomType), nullable=False)
    capacity = Column(Integer, default=1, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    applications = relationship("RoomApplication", back_populates="room")


class RoomApplication(Base):
    __tablename__ = "room_applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    status = Column(String(length=32), default="pending", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("User", back_populates="room_applications")
    room = relationship("Room", back_populates="applications")


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(length=8), default="KES", nullable=False)
    status = Column(SQLAEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    mpesa_checkout_request_id = Column(String(length=128), nullable=True)
    mpesa_transaction_id = Column(String(length=128), nullable=True)
    phone_number = Column(String(length=32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="payments")


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(length=128), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(length=32), default="open", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    student = relationship("User", back_populates="maintenance_requests")
