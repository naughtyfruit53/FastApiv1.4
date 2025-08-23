#!/usr/bin/env python3
"""
Simple validation script for new customer models.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def validate_models():
    """Validate that the new customer models are properly implemented."""
    print("🔍 Validating customer models implementation...")
    
    try:
        # Mock dependencies to avoid full app startup
        from sqlalchemy.orm import declarative_base
        from unittest.mock import MagicMock
        
        # Mock the app.core.database module
        sys.modules['app.core.database'] = MagicMock()
        sys.modules['app.core.database'].Base = declarative_base()
        
        # Import the models
        from app.models.base import Customer, CustomerInteraction, CustomerSegment
        
        print("✅ Successfully imported all customer models")
        
        # Validate CustomerInteraction model
        assert hasattr(CustomerInteraction, '__tablename__')
        assert CustomerInteraction.__tablename__ == "customer_interactions"
        assert hasattr(CustomerInteraction, 'id')
        assert hasattr(CustomerInteraction, 'organization_id')
        assert hasattr(CustomerInteraction, 'customer_id')
        assert hasattr(CustomerInteraction, 'interaction_type')
        assert hasattr(CustomerInteraction, 'subject')
        print("✅ CustomerInteraction model validation passed")
        
        # Validate CustomerSegment model
        assert hasattr(CustomerSegment, '__tablename__')
        assert CustomerSegment.__tablename__ == "customer_segments"
        assert hasattr(CustomerSegment, 'id')
        assert hasattr(CustomerSegment, 'organization_id')
        assert hasattr(CustomerSegment, 'customer_id')
        assert hasattr(CustomerSegment, 'segment_name')
        assert hasattr(CustomerSegment, 'is_active')
        print("✅ CustomerSegment model validation passed")
        
        # Validate Customer model relationships
        assert hasattr(Customer, 'interactions')
        assert hasattr(Customer, 'segments')
        print("✅ Customer model relationships validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

def validate_migration():
    """Validate that the migration file exists and is properly structured."""
    print("🔍 Validating migration file...")
    
    migration_path = os.path.join(
        os.path.dirname(__file__), 
        'migrations', 
        'versions', 
        'b4f8c2d1a9e0_add_customer_interactions_and_segments.py'
    )
    
    if not os.path.exists(migration_path):
        print(f"❌ Migration file not found at: {migration_path}")
        return False
    
    try:
        with open(migration_path, 'r') as f:
            content = f.read()
        
        # Check for required migration components
        required_components = [
            'def upgrade()',
            'def downgrade()', 
            'customer_interactions',
            'customer_segments',
            'organization_id',
            'customer_id',
            'ForeignKeyConstraint'
        ]
        
        for component in required_components:
            if component not in content:
                print(f"❌ Missing migration component: {component}")
                return False
        
        print("✅ Migration file validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Migration file validation failed: {e}")
        return False

def main():
    """Run all validations."""
    print("🚀 Starting customer models and migration validation...\n")
    
    results = []
    
    # Run model validation
    results.append(validate_models())
    
    # Run migration validation
    results.append(validate_migration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validations passed! Models and migration are ready.")
        return True
    else:
        print("⚠️  Some validations failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)