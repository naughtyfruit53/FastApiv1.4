# app/schemas/dispatch.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.schemas.base import BaseSchema


class DispatchOrderStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class DispatchItemStatus(str, Enum):
    PENDING = "pending"
    PACKED = "packed"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"


class InstallationJobStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class InstallationJobPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# DispatchItem Schemas
class DispatchItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0, description="Quantity must be greater than 0")
    unit: str
    description: Optional[str] = None
    serial_numbers: Optional[str] = None
    batch_numbers: Optional[str] = None
    status: DispatchItemStatus = DispatchItemStatus.PENDING


class DispatchItemCreate(DispatchItemBase):
    pass


class DispatchItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[float] = Field(None, gt=0, description="Quantity must be greater than 0")
    unit: Optional[str] = None
    description: Optional[str] = None
    serial_numbers: Optional[str] = None
    batch_numbers: Optional[str] = None
    status: Optional[DispatchItemStatus] = None


class DispatchItemInDB(DispatchItemBase, BaseSchema):
    dispatch_order_id: int
    
    class Config:
        from_attributes = True


# DispatchOrder Schemas
class DispatchOrderBase(BaseModel):
    customer_id: int
    ticket_id: Optional[int] = None
    status: DispatchOrderStatus = DispatchOrderStatus.PENDING
    dispatch_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    delivery_address: str
    delivery_contact_person: Optional[str] = None
    delivery_contact_number: Optional[str] = None
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    courier_name: Optional[str] = None


class DispatchOrderCreate(DispatchOrderBase):
    items: List[DispatchItemCreate] = []

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item is required')
        return v


class DispatchOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    ticket_id: Optional[int] = None
    status: Optional[DispatchOrderStatus] = None
    dispatch_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    delivery_contact_person: Optional[str] = None
    delivery_contact_number: Optional[str] = None
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    courier_name: Optional[str] = None


class DispatchOrderInDB(DispatchOrderBase, BaseSchema):
    order_number: str
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    items: List[DispatchItemInDB] = []
    
    class Config:
        from_attributes = True


# InstallationJob Schemas
class InstallationJobBase(BaseModel):
    customer_id: int
    ticket_id: Optional[int] = None
    status: InstallationJobStatus = InstallationJobStatus.SCHEDULED
    priority: InstallationJobPriority = InstallationJobPriority.MEDIUM
    scheduled_date: Optional[datetime] = None
    estimated_duration_hours: Optional[float] = Field(None, gt=0, description="Duration must be greater than 0")
    installation_address: str
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    installation_notes: Optional[str] = None
    assigned_technician_id: Optional[int] = None


class InstallationJobCreate(InstallationJobBase):
    dispatch_order_id: int


class InstallationJobUpdate(BaseModel):
    customer_id: Optional[int] = None
    ticket_id: Optional[int] = None
    status: Optional[InstallationJobStatus] = None
    priority: Optional[InstallationJobPriority] = None
    scheduled_date: Optional[datetime] = None
    estimated_duration_hours: Optional[float] = Field(None, gt=0, description="Duration must be greater than 0")
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    installation_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    installation_notes: Optional[str] = None
    completion_notes: Optional[str] = None
    customer_feedback: Optional[str] = None
    customer_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1 and 5")
    assigned_technician_id: Optional[int] = None


class InstallationJobInDB(InstallationJobBase, BaseSchema):
    job_number: str
    dispatch_order_id: int
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    completion_notes: Optional[str] = None
    customer_feedback: Optional[str] = None
    customer_rating: Optional[int] = None
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True


# Installation Schedule Prompt Response
class InstallationSchedulePromptResponse(BaseModel):
    create_installation_schedule: bool
    installation_job: Optional[InstallationJobCreate] = None

    @validator('installation_job')
    def validate_installation_job(cls, v, values):
        if values.get('create_installation_schedule') and not v:
            raise ValueError('Installation job details required when creating schedule')
        return v


# List/Filter Schemas
class DispatchOrderFilter(BaseModel):
    status: Optional[DispatchOrderStatus] = None
    customer_id: Optional[int] = None
    ticket_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class InstallationJobFilter(BaseModel):
    status: Optional[InstallationJobStatus] = None
    priority: Optional[InstallationJobPriority] = None
    customer_id: Optional[int] = None
    assigned_technician_id: Optional[int] = None
    dispatch_order_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None