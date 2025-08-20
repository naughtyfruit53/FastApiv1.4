# app/api/v1/vouchers/purchase_return.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import PurchaseReturn
from app.schemas.vouchers import PurchaseReturnCreate, PurchaseReturnInDB, PurchaseReturnUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["purchase-returns"])

@router.get("/", response_model=List[PurchaseReturnInDB])
async def get_purchase_returns(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PurchaseReturn).filter(
        PurchaseReturn.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseReturn.status == status)
    
    returns = query.offset(skip).limit(limit).all()
    return returns

@router.get("/next-number", response_model=str)
async def get_next_purchase_return_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VoucherNumberService.generate_voucher_number(
        db, "PR", current_user.organization_id, PurchaseReturn
    )

@router.post("/", response_model=PurchaseReturnInDB)
async def create_purchase_return(
    return_data: PurchaseReturnCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        data = return_data.dict(exclude={'items'})
        data['created_by'] = current_user.id
        data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not data.get('voucher_number') or data['voucher_number'] == '':
            data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PR", current_user.organization_id, PurchaseReturn
            )
        else:
            existing = db.query(PurchaseReturn).filter(
                PurchaseReturn.organization_id == current_user.organization_id,
                PurchaseReturn.voucher_number == data['voucher_number']
            ).first()
            if existing:
                data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PR", current_user.organization_id, PurchaseReturn
                )
        
        db_return = PurchaseReturn(**data)
        db.add(db_return)
        db.flush()
        
        for item_data in return_data.items:
            from app.models.vouchers import PurchaseReturnItem
            item = PurchaseReturnItem(
                purchase_return_id=db_return.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_return)
        
        if send_email and db_return.vendor and db_return.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_return",
                voucher_id=db_return.id,
                recipient_email=db_return.vendor.email,
                recipient_name=db_return.vendor.name
            )
        
        logger.info(f"Purchase return {db_return.voucher_number} created by {current_user.email}")
        return db_return
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase return"
        )

@router.get("/{return_id}", response_model=PurchaseReturnInDB)
async def get_purchase_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return_ = db.query(PurchaseReturn).filter(
        PurchaseReturn.id == return_id,
        PurchaseReturn.organization_id == current_user.organization_id
    ).first()
    if not return_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase return not found"
        )
    return return_

@router.put("/{return_id}", response_model=PurchaseReturnInDB)
async def update_purchase_return(
    return_id: int,
    return_update: PurchaseReturnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return_ = db.query(PurchaseReturn).filter(
            PurchaseReturn.id == return_id,
            PurchaseReturn.organization_id == current_user.organization_id
        ).first()
        if not return_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        update_data = return_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(return_, field, value)
        
        if return_update.items is not None:
            from app.models.vouchers import PurchaseReturnItem
            db.query(PurchaseReturnItem).filter(PurchaseReturnItem.purchase_return_id == return_id).delete()
            for item_data in return_update.items:
                item = PurchaseReturnItem(
                    purchase_return_id=return_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(return_)
        
        logger.info(f"Purchase return {return_.voucher_number} updated by {current_user.email}")
        return return_
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase return"
        )

@router.delete("/{return_id}")
async def delete_purchase_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return_ = db.query(PurchaseReturn).filter(
            PurchaseReturn.id == return_id,
            PurchaseReturn.organization_id == current_user.organization_id
        ).first()
        if not return_:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase return not found"
            )
        
        from app.models.vouchers import PurchaseReturnItem
        db.query(PurchaseReturnItem).filter(PurchaseReturnItem.purchase_return_id == return_id).delete()
        
        db.delete(return_)
        db.commit()
        
        logger.info(f"Purchase return {return_.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase return deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase return"
        )