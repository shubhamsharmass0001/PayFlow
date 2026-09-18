import base64
import io
import os
import uuid
from typing import Optional
import qrcode
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditAction
from app.modules.audit.service import record_audit
from app.modules.auth.models import User
from app.modules.invoices.models import Invoice
from app.modules.merchants.models import Merchant
from app.modules.payment_requests.models import PaymentRequest
from app.modules.payment_requests.service import get_payment_request_by_id
from app.modules.stores.models import Store
from app.modules.upi_qr.models import QrStatus, QrType, UpiQrCode
from app.modules.upi_qr.schemas import UpiQrResponse


def generate_payment_request_qr(
    db: Session,
    payment_request_id: uuid.UUID,
    actor: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UpiQrResponse:
    """Generates a UPI-intent QR payload and rendered PNG image for a PaymentRequest.

    PROTOTYPE ARCHITECTURE NOTICE:
      This UPI QR generation triggers the PayFlow Mock Payment Provider in this prototype environment.
      It does NOT route live traffic to NPCI/live banking rails.

    Payload format:
      pa=<vpa>&pn=<merchant>&am=<amount>&tr=<request_id>&cu=INR
    """
    pr = get_payment_request_by_id(db, payment_request_id)
    merchant = db.query(Merchant).filter(Merchant.id == pr.merchant_id).first()

    # Resolve store-level or merchant-level UPI VPA
    vpa = merchant.upi_vpa if merchant and merchant.upi_vpa else "payflow.default@mockupi"
    store_id = None
    if pr.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == pr.invoice_id).first()
        if invoice and invoice.store_id:
            store_id = invoice.store_id
            store = db.query(Store).filter(Store.id == invoice.store_id).first()
            if store and store.upi_vpa:
                vpa = store.upi_vpa

    merchant_name = merchant.business_name if merchant and merchant.business_name else "PayFlow Merchant"
    amount_str = f"{pr.amount:.2f}"
    request_id_str = str(pr.id)

    # Construct UPI intent payload string
    # Both standard query parameters and upi:// URI are embedded
    upi_payload = f"pa={vpa}&pn={merchant_name}&am={amount_str}&tr={request_id_str}&cu=INR"
    upi_uri = f"upi://pay?{upi_payload}"

    # Generate QR Code via qrcode library
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Render base64 PNG data URI
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    base64_encoded = base64.b64encode(png_bytes).decode("utf-8")
    qr_data_url = f"data:image/png;base64,{base64_encoded}"

    # Save to local disk under backend/uploads/qr/
    qr_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "qr")
    )
    os.makedirs(qr_dir, exist_ok=True)
    filename = f"qr_{pr.id}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath, format="PNG")
    file_url = f"/uploads/qr/{filename}"

    # Persist or update upi_qr_codes record
    qr_record = (
        db.query(UpiQrCode)
        .filter(UpiQrCode.payment_request_id == pr.id)
        .first()
    )
    is_new = qr_record is None
    if is_new:
        qr_record = UpiQrCode(
            merchant_id=pr.merchant_id,
            store_id=store_id,
            invoice_id=pr.invoice_id,
            payment_request_id=pr.id,
            qr_type=QrType.DYNAMIC,
            upi_string=upi_payload,
            image_url=file_url,
            amount=pr.amount,
            status=QrStatus.ACTIVE,
            expires_at=pr.expires_at,
        )
        db.add(qr_record)
    else:
        qr_record.upi_string = upi_payload
        qr_record.image_url = file_url
        qr_record.amount = pr.amount
        qr_record.expires_at = pr.expires_at
        qr_record.status = QrStatus.ACTIVE

    db.commit()
    db.refresh(qr_record)

    # Record audit log
    record_audit(
        db=db,
        action=AuditAction.CREATE if is_new else AuditAction.UPDATE,
        entity_name="upi_qr_codes",
        entity_id=qr_record.id,
        actor_id=actor.id,
        merchant_id=pr.merchant_id,
        before=None,
        after={
            "payment_request_id": str(pr.id),
            "upi_string": upi_payload,
            "amount": str(pr.amount),
            "file_url": file_url,
            "mock_mode": True,
        },
        ip_address=ip_address,
        user_agent=user_agent,
    )

    response = UpiQrResponse.model_validate(qr_record)
    response.qr_data_url = qr_data_url
    return response
