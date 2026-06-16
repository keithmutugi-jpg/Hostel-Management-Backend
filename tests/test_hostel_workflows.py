from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.main import app
from app.models import Payment, PaymentStatus, RoomType, User
from app.routers import admin as admin_routes
from app.routers import students as student_routes
from app.schemas import AdminApplicationUpdate, MaintenanceRequestCreate, MaintenanceRequestStatusUpdate, RoomApplicationCreate, RoomCreate


def test_student_can_apply_and_admin_approval_updates_room_availability(db_session: Session, student: User, admin: User):
    room = admin_routes.create_room(
        room_in=RoomCreate(number="A101", room_type="single", capacity=1, description="Quiet single room"),
        current_user=admin,
        db=db_session,
    )
    assert room.available_beds == 1

    application = student_routes.apply_room(
        application_in=RoomApplicationCreate(room_id=room.id, notes="Near library"),
        current_user=student,
        db=db_session,
    )
    assert application.status == "pending"

    approved = admin_routes.update_application_status(
        application_id=application.id,
        update_in=AdminApplicationUpdate(status="approved"),
        current_user=admin,
        db=db_session,
    )
    assert approved.status == "approved"

    assert student_routes.list_rooms(db=db_session) == []

    with pytest.raises(HTTPException) as exc_info:
        student_routes.apply_room(
            application_in=RoomApplicationCreate(room_id=room.id),
            current_user=student,
            db=db_session,
        )
    assert exc_info.value.status_code == 409


def test_admin_can_update_maintenance_status(db_session: Session, student: User, admin: User):
    request = student_routes.submit_maintenance(
        request_in=MaintenanceRequestCreate(title="Broken shower", description="The shower does not drain correctly."),
        current_user=student,
        db=db_session,
    )

    updated = admin_routes.update_maintenance_status(
        request_id=request.id,
        update_in=MaintenanceRequestStatusUpdate(status="in_progress"),
        current_user=admin,
        db=db_session,
    )
    assert updated.status == "in_progress"


def test_reports_aggregate_occupancy_and_payments(db_session: Session, admin: User):
    student_id = 1
    single = crud.create_room(db_session, number="B201", room_type=RoomType.single, capacity=1)
    crud.create_room(db_session, number="B202", room_type=RoomType.double, capacity=2)
    application = crud.create_room_application(db_session, student_id=student_id, room_id=single.id)
    crud.update_room_application_status(db_session, application=application, status="approved")

    db_session.add_all(
        [
            Payment(student_id=student_id, amount=Decimal("1200.00"), phone_number="254700000001", status=PaymentStatus.completed),
            Payment(student_id=student_id, amount=Decimal("800.00"), phone_number="254700000002", status=PaymentStatus.pending),
            Payment(student_id=student_id, amount=Decimal("500.00"), phone_number="254700000003", status=PaymentStatus.failed),
        ]
    )
    db_session.commit()

    occupancy_report = admin_routes.occupancy_report(current_user=admin, db=db_session)
    assert occupancy_report == {
        "total_rooms": 2,
        "total_capacity": 3,
        "occupied_beds": 1,
        "available_beds": 2,
        "occupancy_rate": 33.33,
        "unavailable_rooms": 1,
    }

    payment_report = admin_routes.payment_report(current_user=admin, db=db_session)
    assert payment_report["completed_payments"] == 1
    assert payment_report["pending_payments"] == 1
    assert payment_report["failed_payments"] == 1
    assert payment_report["total_collected"] == Decimal("1200.00")
    assert payment_report["pending_amount"] == Decimal("800.00")


def test_openapi_groups_hostel_workflows():
    schema = app.openapi()
    assert "Admin" in {tag["name"] for tag in schema["tags"]}
    assert "/admin/reports/occupancy" in schema["paths"]
    assert "/admin/maintenance/{request_id}/status" in schema["paths"]
