from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import User, Room, RoomApplication, Payment, MaintenanceRequest, UserRole, PaymentStatus, RoomType
from app.security import get_password_hash, verify_password


APPROVED_APPLICATION_STATUS = "approved"


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, full_name: str, email: str, password: str, role: str = UserRole.student) -> User:
    hashed_password = get_password_hash(password)
    user = User(full_name=full_name, email=email, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_room_application(db: Session, student_id: int, room_id: int, notes: str | None = None) -> RoomApplication:
    application = RoomApplication(student_id=student_id, room_id=room_id, notes=notes)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_room(db: Session, room_id: int) -> Room | None:
    room = db.query(Room).filter(Room.id == room_id).first()
    if room:
        add_room_availability(db, room)
    return room


def count_approved_applications_for_room(db: Session, room_id: int) -> int:
    return (
        db.query(func.count(RoomApplication.id))
        .filter(
            RoomApplication.room_id == room_id,
            RoomApplication.status == APPROVED_APPLICATION_STATUS,
        )
        .scalar()
        or 0
    )


def add_room_availability(db: Session, room: Room) -> Room:
    occupied_beds = count_approved_applications_for_room(db, room.id)
    available_beds = max(room.capacity - occupied_beds, 0) if room.is_available else 0
    room.occupied_beds = occupied_beds
    room.available_beds = available_beds
    return room


def list_available_rooms(db: Session) -> list[Room]:
    rooms = db.query(Room).filter(Room.is_available.is_(True)).order_by(Room.number.asc()).all()
    return [add_room_availability(db, room) for room in rooms if count_approved_applications_for_room(db, room.id) < room.capacity]


def list_rooms(db: Session) -> list[Room]:
    rooms = db.query(Room).order_by(Room.id.asc()).all()
    return [add_room_availability(db, room) for room in rooms]


def create_room(db: Session, number: str, room_type: RoomType, capacity: int, is_available: bool = True, description: str | None = None) -> Room:
    room = Room(number=number, room_type=room_type, capacity=capacity, is_available=is_available, description=description)
    db.add(room)
    db.commit()
    db.refresh(room)
    return add_room_availability(db, room)


def update_room(
    db: Session,
    room: Room,
    number: str | None = None,
    room_type: RoomType | None = None,
    capacity: int | None = None,
    is_available: bool | None = None,
    description: str | None = None,
) -> Room:
    if number is not None:
        room.number = number
    if room_type is not None:
        room.room_type = room_type
    if capacity is not None:
        room.capacity = capacity
    if is_available is not None:
        room.is_available = is_available
    if description is not None:
        room.description = description
    db.add(room)
    db.commit()
    db.refresh(room)
    return add_room_availability(db, room)


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()


def get_room_application(db: Session, application_id: int) -> RoomApplication | None:
    return db.query(RoomApplication).filter(RoomApplication.id == application_id).first()


def create_maintenance_request(db: Session, student_id: int, title: str, description: str) -> MaintenanceRequest:
    request = MaintenanceRequest(student_id=student_id, title=title, description=description)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_maintenance_requests_for_student(db: Session, student_id: int) -> list[MaintenanceRequest]:
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.student_id == student_id).order_by(MaintenanceRequest.created_at.desc()).all()


def get_maintenance_request(db: Session, request_id: int) -> MaintenanceRequest | None:
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()


def update_maintenance_request_status(db: Session, request: MaintenanceRequest, status: str) -> MaintenanceRequest:
    request.status = status
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def create_payment(db: Session, student_id: int, amount: float, phone_number: str, checkout_request_id: str | None = None) -> Payment:
    payment = Payment(student_id=student_id, amount=amount, phone_number=phone_number, mpesa_checkout_request_id=checkout_request_id)
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_checkout_request_id(db: Session, checkout_request_id: str) -> Payment | None:
    return db.query(Payment).filter(Payment.mpesa_checkout_request_id == checkout_request_id).first()


def get_payment_by_id(db: Session, payment_id: int) -> Payment | None:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def update_payment_status(db: Session, payment: Payment, status: str, transaction_id: str | None = None) -> Payment:
    payment.status = status
    if transaction_id:
        payment.mpesa_transaction_id = transaction_id
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def list_payments(db: Session, student_id: int | None = None) -> list[Payment]:
    query = db.query(Payment)
    if student_id is not None:
        query = query.filter(Payment.student_id == student_id)
    return query.order_by(Payment.created_at.desc()).all()


def list_room_applications(db: Session) -> list[RoomApplication]:
    return db.query(RoomApplication).order_by(RoomApplication.created_at.desc()).all()


def update_room_application_status(db: Session, application: RoomApplication, status: str, notes: str | None = None) -> RoomApplication:
    application.status = status
    if notes is not None:
        application.notes = notes
    db.add(application)
    db.commit()
    db.refresh(application)
    recalculate_room_availability(db, application.room)
    return application


def list_maintenance_requests(db: Session) -> list[MaintenanceRequest]:
    return db.query(MaintenanceRequest).order_by(MaintenanceRequest.created_at.desc()).all()


def recalculate_room_availability(db: Session, room: Room) -> Room:
    occupied_beds = count_approved_applications_for_room(db, room.id)
    room.is_available = occupied_beds < room.capacity
    db.add(room)
    db.commit()
    db.refresh(room)
    return add_room_availability(db, room)


def get_occupancy_report(db: Session) -> dict:
    rooms = list_rooms(db)
    total_rooms = len(rooms)
    total_capacity = sum(room.capacity for room in rooms)
    occupied_beds = sum(room.occupied_beds for room in rooms)
    available_beds = sum(room.available_beds for room in rooms)
    unavailable_rooms = sum(1 for room in rooms if not room.is_available)
    occupancy_rate = round((occupied_beds / total_capacity) * 100, 2) if total_capacity else 0.0
    return {
        "total_rooms": total_rooms,
        "total_capacity": total_capacity,
        "occupied_beds": occupied_beds,
        "available_beds": available_beds,
        "occupancy_rate": occupancy_rate,
        "unavailable_rooms": unavailable_rooms,
    }


def get_payment_report(db: Session) -> dict:
    payments = list_payments(db)
    completed = [payment for payment in payments if payment.status == PaymentStatus.completed]
    pending = [payment for payment in payments if payment.status == PaymentStatus.pending]
    failed = [payment for payment in payments if payment.status == PaymentStatus.failed]
    return {
        "total_payments": len(payments),
        "completed_payments": len(completed),
        "pending_payments": len(pending),
        "failed_payments": len(failed),
        "total_collected": sum((Decimal(payment.amount) for payment in completed), Decimal("0")),
        "pending_amount": sum((Decimal(payment.amount) for payment in pending), Decimal("0")),
    }
