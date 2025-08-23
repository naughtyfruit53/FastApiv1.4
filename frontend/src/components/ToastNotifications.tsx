// src/components/ToastNotifications.tsx
// In-app toast notification component with queue management

import React, { useState, useEffect, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  Slide,
  SlideProps,
  Stack,
  IconButton,
  Box,
  Typography
} from '@mui/material';
import {
  Close,
  CheckCircle,
  Error,
  Warning,
  Info,
  Notifications
} from '@mui/icons-material';

export interface ToastNotification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  persistent?: boolean;
  actions?: Array<{
    label: string;
    onClick: () => void;
  }>;
}

interface ToastNotificationsProps {
  notifications?: ToastNotification[];
  maxVisible?: number;
  position?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  onClose?: (id: string) => void;
}

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

const ToastNotifications: React.FC<ToastNotificationsProps> = ({
  notifications = [],
  maxVisible = 3,
  position = { vertical: 'bottom', horizontal: 'right' },
  onClose
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState<ToastNotification[]>([]);
  const [queue, setQueue] = useState<ToastNotification[]>([]);

  // Process notification queue
  useEffect(() => {
    if (notifications.length > 0) {
      const newNotifications = notifications.filter(
        notif => !visibleNotifications.some(visible => visible.id === notif.id) &&
                !queue.some(queued => queued.id === notif.id)
      );

      if (newNotifications.length > 0) {
        setQueue(prev => [...prev, ...newNotifications]);
      }
    }
  }, [notifications, visibleNotifications, queue]);

  // Show notifications from queue
  useEffect(() => {
    if (visibleNotifications.length < maxVisible && queue.length > 0) {
      const nextNotification = queue[0];
      setVisibleNotifications(prev => [...prev, nextNotification]);
      setQueue(prev => prev.slice(1));

      // Auto-hide after duration (if not persistent)
      if (!nextNotification.persistent) {
        const duration = nextNotification.duration || 6000;
        setTimeout(() => {
          handleClose(nextNotification.id);
        }, duration);
      }
    }
  }, [visibleNotifications, queue, maxVisible]);

  const handleClose = useCallback((id: string) => {
    setVisibleNotifications(prev => prev.filter(notif => notif.id !== id));
    onClose?.(id);
  }, [onClose]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle />;
      case 'error':
        return <Error />;
      case 'warning':
        return <Warning />;
      case 'info':
        return <Info />;
      default:
        return <Notifications />;
    }
  };

  const getSeverity = (type: string): 'success' | 'error' | 'warning' | 'info' => {
    return ['success', 'error', 'warning', 'info'].includes(type) 
      ? type as 'success' | 'error' | 'warning' | 'info'
      : 'info';
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        zIndex: 9999,
        ...(position.vertical === 'top' ? { top: 24 } : { bottom: 24 }),
        ...(position.horizontal === 'left' && { left: 24 }),
        ...(position.horizontal === 'center' && { 
          left: '50%', 
          transform: 'translateX(-50%)' 
        }),
        ...(position.horizontal === 'right' && { right: 24 }),
        maxWidth: '400px',
        width: '100%'
      }}
    >
      <Stack spacing={1} direction="column-reverse">
        {visibleNotifications.map((notification) => (
          <Snackbar
            key={notification.id}
            open={true}
            TransitionComponent={SlideTransition}
            sx={{ position: 'relative', mb: 1 }}
          >
            <Alert
              severity={getSeverity(notification.type)}
              icon={getIcon(notification.type)}
              action={
                <Box display="flex" alignItems="center" gap={1}>
                  {notification.actions?.map((action, index) => (
                    <IconButton
                      key={index}
                      size="small"
                      onClick={action.onClick}
                      sx={{ color: 'inherit' }}
                    >
                      <Typography variant="caption" sx={{ textDecoration: 'underline' }}>
                        {action.label}
                      </Typography>
                    </IconButton>
                  ))}
                  <IconButton
                    size="small"
                    onClick={() => handleClose(notification.id)}
                    sx={{ color: 'inherit' }}
                  >
                    <Close fontSize="small" />
                  </IconButton>
                </Box>
              }
              sx={{
                width: '100%',
                boxShadow: 2,
                '& .MuiAlert-message': {
                  flex: 1,
                  overflow: 'hidden'
                }
              }}
            >
              <Typography variant="body2" sx={{ wordBreak: 'break-word' }}>
                {notification.message}
              </Typography>
            </Alert>
          </Snackbar>
        ))}
      </Stack>
    </Box>
  );
};

export default ToastNotifications;

// Hook for managing toast notifications
export const useToastNotifications = () => {
  const [notifications, setNotifications] = useState<ToastNotification[]>([]);

  const addNotification = useCallback((notification: Omit<ToastNotification, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: ToastNotification = {
      id,
      ...notification
    };
    
    setNotifications(prev => [...prev, newNotification]);
    return id;
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // Convenience methods
  const showSuccess = useCallback((message: string, options?: Partial<ToastNotification>) => {
    return addNotification({ message, type: 'success', ...options });
  }, [addNotification]);

  const showError = useCallback((message: string, options?: Partial<ToastNotification>) => {
    return addNotification({ message, type: 'error', ...options });
  }, [addNotification]);

  const showWarning = useCallback((message: string, options?: Partial<ToastNotification>) => {
    return addNotification({ message, type: 'warning', ...options });
  }, [addNotification]);

  const showInfo = useCallback((message: string, options?: Partial<ToastNotification>) => {
    return addNotification({ message, type: 'info', ...options });
  }, [addNotification]);

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};