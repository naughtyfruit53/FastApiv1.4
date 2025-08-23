# app/services/dispatch_service.py

"""
Dispatch service for managing dispatch orders and installation jobs
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timezone
import logging

from app.models.base import DispatchOrder, DispatchItem, InstallationJob, User
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)


class DispatchNumberService:
    """Service for generating dispatch and installation job numbers"""
    
    @staticmethod
    def generate_dispatch_order_number(db: Session, organization_id: int) -> str:
        """Generate a unique dispatch order number"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        prefix = "DO"
        
        # Get the latest dispatch order number for this prefix, fiscal year, and organization
        latest_order = db.query(DispatchOrder).filter(
            DispatchOrder.organization_id == organization_id,
            DispatchOrder.order_number.like(f"{prefix}/{fiscal_year}/%")
        ).order_by(DispatchOrder.order_number.desc()).first()
        
        if latest_order:
            # Extract sequence number and increment
            try:
                last_sequence = int(latest_order.order_number.split('/')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        return f"{prefix}/{fiscal_year}/{next_sequence:05d}"
    
    @staticmethod
    def generate_installation_job_number(db: Session, organization_id: int) -> str:
        """Generate a unique installation job number"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        prefix = "IJ"
        
        # Get the latest installation job number for this prefix, fiscal year, and organization
        latest_job = db.query(InstallationJob).filter(
            InstallationJob.organization_id == organization_id,
            InstallationJob.job_number.like(f"{prefix}/{fiscal_year}/%")
        ).order_by(InstallationJob.job_number.desc()).first()
        
        if latest_job:
            # Extract sequence number and increment
            try:
                last_sequence = int(latest_job.job_number.split('/')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        return f"{prefix}/{fiscal_year}/{next_sequence:05d}"


class DispatchService:
    """Service for dispatch order business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_dispatch_order(
        self,
        organization_id: int,
        customer_id: int,
        delivery_address: str,
        items: List[dict],
        created_by_id: int,
        ticket_id: Optional[int] = None,
        **kwargs
    ) -> DispatchOrder:
        """Create a new dispatch order with items"""
        
        # Generate order number
        order_number = DispatchNumberService.generate_dispatch_order_number(
            self.db, organization_id
        )
        
        # Create dispatch order
        dispatch_order = DispatchOrder(
            organization_id=organization_id,
            order_number=order_number,
            customer_id=customer_id,
            ticket_id=ticket_id,
            delivery_address=delivery_address,
            created_by_id=created_by_id,
            **kwargs
        )
        
        self.db.add(dispatch_order)
        self.db.flush()  # Get the ID
        
        # Create dispatch items
        for item_data in items:
            dispatch_item = DispatchItem(
                dispatch_order_id=dispatch_order.id,
                **item_data
            )
            self.db.add(dispatch_item)
        
        self.db.commit()
        self.db.refresh(dispatch_order)
        
        logger.info(f"Created dispatch order {order_number} for organization {organization_id}")
        return dispatch_order
    
    def update_dispatch_status(
        self,
        dispatch_order_id: int,
        status: str,
        updated_by_id: int,
        **kwargs
    ) -> DispatchOrder:
        """Update dispatch order status"""
        
        dispatch_order = self.db.query(DispatchOrder).filter(
            DispatchOrder.id == dispatch_order_id
        ).first()
        
        if not dispatch_order:
            raise ValueError(f"Dispatch order {dispatch_order_id} not found")
        
        dispatch_order.status = status
        dispatch_order.updated_by_id = updated_by_id
        
        # Update specific date fields based on status
        if status == "in_transit" and not dispatch_order.dispatch_date:
            dispatch_order.dispatch_date = datetime.now(timezone.utc)
        elif status == "delivered" and not dispatch_order.actual_delivery_date:
            dispatch_order.actual_delivery_date = datetime.now(timezone.utc)
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(dispatch_order, key):
                setattr(dispatch_order, key, value)
        
        self.db.commit()
        self.db.refresh(dispatch_order)
        
        logger.info(f"Updated dispatch order {dispatch_order.order_number} status to {status}")
        return dispatch_order


class InstallationJobService:
    """Service for installation job business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_installation_job(
        self,
        organization_id: int,
        dispatch_order_id: int,
        customer_id: int,
        installation_address: str,
        created_by_id: int,
        **kwargs
    ) -> InstallationJob:
        """Create a new installation job"""
        
        # Generate job number
        job_number = DispatchNumberService.generate_installation_job_number(
            self.db, organization_id
        )
        
        # Create installation job
        installation_job = InstallationJob(
            organization_id=organization_id,
            job_number=job_number,
            dispatch_order_id=dispatch_order_id,
            customer_id=customer_id,
            installation_address=installation_address,
            created_by_id=created_by_id,
            **kwargs
        )
        
        self.db.add(installation_job)
        self.db.commit()
        self.db.refresh(installation_job)
        
        logger.info(f"Created installation job {job_number} for organization {organization_id}")
        return installation_job
    
    def assign_technician(
        self,
        job_id: int,
        technician_id: int,
        updated_by_id: int
    ) -> InstallationJob:
        """Assign a technician to an installation job"""
        
        job = self.db.query(InstallationJob).filter(
            InstallationJob.id == job_id
        ).first()
        
        if not job:
            raise ValueError(f"Installation job {job_id} not found")
        
        # Verify technician exists and belongs to the same organization
        technician = self.db.query(User).filter(
            User.id == technician_id,
            User.organization_id == job.organization_id
        ).first()
        
        if not technician:
            raise ValueError(f"Technician {technician_id} not found in organization")
        
        job.assigned_technician_id = technician_id
        job.updated_by_id = updated_by_id
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Assigned technician {technician_id} to installation job {job.job_number}")
        return job
    
    def update_job_status(
        self,
        job_id: int,
        status: str,
        updated_by_id: int,
        **kwargs
    ) -> InstallationJob:
        """Update installation job status"""
        
        job = self.db.query(InstallationJob).filter(
            InstallationJob.id == job_id
        ).first()
        
        if not job:
            raise ValueError(f"Installation job {job_id} not found")
        
        job.status = status
        job.updated_by_id = updated_by_id
        
        # Update specific timestamp fields based on status
        if status == "in_progress" and not job.actual_start_time:
            job.actual_start_time = datetime.now(timezone.utc)
        elif status == "completed" and not job.actual_end_time:
            job.actual_end_time = datetime.now(timezone.utc)
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        
        self.db.commit()
        self.db.refresh(job)
        
        logger.info(f"Updated installation job {job.job_number} status to {status}")
        return job