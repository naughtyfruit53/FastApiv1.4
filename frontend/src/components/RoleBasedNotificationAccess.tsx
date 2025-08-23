// src/components/RoleBasedNotificationAccess.tsx
// Role-based access control for notification features

import React from 'react';
import { Box, Alert, Typography, Button } from '@mui/material';
import { Lock, AdminPanelSettings } from '@mui/icons-material';

interface RoleBasedNotificationAccessProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
  userRole?: string;
  fallbackComponent?: React.ReactNode;
  showUpgradeMessage?: boolean;
}

const RoleBasedNotificationAccess: React.FC<RoleBasedNotificationAccessProps> = ({
  children,
  requiredPermissions = ['notification_admin'],
  userRole = 'standard_user',
  fallbackComponent,
  showUpgradeMessage = true
}) => {
  // Simple role hierarchy check (in real app, this would come from auth context)
  const hasPermission = () => {
    const roleHierarchy = {
      'super_admin': ['notification_admin', 'notification_manage', 'crm_admin'],
      'org_admin': ['notification_admin', 'notification_manage'],
      'admin': ['notification_manage'],
      'manager': ['notification_manage'],
      'standard_user': []
    };

    const userPermissions = roleHierarchy[userRole as keyof typeof roleHierarchy] || [];
    return requiredPermissions.some(permission => userPermissions.includes(permission));
  };

  if (hasPermission()) {
    return <>{children}</>;
  }

  if (fallbackComponent) {
    return <>{fallbackComponent}</>;
  }

  if (showUpgradeMessage) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Alert 
          severity="warning"
          icon={<Lock />}
          sx={{ 
            maxWidth: 500, 
            mx: 'auto',
            '& .MuiAlert-message': {
              textAlign: 'left'
            }
          }}
        >
          <Typography variant="h6" gutterBottom>
            Administrator Access Required
          </Typography>
          <Typography variant="body2" paragraph>
            Notification template management requires administrator or manager permissions. 
            Contact your organization administrator to request access.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Current role: <strong>{userRole}</strong><br />
            Required permissions: <strong>{requiredPermissions.join(', ')}</strong>
          </Typography>
        </Alert>
        
        <Box sx={{ mt: 3 }}>
          <Button
            variant="outlined"
            startIcon={<AdminPanelSettings />}
            onClick={() => {
              // In real app, this could redirect to permission request or contact admin
              console.log('Request permission functionality');
            }}
          >
            Request Access
          </Button>
        </Box>
      </Box>
    );
  }

  return null;
};

export default RoleBasedNotificationAccess;

// Helper hook for checking notification permissions
export const useNotificationPermissions = (userRole?: string) => {
  const canManageTemplates = () => {
    const adminRoles = ['super_admin', 'org_admin', 'admin', 'manager'];
    return adminRoles.includes(userRole || '');
  };

  const canViewHistory = () => {
    // All users can view their own notification history
    return true;
  };

  const canManagePreferences = () => {
    // All users can manage their own preferences
    return true;
  };

  const canSendNotifications = () => {
    const allowedRoles = ['super_admin', 'org_admin', 'admin', 'manager'];
    return allowedRoles.includes(userRole || '');
  };

  const canViewAnalytics = () => {
    const analyticsRoles = ['super_admin', 'org_admin', 'admin'];
    return analyticsRoles.includes(userRole || '');
  };

  return {
    canManageTemplates,
    canViewHistory,
    canManagePreferences,
    canSendNotifications,
    canViewAnalytics
  };
};