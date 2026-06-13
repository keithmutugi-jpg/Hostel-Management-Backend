from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_db
from app.schemas import MpesaCallback
from app.models import PaymentStatus

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/mpesa/callback")
def mpesa_callback(payload: MpesaCallback, db: Session = Depends(get_db)):
    callback = payload.Body.stkCallback
    checkout_id = callback.CheckoutRequestID
    payment = crud.get_payment_by_checkout_request_id(db, checkout_request_id=checkout_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

    status_value = PaymentStatus.completed if callback.ResultCode == 0 else PaymentStatus.failed
    transaction_id = None
    if callback.CallbackMetadata and isinstance(callback.CallbackMetadata, dict):
        items = callback.CallbackMetadata.get("Item") or []
        if isinstance(items, list):
            for item in items:
                if item.get("Name") in ("MpesaReceiptNumber", "TransID"):
                    transaction_id = item.get("Value")
                    break

    crud.update_payment_status(db, payment=payment, status=status_value, transaction_id=transaction_id)
    return {"status": "ok", "result_code": callback.ResultCode, "result_desc": callback.ResultDesc}
