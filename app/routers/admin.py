from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_current_active_admin, get_db
from app.models import RoomType
from app.schemas import (
    AdminApplicationUpdate,
    MaintenanceRequestOut,
    PaymentOut,
    RoomApplicationOut,
    RoomBase,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/applications", response_model=list[RoomApplicationOut])
def list_applications(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_room_applications(db)


@router.post("/applications/{application_id}/status", response_model=RoomApplicationOut)
def update_application_status(application_id: int, update_in: AdminApplicationUpdate, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    application = crud.get_room_application(db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return crud.update_room_application_status(db, application=application, status=update_in.status, notes=update_in.notes)


@router.get("/rooms", response_model=list[RoomBase])
def list_rooms(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_rooms(db)


@router.post("/rooms", response_model=RoomBase)
def create_room(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db), room_in: RoomBase = Depends()):
    return crud.create_room(db, number=room_in.number, room_type=RoomType(room_in.room_type), capacity=room_in.capacity, description=room_in.description)


@router.get("/maintenance", response_model=list[MaintenanceRequestOut])
def list_maintenance(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_maintenance_requests(db)


@router.get("/payments", response_model=list[PaymentOut])
def list_payments(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_payments(db)
