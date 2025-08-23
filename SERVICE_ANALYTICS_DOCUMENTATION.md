# Service Analytics & Reporting - Implementation Documentation

## Overview

The Service Analytics & Reporting module provides comprehensive analytics and insights for the Service CRM system. It tracks key performance indicators (KPIs) across job completion, technician performance, customer satisfaction, job volume, and SLA compliance.

## Features Implemented

### Backend Components

#### 1. Database Models

**ServiceAnalyticsEvent**
- Stores individual analytics events for tracking
- Fields: event_type, event_category, metric_value, event_data (JSON)
- Supports job completions, performance metrics, satisfaction scores

**ReportConfiguration**
- Stores user-defined report configurations
- Fields: name, description, metric_types, filters, schedule settings
- Enables custom reports and scheduled generation

**AnalyticsSummary**
- Pre-calculated analytics summaries for performance
- Fields: summary_type, total_jobs, completion metrics, ratings
- Supports daily, weekly, monthly aggregations

#### 2. Analytics Service Layer

**ServiceAnalyticsService**
- Core business logic for calculating metrics
- Methods for each analytics type:
  - `get_job_completion_metrics()` - Job completion rates and trends
  - `get_technician_performance_metrics()` - Individual technician KPIs
  - `get_customer_satisfaction_metrics()` - Satisfaction ratings and NPS
  - `get_job_volume_metrics()` - Volume trends and customer analysis
  - `get_sla_compliance_metrics()` - SLA tracking and breach analysis

#### 3. REST API Endpoints

All endpoints are secured with RBAC (Role-Based Access Control):

**Public Analytics Endpoints:**
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/dashboard`
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/job-completion`
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/customer-satisfaction`
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/job-volume`

**Manager-Only Endpoints:**
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/technician-performance`
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/sla-compliance`

**Utility Endpoints:**
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/technicians`
- `GET /api/v1/service-analytics/organizations/{org_id}/analytics/customers`

### Frontend Components

#### 1. Main Dashboard

**ServiceAnalyticsDashboard**
- Complete analytics dashboard with all metrics
- Real-time data updates every 5 minutes
- Export functionality for CSV reports
- Responsive grid layout for all chart components

#### 2. Chart Components

**JobCompletionChart**
- Completion rates and status breakdown
- Progress bars for completion and on-time rates
- Recent completion trend display

**TechnicianPerformanceChart**
- Individual technician performance table
- Utilization rates and efficiency scores
- Customer ratings and completion times
- Expandable details for each technician

**CustomerSatisfactionChart**
- Overall satisfaction ratings (1-5 scale)
- Breakdown by service quality, timeliness, communication
- NPS (Net Promoter Score) calculation
- Satisfaction distribution analysis

**JobVolumeChart**
- Total job volume and daily averages
- Peak day identification and analysis
- Jobs by priority breakdown
- Top customers by job volume

**SLAComplianceChart**
- Overall SLA compliance percentage
- Compliance rates by job priority
- Common breach reasons analysis
- Performance indicators and trends

#### 3. Filtering System

**AnalyticsFilters**
- Period selection (Today, Week, Month, Quarter, Year, Custom)
- Custom date range picker
- Technician filter with autocomplete
- Customer filter with autocomplete
- Active filters summary display

### Role-Based Access Control

#### Analytics Permissions

**analytics_read**: Basic analytics access
- View dashboard, job completion, customer satisfaction, job volume

**analytics_manage**: Manager-level access (includes analytics_read)
- View technician performance metrics
- View SLA compliance data
- Create and manage report configurations

**analytics_export**: Export permissions
- Export analytics data in various formats
- Download report files

#### Permission Fallbacks

The system includes fallback permissions for backward compatibility:
- `analytics_read` → `VIEW_USERS`, `VIEW_AUDIT_LOGS`
- `analytics_manage` → `MANAGE_USERS`, `MANAGE_ORGANIZATIONS`
- `analytics_export` → `VIEW_AUDIT_LOGS`, `MANAGE_USERS`

## API Usage Examples

### Get Complete Dashboard

```javascript
const dashboard = await serviceAnalyticsService.getAnalyticsDashboard(organizationId, {
  period: ReportPeriod.MONTH,
  technician_id: 123,  // Optional filter
  customer_id: 456     // Optional filter
});
```

### Get Job Completion Metrics

```javascript
const metrics = await serviceAnalyticsService.getJobCompletionMetrics(organizationId, {
  period: ReportPeriod.WEEK
});

// Returns: total_jobs, completed_jobs, completion_rate, trends, etc.
```

### Get Technician Performance (Managers Only)

```javascript
const performance = await serviceAnalyticsService.getTechnicianPerformanceMetrics(organizationId, {
  start_date: '2024-01-01',
  end_date: '2024-01-31'
});

// Returns: array of technician performance metrics
```

### Export Analytics Data

```javascript
const blob = await serviceAnalyticsService.exportAnalyticsData(organizationId, {
  format: 'csv',
  metric_types: ['job_completion', 'customer_satisfaction'],
  filters: { period: ReportPeriod.MONTH }
});

// Creates downloadable CSV file
```

## Database Schema

### ServiceAnalyticsEvent Table

```sql
CREATE TABLE service_analytics_events (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    event_type VARCHAR NOT NULL,
    event_category VARCHAR NOT NULL,
    installation_job_id INTEGER REFERENCES installation_jobs(id),
    technician_id INTEGER REFERENCES users(id),
    customer_id INTEGER REFERENCES customers(id),
    event_data JSON,
    metric_value FLOAT,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### ReportConfiguration Table

```sql
CREATE TABLE report_configurations (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    name VARCHAR NOT NULL,
    description TEXT,
    metric_types JSON NOT NULL,
    default_filters JSON,
    schedule_enabled BOOLEAN DEFAULT FALSE,
    email_recipients JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Frontend Integration

### Adding to Pages

```typescript
import { ServiceAnalyticsDashboard } from '../components/ServiceAnalytics';

// In your page component
<ServiceAnalyticsDashboard organizationId={currentUser.organization_id} />
```

### Custom Hook Usage

```typescript
import { useQuery } from '@tanstack/react-query';
import { serviceAnalyticsService } from '../services/serviceAnalyticsService';

const { data, isLoading, error } = useQuery({
  queryKey: ['analytics-dashboard', organizationId],
  queryFn: () => serviceAnalyticsService.getAnalyticsDashboard(organizationId),
  refetchInterval: 5 * 60 * 1000 // Refresh every 5 minutes
});
```

## Performance Considerations

### Backend Optimizations

1. **Database Indexes**: All queries use optimized indexes on organization_id, dates, and foreign keys
2. **Aggregation Efficiency**: Database-level grouping and counting operations
3. **Caching Ready**: Stateless service design supports future Redis caching
4. **Date Range Limiting**: Configurable limits prevent large data queries

### Frontend Optimizations

1. **React Query Caching**: Intelligent caching with 2-minute stale time
2. **Selective Re-renders**: Components only update when their data changes
3. **Lazy Loading**: Charts load only when visible
4. **Debounced Filters**: Filter changes are debounced to prevent excessive API calls

## Testing

### Backend Tests

```bash
# Run analytics service tests
python -m pytest tests/test_service_analytics.py -v

# Run specific test categories
python -m pytest tests/test_service_analytics.py::TestServiceAnalyticsService -v
python -m pytest tests/test_service_analytics.py::TestServiceAnalyticsAPI -v
```

### Test Coverage

- **Service Layer**: 25+ test cases covering all analytics calculations
- **API Endpoints**: Authentication, authorization, and data validation tests
- **Models**: Database model creation and relationship tests
- **Schemas**: Pydantic schema validation tests

## Future Enhancements

### Planned Features

1. **Advanced Export Formats**
   - PDF reports with charts and company branding
   - Excel exports with multiple sheets
   - Automated email delivery

2. **Real-time Updates**
   - WebSocket integration for live dashboard updates
   - Push notifications for SLA breaches
   - Real-time performance alerts

3. **Predictive Analytics**
   - ML-based workload prediction
   - Customer satisfaction trend forecasting
   - Resource allocation optimization

4. **Custom Dashboards**
   - User-configurable widget layout
   - Personalized KPI tracking
   - Role-specific dashboard views

### API Extensions

1. **Scheduled Reports**
   - Automated report generation
   - Email delivery to stakeholders
   - Report history and versioning

2. **Advanced Filtering**
   - Saved filter presets
   - Complex query builders
   - Cross-metric correlations

3. **Integration Hooks**
   - Webhook notifications for metrics thresholds
   - Third-party analytics platform integration
   - API endpoints for external reporting tools

## Migration Guide

### Database Migration

```bash
# Apply the analytics models migration
alembic upgrade head
```

### Adding Permissions

The migration automatically creates the necessary RBAC permissions:
- `analytics_read`
- `analytics_manage` 
- `analytics_export`

Assign these to appropriate service roles for your organization.

### Frontend Integration

Add the analytics route to your application's routing:

```typescript
// In your routing configuration
{
  path: '/analytics',
  component: ServiceAnalyticsDashboard,
  // Add authentication guard
  meta: { requiresAuth: true, permissions: ['analytics_read'] }
}
```

## Troubleshooting

### Common Issues

1. **No Data Showing**
   - Verify jobs exist with completion records
   - Check date range filters
   - Ensure user has proper permissions

2. **Performance Issues**
   - Check database indexes are applied
   - Verify query date ranges aren't too large
   - Monitor API response times

3. **Permission Errors**
   - Verify user has analytics_read permission
   - Check organization membership
   - Ensure RBAC service is properly configured

### Debug Commands

```bash
# Check analytics data
python manage.py shell
from app.services.service_analytics_service import ServiceAnalyticsService
service = ServiceAnalyticsService(db, organization_id=1)
dashboard = service.get_analytics_dashboard()
```

## Conclusion

The Service Analytics & Reporting module provides a comprehensive solution for tracking and analyzing Service CRM performance. With role-based access control, real-time updates, and export capabilities, it enables organizations to make data-driven decisions about their service operations.

The modular design allows for easy extension and customization, while the robust testing ensures reliability in production environments.