# app/api/v1/vouchers/sales_voucher.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import SalesVoucher
from app.schemas.vouchers import SalesVoucherCreate, SalesVoucherInDB, SalesVoucherUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sales-vouchers"])

@router.get("/", response_model=List[SalesVoucherInDB])
async def get_sales_vouchers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sales vouchers"""
    query = db.query(SalesVoucher).options(joinedload(SalesVoucher.customer)).filter(
        SalesVoucher.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(SalesVoucher.status == status)
    
    vouchers = query.offset(skip).limit(limit).all()
    return vouchers

@router.get("/next-number", response_model=str)
async def get_next_sales_voucher_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available sales voucher number"""
    return VoucherNumberService.generate_voucher_number(
        db, "SV", current_user.organization_id, SalesVoucher
    )

# Register both "" and "/" for POST to support both /api/v1/sales-vouchers and /api/v1/sales-vouchers/
@router.post("", response_model=SalesVoucherInDB, include_in_schema=False)
@router.post("/", response_model=SalesVoucherInDB)
async def create_sales_voucher(
    voucher: SalesVoucherCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new sales voucher"""
    try:
        voucher_data = voucher.dict(exclude={'items'})
        voucher_data['created_by'] = current_user.id
        voucher_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not voucher_data.get('voucher_number') or voucher_data['voucher_number'] == '':
            voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "SV", current_user.organization_id, SalesVoucher
            )
        else:
            existing = db.query(SalesVoucher).filter(
                SalesVoucher.organization_id == current_user.organization_id,
                SalesVoucher.voucher_number == voucher_data['voucher_number']
            ).first()
            if existing:
                voucher_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "SV", current_user.organization_id, SalesVoucher
                )
        
        db_voucher = SalesVoucher(**voucher_data)
        db.add(db_voucher)
        db.flush()
        
        for item_data in voucher.items:
            from app.models.vouchers import SalesVoucherItem
            item = SalesVoucherItem(
                sales_voucher_id=db_voucher.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_voucher)
        
        if send_email and db_voucher.customer and db_voucher.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="sales_voucher",
                voucher_id=db_voucher.id,
                recipient_email=db_voucher.customer.email,
                recipient_name=db_voucher.customer.name
            )
        
        logger.info(f"Sales voucher {db_voucher.voucher_number} created by {current_user.email}")
        return db_voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sales voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sales voucher"
        )

@router.get("/{voucher_id}", response_model=SalesVoucherInDB)
async def get_sales_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sales voucher by ID"""
    voucher = db.query(SalesVoucher).options(joinedload(SalesVoucher.customer)).filter(
        SalesVoucher.id == voucher_id,
        SalesVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales voucher not found"
        )
    return voucher

@router.put("/{voucher_id}", response_model=SalesVoucherInDB)
async def update_sales_voucher(
    voucher_id: int,
    voucher_update: SalesVoucherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update sales voucher"""
    try:
        voucher = db.query(SalesVoucher).filter(
            SalesVoucher.id == voucher_id,
            SalesVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales voucher not found"
            )
        
        update_data = voucher_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(voucher, field, value)
        
        if voucher_update.items is not None:
            from app.models.vouchers import SalesVoucherItem
            db.query(SalesVoucherItem).filter(
                SalesVoucherItem.sales_voucher_id == voucher_id
            ).delete()
            
            for item_data in voucher_update.items:
                item = SalesVoucherItem(
                    sales_voucher_id=voucher_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(voucher)
        
        logger.info(f"Sales voucher {voucher.voucher_number} updated by {current_user.email}")
        return voucher
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating sales voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sales voucher"
        )

@router.delete("/{voucher_id}")
async def delete_sales_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete sales voucher"""
    try:
        voucher = db.query(SalesVoucher).filter(
            SalesVoucher.id == voucher_id,
            SalesVoucher.organization_id == current_user.organization_id
        ).first()
        if not voucher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sales voucher not found"
            )
        
        from app.models.vouchers import SalesVoucherItem
        db.query(SalesVoucherItem).filter(
            SalesVoucherItem.sales_voucher_id == voucher_id
        ).delete()
        
        db.delete(voucher)
        db.commit()
        
        logger.info(f"Sales voucher {voucher.voucher_number} deleted by {current_user.email}")
        return {"message": "Sales voucher deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting sales voucher: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sales voucher"
        )

@router.post("/{voucher_id}/send-email")
async def send_sales_voucher_email(
    voucher_id: int,
    background_tasks: BackgroundTasks,
    custom_email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    voucher = db.query(SalesVoucher).filter(
        SalesVoucher.id == voucher_id,
        SalesVoucher.organization_id == current_user.organization_id
    ).first()
    if not voucher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales voucher not found")
    
    recipient_email = custom_email or (voucher.customer.email if voucher.customer else None)
    if not recipient_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No email address available")
    
    background_tasks.add_task(
        send_voucher_email,
        voucher_type="sales_voucher",
        voucher_id=voucher_id,
        recipient_email=recipient_email,
        recipient_name=voucher.customer.name if voucher.customer else "Customer"
    )
    
    return {"message": "Email sending scheduled"}