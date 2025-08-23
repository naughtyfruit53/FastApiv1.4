# Service CRM Integration - Architecture & Implementation Plan

## Overview

This document outlines the comprehensive architecture and implementation plan for integrating Service Customer Relationship Management (CRM) capabilities into the existing TRITIQ ERP system. The Service CRM module will extend the current multi-tenant ERP platform to support service-oriented businesses with appointment scheduling, technician management, service catalog, and customer relationship features.

## 🎯 Business Objectives

### Primary Goals
- **Service Business Support**: Enable service companies to manage their operations end-to-end
- **Customer Experience**: Provide seamless customer booking and service tracking
- **Workforce Management**: Efficiently manage technicians and service delivery
- **Revenue Integration**: Seamlessly integrate service billing with existing financial system
- **Compliance**: Maintain data privacy, security, and regulatory compliance

### Key Metrics
- Reduce service booking time by 70%
- Improve technician utilization by 40%
- Increase customer satisfaction through better service tracking
- Streamline service-to-cash workflow integration

## 🏗️ High-Level Architecture

### System Integration Approach
```
┌─────────────────────────────────────────────────────────────┐
│                    TRITIQ ERP Platform                     │
├─────────────────────────────────────────────────────────────┤
│  Existing Core Modules           │  New Service CRM Module   │
├─────────────────────────────────────────────────────────────┤
│  • Organization Management       │  • Service Catalog        │
│  • User & Role Management        │  • Appointment Scheduling │
│  • Financial Vouchers            │  • Technician Management  │
│  • Customer/Vendor Master        │  • Service History        │
│  • Product/Stock Management      │  • Customer Portal        │
│  • Multi-tenant Infrastructure   │  • Mobile Workforce App   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Shared Foundation                          │
├─────────────────────────────────────────────────────────────┤
│  • Database (PostgreSQL)                                   │
│  • Authentication & Authorization                          │
│  • API Gateway & Rate Limiting                            │
│  • Email/SMS Notifications                                │
│  • File Storage & Document Management                     │
│  • Audit Logging & Compliance                             │
└─────────────────────────────────────────────────────────────┘
```

### Integration Strategy
1. **Extension Pattern**: Build on existing multi-tenant foundation
2. **Data Consistency**: Leverage existing customer/organization models
3. **API Consistency**: Follow established REST patterns and authentication
4. **UI Consistency**: Extend existing Next.js frontend with new modules
5. **Workflow Integration**: Connect service processes with financial vouchers

## 📊 Domain Model

### Core Service CRM Entities

```
Organization (existing)
├── Services
│   ├── ServiceCategory
│   └── ServiceItem
├── Technicians
│   ├── TechnicianProfile
│   ├── TechnicianSkills
│   └── TechnicianSchedule
├── Appointments
│   ├── AppointmentBooking
│   ├── AppointmentStatus
│   └── AppointmentHistory
├── CustomerService (extends existing Customer)
│   ├── ServiceHistory
│   ├── CustomerPreferences
│   └── CustomerContacts
└── ServiceDelivery
    ├── ServiceExecution
    ├── ServiceNotes
    └── ServiceRating
```

### Entity Relationship Diagram (ASCII)

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
                       │              │              │
                       │              │              │
                       └──────────────┼──────────────┘
                                      │
                                   Ticket ◄─────── Customer
                                      │
                               ┌──────┴──────┐
                               │             │
                         TicketHistory  TicketAttachment
```

## 🗄️ Database Schema Extensions

### New Tables to be Added

#### 1. Service Management Tables

```sql
-- Service categories for organization
service_categories:
  - id, organization_id, name, description, is_active, created_at, updated_at

-- Individual services offered
service_items:
  - id, organization_id, category_id, name, description
  - duration_minutes, price, is_active, requires_appointment
  - skills_required (JSON), equipment_needed (JSON)
  - created_at, updated_at

-- Service pricing tiers
service_pricing:
  - id, service_id, tier_name, price, effective_from, effective_to
  - is_default, created_at, updated_at
```

#### 2. Technician Management Tables

```sql
-- Technician profiles
technicians:
  - id, organization_id, user_id (FK to users), employee_id
  - hire_date, status, phone, emergency_contact
  - certifications (JSON), created_at, updated_at

-- Technician skills mapping
technician_skills:
  - id, technician_id, skill_name, proficiency_level
  - certified_date, expires_date, created_at, updated_at

-- Technician availability
technician_schedules:
  - id, technician_id, day_of_week, start_time, end_time
  - is_available, break_start, break_end, created_at, updated_at
```

#### 3. Appointment & Service Delivery Tables

```sql
-- Appointment bookings
appointments:
  - id, organization_id, customer_id, service_id, technician_id
  - appointment_date, start_time, end_time, status
  - customer_notes, internal_notes, priority
  - address (JSON), contact_person, contact_phone
  - created_at, updated_at, created_by

-- Service execution tracking
service_executions:
  - id, appointment_id, technician_id, started_at, completed_at
  - status, work_performed, parts_used (JSON)
  - customer_signature, photos (JSON), created_at, updated_at

-- Service notes and updates
service_notes:
  - id, execution_id, note_type, content, visibility
  - created_by, created_at, updated_at

-- Customer service history
customer_service_history:
  - id, customer_id, service_id, execution_id
  - service_date, satisfaction_rating, feedback
  - total_amount, payment_status, created_at, updated_at
```

#### 4. Extended Customer Tables

```sql
-- Customer preferences
customer_preferences:
  - id, customer_id, preferred_technician_id
  - preferred_time_slots (JSON), communication_method
  - special_instructions, created_at, updated_at

-- Customer contacts (multiple contacts per customer)
customer_contacts:
  - id, customer_id, contact_type, name, phone, email
  - is_primary, is_active, created_at, updated_at
```

#### 5. Ticket Management Tables

```sql
-- Customer support tickets
tickets:
  - id, organization_id, ticket_number (unique per org), customer_id
  - assigned_to_id (FK to users), created_by_id (FK to users)
  - title, description, status (open, in_progress, resolved, closed, cancelled)
  - priority (low, medium, high, urgent), ticket_type (support, maintenance, installation, complaint)
  - resolution, resolved_at, closed_at, due_date
  - estimated_hours, actual_hours, customer_rating (1-5), customer_feedback
  - created_at, updated_at

-- Ticket status change history and audit trail
ticket_history:
  - id, organization_id, ticket_id, action (created, status_changed, assigned, updated, commented)
  - field_changed, old_value, new_value, comment
  - changed_by_id (FK to users), created_at

-- Ticket file attachments
ticket_attachments:
  - id, organization_id, ticket_id, filename, original_filename
  - file_path, file_size, content_type, file_type (general, screenshot, document)
  - uploaded_by_id (FK to users), created_at, updated_at
```

### Database Indexes Strategy

```sql
-- Performance optimization indexes
CREATE INDEX idx_appointments_org_date ON appointments(organization_id, appointment_date);
CREATE INDEX idx_appointments_technician_date ON appointments(technician_id, appointment_date);
CREATE INDEX idx_appointments_customer ON appointments(customer_id, status);
CREATE INDEX idx_service_executions_status ON service_executions(status, started_at);
CREATE INDEX idx_technician_skills_lookup ON technician_skills(technician_id, skill_name);

-- Ticket management indexes
CREATE INDEX idx_ticket_org_status ON tickets(organization_id, status);
CREATE INDEX idx_ticket_org_priority ON tickets(organization_id, priority);
CREATE INDEX idx_ticket_org_customer ON tickets(organization_id, customer_id);
CREATE INDEX idx_ticket_org_assigned ON tickets(organization_id, assigned_to_id);
CREATE INDEX idx_ticket_created_at ON tickets(created_at);
CREATE INDEX idx_ticket_due_date ON tickets(due_date);
CREATE INDEX idx_ticket_history_org_ticket ON ticket_history(organization_id, ticket_id);
CREATE INDEX idx_ticket_attachment_org_ticket ON ticket_attachments(organization_id, ticket_id);
```

## 🔌 API Endpoint Architecture

### Service Management APIs

#### Service Catalog Management
```
GET    /api/v1/organizations/{org_id}/services/categories
POST   /api/v1/organizations/{org_id}/services/categories
PUT    /api/v1/organizations/{org_id}/services/categories/{id}
DELETE /api/v1/organizations/{org_id}/services/categories/{id}

GET    /api/v1/organizations/{org_id}/services/items
POST   /api/v1/organizations/{org_id}/services/items
PUT    /api/v1/organizations/{org_id}/services/items/{id}
DELETE /api/v1/organizations/{org_id}/services/items/{id}
GET    /api/v1/organizations/{org_id}/services/items/{id}/pricing
```

#### Technician Management
```
GET    /api/v1/organizations/{org_id}/technicians
POST   /api/v1/organizations/{org_id}/technicians
PUT    /api/v1/organizations/{org_id}/technicians/{id}
DELETE /api/v1/organizations/{org_id}/technicians/{id}

GET    /api/v1/organizations/{org_id}/technicians/{id}/skills
POST   /api/v1/organizations/{org_id}/technicians/{id}/skills
PUT    /api/v1/organizations/{org_id}/technicians/{id}/skills/{skill_id}
DELETE /api/v1/organizations/{org_id}/technicians/{id}/skills/{skill_id}

GET    /api/v1/organizations/{org_id}/technicians/{id}/schedule
PUT    /api/v1/organizations/{org_id}/technicians/{id}/schedule
GET    /api/v1/organizations/{org_id}/technicians/availability
```

#### Appointment Management
```
GET    /api/v1/organizations/{org_id}/appointments
POST   /api/v1/organizations/{org_id}/appointments
PUT    /api/v1/organizations/{org_id}/appointments/{id}
DELETE /api/v1/organizations/{org_id}/appointments/{id}

GET    /api/v1/organizations/{org_id}/appointments/{id}/execution
POST   /api/v1/organizations/{org_id}/appointments/{id}/execution
PUT    /api/v1/organizations/{org_id}/appointments/{id}/execution/{exec_id}

POST   /api/v1/organizations/{org_id}/appointments/{id}/notes
GET    /api/v1/organizations/{org_id}/appointments/{id}/history
```

#### Customer Portal APIs
```
GET    /api/v1/customer-portal/services
POST   /api/v1/customer-portal/appointments
GET    /api/v1/customer-portal/appointments
PUT    /api/v1/customer-portal/appointments/{id}
GET    /api/v1/customer-portal/service-history
GET    /api/v1/customer-portal/technician-availability
```

#### Mobile Workforce APIs
```
GET    /api/v1/mobile/technician/{id}/assignments
PUT    /api/v1/mobile/technician/{id}/assignments/{appointment_id}/status
POST   /api/v1/mobile/technician/{id}/assignments/{appointment_id}/notes
POST   /api/v1/mobile/technician/{id}/assignments/{appointment_id}/photos
GET    /api/v1/mobile/technician/{id}/schedule
```

### Integration with Existing APIs

#### Financial Integration
```
POST   /api/v1/organizations/{org_id}/vouchers/service-invoice
  # Creates service invoice voucher from completed appointment
  
GET    /api/v1/organizations/{org_id}/vouchers/service-revenue
  # Service revenue reporting integration
```

#### Customer Integration  
```
GET    /api/v1/organizations/{org_id}/customers/{id}/service-history
GET    /api/v1/organizations/{org_id}/customers/{id}/upcoming-appointments
GET    /api/v1/organizations/{org_id}/customers/{id}/service-preferences
```

#### Ticket Management APIs
```
# Ticket CRUD operations
GET    /api/v1/organizations/{org_id}/tickets
POST   /api/v1/organizations/{org_id}/tickets
GET    /api/v1/organizations/{org_id}/tickets/{ticket_id}
PUT    /api/v1/organizations/{org_id}/tickets/{ticket_id}
DELETE /api/v1/organizations/{org_id}/tickets/{ticket_id}

# Ticket status and assignment
PUT    /api/v1/organizations/{org_id}/tickets/{ticket_id}/status
PUT    /api/v1/organizations/{org_id}/tickets/{ticket_id}/assign
PUT    /api/v1/organizations/{org_id}/tickets/{ticket_id}/priority

# Ticket history and comments
GET    /api/v1/organizations/{org_id}/tickets/{ticket_id}/history
POST   /api/v1/organizations/{org_id}/tickets/{ticket_id}/comments

# Ticket attachments
GET    /api/v1/organizations/{org_id}/tickets/{ticket_id}/attachments
POST   /api/v1/organizations/{org_id}/tickets/{ticket_id}/attachments
DELETE /api/v1/organizations/{org_id}/tickets/{ticket_id}/attachments/{attachment_id}

# Ticket analytics and reporting
GET    /api/v1/organizations/{org_id}/tickets/analytics
GET    /api/v1/organizations/{org_id}/tickets/metrics
```

## 🚀 Implementation Roadmap

### Phase 1: Foundation (PRs 1-3)
**Timeline: 2-3 weeks**

| PR # | Scope | Description | Estimated Effort |
|------|-------|-------------|------------------|
| 1 | Database Schema | Core service tables, technician models, appointment foundation | 5 days |
| 2 | Service Catalog APIs | Service categories, items, pricing management | 4 days |
| 3 | Technician Management | Technician profiles, skills, schedule management | 4 days |

### Phase 2: Core Functionality (PRs 4-7)
**Timeline: 3-4 weeks**

| PR # | Scope | Description | Estimated Effort |
|------|-------|-------------|------------------|
| 4 | Appointment System | Booking, scheduling, availability logic | 6 days |
| 5 | Service Execution | Work tracking, notes, completion workflow | 5 days |
| 6 | Customer Integration | Service history, preferences, extended customer data | 4 days |
| 7 | Ticket Management | **✅ IMPLEMENTED** - Ticket models, history, attachments for support CRM | 3 days |

### Phase 3: User Interfaces (PRs 8-10)
**Timeline: 3-4 weeks**

| PR # | Scope | Description | Estimated Effort |
|------|-------|-------------|------------------|
| 8 | Admin Dashboard | Service management, technician admin, reporting UI | 7 days |
| 9 | Customer Portal | Self-service booking, history, preferences UI | 6 days |
| 10 | Mobile Workforce | Technician mobile app interface | 6 days |

### Phase 4: Advanced Features (PRs 11-13)
**Timeline: 2-3 weeks**

| PR # | Scope | Description | Estimated Effort |
|------|-------|-------------|------------------|
| 11 | Financial Integration | Service invoicing, revenue tracking, payment integration | 5 days |
| 12 | Notifications & Automation | Email/SMS notifications, automated workflows | 4 days |
| 13 | Analytics & Reporting | Service metrics, technician performance, customer insights | 5 days |

### Phase 5: Compliance & Production (PRs 14-16)
**Timeline: 2 weeks**

| PR # | Scope | Description | Estimated Effort |
|------|-------|-------------|------------------|
| 14 | Security & Compliance | Data privacy, audit trails, access controls | 4 days |
| 15 | Performance Optimization | Caching, indexing, query optimization | 3 days |
| 16 | Documentation & Training | User guides, API documentation, training materials | 3 days |

## 🔐 Security & Compliance Considerations

### Data Privacy
- **Customer Data Protection**: Implement field-level encryption for sensitive customer information
- **Consent Management**: Track customer consent for data usage and marketing
- **Data Retention**: Automated data archival and deletion policies
- **Access Logging**: Comprehensive audit trails for customer data access

### Role-Based Access Control
- **Service Manager**: Full service catalog and technician management
- **Dispatcher**: Appointment scheduling and technician assignment
- **Technician**: Mobile access to assigned appointments and execution
- **Customer Service**: Customer interaction and basic service management
- **Finance**: Service billing and revenue reporting access

### API Security
- **Rate Limiting**: Prevent abuse of public customer portal APIs
- **Input Validation**: Strict validation for all service-related inputs
- **Authentication**: OAuth2/JWT integration with existing auth system
- **Encryption**: TLS 1.3 for all API communications

## 📈 Success Metrics & KPIs

### Operational Metrics
- **Appointment Booking Time**: Target < 3 minutes average
- **Technician Utilization**: Target 85% billable hour utilization
- **First-Time Fix Rate**: Target 90% of services completed on first visit
- **Customer Wait Time**: Target < 24 hours for urgent services

### Business Metrics
- **Revenue per Technician**: Track monthly revenue generation
- **Customer Retention**: Monitor repeat service usage
- **Service Margin**: Optimize pricing vs. delivery costs
- **Growth Metrics**: New customers, service expansion, market penetration

### Technical Metrics
- **API Response Time**: < 200ms for 95% of requests
- **System Uptime**: 99.9% availability target
- **Mobile App Performance**: < 3 second load times
- **Data Accuracy**: < 0.1% data discrepancy rate

## 🔄 Migration & Rollout Strategy

### Data Migration Approach
1. **Customer Data Enhancement**: Extend existing customer records with service preferences
2. **Service Catalog Setup**: Bulk import existing service offerings
3. **Technician Onboarding**: Import technician data from HR systems
4. **Historical Data**: Optional import of past service records

### Rollout Phases
1. **Pilot Organization**: Start with one test organization
2. **Limited Beta**: Roll out to 3-5 organizations
3. **Gradual Expansion**: Weekly rollouts to additional organizations
4. **Full Production**: All organizations enabled

### Training & Support
- **Admin Training**: 2-day workshop for service managers
- **Technician Training**: 4-hour mobile app training
- **Customer Communication**: Email campaigns and portal guides
- **Support Resources**: Video tutorials, documentation, help desk

## 🎯 Next Steps

### Immediate Actions
1. **Stakeholder Review**: Get approval on architecture and scope
2. **Team Assignment**: Assign developers to each implementation phase
3. **Environment Setup**: Prepare development and testing environments
4. **Database Design Review**: Detailed schema validation with DBA team

### Dependencies
- **Mobile Framework Decision**: Choose React Native vs. Progressive Web App
- **Notification Service**: Integrate with existing email service or add SMS capability
- **Payment Integration**: Determine payment gateway requirements
- **Compliance Review**: Legal and compliance team validation

This architecture provides a solid foundation for transforming the TRITIQ ERP platform into a comprehensive service management solution while maintaining the existing multi-tenant, secure, and scalable architecture.