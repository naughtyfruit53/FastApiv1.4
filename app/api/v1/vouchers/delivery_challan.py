# app/api/v1/vouchers/delivery_challan.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional  # Add Optional import
from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models.base import User
from app.models.vouchers import DeliveryChallan
from app.schemas.vouchers import DeliveryChallanCreate, DeliveryChallanInDB, DeliveryChallanUpdate
from app.services.email_service import send_voucher_email
from app.services.voucher_service import VoucherNumberService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["delivery-challans"])

@router.get("/", response_model=List[DeliveryChallanInDB])
async def get_delivery_challans(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,  # Change to Optional[str]
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(DeliveryChallan).options(joinedload(DeliveryChallan.customer)).filter(
        DeliveryChallan.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(DeliveryChallan.status == status)
    
    items = query.offset(skip).limit(limit).all()
    return items

@router.get("/next-number", response_model=str)
async def get_next_delivery_challan_number(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the next available delivery challan number"""
    return VoucherNumberService.generate_voucher_number(
        db, "DC", current_user.organization_id, DeliveryChallan
    )

# Register both "" and "/" for POST to support both /api/v1/delivery-challans and /api/v1/delivery-challans/
@router.post("", response_model=DeliveryChallanInDB, include_in_schema=False)
@router.post("/", response_model=DeliveryChallanInDB)
async def create_delivery_challan(
    challan: DeliveryChallanCreate,
    background_tasks: BackgroundTasks,
    send_email: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        challan_data = challan.dict(exclude={'items'})
        challan_data['created_by'] = current_user.id
        challan_data['organization_id'] = current_user.organization_id
        
        # Generate unique voucher number if not provided or blank
        if not challan_data.get('voucher_number') or challan_data['voucher_number'] == '':
            challan_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                db, "DC", current_user.organization_id, DeliveryChallan
            )
        else:
            existing = db.query(DeliveryChallan).filter(
                DeliveryChallan.organization_id == current_user.organization_id,
                DeliveryChallan.voucher_number == challan_data['voucher_number']
            ).first()
            if existing:
                challan_data['voucher_number'] = VoucherNumberService.generate_voucher_number(
                    db, "DC", current_user.organization_id, DeliveryChallan
                )
        
        db_challan = DeliveryChallan(**challan_data)
        db.add(db_challan)
        db.flush()
        
        for item_data in challan.items:
            from app.models.vouchers import DeliveryChallanItem
            item = DeliveryChallanItem(
                delivery_challan_id=db_challan.id,
                **item_data.dict()
            )
            db.add(item)
        
        db.commit()
        db.refresh(db_challan)
        
        if send_email and db_challan.customer and db_challan.customer.email:
            background_tasks.add_task(
                send_voucher_email,
                voucher_type="delivery_challan",
                voucher_id=db_challan.id,
                recipient_email=db_challan.customer.email,
                recipient_name=db_challan.customer.name
            )
        
        logger.info(f"Delivery Challan {db_challan.voucher_number} created by {current_user.email}")
        return db_challan
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating Delivery Challan: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Delivery Challan")

@router.get("/{challan_id}", response_model=DeliveryChallanInDB)
async def get_delivery_challan(
    challan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    challan = db.query(DeliveryChallan).options(joinedload(DeliveryChallan.customer)).filter(
        DeliveryChallan.id == challan_id,
        DeliveryChallan.organization_id == current_user.organization_id
    ).first()
    if not challan:
        raise HTTPException(status_code=404, detail="Delivery Challan not found")
    return challan

@router.put("/{challan_id}", response_model=DeliveryChallanInDB)
async def update_delivery_challan(
    challan_id: int,
    challan_update: DeliveryChallanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        challan = db.query(DeliveryChallan).filter(
            DeliveryChallan.id == challan_id,
            DeliveryChallan.organization_id == current_user.organization_id
        ).first()
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery Challan not found")
        
        update_data = challan_update.dict(exclude_unset=True, exclude={'items'})
        for field, value in update_data.items():
            setattr(challan, field, value)
        
        if challan_update.items is not None:
            from app.models.vouchers import DeliveryChallanItem
            db.query(DeliveryChallanItem).filter(
                DeliveryChallanItem.delivery_challan_id == challan_id
            ).delete()
            
            for item_data in challan_update.items:
                item = DeliveryChallanItem(
                    delivery_challan_id=challan_id,
                    **item_data.dict()
                )
                db.add(item)
        
        db.commit()
        db.refresh(challan)
        
        logger.info(f"Delivery Challan {challan.voucher_number} updated by {current_user.email}")
        return challan
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating Delivery Challan: {e}")
        raise HTTPException(status_code=500, detail="Failed to update Delivery Challan")

@router.delete("/{challan_id}")
async def delete_delivery_challan(
    challan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        challan = db.query(DeliveryChallan).filter(
            DeliveryChallan.id == challan_id,
            DeliveryChallan.organization_id == current_user.organization_id
        ).first()
        if not challan:
            raise HTTPException(status_code=404, detail="Delivery Challan not found")
        
        from app.models.vouchers import DeliveryChallanItem
        db.query(DeliveryChallanItem).filter(
            DeliveryChallanItem.delivery_challan_id == challan_id
        ).delete()
        
        db.delete(challan)
        db.commit()
        
        logger.info(f"Delivery Challan {challan.voucher_number} deleted by {current_user.email}")
        return {"message": "Delivery Challan deleted successfully"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting Delivery Challan: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete Delivery Challan")