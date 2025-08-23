# Customer Feedback & Service Closure Workflow - Integration Guide

## Overview

The Customer Feedback & Service Closure Workflow is a complete vertical slice of the Service CRM that enables:

- **Customer Feedback Collection**: Comprehensive rating system with comments and suggestions
- **Service Closure Management**: Manager-approved workflow for closing service tickets
- **Analytics & Reporting**: Satisfaction metrics and performance tracking
- **Role-based Access**: Different interfaces for customers vs managers

## Backend API Integration

### Endpoints Available

#### Customer Feedback
```
POST   /api/v1/feedback/feedback                    # Submit customer feedback
GET    /api/v1/feedback/feedback                    # List feedback (filtered)
GET    /api/v1/feedback/feedback/{id}               # Get specific feedback
PUT    /api/v1/feedback/feedback/{id}               # Update feedback
POST   /api/v1/feedback/feedback/{id}/review        # Manager review feedback
```

#### Service Closure  
```
POST   /api/v1/feedback/service-closure             # Create closure request
GET    /api/v1/feedback/service-closure             # List closures (filtered)
GET    /api/v1/feedback/service-closure/{id}        # Get specific closure
POST   /api/v1/feedback/service-closure/{id}/approve # Manager approve closure
POST   /api/v1/feedback/service-closure/{id}/close  # Manager close service
POST   /api/v1/feedback/service-closure/{id}/reopen # Reopen closed service
```

#### Analytics
```
GET    /api/v1/feedback/feedback/analytics/summary          # Feedback metrics
GET    /api/v1/feedback/service-closure/analytics/summary   # Closure metrics
```

### Example API Usage

#### Submit Customer Feedback
```python
feedback_data = {
    "installation_job_id": 123,
    "customer_id": 456,
    "overall_rating": 5,
    "service_quality_rating": 4,
    "technician_rating": 5,
    "feedback_comments": "Excellent service!",
    "would_recommend": true,
    "satisfaction_level": "very_satisfied"
}

response = requests.post(
    "/api/v1/feedback/feedback",
    json=feedback_data,
    headers={"Authorization": "Bearer <token>"}
)
```

#### Create Service Closure
```python
closure_data = {
    "installation_job_id": 123,
    "customer_feedback_id": 789,
    "closure_reason": "completed",
    "closure_notes": "Service completed successfully",
    "requires_manager_approval": true
}

response = requests.post(
    "/api/v1/feedback/service-closure",
    json=closure_data,
    headers={"Authorization": "Bearer <token>"}
)
```

## Frontend Integration

### React Components

Import the feedback workflow components:

```typescript
import {
  CustomerFeedbackModal,
  ServiceClosureDialog,
  FeedbackStatusList,
  FeedbackWorkflowIntegration
} from '@/components/FeedbackWorkflow';

import feedbackService from '@/services/feedbackService';
```

### Customer Feedback Modal

```tsx
const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);

const handleSubmitFeedback = async (feedbackData) => {
  try {
    await feedbackService.submitFeedback(feedbackData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};

return (
  <CustomerFeedbackModal
    open={feedbackModalOpen}
    onClose={() => setFeedbackModalOpen(false)}
    installationJobId={jobId}
    customerId={customerId}
    onSubmit={handleSubmitFeedback}
  />
);
```

### Service Closure Dialog

```tsx
const [closureDialogOpen, setClosureDialogOpen] = useState(false);

const handleCreateClosure = async (closureData) => {
  try {
    await feedbackService.createServiceClosure(closureData);
    // Handle success
  } catch (error) {
    // Handle error
  }
};

return (
  <ServiceClosureDialog
    open={closureDialogOpen}
    onClose={() => setClosureDialogOpen(false)}
    installationJobId={jobId}
    customerFeedbackId={feedbackId}
    userRole={userRole}
    onSubmit={handleCreateClosure}
  />
);
```

### Role-based UI

```tsx
import { useAuth } from '@/context/AuthContext';

function ServiceManagementPage() {
  const { user } = useAuth();
  
  return (
    <div>
      {/* Customer Interface */}
      {user.role === 'customer' && (
        <Button onClick={() => setFeedbackModalOpen(true)}>
          Submit Feedback
        </Button>
      )}
      
      {/* Manager Interface */}
      {user.role === 'manager' && (
        <>
          <Button onClick={() => setClosureDialogOpen(true)}>
            Close Service
          </Button>
          <FeedbackStatusList />
        </>
      )}
    </div>
  );
}
```

## Workflow Integration

### Job Completion → Feedback Request

```typescript
// After marking a job as complete
const triggerFeedbackRequest = async (jobId: number) => {
  try {
    await feedbackService.triggerFeedbackRequest(jobId);
    console.log('Feedback request sent to customer');
  } catch (error) {
    console.error('Failed to trigger feedback request:', error);
  }
};
```

### Feedback → Service Closure

```typescript
// Check if service can be closed
const canClose = await feedbackService.canClosureBeCreated(jobId);

if (canClose) {
  // Show service closure dialog
  setClosureDialogOpen(true);
}
```

## RBAC Permissions

### Required Permissions

| Action | Permission | Role |
|--------|------------|------|
| Submit Feedback | `customer_feedback_submit` | Customer |
| View Feedback | `customer_feedback_read` | All |
| Review Feedback | `customer_feedback_update` | Support/Manager |
| Create Closure | `service_closure_create` | Support/Manager |
| Approve Closure | `service_closure_approve` | Manager |
| Close Service | `service_closure_close` | Manager |

### Permission Mapping

The system maps service permissions to existing system permissions for fallback:

```python
# Feedback permissions
"customer_feedback_submit": [Permission.VIEW_USERS]     # Customers can submit
"customer_feedback_read": [Permission.VIEW_USERS]
"customer_feedback_update": [Permission.MANAGE_USERS]

# Service closure permissions  
"service_closure_create": [Permission.MANAGE_USERS]
"service_closure_approve": [Permission.MANAGE_ORGANIZATIONS]  # Manager only
"service_closure_close": [Permission.MANAGE_ORGANIZATIONS]    # Manager only
```

## Database Schema

### CustomerFeedback Table

```sql
CREATE TABLE customer_feedback (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    installation_job_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    completion_record_id INTEGER,
    overall_rating INTEGER NOT NULL,
    service_quality_rating INTEGER,
    technician_rating INTEGER,
    timeliness_rating INTEGER,
    communication_rating INTEGER,
    feedback_comments TEXT,
    improvement_suggestions TEXT,
    survey_responses TEXT,  -- JSON
    would_recommend BOOLEAN,
    satisfaction_level VARCHAR,
    follow_up_preferred BOOLEAN DEFAULT FALSE,
    preferred_contact_method VARCHAR,
    feedback_status VARCHAR DEFAULT 'submitted',
    reviewed_by_id INTEGER,
    reviewed_at DATETIME,
    response_notes TEXT,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

### ServiceClosure Table

```sql
CREATE TABLE service_closures (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    installation_job_id INTEGER NOT NULL UNIQUE,
    completion_record_id INTEGER,
    customer_feedback_id INTEGER,
    closure_status VARCHAR DEFAULT 'pending',
    closure_reason VARCHAR,
    closure_notes TEXT,
    requires_manager_approval BOOLEAN DEFAULT TRUE,
    approved_by_id INTEGER,
    approved_at DATETIME,
    approval_notes TEXT,
    closed_by_id INTEGER,
    closed_at DATETIME,
    final_closure_notes TEXT,
    feedback_received BOOLEAN DEFAULT FALSE,
    minimum_rating_met BOOLEAN DEFAULT FALSE,
    escalation_required BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    reopened_count INTEGER DEFAULT 0,
    last_reopened_at DATETIME,
    last_reopened_by_id INTEGER,
    reopening_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

## Analytics

### Feedback Analytics

```typescript
const analytics = await feedbackService.getFeedbackAnalytics(30); // Last 30 days

// Returns:
{
  period_days: 30,
  total_feedback: 150,
  average_rating: 4.2,
  positive_feedback: 120,    // 4+ stars
  negative_feedback: 15,     // 1-2 stars
  satisfaction_rate: 80.0    // Percentage positive
}
```

### Closure Analytics

```typescript
const analytics = await feedbackService.getClosureAnalytics(30);

// Returns:
{
  period_days: 30,
  total_closures: 100,
  completed_closures: 95,
  escalated_closures: 5,
  average_reopens: 0.2,
  completion_rate: 95.0
}
```

## Testing

### Backend Tests

Run the feedback workflow tests:

```bash
cd /home/runner/work/FastApiv1.4/FastApiv1.4
python tests/test_feedback_workflow.py
```

### Comprehensive Verification

```bash
python test_complete_implementation.py
```

## Production Deployment

### Environment Variables

Add to your `.env` file:

```env
# Feedback workflow is already integrated, no additional config needed
# Uses existing DATABASE_URL and RBAC configuration
```

### Migration

```bash
alembic upgrade head  # Applies feedback migration: 8b772bffd5ee
```

### RBAC Setup

Ensure service permissions are seeded:

```python
# Run after migration
python -c "
from app.core.database import SessionLocal
from app.services.rbac import RBACService

db = SessionLocal()
rbac = RBACService(db)
rbac.seed_default_service_permissions()
db.close()
"
```

## Complete Implementation Status

✅ **Backend**: Models, migrations, services, API endpoints, RBAC integration
✅ **Frontend**: React components, TypeScript service, Material-UI interface  
✅ **Database**: Applied migrations with proper relationships and indexes
✅ **Testing**: Unit tests and integration verification
✅ **Documentation**: Complete API documentation and integration guide
✅ **Analytics**: Feedback and closure metrics with reporting endpoints

The Customer Feedback & Service Closure Workflow is **production-ready** and fully integrated with the existing Service CRM architecture.