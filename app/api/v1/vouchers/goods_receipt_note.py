# app/api/v1/vouchers/goods_receipt_note.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import GoodsReceiptNote
from app.schemas.vouchers import GRNCreate, GRNInDB, GRNUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["goods-receipt-notes"])

@router.get("", response_model=List[GRNInDB])  # Added to handle without trailing /
@router.get("/", response_model=List[GRNInDB])
async def get_goods_receipt_notes(
    skip: int = Query(0, ge=0, description="Number of records to skip (for pagination)"),
    limit: int = Query(5, ge=1, le=500, description="Maximum number of records to return (default 5 for UI standard)"),
    status: Optional[str] = Query(None, description="Optional filter by voucher status (e.g., 'draft', 'approved')"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all goods receipt notes"""
    query = db.query(GoodsReceiptNote).options(joinedload(GoodsReceiptNote.vendor)).filter(
        GoodsReceiptNote.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(GoodsReceiptNote.status == status)
    
    # Enhanced sorting - latest first by default
    if hasattr(GoodsReceiptNote, sortBy):
        sort_attr = getattr(GoodsReceiptNote, sortBy)
        if sort.lower() == "asc":
            query = query.order_by(sort_attr.asc())
        else:
            query = query.order_by(sort_attr.desc())
    else:
        # Default to created_at desc if invalid sortBy field
        query = query.order_by(GoodsReceiptNote.created_at.desc())
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

@router.get("/next-number", response_model=str)
async def get_next_goods_receipt_note_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available goods receipt note number"""
    return VoucherNumberService.generate_voucher_number(
        db, "GRN", current_user.organization_id, GoodsReceiptNote
    )

# Register both "" and "/" for POST to support both /api/v1/goods-receipt-notes and /api/v1/goods-receipt-notes/
@router.post("", response_model=GRNInDB, include_in_schema=False)
@router.post("/", response_model=GRNInDB)
async def create_goods_receipt_note(
    invoice: GRNCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new goods receipt note"""
    try:
        invoice_data = invoice.dict(exclude={'items'})
        invoice_data['created_by'] = current_user.id
        invoice_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not invoice_data.get('voucher_number') or invoice_data['voucher_number'] == '':
            invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "GRN", current_user.organization_id, GoodsReceiptNote
            )
        else:
            existing = db.query(GoodsReceiptNote).filter(
                GoodsReceiptNote.organization_id == current_user.organization_id,
                GoodsReceiptNote.voucher_number == invoice_data['voucher_number']
            ).first()
            if existing:
                invoice_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "GRN", current_user.organization_id, GoodsReceiptNote
                )
        
        db_invoice = GoodsReceiptNote(**invoice_data)
        db.add(db_invoice)
        db.flush()
        
        for item_data in invoice.items:
            from app.models.vouchers import GoodsReceiptNoteItem
            item = GoodsReceiptNoteItem(
                goods_receipt_note_id=db_invoice.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_invoice)
        
        if send_email and db_invoice.vendor and db_invoice.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="goods_receipt_note",
                voucher_id=db_invoice.id,
                recipient_email=db_invoice.vendor.email,
                recipient_name=db_invoice.vendor.name
            )
        
        logger.info(f"Goods receipt note {db_invoice.voucher_number} created by {current_user.email}")
        return db_invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goods receipt note"
        )

@router.get("/{invoice_id}", response_model=GRNInDB)
async def get_goods_receipt_note(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    invoice = db.query(GoodsReceiptNote).options(joinedload(GoodsReceiptNote.vendor)).filter(
        GoodsReceiptNote.id == invoice_id,
        GoodsReceiptNote.organization_id == current_user.organization_id
    ).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goods receipt note not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=GRNInDB)
async def update_goods_receipt_note(
    invoice_id: int,
    invoice_update: GRNUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(GoodsReceiptNote).filter(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        update_data = invoice_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        if invoice_update.items is not None:
            from app.models.vouchers import GoodsReceiptNoteItem
            db.query(GoodsReceiptNoteItem).filter(GoodsReceiptNoteItem.goods_receipt_note_id == invoice_id).delete()
            for item_data in invoice_update.items:
                item = GoodsReceiptNoteItem(
                    goods_receipt_note_id=invoice_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"Goods receipt note {invoice.voucher_number} updated by {current_user.email}")
        return invoice
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goods receipt note"
        )

@router.delete("/{invoice_id}")
async def delete_goods_receipt_note(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        invoice = db.query(GoodsReceiptNote).filter(
            GoodsReceiptNote.id == invoice_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
        ).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        from app.models.vouchers import GoodsReceiptNoteItem
        db.query(GoodsReceiptNoteItem).filter(GoodsReceiptNoteItem.goods_receipt_note_id == invoice_id).delete()
        
        db.delete(invoice)
        db.commit()
        
        logger.info(f"Goods receipt note {invoice.voucher_number} deleted by {current_user.email}")
        return {"message": "Goods receipt note deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goods receipt note"
        )