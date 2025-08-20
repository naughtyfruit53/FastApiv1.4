# app/api/v1/vouchers/sales_return.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional  # Add Optional import
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import SalesReturn
from app.schemas.vouchers import SalesReturnCreate, SalesReturnInDB, SalesReturnUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sales-returns"])

@router.get("/", response_model=List[SalesReturnInDB])
async def get_sales_returns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,  # Change to Optional[str]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sales returns"""
    query = db.query(SalesReturn).options(joinedload(SalesReturn.customer)).filter(
        SalesReturn.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(SalesReturn.status == status)
    
    returns = query.offset(skip).limit(limit).all()
    return returns

@router.get("/next-number", response_model=str)
async def get_next_sales_return_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available sales return number"""
    return VoucherNumberService.generate_voucher_number(
        db, "SR", current_user.organization_id, SalesReturn
    )

# Register both "" and "/" for POST to support both /api/v1/sales-returns and /api/v1/sales-returns/
@router.post("", response_model=SalesReturnInDB, include_in_schema=False)
@router.post("/", response_model=SalesReturnInDB)
async def create_sales_return(
    return_data: SalesReturnCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new sales return"""
    try:
        data = return_data.dict(exclude={'items'})
        data['created_by'] = current_user.id
        data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not data.get('voucher_number') or data['voucher_number'] == '':
            data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "SR", current_user.organization_id, SalesReturn
            )
        else:
            existing = db.query(SalesReturn).filter(
                SalesReturn.organization_id == current_user.organization_id,
                SalesReturn.voucher_number == data['voucher_number']
            ).first()
            if existing:
                data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "SR", current_user.organization_id, SalesReturn
                )
        
        db_return = SalesReturn(**data)
        db.add(db_return)
        db.flush()
        
        for item_data in return_data.items:
            from app.models.vouchers import SalesReturnItem
            item = SalesReturnItem(
                sales_return_id=db_return.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_return)
        
        if send_email and db_return.customer and db_return.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="sales_return",
                voucher_id=db_return.id,
                recipient_email=db_return.customer.email,
                recipient_name=db_return.customer.name
            )
        
        logger.info(f"Sales return {db_return.voucher_number} created by {current_user.email}")
        return db_return
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sales return"
        )

@router.get("/{return_id}", response_model=SalesReturnInDB)
async def get_sales_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales return by ID"""
    return_ = db.query(SalesReturn).options(joinedload(SalesReturn.customer)).filter(
        SalesReturn.id == return_id,
        SalesReturn.organization_id == current_user.organization_id
    ).first()
    if not return_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales return not found"
        )
    return return_

@router.put("/{return_id}", response_model=SalesReturnInDB)
async def update_sales_return(
    return_id: int,
    return_update: SalesReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update sales return"""
    try:
        return_ = db.query(SalesReturn).filter(
            SalesReturn.id == return_id,
            SalesReturn.organization_id == current_user.organization_id
        ).first()
        if not return_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales return not found"
            )
        
        update_data = return_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(return_, field, value)
        
        if return_update.items is not None:
            from app.models.vouchers import SalesReturnItem
            db.query(SalesReturnItem).filter(SalesReturnItem.sales_return_id == return_id).delete()
            for item_data in return_update.items:
                item = SalesReturnItem(
                    sales_return_id=return_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(return_)
        
        logger.info(f"Sales return {return_.voucher_number} updated by {current_user.email}")
        return return_
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sales return"
        )

@router.delete("/{return_id}")
async def delete_sales_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete sales return"""
    try:
        return_ = db.query(SalesReturn).filter(
            SalesReturn.id == return_id,
            SalesReturn.organization_id == current_user.organization_id
        ).first()
        if not return_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales return not found"
            )
        
        from app.models.vouchers import SalesReturnItem
        db.query(SalesReturnItem).filter(SalesReturnItem.sales_return_id == return_id).delete()
        
        db.delete(return_)
        db.commit()
        
        logger.info(f"Sales return {return_.voucher_number} deleted by {current_user.email}")
        return {"message": "Sales return deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sales return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sales return"
        )