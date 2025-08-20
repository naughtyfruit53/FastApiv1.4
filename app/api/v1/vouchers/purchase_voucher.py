# app/api/v1/vouchers/purchase_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import PurchaseVoucher
from app.schemas.vouchers import PurchaseVoucherCreate, PurchaseVoucherInDB, PurchaseVoucherUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-vouchers"])

@router.get("", response_model=List[PurchaseVoucherInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[PurchaseVoucherInDB])
async def get_purchase_vouchers(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all purchase vouchers"""
    query = db.query(PurchaseVoucher).options(joinedload(PurchaseVoucher.vendor)).filter(
        PurchaseVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseVoucher.status == status)
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_purchase_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available purchase voucher number"""
    return VoucherNumberService.generate_voucher_number(
        db, "PV", current_user.organization_id, PurchaseVoucher
    )

# Register both "" and "/" for POST to support both /api/v1/purchase-vouchers and /api/v1/purchase-vouchers/
@router.post("", response_model=PurchaseVoucherInDB, include_in_schema=False)
@router.post("/", response_model=PurchaseVoucherInDB)
async def create_purchase_voucher(
    invoice: PurchaseVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new purchase voucher"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PV", current_user.organization_id, PurchaseVoucher
            )
        else:
            existing = db.query(PurchaseVoucher).filter(
                PurchaseVoucher.organization_id == current_user.organization_id,
                PurchaseVoucher.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PV", current_user.organization_id, PurchaseVoucher
                )
        
        db_invoice = PurchaseVoucher(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            from app.models.vouchers import PurchaseVoucherItem
            item = PurchaseVoucherItem(
                purchase_voucher_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_voucher",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Purchase voucher {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase voucher"
        )

@router.get("/{invoice_id}", response_model=PurchaseVoucherInDB)
async def get_purchase_voucher(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(PurchaseVoucher).options(joinedload(PurchaseVoucher.vendor)).filter(
        PurchaseVoucher.id == invoice_id,
        PurchaseVoucher.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase voucher not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=PurchaseVoucherInDB)
async def update_purchase_voucher(
    invoice_id: int,
    invoice_update: PurchaseVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseVoucher).filter(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from app.models.vouchers import PurchaseVoucherItem
            db.query(PurchaseVoucherItem).filter(PurchaseVoucherItem.purchase_voucher_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = PurchaseVoucherItem(
                    purchase_voucher_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Purchase voucher {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase voucher"
        )

@router.delete("/{invoice_id}")
async def delete_purchase_voucher(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(PurchaseVoucher).filter(
            PurchaseVoucher.id == invoice_id,
            PurchaseVoucher.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        from app.models.vouchers import PurchaseVoucherItem
        db.query(PurchaseVoucherItem).filter(PurchaseVoucherItem.purchase_voucher_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Purchase voucher {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase voucher"
        )