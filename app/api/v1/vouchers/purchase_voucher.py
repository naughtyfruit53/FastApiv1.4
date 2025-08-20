# app/api/v1/vouchers/purchase_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
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

@router.get("/", response_model=List[PurchaseVoucherInDB])
async def get_purchase_vouchers(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PurchaseVoucher).filter(
        PurchaseVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PurchaseVoucher.status == status)
    
    vouchers = query.offset(skip).limit(limit).all()
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_purchase_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return VoucherNumberService.generate_voucher_number(
        db, "PV", current_user.organization_id, PurchaseVoucher
    )

@router.post("/", response_model=PurchaseVoucherInDB)
async def create_purchase_voucher(
    voucher: PurchaseVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher_data = voucher.dict(exclude={'items'})
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "PV", current_user.organization_id, PurchaseVoucher
            )
        else:
            existing = db.query(PurchaseVoucher).filter(
                PurchaseVoucher.organization_id == current_user.organization_id,
                PurchaseVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "PV", current_user.organization_id, PurchaseVoucher
                )
        
        db_voucher = PurchaseVoucher(**voucher_data)
        db.add(db_voucher)
        db.flush()
        
        for item_data in voucher.items:
            from app.models.vouchers import PurchaseVoucherItem
            item = PurchaseVoucherItem(
                purchase_voucher_id=db_voucher.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_voucher)
        
        if send_email and db_voucher.vendor and db_voucher.vendor.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="purchase_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.vendor.email,
                recipient_name=db_voucher.vendor.name
            )
        
        logger.info(f"Purchase voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create purchase voucher"
        )

@router.get("/{voucher_id}", response_model=PurchaseVoucherInDB)
async def get_purchase_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(PurchaseVoucher).filter(
        PurchaseVoucher.id == voucher_id,
        PurchaseVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase voucher not found"
        )
    return voucher

@router.put("/{voucher_id}", response_model=PurchaseVoucherInDB)
async def update_purchase_voucher(
    voucher_id: int,
    voucher_update: PurchaseVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(PurchaseVoucher).filter(
            PurchaseVoucher.id == voucher_id,
            PurchaseVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        update_data = voucher_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        if voucher_update.items is not None:
            from app.models.vouchers import PurchaseVoucherItem
            db.query(PurchaseVoucherItem).filter(
                PurchaseVoucherItem.purchase_voucher_id == voucher_id
            ).delete()
            
            for item_data in voucher_update.items:
                item = PurchaseVoucherItem(
                    purchase_voucher_id=voucher_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(voucher)
        
        logger.info(f"Purchase voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update purchase voucher"
        )

@router.delete("/{voucher_id}")
async def delete_purchase_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        voucher = db.query(PurchaseVoucher).filter(
            PurchaseVoucher.id == voucher_id,
            PurchaseVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase voucher not found"
            )
        
        from app.models.vouchers import PurchaseVoucherItem
        db.query(PurchaseVoucherItem).filter(
            PurchaseVoucherItem.purchase_voucher_id == voucher_id
        ).delete()
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Purchase voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Purchase voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting purchase voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete purchase voucher"
        )