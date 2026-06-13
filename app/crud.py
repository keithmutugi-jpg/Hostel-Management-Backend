from sqlalchemy.orm import Session

from app.models import User, Room, RoomApplication, Payment, MaintenanceRequest, UserRole, PaymentStatus
from app.security import get_password_hash, verify_password


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


def list_available_rooms(db: Session) -> list[Room]:
    return db.query(Room).filter(Room.is_available.is_(True)).all()


def create_maintenance_request(db: Session, student_id: int, title: str, description: str) -> MaintenanceRequest:
    request = MaintenanceRequest(student_id=student_id, title=title, description=description)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_maintenance_requests_for_student(db: Session, student_id: int) -> list[MaintenanceRequest]:
    return db.query(MaintenanceRequest).filter(MaintenanceRequest.student_id == student_id).order_by(MaintenanceRequest.created_at.desc()).all()


def create_payment(db: Session, student_id: int, amount: float, phone_number: str, checkout_request_id: str | None = None) -> Payment:
    payment = Payment(student_id=student_id, amount=amount, phone_number=phone_number, checkout_request_id=checkout_request_id)
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
    return application


def list_maintenance_requests(db: Session) -> list[MaintenanceRequest]:
    return db.query(MaintenanceRequest).order_by(MaintenanceRequest.created_at.desc()).all()
