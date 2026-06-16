from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_current_active_admin, get_db
from app.models import RoomType as ModelRoomType
from app.schemas import (
    AdminApplicationUpdate,
    MaintenanceRequestOut,
    MaintenanceRequestStatusUpdate,
    OccupancyReport,
    PaymentOut,
    PaymentReport,
    RoomApplicationOut,
    RoomCreate,
    RoomOut,
    RoomUpdate,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/applications", response_model=list[RoomApplicationOut], summary="List room applications")
def list_applications(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_room_applications(db)


@router.patch("/applications/{application_id}/status", response_model=RoomApplicationOut, summary="Change an application status")
def update_application_status(application_id: int, update_in: AdminApplicationUpdate, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    application = crud.get_room_application(db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    if update_in.status == "approved":
        room = crud.get_room(db, room_id=application.room_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
        if application.status != "approved" and room.available_beds <= 0:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room has no available beds")
    return crud.update_room_application_status(db, application=application, status=update_in.status.value, notes=update_in.notes)


@router.post("/applications/{application_id}/status", response_model=RoomApplicationOut, include_in_schema=False)
def update_application_status_legacy(application_id: int, update_in: AdminApplicationUpdate, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return update_application_status(application_id=application_id, update_in=update_in, current_user=current_user, db=db)


@router.get("/rooms", response_model=list[RoomOut], summary="List all rooms")
def list_rooms(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_rooms(db)


@router.get("/rooms/{room_id}", response_model=RoomOut, summary="Get room details")
def get_room(room_id: int, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED, summary="Create a room")
def create_room(room_in: RoomCreate, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    try:
        return crud.create_room(
            db,
            number=room_in.number,
            room_type=ModelRoomType(room_in.room_type.value),
            capacity=room_in.capacity,
            is_available=room_in.is_available,
            description=room_in.description,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")


@router.patch("/rooms/{room_id}", response_model=RoomOut, summary="Update a room")
def update_room(room_id: int, room_in: RoomUpdate, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room_in.capacity is not None and room_in.capacity < room.occupied_beds:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Capacity cannot be below occupied beds")
    try:
        return crud.update_room(
            db,
            room=room,
            number=room_in.number,
            room_type=ModelRoomType(room_in.room_type.value) if room_in.room_type else None,
            capacity=room_in.capacity,
            is_available=room_in.is_available,
            description=room_in.description,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room number already exists")


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a room")
def delete_room(room_id: int, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id=room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    if room.applications:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room has applications and cannot be deleted")
    crud.delete_room(db, room=room)
    return None


@router.get("/maintenance", response_model=list[MaintenanceRequestOut], summary="List maintenance requests")
def list_maintenance(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_maintenance_requests(db)


@router.patch("/maintenance/{request_id}/status", response_model=MaintenanceRequestOut, summary="Update maintenance request status")
def update_maintenance_status(request_id: int, update_in: MaintenanceRequestStatusUpdate, current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    request = crud.get_maintenance_request(db, request_id=request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance request not found")
    return crud.update_maintenance_request_status(db, request=request, status=update_in.status.value)


@router.get("/payments", response_model=list[PaymentOut], summary="List payments")
def list_payments(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.list_payments(db)


@router.get("/reports/occupancy", response_model=OccupancyReport, summary="Get occupancy report")
def occupancy_report(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.get_occupancy_report(db)


@router.get("/reports/payments", response_model=PaymentReport, summary="Get payment report")
def payment_report(current_user=Depends(get_current_active_admin), db: Session = Depends(get_db)):
    return crud.get_payment_report(db)
