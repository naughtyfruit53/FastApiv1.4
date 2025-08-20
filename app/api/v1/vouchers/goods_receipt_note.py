# app/api/v1/vouchers/goods_receipt_note.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import GoodsReceiptNote
from app.schemas.vouchers import GRNCreate, GRNInDB, GRNUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["goods-receipt-notes"])

@router.get("/", response_model=List[GRNInDB])
async def get_goods_receipt_notes(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(GoodsReceiptNote).filter(
        GoodsReceiptNote.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(GoodsReceiptNote.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/next-number", response_model=str)
async def get_next_goods_receipt_note_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VoucherNumberService.generate_voucher_number(
        db, "GRN", current_user.organization_id, GoodsReceiptNote
    )

@router.post("/", response_model=GRNInDB)
async def create_goods_receipt_note(
    order: GRNCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        order_data = order.dict(exclude={'items'})
        order_data['created_by'] = current_user.id
        order_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not order_data.get('voucher_number') or order_data['voucher_number'] == '':
            order_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "GRN", current_user.organization_id, GoodsReceiptNote
            )
        else:
            existing = db.query(GoodsReceiptNote).filter(
                GoodsReceiptNote.organization_id == current_user.organization_id,
                GoodsReceiptNote.voucher_number == order_data['voucher_number']
            ).first()
            if existing:
                order_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "GRN", current_user.organization_id, GoodsReceiptNote
                )
        
        db_order = GoodsReceiptNote(**order_data)
        db.add(db_order)
        db.flush()
        
        for item_data in order.items:
            from app.models.vouchers import GoodsReceiptNoteItem
            item = GoodsReceiptNoteItem(
                grn_id=db_order.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_order)
        
        logger.info(f"Goods receipt note {db_order.voucher_number} created by {current_user.email}")
        return db_order
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goods receipt note"
        )

@router.get("/{order_id}", response_model=GRNInDB)
async def get_goods_receipt_note(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(GoodsReceiptNote).filter(
        GoodsReceiptNote.id == order_id,
        GoodsReceiptNote.organization_id == current_user.organization_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goods receipt note not found"
        )
    return order

@router.put("/{order_id}", response_model=GRNInDB)
async def update_goods_receipt_note(
    order_id: int,
    order_update: GRNUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        order = db.query(GoodsReceiptNote).filter(
            GoodsReceiptNote.id == order_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        update_data = order_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(order, field, value)
        
        if order_update.items is not None:
            from app.models.vouchers import GoodsReceiptNoteItem
            db.query(GoodsReceiptNoteItem).filter(
                GoodsReceiptNoteItem.grn_id == order_id
            ).delete()
            
            for item_data in order_update.items:
                item = GoodsReceiptNoteItem(
                    grn_id=order_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Goods receipt note {order.voucher_number} updated by {current_user.email}")
        return order
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update goods receipt note"
        )

@router.delete("/{order_id}")
async def delete_goods_receipt_note(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        order = db.query(GoodsReceiptNote).filter(
            GoodsReceiptNote.id == order_id,
            GoodsReceiptNote.organization_id == current_user.organization_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goods receipt note not found"
            )
        
        from app.models.vouchers import GoodsReceiptNoteItem
        db.query(GoodsReceiptNoteItem).filter(
            GoodsReceiptNoteItem.grn_id == order_id
        ).delete()
        
        db.delete(order)
        db.commit()
        
        logger.info(f"Goods receipt note {order.voucher_number} deleted by {current_user.email}")
        return {"message": "Goods receipt note deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting goods receipt note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete goods receipt note"
        )