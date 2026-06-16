from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_current_active_user, get_db
from app.schemas import (
    MaintenanceRequestCreate,
    MaintenanceRequestOut,
    PaymentInitiate,
    PaymentOut,
    RoomApplicationCreate,
    RoomApplicationOut,
    RoomOut,
)
from app.services import mpesa

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/rooms", response_model=list[RoomOut], summary="Browse available rooms")
def list_rooms(db: Session = Depends(get_db)):
    return crud.list_available_rooms(db)


@router.post("/applications", response_model=RoomApplicationOut, status_code=status.HTTP_201_CREATED, summary="Submit a room application")
def apply_room(application_in: RoomApplicationCreate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id=application_in.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.available_beds <= 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room is not currently available")
    return crud.create_room_application(db, student_id=current_user.id, room_id=application_in.room_id, notes=application_in.notes)


@router.get("/maintenance", response_model=list[MaintenanceRequestOut], summary="List my maintenance requests")
def list_my_maintenance(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return crud.get_maintenance_requests_for_student(db, student_id=current_user.id)


@router.post("/maintenance", response_model=MaintenanceRequestOut, status_code=status.HTTP_201_CREATED, summary="Submit a maintenance request")
def submit_maintenance(request_in: MaintenanceRequestCreate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return crud.create_maintenance_request(db, student_id=current_user.id, title=request_in.title, description=request_in.description)


@router.post("/payments/mpesa", response_model=PaymentOut, status_code=status.HTTP_201_CREATED, summary="Start an M-Pesa payment")
def start_mpesa_payment(payment_in: PaymentInitiate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    try:
        response = mpesa.initiate_stk_push(
            phone_number=payment_in.phone_number,
            amount=float(payment_in.amount),
            account_reference=f"HOSTEL-{current_user.id}",
            transaction_desc="Hostel fee payment",
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    checkout_request_id = response.get("CheckoutRequestID")
    if not checkout_request_id:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="M-Pesa did not return a checkout request ID")

    payment = crud.create_payment(
        db,
        student_id=current_user.id,
        amount=float(payment_in.amount),
        phone_number=payment_in.phone_number,
        checkout_request_id=checkout_request_id,
    )
    return payment


@router.get("/payments", response_model=list[PaymentOut], summary="List my payments")
def list_my_payments(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    return crud.list_payments(db, student_id=current_user.id)
