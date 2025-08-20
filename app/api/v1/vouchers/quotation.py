# app/api/v1/vouchers/quotation.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional  # Add Optional import
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import Quotation
from app.schemas.vouchers import QuotationCreate, QuotationInDB, QuotationUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["quotations"])

def calculate_item_amount(item):
    subtotal = item.quantity * item.unit_price
    discount_amount = subtotal * (item.discount_percentage / 100)
    taxable_amount = subtotal - discount_amount
    gst_amount = taxable_amount * (item.gst_rate / 100)
    return taxable_amount + gst_amount

def calculate_quotation_total(quotation):
    if quotation.items:
        return sum(calculate_item_amount(item) for item in quotation.items)
    return 0

@router.get("/", response_model=List[QuotationInDB])
async def get_quotations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,  # Change to Optional[str]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all quotations"""
    query = db.query(Quotation).options(joinedload(Quotation.customer), joinedload(Quotation.items)).filter(
        Quotation.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(Quotation.status == status)
    
    quotations = query.offset(skip).limit(limit).all()
    
    # Calculate total_amount for each quotation if not set
    for quotation in quotations:
        if quotation.total_amount is None:
            quotation.total_amount = calculate_quotation_total(quotation)
    
    return quotations

@router.get("/next-number", response_model=str)
async def get_next_quotation_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available quotation number"""
    return VoucherNumberService.generate_voucher_number(
        db, "QT", current_user.organization_id, Quotation
    )

# Register both "" and "/" for POST to support both /api/v1/quotations and /api/v1/quotations/
@router.post("", response_model=QuotationInDB, include_in_schema=False)
@router.post("/", response_model=QuotationInDB)
async def create_quotation(
    quotation: QuotationCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new quotation"""
    try:
        quotation_data = quotation.dict(exclude={'items'})
        quotation_data['created_by'] = current_user.id
        quotation_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not quotation_data.get('voucher_number') or quotation_data['voucher_number'] == '':
            quotation_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "QT", current_user.organization_id, Quotation
            )
        else:
            existing = db.query(Quotation).filter(
                Quotation.organization_id == current_user.organization_id,
                Quotation.voucher_number == quotation_data['voucher_number']
            ).first()
            if existing:
                quotation_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "QT", current_user.organization_id, Quotation
                )
        
        db_quotation = Quotation(**quotation_data)
        db.add(db_quotation)
        db.flush()
        
        total_amount = 0
        for item_data in quotation.items:
            from app.models.vouchers import QuotationItem
            item = QuotationItem(
                quotation_id=db_quotation.id,
                **item_data.dict()
            )
            item.amount = calculate_item_amount(item)
            total_amount += item.amount
            db.add(item)
        
        db_quotation.total_amount = total_amount
        
        db.commit()
        db.refresh(db_quotation)
        
        if send_email and db_quotation.customer and db_quotation.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="quotation",
                voucher_id=db_quotation.id,
                recipient_email=db_quotation.customer.email,
                recipient_name=db_quotation.customer.name
            )
        
        logger.info(f"Quotation {db_quotation.voucher_number} created by {current_user.email}")
        return db_quotation
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating quotation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quotation"
        )

@router.get("/{quotation_id}", response_model=QuotationInDB)
async def get_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    quotation = db.query(Quotation).options(joinedload(Quotation.customer), joinedload(Quotation.items)).filter(
        Quotation.id == quotation_id,
        Quotation.organization_id == current_user.organization_id
    ).first()
    if not quotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found"
        )
    
    # Calculate total_amount if not set
    if quotation.total_amount is None:
        quotation.total_amount = calculate_quotation_total(quotation)
    
    return quotation

@router.put("/{quotation_id}", response_model=QuotationInDB)
async def update_quotation(
    quotation_id: int,
    quotation_update: QuotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        quotation = db.query(Quotation).filter(
            Quotation.id == quotation_id,
            Quotation.organization_id == current_user.organization_id
        ).first()
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        update_data = quotation_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(quotation, field, value)
        
        if quotation_update.items is not None:
            from app.models.vouchers import QuotationItem
            db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation_id).delete()
            total_amount = 0
            for item_data in quotation_update.items:
                item = QuotationItem(
                    quotation_id=quotation_id,
                    **item_data.dict()
                )
                item.amount = calculate_item_amount(item)
                total_amount += item.amount
                db.add(item)
            quotation.total_amount = total_amount
        
        db.commit()
        db.refresh(quotation)
        
        logger.info(f"Quotation {quotation.voucher_number} updated by {current_user.email}")
        return quotation
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating quotation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update quotation"
        )

@router.delete("/{quotation_id}")
async def delete_quotation(
    quotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        quotation = db.query(Quotation).filter(
            Quotation.id == quotation_id,
            Quotation.organization_id == current_user.organization_id
        ).first()
        if not quotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quotation not found"
            )
        
        from app.models.vouchers import QuotationItem
        db.query(QuotationItem).filter(QuotationItem.quotation_id == quotation_id).delete()
        
        db.delete(quotation)
        db.commit()
        
        logger.info(f"Quotation {quotation.voucher_number} deleted by {current_user.email}")
        return {"message": "Quotation deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting quotation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete quotation"
        )