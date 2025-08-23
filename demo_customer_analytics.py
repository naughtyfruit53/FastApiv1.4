#!/usr/bin/env python3
"""
Customer Analytics Demo Script

This script demonstrates the Customer Analytics module functionality
by creating sample data and showing the API responses.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any


def create_sample_analytics_data() -> Dict[str, Any]:
    """Create sample analytics data that would be returned by the API"""
    
    # Sample customer analytics data
    customer_analytics = {
        "customer_id": 1,
        "customer_name": "Acme Corporation",
        "total_interactions": 23,
        "last_interaction_date": "2024-01-15T14:30:00Z",
        "interaction_types": {
            "call": 8,
            "email": 12,
            "meeting": 2,
            "support_ticket": 1
        },
        "interaction_status": {
            "completed": 18,
            "pending": 3,
            "in_progress": 2
        },
        "segments": [
            {
                "segment_name": "premium",
                "segment_value": 150.0,
                "assigned_date": "2024-01-01T00:00:00Z",
                "description": "Premium customer with high engagement"
            },
            {
                "segment_name": "high_value",
                "segment_value": 500.0,
                "assigned_date": "2024-01-10T00:00:00Z",
                "description": "High-value customer based on revenue"
            }
        ],
        "recent_interactions": [
            {
                "interaction_type": "email",
                "subject": "Product inquiry follow-up",
                "status": "completed",
                "interaction_date": "2024-01-15T14:30:00Z"
            },
            {
                "interaction_type": "call",
                "subject": "Technical support request",
                "status": "in_progress",
                "interaction_date": "2024-01-15T10:15:00Z"
            },
            {
                "interaction_type": "meeting",
                "subject": "Quarterly business review",
                "status": "completed",
                "interaction_date": "2024-01-14T16:00:00Z"
            }
        ],
        "calculated_at": "2024-01-16T12:00:00Z"
    }
    
    # Sample segment analytics data
    segment_analytics = {
        "segment_name": "premium",
        "total_customers": 25,
        "total_interactions": 312,
        "avg_interactions_per_customer": 12.48,
        "interaction_distribution": {
            "call": 125,
            "email": 150,
            "meeting": 25,
            "support_ticket": 8,
            "feedback": 4
        },
        "activity_timeline": [
            {"date": "2024-01-10", "interaction_count": 8},
            {"date": "2024-01-11", "interaction_count": 12},
            {"date": "2024-01-12", "interaction_count": 10},
            {"date": "2024-01-13", "interaction_count": 6},
            {"date": "2024-01-14", "interaction_count": 15},
            {"date": "2024-01-15", "interaction_count": 9}
        ],
        "calculated_at": "2024-01-16T12:00:00Z"
    }
    
    # Sample organization summary
    organization_summary = {
        "organization_id": 1,
        "total_customers": 150,
        "total_interactions": 1250,
        "segment_distribution": {
            "premium": 25,
            "regular": 85,
            "vip": 15,
            "new": 20,
            "at_risk": 5
        },
        "interaction_trends": [
            {"date": "2024-01-10", "interaction_count": 45},
            {"date": "2024-01-11", "interaction_count": 52},
            {"date": "2024-01-12", "interaction_count": 38},
            {"date": "2024-01-13", "interaction_count": 41},
            {"date": "2024-01-14", "interaction_count": 55},
            {"date": "2024-01-15", "interaction_count": 48}
        ],
        "calculated_at": "2024-01-16T12:00:00Z"
    }
    
    # Sample dashboard metrics
    dashboard_metrics = {
        "total_customers": 150,
        "total_interactions_today": 12,
        "total_interactions_week": 89,
        "total_interactions_month": 356,
        "top_segments": [
            {"segment_name": "regular", "customer_count": 85},
            {"segment_name": "premium", "customer_count": 25},
            {"segment_name": "new", "customer_count": 20},
            {"segment_name": "vip", "customer_count": 15},
            {"segment_name": "at_risk", "customer_count": 5}
        ],
        "recent_activity": [
            {"date": "2024-01-11", "interaction_count": 52},
            {"date": "2024-01-12", "interaction_count": 38},
            {"date": "2024-01-13", "interaction_count": 41},
            {"date": "2024-01-14", "interaction_count": 55},
            {"date": "2024-01-15", "interaction_count": 48}
        ],
        "calculated_at": "2024-01-16T12:00:00Z"
    }
    
    return {
        "customer_analytics": customer_analytics,
        "segment_analytics": segment_analytics,
        "organization_summary": organization_summary,
        "dashboard_metrics": dashboard_metrics
    }


def format_json_output(data: Dict[str, Any], title: str) -> str:
    """Format JSON data for pretty printing"""
    separator = "=" * 60
    return f"\n{separator}\n{title}\n{separator}\n{json.dumps(data, indent=2)}\n"


def demonstrate_api_endpoints():
    """Demonstrate the API endpoints with sample data"""
    
    print("🚀 Customer Analytics API Demonstration")
    print("=" * 60)
    print("\nThis demo shows the structure and data returned by the")
    print("Customer Analytics API endpoints.\n")
    
    # Get sample data
    sample_data = create_sample_analytics_data()
    
    # Demonstrate each endpoint
    print("\n📊 API ENDPOINT DEMONSTRATIONS")
    
    # 1. Customer Analytics
    print(format_json_output(
        sample_data["customer_analytics"],
        "🔍 GET /api/v1/analytics/customers/{customer_id}/analytics"
    ))
    
    print("Key insights from customer analytics:")
    print("• Customer has 23 total interactions with strong email engagement")
    print("• Currently in 'premium' and 'high_value' segments")
    print("• Most recent activity shows ongoing technical support")
    print("• High completion rate (78% of interactions completed)")
    
    # 2. Segment Analytics
    print(format_json_output(
        sample_data["segment_analytics"],
        "📈 GET /api/v1/analytics/segments/{segment_name}/analytics"
    ))
    
    print("Key insights from segment analytics:")
    print("• Premium segment has 25 customers averaging 12.5 interactions each")
    print("• Email is the most common interaction type (48%)")
    print("• Consistent daily activity with weekend dips")
    print("• Strong engagement levels across the segment")
    
    # 3. Organization Summary
    print(format_json_output(
        sample_data["organization_summary"],
        "🏢 GET /api/v1/analytics/organization/summary"
    ))
    
    print("Key insights from organization summary:")
    print("• 150 total customers with 1,250 interactions")
    print("• Majority are regular customers (57%), with good premium mix (17%)")
    print("• Only 3% at-risk customers - healthy customer base")
    print("• Steady interaction trends with growth opportunity")
    
    # 4. Dashboard Metrics
    print(format_json_output(
        sample_data["dashboard_metrics"],
        "📋 GET /api/v1/analytics/dashboard/metrics"
    ))
    
    print("Key insights from dashboard metrics:")
    print("• 12 interactions today - good daily activity")
    print("• 89 interactions this week - consistent engagement")
    print("• Regular customers dominate but premium segment is significant")
    print("• Recent activity shows strong engagement levels")


def demonstrate_use_cases():
    """Demonstrate practical use cases for the analytics"""
    
    print("\n" + "=" * 60)
    print("💡 PRACTICAL USE CASES")
    print("=" * 60)
    
    use_cases = [
        {
            "title": "Customer Health Monitoring",
            "description": "Track interaction frequency and types to identify customers who may need attention",
            "api_call": "GET /api/v1/analytics/customers/{id}/analytics",
            "insight": "Customers with no recent interactions or declining engagement patterns"
        },
        {
            "title": "Segment Performance Analysis",
            "description": "Compare interaction patterns across customer segments to optimize engagement strategies",
            "api_call": "GET /api/v1/analytics/segments/{segment}/analytics",
            "insight": "Premium customers average 12.5 interactions vs 4.2 for regular customers"
        },
        {
            "title": "Daily Operations Dashboard",
            "description": "Monitor real-time customer service metrics and team performance",
            "api_call": "GET /api/v1/analytics/dashboard/metrics",
            "insight": "Today's 12 interactions vs weekly average of 12.7 - normal activity"
        },
        {
            "title": "Executive Reporting",
            "description": "Provide high-level customer engagement summaries for leadership",
            "api_call": "GET /api/v1/analytics/organization/summary",
            "insight": "8.3 average interactions per customer with 78% completion rate"
        },
        {
            "title": "Proactive Customer Success",
            "description": "Identify at-risk customers and high-value engagement opportunities",
            "api_call": "Multiple endpoints for comprehensive view",
            "insight": "5 at-risk customers need immediate attention, 15 VIP customers for upselling"
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"\n{i}. {use_case['title']}")
        print(f"   Description: {use_case['description']}")
        print(f"   API Call: {use_case['api_call']}")
        print(f"   Insight: {use_case['insight']}")


def demonstrate_integration():
    """Show integration examples"""
    
    print("\n" + "=" * 60)
    print("🔧 INTEGRATION EXAMPLES")
    print("=" * 60)
    
    # Frontend integration example
    print("\n📱 Frontend Integration (React/JavaScript):")
    print("""
```javascript
// Customer analytics hook
const useCustomerAnalytics = (customerId) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch(`/api/v1/analytics/customers/${customerId}/analytics`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
      setAnalytics(data);
      setLoading(false);
    });
  }, [customerId]);
  
  return { analytics, loading };
};

// Dashboard component
const CustomerDashboard = () => {
  const { analytics, loading } = useCustomerAnalytics(customerId);
  
  if (loading) return <Spinner />;
  
  return (
    <div>
      <h2>{analytics.customer_name}</h2>
      <MetricCard 
        title="Total Interactions" 
        value={analytics.total_interactions} 
      />
      <InteractionChart data={analytics.interaction_types} />
      <SegmentBadges segments={analytics.segments} />
    </div>
  );
};
```""")
    
    # Backend service integration
    print("\n🔧 Backend Service Integration (Python):")
    print("""
```python
# Service integration example
from app.services.customer_analytics_service import CustomerAnalyticsService

class CustomerService:
    def __init__(self, db: Session, org_id: int):
        self.db = db
        self.org_id = org_id
        self.analytics = CustomerAnalyticsService(db, org_id)
    
    def get_customer_dashboard_data(self, customer_id: int):
        # Get basic customer info
        customer = self.get_customer(customer_id)
        
        # Get analytics
        analytics = self.analytics.get_customer_metrics(customer_id)
        
        # Combine data
        return {
            'customer': customer,
            'analytics': analytics,
            'health_score': self.calculate_health_score(analytics)
        }
    
    def calculate_health_score(self, analytics):
        # Custom business logic
        if analytics['total_interactions'] > 10:
            return 'healthy'
        elif analytics['total_interactions'] > 5:
            return 'moderate'
        else:
            return 'at_risk'
```""")


def main():
    """Run the complete demonstration"""
    demonstrate_api_endpoints()
    demonstrate_use_cases()
    demonstrate_integration()
    
    print("\n" + "=" * 60)
    print("✅ CUSTOMER ANALYTICS MODULE READY")
    print("=" * 60)
    print("\nThe Customer Analytics module provides:")
    print("• 5 comprehensive API endpoints")
    print("• Multi-tenant data isolation")
    print("• Performance-optimized queries")
    print("• Comprehensive test coverage")
    print("• Full documentation")
    print("• Backward compatibility")
    print("\nReady for production deployment! 🚀")


if __name__ == "__main__":
    main()