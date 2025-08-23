# Material Dispatch Management System Documentation

## Overview

The Material Dispatch Management System is a comprehensive module within the Service CRM that handles the dispatch of materials/products to customers and manages installation scheduling workflows. This system seamlessly integrates with the existing ERP voucher system (Delivery Challan, Service Voucher) to provide end-to-end material dispatch and installation management.

## Architecture

### Database Models

#### DispatchOrder
- **Purpose**: Tracks material dispatch orders to customers
- **Key Fields**:
  - `order_number`: Auto-generated unique identifier (DO/YY/XXXXX)
  - `customer_id`: Link to customer
  - `ticket_id`: Optional link to support ticket
  - `status`: pending, in_transit, delivered, cancelled
  - `delivery_address`: Where materials are being shipped
  - `dispatch_date`, `expected_delivery_date`, `actual_delivery_date`
  - `tracking_number`, `courier_name`: Shipping details

#### DispatchItem
- **Purpose**: Individual items within a dispatch order
- **Key Fields**:
  - `product_id`: Link to product catalog
  - `quantity`, `unit`: Quantity being dispatched
  - `serial_numbers`, `batch_numbers`: Tracking information
  - `status`: pending, packed, dispatched, delivered

#### InstallationJob
- **Purpose**: Installation jobs created from dispatch orders
- **Key Fields**:
  - `job_number`: Auto-generated unique identifier (IJ/YY/XXXXX)
  - `dispatch_order_id`: Link to originating dispatch order
  - `status`: scheduled, in_progress, completed, cancelled, rescheduled
  - `priority`: low, medium, high, urgent
  - `scheduled_date`, `estimated_duration_hours`
  - `assigned_technician_id`: Assigned installation technician
  - `installation_address`: Where installation will occur
  - `customer_rating`, `customer_feedback`: Post-installation feedback

### Business Logic

#### Dispatch Order Workflow
1. **Creation**: Dispatch orders can be created manually or triggered from delivery challan
2. **Status Progression**: pending → in_transit → delivered
3. **Auto-dating**: 
   - `dispatch_date` set when status changes to "in_transit"
   - `actual_delivery_date` set when status changes to "delivered"
4. **Validation**: Only pending orders can be deleted

#### Installation Job Workflow
1. **Creation**: Can be created from dispatch orders or triggered by installation prompt
2. **Technician Assignment**: Validates technician belongs to same organization
3. **Status Progression**: scheduled → in_progress → completed
4. **Auto-timing**:
   - `actual_start_time` set when status changes to "in_progress"
   - `actual_end_time` set when status changes to "completed"

#### Installation Schedule Prompt
- **Trigger**: After delivery challan or service voucher creation
- **Purpose**: Prompts user to create installation schedule for delivered items
- **Workflow**:
  1. User creates delivery challan/service voucher
  2. System shows installation prompt modal
  3. User chooses to create or skip installation schedule
  4. If confirmed, installation job is created and linked to dispatch order

## API Endpoints

### Dispatch Orders

#### GET /api/v1/dispatch/orders
- **Purpose**: List dispatch orders with filtering and pagination
- **Parameters**:
  - `skip`, `limit`: Pagination
  - `status`: Filter by dispatch status
  - `customer_id`: Filter by customer
  - `ticket_id`: Filter by ticket
  - `from_date`, `to_date`: Date range filter
- **Returns**: Array of DispatchOrderInDB

#### POST /api/v1/dispatch/orders
- **Purpose**: Create new dispatch order
- **Body**: DispatchOrderCreate (includes items array)
- **Returns**: DispatchOrderInDB
- **Validation**: Requires at least one item

#### GET /api/v1/dispatch/orders/{order_id}
- **Purpose**: Get specific dispatch order
- **Returns**: DispatchOrderInDB with items

#### PUT /api/v1/dispatch/orders/{order_id}
- **Purpose**: Update dispatch order
- **Body**: DispatchOrderUpdate
- **Returns**: DispatchOrderInDB
- **Special Logic**: Handles status-based auto-dating

#### DELETE /api/v1/dispatch/orders/{order_id}
- **Purpose**: Delete dispatch order
- **Restriction**: Only allowed for pending orders
- **Returns**: 204 No Content

### Installation Jobs

#### GET /api/v1/dispatch/installation-jobs
- **Purpose**: List installation jobs with filtering and pagination
- **Parameters**:
  - `skip`, `limit`: Pagination
  - `status`: Filter by job status
  - `priority`: Filter by priority
  - `customer_id`: Filter by customer
  - `assigned_technician_id`: Filter by technician
  - `dispatch_order_id`: Filter by dispatch order
  - `from_date`, `to_date`: Date range filter
- **Returns**: Array of InstallationJobInDB

#### POST /api/v1/dispatch/installation-jobs
- **Purpose**: Create new installation job
- **Body**: InstallationJobCreate
- **Returns**: InstallationJobInDB
- **Validation**: Validates dispatch order exists and belongs to organization

#### GET /api/v1/dispatch/installation-jobs/{job_id}
- **Purpose**: Get specific installation job
- **Returns**: InstallationJobInDB

#### PUT /api/v1/dispatch/installation-jobs/{job_id}
- **Purpose**: Update installation job
- **Body**: InstallationJobUpdate
- **Returns**: InstallationJobInDB
- **Special Logic**: 
  - Handles technician assignment validation
  - Status-based auto-timing

#### DELETE /api/v1/dispatch/installation-jobs/{job_id}
- **Purpose**: Delete installation job
- **Restriction**: Only allowed for scheduled or cancelled jobs
- **Returns**: 204 No Content

### Installation Schedule Prompt

#### POST /api/v1/dispatch/installation-schedule-prompt
- **Purpose**: Handle installation schedule prompt from delivery challan workflow
- **Body**: InstallationSchedulePromptResponse
- **Returns**: InstallationJobInDB (if schedule created)
- **Logic**: Creates installation job if user confirms, otherwise skips

## Frontend Components

### DispatchManagement
- **Purpose**: Main management interface for dispatch orders and installation jobs
- **Features**:
  - Tabbed interface (Dispatch Orders, Installation Jobs)
  - Filtering and search capabilities
  - CRUD operations with role-based permissions
  - Pagination
- **Permissions**:
  - View: org_admin, admin, manager, support, standard_user
  - Manage: org_admin, admin, manager

### DispatchOrderDialog
- **Purpose**: Create/edit dispatch order dialog
- **Features**:
  - Form for order details
  - Dynamic items table with add/remove
  - Status management
  - Validation

### InstallationSchedulePromptModal
- **Purpose**: Prompt for installation schedule creation
- **Trigger**: After delivery challan/service voucher creation
- **Implementation**: Should be imported and used in delivery challan success callback
  ```typescript
  // Example usage in delivery challan component
  import { InstallationSchedulePromptModal } from '../DispatchManagement';
  
  const handleDeliveryChallanSuccess = (challan) => {
    // Show installation prompt after successful creation
    setInstallationPromptData({
      dispatchOrderId: challan.id,
      customerId: challan.customer_id,
      customerName: challan.customer?.name,
      deliveryAddress: challan.shipping_address
    });
    setInstallationPromptOpen(true);
  };
  ```
- **Features**:
  - Yes/No radio selection
  - Installation details form (when yes selected)
  - Priority, scheduling, technician assignment
  - Address and contact information

## Role-Based Access Control

### Dispatch Orders
- **View Access**: All roles (org_admin, admin, manager, support, standard_user)
- **Management Access**: org_admin, admin, manager
- **Delete Access**: Only for pending orders by management roles

### Installation Jobs
- **View Access**: org_admin, admin, manager, support, technician, standard_user
- **Management Access**: org_admin, admin, manager
- **Delete Access**: Only for scheduled/cancelled jobs by management roles

## Integration Points

### Delivery Challan Integration
The installation schedule prompt is triggered after successful delivery challan creation. The integration works as follows:

1. **Frontend Integration**: After successful delivery challan creation, the frontend should:
   ```typescript
   // After delivery challan is successfully created
   const deliveryChallan = await deliveryChallanService.create(challanData);
   
   // Show installation schedule prompt
   setInstallationPromptData({
     dispatchOrderId: deliveryChallan.id, // Use challan ID as reference
     customerId: deliveryChallan.customer_id,
     customerName: deliveryChallan.customer.name,
     deliveryAddress: deliveryChallan.shipping_address || deliveryChallan.customer.address
   });
   setInstallationPromptOpen(true);
   ```

2. **API Integration**: The installation prompt can create dispatch orders that reference the delivery challan:
   ```python
   # When installation job is created from prompt
   installation_job = InstallationJob(
       dispatch_order_id=dispatch_order.id,
       customer_id=delivery_challan.customer_id,
       # ... other fields
   )
   ```

3. **Traceability**: Links are maintained between:
   - Delivery Challan → Dispatch Order (via reference or notes)
   - Dispatch Order → Installation Job
   - Installation Job → Customer feedback and completion

### Service Voucher Integration
- Service vouchers can trigger installation scheduling
- Supports service-based installations (not just product delivery)
- Links to support tickets when applicable

### Customer Management
- All dispatch orders linked to customer records
- Customer address pre-populated in forms
- Customer service history includes dispatch records

### Product Catalog
- Dispatch items linked to product catalog
- Quantity and unit validation against product definitions
- Serial number and batch tracking support

## Testing

### Unit Tests (8/8 passing)
- Model creation and validation
- Service layer business logic
- Number generation (dispatch orders, installation jobs)
- Status transition logic
- Permission validation

### Integration Tests
- API endpoint testing
- Database constraint validation
- Multi-tenant isolation
- RBAC enforcement

## Number Generation

### Dispatch Order Numbers
- **Format**: DO/YY/XXXXX (e.g., DO/24/00001)
- **Logic**: Fiscal year based, auto-increment per organization
- **Uniqueness**: Per organization constraint

### Installation Job Numbers
- **Format**: IJ/YY/XXXXX (e.g., IJ/24/00001)  
- **Logic**: Fiscal year based, auto-increment per organization
- **Uniqueness**: Per organization constraint

## Status Configurations

### Dispatch Order Statuses
- **pending**: Order created, not yet dispatched
- **in_transit**: Order dispatched, in delivery
- **delivered**: Order successfully delivered
- **cancelled**: Order cancelled

### Installation Job Statuses
- **scheduled**: Job scheduled but not started
- **in_progress**: Installation in progress
- **completed**: Installation completed successfully
- **cancelled**: Job cancelled
- **rescheduled**: Job rescheduled to new date

### Installation Job Priorities
- **low**: Non-urgent installation
- **medium**: Standard priority (default)
- **high**: High priority installation
- **urgent**: Emergency installation required

## Future Enhancements

### Planned Features
1. **Mobile App Integration**: Technician mobile interface for job management
2. **GPS Tracking**: Real-time location tracking for dispatch and installation
3. **Photo Documentation**: Installation progress photos and completion documentation
4. **Customer Notifications**: Automated SMS/email updates for dispatch and installation
5. **Inventory Integration**: Automatic stock deduction on dispatch
6. **Route Optimization**: Optimal routing for multiple installations
7. **Signature Capture**: Digital signature for delivery and installation completion

### Technical Improvements
1. **Bulk Operations**: Bulk dispatch order creation and updates
2. **Advanced Filtering**: Date range, technician availability, geographic filters
3. **Reporting Dashboard**: Analytics and KPI tracking
4. **Integration Webhooks**: External system integration capabilities
5. **Offline Support**: Mobile app offline functionality

## Conclusion

The Material Dispatch Management System provides a comprehensive solution for managing the dispatch of materials and scheduling of installations. It seamlessly integrates with the existing ERP system while providing dedicated workflows for service-oriented businesses. The system maintains the existing multi-tenant architecture and RBAC patterns while adding specialized functionality for dispatch and installation management.