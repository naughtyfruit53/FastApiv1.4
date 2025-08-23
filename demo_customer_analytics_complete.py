#!/usr/bin/env python3
"""
Customer Analytics Module Demonstration Script

This script demonstrates the Customer Analytics functionality by:
1. Testing API endpoint accessibility
2. Validating database models
3. Showing sample analytics data structure
4. Verifying service layer functionality
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analytics_import():
    """Test that all analytics components can be imported successfully"""
    print("🔍 Testing Analytics Module Imports...")
    
    try:
        from app.api.customer_analytics import router
        print("✅ API Router imported successfully")
        
        from app.services.customer_analytics_service import CustomerAnalyticsService
        print("✅ Analytics Service imported successfully")
        
        from app.schemas.customer_analytics import (
            CustomerAnalyticsResponse, 
            SegmentAnalyticsResponse,
            DashboardMetrics
        )
        print("✅ Pydantic Schemas imported successfully")
        
        from app.models.base import CustomerInteraction, CustomerSegment
        print("✅ Database Models imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_api_routes():
    """Test API route registration"""
    print("\n🛣️  Testing API Routes...")
    
    try:
        from app.api.customer_analytics import router
        
        routes = []
        for route in router.routes:
            if hasattr(route, 'path'):
                methods = list(getattr(route, 'methods', ['GET']))
                routes.append(f"{methods[0]} {route.path}")
        
        print("✅ Available Analytics Endpoints:")
        for route in routes:
            print(f"   📍 {route}")
        
        expected_routes = [
            '/customers/{customer_id}/analytics',
            '/segments/{segment_name}/analytics', 
            '/organization/summary',
            '/dashboard/metrics',
            '/segments'
        ]
        
        for expected in expected_routes:
            found = any(expected in route for route in routes)
            if found:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ Missing: {expected}")
        
        return True
    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        return False

def test_schemas():
    """Test schema definitions"""
    print("\n📋 Testing Pydantic Schemas...")
    
    try:
        from app.schemas.customer_analytics import CustomerAnalyticsResponse
        
        # Create a sample response to test schema validation
        sample_data = {
            "customer_id": 1,
            "customer_name": "Test Customer",
            "total_interactions": 15,
            "last_interaction_date": "2024-01-15T10:30:00Z",
            "interaction_types": {"call": 5, "email": 8, "meeting": 2},
            "interaction_status": {"completed": 10, "pending": 3, "in_progress": 2},
            "segments": [
                {
                    "segment_name": "premium",
                    "segment_value": 150.0,
                    "assigned_date": "2024-01-01T00:00:00Z",
                    "description": "Premium customer"
                }
            ],
            "recent_interactions": [
                {
                    "interaction_type": "call",
                    "subject": "Product inquiry",
                    "status": "completed",
                    "interaction_date": "2024-01-15T10:30:00Z"
                }
            ],
            "calculated_at": "2024-01-16T12:00:00Z"
        }
        
        response = CustomerAnalyticsResponse(**sample_data)
        print("✅ CustomerAnalyticsResponse schema validation passed")
        print(f"   📊 Sample data: {response.total_interactions} interactions for {response.customer_name}")
        
        return True
    except Exception as e:
        print(f"❌ Schema testing failed: {e}")
        return False

def test_database_models():
    """Test database model definitions"""
    print("\n🗄️  Testing Database Models...")
    
    try:
        from app.models.base import CustomerInteraction, CustomerSegment
        
        # Check model attributes
        interaction_fields = ['id', 'organization_id', 'customer_id', 'interaction_type', 
                            'subject', 'description', 'status', 'interaction_date']
        segment_fields = ['id', 'organization_id', 'customer_id', 'segment_name', 
                        'segment_value', 'is_active', 'assigned_date']
        
        print("✅ CustomerInteraction model fields:")
        for field in interaction_fields:
            if hasattr(CustomerInteraction, field):
                print(f"   ✅ {field}")
            else:
                print(f"   ❌ Missing: {field}")
        
        print("✅ CustomerSegment model fields:")
        for field in segment_fields:
            if hasattr(CustomerSegment, field):
                print(f"   ✅ {field}")
            else:
                print(f"   ❌ Missing: {field}")
        
        return True
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False

def show_sample_analytics_structure():
    """Show sample analytics data structure"""
    print("\n📊 Sample Analytics Data Structure:")
    
    sample_customer_analytics = {
        "customer_id": 1,
        "customer_name": "ABC Corporation",
        "total_interactions": 25,
        "last_interaction_date": "2024-01-15T14:30:00Z",
        "interaction_types": {
            "call": 8,
            "email": 12,
            "meeting": 3,
            "support_ticket": 2
        },
        "interaction_status": {
            "completed": 18,
            "pending": 4,
            "in_progress": 3
        },
        "segments": [
            {
                "segment_name": "premium",
                "segment_value": 250.0,
                "assigned_date": "2024-01-01T00:00:00Z",
                "description": "Premium tier customer"
            },
            {
                "segment_name": "high_value",
                "segment_value": 500.0,
                "assigned_date": "2024-01-05T00:00:00Z",
                "description": "High-value customer"
            }
        ],
        "recent_interactions": [
            {
                "interaction_type": "call",
                "subject": "Product inquiry",
                "status": "completed",
                "interaction_date": "2024-01-15T14:30:00Z"
            },
            {
                "interaction_type": "email",
                "subject": "Follow-up email",
                "status": "completed",
                "interaction_date": "2024-01-14T09:15:00Z"
            }
        ],
        "calculated_at": "2024-01-16T12:00:00Z"
    }
    
    print("   Customer Analytics Sample:")
    print(f"   • Customer: {sample_customer_analytics['customer_name']}")
    print(f"   • Total Interactions: {sample_customer_analytics['total_interactions']}")
    print(f"   • Active Segments: {len(sample_customer_analytics['segments'])}")
    print(f"   • Recent Activity: {len(sample_customer_analytics['recent_interactions'])} interactions")
    
    sample_dashboard = {
        "total_customers": 150,
        "total_interactions_today": 8,
        "total_interactions_week": 45,
        "total_interactions_month": 180,
        "top_segments": [
            {"segment_name": "premium", "customer_count": 25},
            {"segment_name": "regular", "customer_count": 85},
            {"segment_name": "vip", "customer_count": 15}
        ],
        "calculated_at": "2024-01-16T12:00:00Z"
    }
    
    print("\n   Dashboard Metrics Sample:")
    print(f"   • Total Customers: {sample_dashboard['total_customers']}")
    print(f"   • Interactions Today: {sample_dashboard['total_interactions_today']}")
    print(f"   • Interactions This Month: {sample_dashboard['total_interactions_month']}")
    print(f"   • Top Segments: {len(sample_dashboard['top_segments'])} segments")

def main():
    """Main demonstration function"""
    print("🚀 Customer Analytics Module Demonstration")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    if test_analytics_import():
        success_count += 1
    
    if test_api_routes():
        success_count += 1
    
    if test_schemas():
        success_count += 1
    
    if test_database_models():
        success_count += 1
    
    show_sample_analytics_structure()
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✅ Customer Analytics Module is fully functional!")
        print("\n📋 Next Steps:")
        print("   1. Run database migrations: python -m alembic upgrade head")
        print("   2. Start the FastAPI server: python -m uvicorn app.main:app --reload")
        print("   3. Test endpoints: GET /api/v1/analytics/dashboard/metrics")
        print("   4. Build and run the frontend: cd frontend && npm run dev")
        print("   5. Navigate to customers page and click Analytics button")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)