# Revised app.models.base.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime

# Platform User Model - For SaaS platform-level users
class PlatformUser(Base):
    __tablename__ = "platform_users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # User credentials
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    
    # User details
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="super_admin")  # super_admin, platform_admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Temporary master password support
    temp_password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Temporary password hash
    temp_password_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Expiry for temp password
    force_password_reset: Mapped[bool] = mapped_column(Boolean, default=False)  # Force password reset on next login
    
    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_platform_user_email', 'email'),
        Index('idx_platform_user_active', 'is_active'),
    )

# Organization/Tenant Model - Core of Multi-tenancy
class Organization(Base):
    __tablename__ = "organizations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    subdomain: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)  # For subdomain-based tenancy
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")  # active, suspended, trial
    
    # Business details
    business_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # manufacturing, trading, service, etc.
    industry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Contact information
    primary_email: Mapped[str] = mapped_column(String, nullable=False)
    primary_phone: Mapped[str] = mapped_column(String, nullable=False)
    
    # Address
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False, default="India")
    state_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Legal details
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Corporate Identification Number
    
    # Subscription details
    plan_type: Mapped[str] = mapped_column(String, default="trial")  # trial, basic, premium, enterprise
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    storage_limit_gb: Mapped[int] = mapped_column(Integer, default=1)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Feature flags
    
    # Settings
    timezone: Mapped[str] = mapped_column(String, default="Asia/Kolkata")
    currency: Mapped[str] = mapped_column(String, default="INR")
    date_format: Mapped[str] = mapped_column(String, default="DD/MM/YYYY")
    financial_year_start: Mapped[str] = mapped_column(String, default="04/01")  # April 1st
    
    # Onboarding status
    company_details_completed: Mapped[bool] = mapped_column(Boolean, default=False)  # Track if company details have been filled
    
    # Custom org code
    org_code: Mapped[Optional[str]] = mapped_column(String, nullable=True, unique=True, index=True)  # Custom format: yy/mm-(total user)-tqnnnn
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
    companies: Mapped[List["Company"]] = relationship("Company", back_populates="organization")
    vendors: Mapped[List["Vendor"]] = relationship("Vendor", back_populates="organization")
    customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="organization")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="organization")
    stock_entries: Mapped[List["Stock"]] = relationship("Stock", back_populates="organization")
    
    __table_args__ = (
        Index('idx_org_status_subdomain', 'status', 'subdomain'),
    )

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant fields - REQUIRED for all organization users
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # User credentials
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    
    # Supabase Auth integration
    supabase_uuid: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)  # Supabase user UUID for auth integration
    
    # User details
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="standard_user")  # org_admin, admin, standard_user
    department: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Permissions and status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_super_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    has_stock_access: Mapped[bool] = mapped_column(Boolean, default=True)  # Module access for stock functionality
    
    # Temporary master password support
    temp_password_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Temporary password hash
    temp_password_expires: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Expiry for temp password
    force_password_reset: Mapped[bool] = mapped_column(Boolean, default=False)  # Force password reset on next login
    
    # Profile
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="users")
    
    __table_args__ = (
        # Unique email per organization
        UniqueConstraint('organization_id', 'email', name='uq_user_org_email'),
        # Unique username per organization
        UniqueConstraint('organization_id', 'username', name='uq_user_org_username'),
        Index('idx_user_org_email', 'organization_id', 'email'),
        Index('idx_user_org_username', 'organization_id', 'username'),
        Index('idx_user_org_active', 'organization_id', 'is_active'),
    )

class Company(Base):
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Company details
    name: Mapped[str] = mapped_column(String, nullable=False)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String, nullable=False)
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contact_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logo_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="companies")
    
    __table_args__ = (
        Index('idx_company_org_name', 'organization_id', 'name'),
    )

class Vendor(Base):
    __tablename__ = "vendors"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Vendor details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String, nullable=False)
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="vendors")
    files: Mapped[List["VendorFile"]] = relationship("VendorFile", back_populates="vendor")
    
    __table_args__ = (
        # Unique vendor name per organization
        UniqueConstraint('organization_id', 'name', name='uq_vendor_org_name'),
        Index('idx_vendor_org_name', 'organization_id', 'name'),
        Index('idx_vendor_org_active', 'organization_id', 'is_active'),
    )

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Customer details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contact_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address1: Mapped[str] = mapped_column(String, nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_code: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[str] = mapped_column(String, nullable=False)
    gst_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="customers")
    files: Mapped[List["CustomerFile"]] = relationship("CustomerFile", back_populates="customer")
    interactions: Mapped[List["CustomerInteraction"]] = relationship("CustomerInteraction", back_populates="customer")
    segments: Mapped[List["CustomerSegment"]] = relationship("CustomerSegment", back_populates="customer")
    
    __table_args__ = (
        # Unique customer name per organization
        UniqueConstraint('organization_id', 'name', name='uq_customer_org_name'),
        Index('idx_customer_org_name', 'organization_id', 'name'),
        Index('idx_customer_org_active', 'organization_id', 'is_active'),
    )

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Product details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    hsn_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    part_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    gst_rate: Mapped[float] = mapped_column(Float, default=0.0)
    is_gst_inclusive: Mapped[bool] = mapped_column(Boolean, default=False)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_manufactured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="products")
    files: Mapped[List["ProductFile"]] = relationship("ProductFile", back_populates="product", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique product name per organization
        UniqueConstraint('organization_id', 'name', name='uq_product_org_name'),
        # Unique part number per organization (if provided)
        UniqueConstraint('organization_id', 'part_number', name='uq_product_org_part_number'),
        Index('idx_product_org_name', 'organization_id', 'name'),
        Index('idx_product_org_active', 'organization_id', 'is_active'),
        Index('idx_product_org_hsn', 'organization_id', 'hsn_code'),
    )

class ProductFile(Base):
    __tablename__ = "product_files"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # File details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="files")
    organization: Mapped["Organization"] = relationship("Organization")
    
    __table_args__ = (
        Index('idx_product_file_org_product', 'organization_id', 'product_id'),
    )

class CustomerFile(Base):
    __tablename__ = "customer_files"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # File details
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False, default="general")  # general, gst_certificate, pan_card, etc.
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="files")
    organization: Mapped["Organization"] = relationship("Organization")
    
    __table_args__ = (
        Index('idx_customer_file_org_customer', 'organization_id', 'customer_id'),
    )

class CustomerInteraction(Base):
    """
    Model for tracking customer interactions and communications.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "customer_interactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Customer reference
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Interaction details
    interaction_type: Mapped[str] = mapped_column(String, nullable=False)  # 'call', 'email', 'meeting', 'support_ticket', 'complaint', 'feedback'
    subject: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # 'pending', 'in_progress', 'completed', 'cancelled'
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # User who created this interaction record
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="interactions")
    organization: Mapped["Organization"] = relationship("Organization")
    created_by_user: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_customer_interaction_org_customer', 'organization_id', 'customer_id'),
        Index('idx_customer_interaction_type_status', 'interaction_type', 'status'),
        Index('idx_customer_interaction_date', 'interaction_date'),
    )

class CustomerSegment(Base):
    """
    Model for categorizing customers into segments for business and marketing purposes.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "customer_segments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Customer reference
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Segment details
    segment_name: Mapped[str] = mapped_column(String, nullable=False)  # 'vip', 'premium', 'regular', 'new', 'high_value', 'at_risk'
    segment_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Optional numeric value for the segment
    segment_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    assigned_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # User who assigned this segment
    assigned_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="segments")
    organization: Mapped["Organization"] = relationship("Organization")
    assigned_by_user: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_customer_segment_org_customer', 'organization_id', 'customer_id'),
        Index('idx_customer_segment_name_active', 'segment_name', 'is_active'),
        Index('idx_customer_segment_assigned_date', 'assigned_date'),
        # Ensure a customer can only have one active segment of the same name per organization
        UniqueConstraint('organization_id', 'customer_id', 'segment_name', name='uq_customer_segment_org_customer_name'),
    )

class VendorFile(Base):
    __tablename__ = "vendor_files"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # File details
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False, default="general")  # general, gst_certificate, pan_card, etc.
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="files")
    organization: Mapped["Organization"] = relationship("Organization")
    
    __table_args__ = (
        Index('idx_vendor_file_org_vendor', 'organization_id', 'vendor_id'),
    )

class Stock(Base):
    __tablename__ = "stock"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Stock details
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="stock_entries")
    product: Mapped["Product"] = relationship("Product", backref="stock_entries")
    
    __table_args__ = (
        # Unique stock entry entry per product per organization per location
        UniqueConstraint('organization_id', 'product_id', 'location', name='uq_stock_org_product_location'),
        Index('idx_stock_org_product', 'organization_id', 'product_id'),
        Index('idx_stock_org_location', 'organization_id', 'location'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Audit details
    table_name: Mapped[str] = mapped_column(String, nullable=False)
    record_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)  # CREATE, UPDATE, DELETE
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    changes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Store the changes made
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_audit_org_table_action', 'organization_id', 'table_name', 'action'),
        Index('idx_audit_org_timestamp', 'organization_id', 'timestamp'),
    )

class EmailNotification(Base):
    __tablename__ = "email_notifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Email details
    to_email: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    voucher_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    voucher_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, sent, failed
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_email_org_status', 'organization_id', 'status'),
    )

# Notification Templates for Service CRM
class NotificationTemplate(Base):
    """
    Model for notification templates supporting multi-channel messaging.
    Supports email, SMS, and push notifications with variable substitution.
    """
    __tablename__ = "notification_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Template details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_type: Mapped[str] = mapped_column(String, nullable=False)  # appointment_reminder, service_completion, follow_up, marketing
    
    # Channel support
    channel: Mapped[str] = mapped_column(String, nullable=False)  # email, sms, push, in_app
    
    # Message content
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # For email/push notifications
    body: Mapped[str] = mapped_column(Text, nullable=False)  # Main message content
    html_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # HTML version for emails
    
    # Trigger configuration
    trigger_event: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # customer_interaction, low_engagement, appointment_scheduled
    trigger_conditions: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # JSON conditions for automated triggers
    
    # Template variables (JSON array of variable names that can be substituted)
    variables: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # ["customer_name", "appointment_date", "service_type"]
    
    # Status and metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_notification_template_org_type', 'organization_id', 'template_type'),
        Index('idx_notification_template_org_channel', 'organization_id', 'channel'),
        UniqueConstraint('organization_id', 'name', name='uq_notification_template_org_name'),
    )

# Notification Logs for tracking sent notifications
class NotificationLog(Base):
    """
    Model for tracking all sent notifications with delivery status and metadata.
    """
    __tablename__ = "notification_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Template reference (optional - can send without template)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("notification_templates.id"), nullable=True)
    
    # Recipient information
    recipient_type: Mapped[str] = mapped_column(String, nullable=False)  # customer, user, segment
    recipient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # customer_id or user_id
    recipient_identifier: Mapped[str] = mapped_column(String, nullable=False)  # email, phone, device_token
    
    # Notification details
    channel: Mapped[str] = mapped_column(String, nullable=False)  # email, sms, push, in_app
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Delivery tracking
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, sent, delivered, failed, bounced
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # For email tracking
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # For link tracking
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Context information
    trigger_event: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # What triggered this notification
    context_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # Additional context data
    
    # Metadata
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_notification_log_org_status', 'organization_id', 'status'),
        Index('idx_notification_log_org_channel', 'organization_id', 'channel'),
        Index('idx_notification_log_recipient', 'recipient_type', 'recipient_id'),
        Index('idx_notification_log_sent_at', 'sent_at'),
    )

# Notification Preferences for users and customers
class NotificationPreference(Base):
    """
    Model for managing notification preferences for users and customers.
    """
    __tablename__ = "notification_preferences"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Subject (user or customer)
    subject_type: Mapped[str] = mapped_column(String, nullable=False)  # user, customer
    subject_id: Mapped[int] = mapped_column(Integer, nullable=False)  # user_id or customer_id
    
    # Preference details
    notification_type: Mapped[str] = mapped_column(String, nullable=False)  # appointment_reminder, service_completion, marketing, etc.
    channel: Mapped[str] = mapped_column(String, nullable=False)  # email, sms, push, in_app
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Channel-specific settings
    settings: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # Channel-specific preferences
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_notification_pref_org_subject', 'organization_id', 'subject_type', 'subject_id'),
        UniqueConstraint('organization_id', 'subject_type', 'subject_id', 'notification_type', 'channel', 
                        name='uq_notification_pref_subject_type_channel'),
    )
    
# Payment Terms
class PaymentTerm(Base):
    __tablename__ = "payment_terms"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Payment term details
    name: Mapped[str] = mapped_column(String, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index('idx_payment_term_org_name', 'organization_id', 'name'),
    )

class OTPVerification(Base):
    __tablename__ = "otp_verifications"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String, nullable=False)  # Store hashed OTP for security
    purpose: Mapped[str] = mapped_column(String, nullable=False, default="login")  # login, password_reset, registration
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_otp_email_purpose', 'email', 'purpose'),
        Index('idx_otp_expires', 'expires_at'),
    )


# Service CRM RBAC Models
class ServiceRole(Base):
    """Service CRM roles (admin, manager, support, viewer)"""
    __tablename__ = "service_roles"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Role details
    name: Mapped[str] = mapped_column(String, nullable=False)  # admin, manager, support, viewer
    display_name: Mapped[str] = mapped_column(String, nullable=False)  # Human-readable name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    user_assignments: Mapped[List["UserServiceRole"]] = relationship("UserServiceRole", back_populates="role")
    role_permissions: Mapped[List["ServiceRolePermission"]] = relationship("ServiceRolePermission", back_populates="role")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_service_role_org_name'),
        Index('idx_service_role_org_active', 'organization_id', 'is_active'),
    )


class ServicePermission(Base):
    """Service CRM permissions for granular access control"""
    __tablename__ = "service_permissions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Permission details
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)  # e.g., service_create, technician_read
    display_name: Mapped[str] = mapped_column(String, nullable=False)  # Human-readable name
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    module: Mapped[str] = mapped_column(String, nullable=False, index=True)  # service, technician, appointment, etc.
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)  # create, read, update, delete
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    role_permissions: Mapped[List["ServiceRolePermission"]] = relationship("ServiceRolePermission", back_populates="permission")
    
    __table_args__ = (
        Index('idx_service_permission_module_action', 'module', 'action'),
    )


class ServiceRolePermission(Base):
    """Many-to-many relationship between Service roles and permissions"""
    __tablename__ = "service_role_permissions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_roles.id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_permissions.id"), nullable=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    role: Mapped["ServiceRole"] = relationship("ServiceRole", back_populates="role_permissions")
    permission: Mapped["ServicePermission"] = relationship("ServicePermission", back_populates="role_permissions")
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_service_role_permission'),
        Index('idx_service_role_permission_role', 'role_id'),
        Index('idx_service_role_permission_permission', 'permission_id'),
    )


class UserServiceRole(Base):
    """Many-to-many relationship between Users and Service roles"""
    __tablename__ = "user_service_roles"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_roles.id"), nullable=False)
    
    # Assignment details
    assigned_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    role: Mapped["ServiceRole"] = relationship("ServiceRole", back_populates="user_assignments")
    assigned_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_by_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_service_role'),
        Index('idx_user_service_role_user', 'user_id'),
        Index('idx_user_service_role_role', 'role_id'),
        Index('idx_user_service_role_active', 'is_active'),
    )


class Ticket(Base):
    """
    Model for customer support tickets in the Service CRM.
    Supports multi-tenant architecture with organization-level isolation.
    """
    __tablename__ = "tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Ticket identification
    ticket_number: Mapped[str] = mapped_column(String, nullable=False, index=True)  # Auto-generated unique ticket number
    
    # Customer and assignment
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Assigned technician/user
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)  # Who created the ticket
    
    # Ticket details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")  # 'open', 'in_progress', 'resolved', 'closed', 'cancelled'
    priority: Mapped[str] = mapped_column(String, nullable=False, default="medium")  # 'low', 'medium', 'high', 'urgent'
    ticket_type: Mapped[str] = mapped_column(String, nullable=False, default="support")  # 'support', 'maintenance', 'installation', 'complaint'
    
    # Resolution details
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # SLA and business metrics
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Customer satisfaction
    customer_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 rating
    customer_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped["Customer"] = relationship("Customer")
    assigned_to: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to_id])
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_id])
    history: Mapped[List["TicketHistory"]] = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")
    attachments: Mapped[List["TicketAttachment"]] = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    
    __table_args__ = (
        # Unique ticket number per organization
        UniqueConstraint('organization_id', 'ticket_number', name='uq_ticket_org_number'),
        Index('idx_ticket_org_status', 'organization_id', 'status'),
        Index('idx_ticket_org_priority', 'organization_id', 'priority'),
        Index('idx_ticket_org_type', 'organization_id', 'ticket_type'),
        Index('idx_ticket_org_customer', 'organization_id', 'customer_id'),
        Index('idx_ticket_org_assigned', 'organization_id', 'assigned_to_id'),
        Index('idx_ticket_created_at', 'created_at'),
        Index('idx_ticket_due_date', 'due_date'),
    )


class TicketHistory(Base):
    """
    Model for tracking ticket status changes and updates.
    Provides audit trail for all ticket modifications.
    """
    __tablename__ = "ticket_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Ticket reference
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    
    # Change details
    action: Mapped[str] = mapped_column(String, nullable=False)  # 'created', 'status_changed', 'assigned', 'updated', 'commented'
    field_changed: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Which field was changed
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Previous value
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # New value
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Additional comments
    
    # User who made the change
    changed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="history")
    changed_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_ticket_history_org_ticket', 'organization_id', 'ticket_id'),
        Index('idx_ticket_history_action', 'action'),
        Index('idx_ticket_history_created_at', 'created_at'),
        Index('idx_ticket_history_user', 'changed_by_id'),
    )


class TicketAttachment(Base):
    """
    Model for file attachments on tickets.
    Follows the same pattern as CustomerFile and VendorFile.
    """
    __tablename__ = "ticket_attachments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Ticket reference
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    
    # File details
    filename: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False, default="general")  # general, screenshot, document, etc.
    
    # Upload details
    uploaded_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="attachments")
    uploaded_by: Mapped[Optional["User"]] = relationship("User")
    
    __table_args__ = (
        Index('idx_ticket_attachment_org_ticket', 'organization_id', 'ticket_id'),
        Index('idx_ticket_attachment_type', 'file_type'),
        Index('idx_ticket_attachment_uploaded_by', 'uploaded_by_id'),
    )