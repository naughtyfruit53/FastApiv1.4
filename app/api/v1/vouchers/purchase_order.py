# app/api/v1/vouchers/purchase_order.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import PurchaseOrder
from app.schemas.vouchers import PurchaseOrderCreate, PurchaseOrderInDB, PurchaseOrderUpdate
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-orders"])

@router.get("/", response_model=List[PurchaseOrderInDB])
async def get_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PurchaseOrder).filter(
        PurchaseOrder.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/next-number", response_model=str)
async def get_next_purchase_order_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VoucherNumberService.generate_voucher_number(
        db, "PO", current_user.organization_id, PurchaseOrder
    )

@router.post("/", response_model=PurchaseOrderInDB)
async def create_purchase_order(
    order: PurchaseOrderCreate,
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
                db, "PO", current_user.organization_id, PurchaseOrder
            )
        else:
            existing = db.query(PurchaseOrder).filter(
                PurchaseOrder.organization_id == current_user.organization_id,
                PurchaseOrder.voucher_number == order_data['voucher_number']
            ).first()
            if existing:
                order_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PO", current_user.organization_id, PurchaseOrder
                )
        
        db_order = PurchaseOrder(**order_data)
        db.add(db_order)
        db.flush()
        
        for item_data in order.items:
            from app.models.vouchers import PurchaseOrderItem
            item = PurchaseOrderItem(
                purchase_order_id=db_order.id,
                delivered_quantity=0.0,
                pending_quantity=item_data.quantity,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_order)
        
        logger.info(f"Purchase order {db_order.voucher_number} created by {current_user.email}")
        return db_order
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase order"
        )

@router.get("/{order_id}", response_model=PurchaseOrderInDB)
async def get_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == order_id,
        PurchaseOrder.organization_id == current_user.organization_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return order

@router.put("/{order_id}", response_model=PurchaseOrderInDB)
async def update_purchase_order(
    order_id: int,
    order_update: PurchaseOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        order = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == order_id,
            PurchaseOrder.organization_id == current_user.organization_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        update_data = order_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(order, field, value)
        
        if order_update.items is not None:
            from app.models.vouchers import PurchaseOrderItem
            db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.purchase_order_id == order_id
            ).delete()
            
            for item_data in order_update.items:
                item = PurchaseOrderItem(
                    purchase_order_id=order_id,
                    delivered_quantity=0.0,
                    pending_quantity=item_data.quantity,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Purchase order {order.voucher_number} updated by {current_user.email}")
        return order
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase order"
        )

@router.delete("/{order_id}")
async def delete_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        order = db.query(PurchaseOrder).filter(
            PurchaseOrder.id == order_id,
            PurchaseOrder.organization_id == current_user.organization_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found"
            )
        
        from app.models.vouchers import PurchaseOrderItem
        db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.purchase_order_id == order_id
        ).delete()
        
        db.delete(order)
        db.commit()
        
        logger.info(f"Purchase order {order.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase order deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase order"
        )