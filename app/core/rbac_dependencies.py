# app/core/rbac_dependencies.py

"""
FastAPI dependencies for Service CRM RBAC (Role-Based Access Control)
"""

from typing import List, Optional, Callable
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.base import User
from app.services.rbac import RBACService
from app.core.permissions import Permission
import logging

logger = logging.getLogger(__name__)


class RBACDependency:
    """FastAPI dependency class for RBAC permission checking"""
    
    def __init__(self, required_permission: str, organization_scoped: bool = True):
        self.required_permission = required_permission
        self.organization_scoped = organization_scoped
    
    def __call__(self, 
                 current_user: User = Depends(lambda: None),  # Will be injected properly
                 db: Session = Depends(get_db),
                 request: Request = None) -> User:
        """Check if current user has required service permission"""
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Super admins bypass all checks
        if getattr(current_user, 'is_super_admin', False):
            return current_user
        
        # Check service permission through RBAC
        rbac_service = RBACService(db)
        
        if rbac_service.user_has_service_permission(current_user.id, self.required_permission):
            logger.info(f"User {current_user.id} has service permission: {self.required_permission}")
            return current_user
        
        # If organization scoped, check if user has sufficient regular permissions as fallback
        if self.organization_scoped and current_user.organization_id:
            # Map service permissions to regular permissions for fallback
            fallback_permissions = _get_fallback_permissions(self.required_permission)
            
            from app.core.permissions import PermissionChecker
            for fallback_perm in fallback_permissions:
                if PermissionChecker.has_permission(current_user, fallback_perm):
                    logger.info(f"User {current_user.id} has fallback permission: {fallback_perm}")
                    return current_user
        
        logger.warning(f"User {current_user.id} denied access - missing permission: {self.required_permission}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {self.required_permission}"
        )


def _get_fallback_permissions(service_permission: str) -> List[str]:
    """Map service permissions to regular system permissions for fallback"""
    fallback_map = {
        # Service management permissions
        "service_create": [Permission.CREATE_USERS],  # Using create as analogy
        "service_read": [Permission.VIEW_USERS],
        "service_update": [Permission.MANAGE_USERS],
        "service_delete": [Permission.DELETE_USERS],
        
        # Technician management permissions
        "technician_create": [Permission.CREATE_USERS],
        "technician_read": [Permission.VIEW_USERS],
        "technician_update": [Permission.MANAGE_USERS],
        "technician_delete": [Permission.DELETE_USERS],
        
        # Appointment permissions - map to user management
        "appointment_create": [Permission.CREATE_USERS],
        "appointment_read": [Permission.VIEW_USERS],
        "appointment_update": [Permission.MANAGE_USERS],
        "appointment_delete": [Permission.DELETE_USERS],
        
        # Customer service permissions
        "customer_service_create": [Permission.CREATE_USERS],
        "customer_service_read": [Permission.VIEW_USERS],
        "customer_service_update": [Permission.MANAGE_USERS],
        "customer_service_delete": [Permission.DELETE_USERS],
        
        # Work order permissions
        "work_order_create": [Permission.CREATE_USERS],
        "work_order_read": [Permission.VIEW_USERS],
        "work_order_update": [Permission.MANAGE_USERS],
        "work_order_delete": [Permission.DELETE_USERS],
        
        # Reports permissions
        "service_reports_read": [Permission.VIEW_AUDIT_LOGS],
        "service_reports_export": [Permission.VIEW_AUDIT_LOGS],
        
        # Admin permissions
        "crm_admin": [Permission.MANAGE_ORGANIZATIONS, Permission.SUPER_ADMIN],
        "crm_settings": [Permission.MANAGE_ORGANIZATIONS, Permission.ACCESS_ORG_SETTINGS],
        
        # SLA management permissions
        "sla_create": [Permission.CREATE_USERS],
        "sla_read": [Permission.VIEW_USERS],
        "sla_update": [Permission.MANAGE_USERS],
        "sla_delete": [Permission.DELETE_USERS],
        "sla_escalate": [Permission.MANAGE_USERS],
        
        # Dispatch management permissions
        "dispatch_create": [Permission.CREATE_USERS],
        "dispatch_read": [Permission.VIEW_USERS],
        "dispatch_update": [Permission.MANAGE_USERS],
        "dispatch_delete": [Permission.DELETE_USERS],
        
        # Installation job permissions
        "installation_create": [Permission.CREATE_USERS],
        "installation_read": [Permission.VIEW_USERS],
        "installation_update": [Permission.MANAGE_USERS],
        "installation_delete": [Permission.DELETE_USERS],
    }
    
    return fallback_map.get(service_permission, [])


# Convenience dependency creators
def require_service_permission(permission: str, organization_scoped: bool = True) -> Callable:
    """Create a dependency that requires a specific service permission"""
    return RBACDependency(permission, organization_scoped)


# Common service permission dependencies
require_service_admin = RBACDependency("crm_admin")
require_service_settings = RBACDependency("crm_settings")

# Service management dependencies
require_service_create = RBACDependency("service_create")
require_service_read = RBACDependency("service_read")
require_service_update = RBACDependency("service_update")
require_service_delete = RBACDependency("service_delete")

# Technician management dependencies
require_technician_create = RBACDependency("technician_create")
require_technician_read = RBACDependency("technician_read")
require_technician_update = RBACDependency("technician_update")
require_technician_delete = RBACDependency("technician_delete")

# Appointment management dependencies
require_appointment_create = RBACDependency("appointment_create")
require_appointment_read = RBACDependency("appointment_read")
require_appointment_update = RBACDependency("appointment_update")
require_appointment_delete = RBACDependency("appointment_delete")

# Customer service dependencies
require_customer_service_create = RBACDependency("customer_service_create")
require_customer_service_read = RBACDependency("customer_service_read")
require_customer_service_update = RBACDependency("customer_service_update")
require_customer_service_delete = RBACDependency("customer_service_delete")

# Work order dependencies
require_work_order_create = RBACDependency("work_order_create")
require_work_order_read = RBACDependency("work_order_read")
require_work_order_update = RBACDependency("work_order_update")
require_work_order_delete = RBACDependency("work_order_delete")

# SLA management dependencies
require_sla_create = RBACDependency("sla_create")
require_sla_read = RBACDependency("sla_read")
require_sla_update = RBACDependency("sla_update")
require_sla_delete = RBACDependency("sla_delete")
require_sla_escalate = RBACDependency("sla_escalate")

# Reports dependencies
require_service_reports_read = RBACDependency("service_reports_read")
require_service_reports_export = RBACDependency("service_reports_export")

# Dispatch management dependencies
require_dispatch_create = RBACDependency("dispatch_create")
require_dispatch_read = RBACDependency("dispatch_read")
require_dispatch_update = RBACDependency("dispatch_update")
require_dispatch_delete = RBACDependency("dispatch_delete")

# Installation job dependencies
require_installation_create = RBACDependency("installation_create")
require_installation_read = RBACDependency("installation_read")
require_installation_update = RBACDependency("installation_update")
require_installation_delete = RBACDependency("installation_delete")


# Helper functions for getting RBAC service
def get_rbac_service(db: Session = Depends(get_db)) -> RBACService:
    """Get RBAC service instance"""
    return RBACService(db)


def get_user_service_permissions(
    current_user: User = Depends(lambda: None),
    rbac_service: RBACService = Depends(get_rbac_service)
) -> set:
    """Get all service permissions for current user"""
    if not current_user:
        return set()
    
    return rbac_service.get_user_service_permissions(current_user.id)


# Role management dependencies (for administrative functions)
def require_role_management_permission(
    current_user: User = Depends(lambda: None),
    db: Session = Depends(get_db)
) -> User:
    """Require permission to manage service roles"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Super admins can manage roles
    if getattr(current_user, 'is_super_admin', False):
        return current_user
    
    # Org admins can manage roles in their organization
    from app.core.permissions import PermissionChecker
    if PermissionChecker.has_permission(current_user, Permission.MANAGE_USERS):
        return current_user
    
    # Service admins can manage roles
    rbac_service = RBACService(db)
    if rbac_service.user_has_service_permission(current_user.id, "crm_admin"):
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions to manage service roles"
    )


def require_same_organization(
    current_user: User = Depends(lambda: None)
) -> Callable[[int], int]:
    """Ensure operations are scoped to user's organization"""
    def check_organization(target_organization_id: int) -> int:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Super admins can access any organization
        if getattr(current_user, 'is_super_admin', False):
            return target_organization_id
        
        # Regular users must stay within their organization
        if current_user.organization_id != target_organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Organization mismatch."
            )
        
        return target_organization_id
    
    return check_organization