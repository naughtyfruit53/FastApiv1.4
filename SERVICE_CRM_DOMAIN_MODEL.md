# Service CRM Domain Model Specification

## Overview

This document provides a comprehensive domain model specification for the Service CRM integration into the TRITIQ ERP system. The domain model defines the business entities, relationships, and behaviors that support service-oriented business operations while maintaining seamless integration with the existing ERP foundation.

## 🏗️ Domain Architecture

### Core Domain Concepts

The Service CRM domain extends the existing ERP domain with service-specific business concepts:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Service CRM Domain                      │
├─────────────────────────────────────────────────────────────────┤
│  Service Management    │  Workforce Management  │  Customer Care │
│  • Service Catalog     │  • Technicians         │  • Service History│
│  • Service Categories  │  • Skills & Certs      │  • Preferences  │
│  • Pricing Tiers      │  • Schedules           │  • Communication│
│                        │  • Availability        │  • Satisfaction │
├─────────────────────────────────────────────────────────────────┤
│                    Core Business Processes                     │
│  • Appointment Scheduling  • Service Execution  • Billing      │
│  • Resource Assignment    • Quality Control     • Reporting    │
├─────────────────────────────────────────────────────────────────┤
│                    Existing ERP Foundation                     │
│  • Organizations  • Users  • Customers  • Financial Vouchers   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Business Entities and Relationships

### Entity Relationship Diagram

```
                                   Organization
                                       │
                      ┌────────────────┼────────────────┐
                      │                │                │
                  Customer         ServiceItem      Technician
                      │                │                │
                      │                │                │
               ┌──────┴──────┐        │        ┌──────┴──────┐
               │             │        │        │             │
        CustomerContact CustomerPrefs │   TechSkills  TechSchedule
               │             │        │        │             │
               │             │        │        │             │
               └─────────────┴────────┼────────┴─────────────┘
                                      │
                                 Appointment
                                      │
                                      │
                              ServiceExecution
                                      │
                       ┌──────────────┼──────────────┐
                       │              │              │
                 ServiceNotes    ServicePhotos  PartsUsed
```

### Detailed Entity Specifications

#### 1. Service Management Entities

##### ServiceCategory
**Purpose**: Hierarchical organization of services offered by the organization

```python
class ServiceCategory:
    # Identity
    id: int
    organization_id: int  # Multi-tenant isolation
    parent_category_id: Optional[int]  # For hierarchy
    
    # Business Data
    name: str  # "HVAC", "Electrical", "Plumbing"
    description: Optional[str]
    icon_url: Optional[str]  # For UI display
    sort_order: int  # Display ordering
    
    # Status
    is_active: bool
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: int
    
    # Business Rules
    def validate_hierarchy_depth(self) -> bool:
        """Ensure category hierarchy doesn't exceed 3 levels"""
        pass
    
    def get_all_subcategories(self) -> List['ServiceCategory']:
        """Get all subcategories recursively"""
        pass
```

##### ServiceItem
**Purpose**: Individual services that can be booked and performed

```python
class ServiceItem:
    # Identity
    id: int
    organization_id: int
    category_id: int
    
    # Business Data
    name: str  # "AC Installation", "Brake Repair"
    description: str  # Detailed service description
    short_description: Optional[str]  # For lists/summaries
    
    # Service Characteristics
    estimated_duration_minutes: int  # 120 for 2-hour service
    requires_appointment: bool  # vs walk-in service
    requires_customer_presence: bool
    
    # Skill Requirements
    required_skills: List[str]  # JSON: ["electrical_level_2", "hvac_certified"]
    required_equipment: List[str]  # JSON: ["multimeter", "ladder", "safety_gear"]
    
    # Pricing
    base_price: Decimal
    pricing_model: str  # "fixed", "hourly", "quote_based"
    
    # Status and Availability
    is_active: bool
    is_bookable_online: bool
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def calculate_price(self, duration: int, parts: List[str]) -> Decimal:
        """Calculate total service price including parts"""
        pass
    
    def get_available_technicians(self, date: datetime) -> List[Technician]:
        """Find technicians qualified and available for this service"""
        pass
```

##### ServicePricing
**Purpose**: Flexible pricing tiers and special pricing rules

```python
class ServicePricing:
    # Identity
    id: int
    service_id: int
    
    # Pricing Details
    tier_name: str  # "standard", "premium", "emergency"
    price: Decimal
    pricing_unit: str  # "fixed", "per_hour", "per_item"
    
    # Validity
    effective_from: datetime
    effective_to: Optional[datetime]
    is_default: bool
    
    # Conditions
    minimum_notice_hours: Optional[int]  # For emergency pricing
    customer_type_restriction: Optional[str]  # "premium_only"
    time_restrictions: Optional[dict]  # JSON: {"weekends": true, "after_hours": true}
    
    # Business Rules
    def is_applicable(self, customer: Customer, appointment_time: datetime) -> bool:
        """Check if pricing tier applies to specific booking"""
        pass
```

#### 2. Workforce Management Entities

##### Technician
**Purpose**: Service technicians linked to system users

```python
class Technician:
    # Identity
    id: int
    organization_id: int
    user_id: int  # Links to existing User model
    
    # Employment Details
    employee_id: str  # Company employee ID
    hire_date: date
    employment_status: str  # "active", "inactive", "vacation"
    
    # Contact Information
    mobile_phone: str
    emergency_contact_name: str
    emergency_contact_phone: str
    
    # Professional Details
    certifications: List[dict]  # JSON: [{"name": "HVAC Level 2", "expires": "2025-01-01"}]
    specializations: List[str]  # ["residential_hvac", "commercial_electrical"]
    
    # Service Assignment
    service_territory: Optional[dict]  # JSON: Geographic boundaries
    max_daily_assignments: int  # Workload management
    
    # Performance Metrics
    average_rating: Optional[float]
    completion_rate: Optional[float]
    response_time_avg_minutes: Optional[int]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def is_qualified_for_service(self, service: ServiceItem) -> bool:
        """Check if technician has required skills for service"""
        pass
    
    def get_current_workload(self, date: date) -> int:
        """Get number of assignments for specific date"""
        pass
```

##### TechnicianSkill
**Purpose**: Skills and competencies tracking

```python
class TechnicianSkill:
    # Identity
    id: int
    technician_id: int
    
    # Skill Details
    skill_name: str  # "electrical_wiring", "hvac_diagnosis"
    proficiency_level: str  # "beginner", "intermediate", "advanced", "expert"
    
    # Certification
    is_certified: bool
    certification_date: Optional[date]
    certification_expires: Optional[date]
    certifying_body: Optional[str]
    
    # Performance
    years_experience: Optional[int]
    last_training_date: Optional[date]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def is_current_certification(self) -> bool:
        """Check if certification is still valid"""
        pass
    
    def needs_renewal_soon(self, days_ahead: int = 90) -> bool:
        """Check if certification expires within specified days"""
        pass
```

##### TechnicianSchedule
**Purpose**: Work schedule and availability management

```python
class TechnicianSchedule:
    # Identity
    id: int
    technician_id: int
    
    # Schedule Details
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time  # 08:00
    end_time: time    # 17:00
    
    # Break Times
    break_start: Optional[time]  # 12:00
    break_end: Optional[time]    # 13:00
    
    # Availability
    is_available: bool
    is_on_call: bool  # Available for emergency calls
    
    # Schedule Variations
    effective_from: date
    effective_to: Optional[date]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def get_available_hours(self) -> float:
        """Calculate available working hours for the day"""
        pass
    
    def has_conflict_with_appointment(self, start: time, end: time) -> bool:
        """Check if appointment time conflicts with schedule"""
        pass
```

#### 3. Appointment and Service Execution Entities

##### Appointment
**Purpose**: Central entity for service bookings and scheduling

```python
class Appointment:
    # Identity
    id: int
    organization_id: int
    
    # Core Relationships
    customer_id: int
    service_id: int
    technician_id: Optional[int]  # Assigned technician
    
    # Scheduling
    appointment_date: date
    start_time: time
    end_time: time
    estimated_duration_minutes: int
    
    # Location
    service_address: dict  # JSON: Full address including GPS coordinates
    access_instructions: Optional[str]  # "Use side entrance", "Call on arrival"
    
    # Status Management
    status: str  # "scheduled", "confirmed", "in_progress", "completed", "cancelled"
    priority: str  # "standard", "urgent", "emergency"
    
    # Customer Communication
    customer_phone: str  # May differ from customer's primary phone
    customer_email: str
    customer_notes: Optional[str]  # Special requests, preferences
    
    # Internal Management
    internal_notes: Optional[str]  # Staff-only notes
    assigned_by: Optional[int]  # User who assigned technician
    assigned_at: Optional[datetime]
    
    # Billing
    quoted_price: Optional[Decimal]
    pricing_tier: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: int
    
    # Business Rules
    def can_be_assigned_to_technician(self, technician: Technician) -> bool:
        """Validate technician assignment considering skills and availability"""
        pass
    
    def calculate_travel_time(self, from_location: dict) -> int:
        """Calculate travel time from previous appointment or depot"""
        pass
    
    def get_status_history(self) -> List[dict]:
        """Get chronological status changes"""
        pass
```

##### ServiceExecution
**Purpose**: Tracking actual service work performed

```python
class ServiceExecution:
    # Identity
    id: int
    appointment_id: int
    technician_id: int
    
    # Execution Timeline
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    actual_duration_minutes: Optional[int]
    
    # Work Performed
    work_description: str  # What was actually done
    work_category: str  # "installation", "repair", "maintenance", "diagnostic"
    
    # Service Outcome
    status: str  # "in_progress", "completed", "incomplete", "cancelled"
    completion_reason: Optional[str]  # "completed_successfully", "customer_cancelled", "parts_needed"
    
    # Quality Control
    quality_check_passed: Optional[bool]
    quality_notes: Optional[str]
    
    # Customer Interaction
    customer_present: bool
    customer_signature_captured: bool
    customer_signature_data: Optional[str]  # Base64 signature image
    
    # Parts and Materials
    parts_used: List[dict]  # JSON: [{"part_id": 123, "quantity": 2, "cost": 45.99}]
    materials_cost: Optional[Decimal]
    
    # Follow-up
    requires_follow_up: bool
    follow_up_date: Optional[date]
    follow_up_notes: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def calculate_total_cost(self) -> Decimal:
        """Calculate total cost including labor and parts"""
        pass
    
    def generate_service_report(self) -> dict:
        """Generate customer service report"""
        pass
```

##### ServiceNote
**Purpose**: Communication and documentation throughout service lifecycle

```python
class ServiceNote:
    # Identity
    id: int
    execution_id: int
    
    # Note Details
    note_type: str  # "work_log", "customer_communication", "issue", "solution"
    content: str
    
    # Visibility and Access
    visibility: str  # "internal", "customer_visible", "technician_only"
    is_important: bool  # Flag for highlighting
    
    # Authorship
    created_by: int  # User ID
    created_by_role: str  # "technician", "dispatcher", "manager"
    
    # Customer Communication
    sent_to_customer: bool
    customer_acknowledged: bool
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def can_be_edited_by(self, user_id: int, user_role: str) -> bool:
        """Check if user can edit this note"""
        pass
```

#### 4. Customer Service Enhancement Entities

##### CustomerPreference
**Purpose**: Customer service preferences and requirements

```python
class CustomerPreference:
    # Identity
    id: int
    customer_id: int
    
    # Technician Preferences
    preferred_technician_id: Optional[int]
    avoid_technician_ids: List[int]  # JSON array
    
    # Scheduling Preferences
    preferred_time_slots: dict  # JSON: {"morning": true, "afternoon": false, "weekend": true}
    preferred_days: List[int]  # JSON: [1,2,3,4,5] for weekdays
    advance_notice_required_hours: int  # Minimum booking notice
    
    # Communication Preferences
    communication_method: str  # "email", "sms", "phone", "app_notification"
    send_reminders: bool
    reminder_hours_before: int  # 24, 2, etc.
    
    # Service Preferences
    special_instructions: Optional[str]
    access_information: Optional[str]  # Gate codes, key location
    pet_information: Optional[str]  # "Large dog - friendly", "Cat - allergic"
    
    # Billing Preferences
    preferred_payment_method: str
    requires_quote_approval: bool
    spending_limit: Optional[Decimal]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    # Business Rules
    def is_time_slot_preferred(self, appointment_time: datetime) -> bool:
        """Check if appointment time matches preferences"""
        pass
```

##### CustomerServiceHistory
**Purpose**: Aggregated service history for customer insights

```python
class CustomerServiceHistory:
    # Identity
    id: int
    customer_id: int
    service_id: int
    execution_id: int
    
    # Service Details
    service_date: date
    service_category: str
    service_description: str
    technician_name: str
    
    # Financial
    total_amount: Decimal
    payment_status: str  # "paid", "pending", "overdue"
    payment_method: Optional[str]
    
    # Customer Experience
    satisfaction_rating: Optional[int]  # 1-5 stars
    customer_feedback: Optional[str]
    would_recommend: Optional[bool]
    
    # Service Outcome
    issue_resolved: bool
    requires_follow_up: bool
    warranty_period_days: Optional[int]
    
    # Metadata
    created_at: datetime
    
    # Business Rules
    def is_under_warranty(self) -> bool:
        """Check if service is still under warranty"""
        pass
    
    def calculate_customer_lifetime_value(self) -> Decimal:
        """Calculate total value from this customer"""
        pass
```

## 🔄 Business Process Flows

### 1. Service Booking Process

```
Customer Request → Service Selection → Availability Check → Technician Assignment → Confirmation
      │                   │                  │                     │                │
      ▼                   ▼                  ▼                     ▼                ▼
Customer Portal      Service Catalog    Schedule Check      Skill Matching    Email/SMS
Phone Call          Pricing Lookup     Conflict Detection   Workload Balance   Confirmation
Walk-in             Quote Generation   Travel Time Calc     Auto-assignment    Calendar Entry
```

### 2. Service Execution Workflow

```
Appointment Scheduled → Pre-Service → Service Start → Work Performance → Service Completion
         │                  │            │               │                    │
         ▼                  ▼            ▼               ▼                    ▼
Route Optimization    Customer Contact   Check-in       Work Documentation   Customer Sign-off
Technician Notice     Parts Preparation  Status Update   Photo Capture       Quality Check
Equipment Check       Access Confirm     Time Tracking   Parts Recording     Invoice Generation
```

### 3. Customer Satisfaction Loop

```
Service Completion → Feedback Request → Rating Collection → Issue Resolution → Improvement
        │                  │                │                   │              │
        ▼                  ▼                ▼                   ▼              ▼
Auto Email/SMS        Survey Form        Database Update     Follow-up Call   Process Refinement
Follow-up Call        Mobile App         Analytics Update    Service Credit   Training Update
Quality Check         Portal Rating      Report Generation   Technician Feedback  System Enhancement
```

## 🔀 Domain Events

### Service Lifecycle Events

```python
# Domain events for service business processes
class ServiceDomainEvent:
    event_id: str
    organization_id: int
    timestamp: datetime
    event_type: str
    event_data: dict

# Key domain events
APPOINTMENT_SCHEDULED = "appointment.scheduled"
TECHNICIAN_ASSIGNED = "technician.assigned"
SERVICE_STARTED = "service.started"
SERVICE_COMPLETED = "service.completed"
CUSTOMER_RATING_RECEIVED = "customer.rating_received"
PAYMENT_PROCESSED = "payment.processed"

# Event handlers for business process automation
class ServiceEventHandler:
    async def handle_appointment_scheduled(self, event: ServiceDomainEvent):
        """Handle new appointment scheduling"""
        # Send confirmation email
        # Add to technician calendar
        # Update availability
        # Schedule reminders
    
    async def handle_service_completed(self, event: ServiceDomainEvent):
        """Handle service completion"""
        # Generate invoice
        # Send satisfaction survey
        # Update customer history
        # Calculate technician performance metrics
```

## 🎯 Business Rules and Constraints

### Core Business Rules

1. **Appointment Scheduling Rules**
   - No double-booking of technicians
   - Minimum 2-hour advance booking (configurable per organization)
   - Maximum 8 appointments per technician per day
   - Emergency appointments can override normal scheduling rules

2. **Technician Assignment Rules**
   - Technician must have required skills for service
   - Consider travel time between appointments
   - Respect technician working hours and schedules
   - Balance workload across available technicians

3. **Pricing Rules**
   - Emergency services have 50% surcharge after hours
   - Loyal customers (5+ services) get 10% discount
   - Pricing tiers based on service complexity and timing
   - Parts markup of 15-30% based on cost

4. **Customer Communication Rules**
   - Respect customer communication preferences
   - Mandatory confirmation for appointments over $500
   - Send reminder 24 hours and 2 hours before appointment
   - Follow up within 24 hours of service completion

### Data Integrity Constraints

```python
# Database constraints for business rule enforcement
class ServiceBusinessRules:
    
    @validates('appointment.technician_assignment')
    def validate_technician_availability(self, appointment: Appointment):
        """Ensure technician is available for appointment time"""
        conflicts = check_technician_conflicts(
            appointment.technician_id,
            appointment.appointment_date,
            appointment.start_time,
            appointment.end_time
        )
        if conflicts:
            raise ValueError(f"Technician has conflicting appointment: {conflicts}")
    
    @validates('service_execution.completion')
    def validate_service_completion(self, execution: ServiceExecution):
        """Ensure service completion data is valid"""
        if execution.status == 'completed':
            if not execution.completed_at:
                raise ValueError("Completion timestamp required for completed services")
            if not execution.customer_signature_captured and execution.requires_signature:
                raise ValueError("Customer signature required for this service type")
```

## 📊 Domain Metrics and KPIs

### Service Performance Metrics

```python
class ServiceMetrics:
    """Business metrics for service domain"""
    
    # Operational Metrics
    first_time_fix_rate: float  # Percentage of services completed on first visit
    average_response_time: int  # Minutes from appointment to service start
    technician_utilization: float  # Percentage of available hours booked
    customer_satisfaction_score: float  # Average rating 1-5
    
    # Financial Metrics
    revenue_per_technician: Decimal  # Monthly revenue per technician
    service_margin: float  # Profit margin percentage
    average_service_value: Decimal  # Average revenue per service
    
    # Quality Metrics
    completion_rate: float  # Percentage of scheduled appointments completed
    rework_rate: float  # Percentage of services requiring follow-up
    customer_retention_rate: float  # Percentage of repeat customers
    
    def calculate_service_efficiency(self, period: str) -> dict:
        """Calculate comprehensive efficiency metrics"""
        pass
    
    def generate_performance_dashboard(self) -> dict:
        """Generate executive dashboard data"""
        pass
```

This domain model provides a comprehensive foundation for implementing the Service CRM integration while maintaining alignment with existing ERP business processes and ensuring scalability for various service-oriented business models.