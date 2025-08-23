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
    
    __table_args__ = (
        # Unique customer name per organization
        UniqueConstraint('organization_id', 'name', name='uq_customer_org_name'),
        Index('idx_customer_org_name', 'organization_id', 'name'),
        Index('idx_customer_org_active', 'organization_id', 'is_active'),
    )

class CustomerInteraction(Base):
    __tablename__ = "customer_interactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Customer reference
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Interaction details
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="interactions")
    
    __table_args__ = (
        Index('idx_customer_interaction_org_customer', 'organization_id', 'customer_id'),
        Index('idx_customer_interaction_org_date', 'organization_id', 'date'),
        Index('idx_customer_interaction_org_type', 'organization_id', 'type'),
    )

class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Segment details
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    
    __table_args__ = (
        # Unique segment name per organization
        UniqueConstraint('organization_id', 'name', name='uq_customer_segment_org_name'),
        Index('idx_customer_segment_org_name', 'organization_id', 'name'),
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