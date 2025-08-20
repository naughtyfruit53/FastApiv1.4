# app/api/v1/vouchers/sales_order.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional  # Add Optional import
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import SalesOrder
from app.schemas.vouchers import SalesOrderCreate, SalesOrderInDB, SalesOrderUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sales-orders"])

@router.get("/", response_model=List[SalesOrderInDB])
async def get_sales_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,  # Change to Optional[str]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sales orders"""
    query = db.query(SalesOrder).options(joinedload(SalesOrder.customer)).filter(
        SalesOrder.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(SalesOrder.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/next-number", response_model=str)
async def get_next_sales_order_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available sales order number"""
    return VoucherNumberService.generate_voucher_number(
        db, "SO", current_user.organization_id, SalesOrder
    )

# Register both "" and "/" for POST to support both /api/v1/sales-orders and /api/v1/sales-orders/
@router.post("", response_model=SalesOrderInDB, include_in_schema=False)
@router.post("/", response_model=SalesOrderInDB)
async def create_sales_order(
    order: SalesOrderCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new sales order"""
    try:
        order_data = order.dict(exclude={'items'})
        order_data['created_by'] = current_user.id
        order_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not order_data.get('voucher_number') or order_data['voucher_number'] == '':
            order_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "SO", current_user.organization_id, SalesOrder
            )
        else:
            existing = db.query(SalesOrder).filter(
                SalesOrder.organization_id == current_user.organization_id,
                SalesOrder.voucher_number == order_data['voucher_number']
            ).first()
            if existing:
                order_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "SO", current_user.organization_id, SalesOrder
                )
        
        db_order = SalesOrder(**order_data)
        db.add(db_order)
        db.flush()
        
        for item_data in order.items:
            from app.models.vouchers import SalesOrderItem
            item = SalesOrderItem(
                sales_order_id=db_order.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_order)
        
        if send_email and db_order.customer and db_order.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="sales_order",
                voucher_id=db_order.id,
                recipient_email=db_order.customer.email,
                recipient_name=db_order.customer.name
            )
        
        logger.info(f"Sales order {db_order.voucher_number} created by {current_user.email}")
        return db_order
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sales order"
        )

@router.get("/{order_id}", response_model=SalesOrderInDB)
async def get_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales order by ID"""
    order = db.query(SalesOrder).options(joinedload(SalesOrder.customer)).filter(
        SalesOrder.id == order_id,
        SalesOrder.organization_id == current_user.organization_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found"
        )
    return order

@router.put("/{order_id}", response_model=SalesOrderInDB)
async def update_sales_order(
    order_id: int,
    order_update: SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update sales order"""
    try:
        order = db.query(SalesOrder).filter(
            SalesOrder.id == order_id,
            SalesOrder.organization_id == current_user.organization_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        update_data = order_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(order, field, value)
        
        if order_update.items is not None:
            from app.models.vouchers import SalesOrderItem
            db.query(SalesOrderItem).filter(
                SalesOrderItem.sales_order_id == order_id
            ).delete()
            
            for item_data in order_update.items:
                item = SalesOrderItem(
                    sales_order_id=order_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Sales order {order.voucher_number} updated by {current_user.email}")
        return order
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sales order"
        )

@router.delete("/{order_id}")
async def delete_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete sales order"""
    try:
        order = db.query(SalesOrder).filter(
            SalesOrder.id == order_id,
            SalesOrder.organization_id == current_user.organization_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales order not found"
            )
        
        from app.models.vouchers import SalesOrderItem
        db.query(SalesOrderItem).filter(
            SalesOrderItem.sales_order_id == order_id
        ).delete()
        
        db.delete(order)
        db.commit()
        
        logger.info(f"Sales order {order.voucher_number} deleted by {current_user.email}")
        return {"message": "Sales order deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sales order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sales order"
        )