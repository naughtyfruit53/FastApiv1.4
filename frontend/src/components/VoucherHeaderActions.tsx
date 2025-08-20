'use client';

import React from 'react';
import { Box, Typography } from '@mui/material';
import { useRouter } from 'next/navigation';

interface VoucherHeaderActionsProps {
  mode: 'create' | 'edit' | 'view';
  voucherType: string; // e.g., 'Purchase Order', 'Sales Voucher', etc.
  voucherRoute: string; // The base route for this voucher type
  currentId?: number; // Current voucher ID (for edit route)
  // Additional props for compatibility
  onModeChange?: (mode: 'create' | 'edit' | 'view') => void;
  onModalOpen?: () => void;
  voucherList?: any[];
  onEdit?: (voucher: any) => void;
  onView?: (voucher: any) => void;
  isLoading?: boolean;
}

const VoucherHeaderActions: React.FC<VoucherHeaderActionsProps> = ({
  mode,
  voucherType,
  voucherRoute,
  currentId,
  // Additional props for compatibility (ignored for now)
  onModeChange,
  onModalOpen,
  voucherList,
  onEdit,
  onView,
  isLoading,
}) => {
  const router = useRouter();

  const handleEdit = () => {
    if (currentId) {
      router.push(`${voucherRoute}?mode=edit&id=${currentId}`);
    }
  };

  const handleCreate = () => {
    router.push(`${voucherRoute}?mode=create`);
  };

  const actionStyle = {
    color: '#001f3f',
    fontSize: '15px',
    fontWeight: 'normal',
    textDecoration: 'underline',
    cursor: 'pointer',
    marginLeft: '20px',
    '&:hover': {
      textDecoration: 'none',
    },
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0 }}>
      {mode === 'view' && (
        <>
          <Typography 
            sx={{
              ...actionStyle,
              color: '#FFD700', // Yellow for EDIT
              textTransform: 'uppercase',
              fontWeight: 'bold',
            }}
            onClick={handleEdit}
          >
            EDIT {voucherType.toLowerCase()}
          </Typography>
          <Typography 
            sx={{
              ...actionStyle,
              color: '#28a745', // Green for CREATE
              textTransform: 'uppercase',
              fontWeight: 'bold',
            }}
            onClick={handleCreate}
          >
            CREATE {voucherType.toLowerCase()}
          </Typography>
        </>
      )}
      {mode === 'edit' && (
        <Typography 
          sx={{
            ...actionStyle,
            color: '#28a745', // Green for CREATE
            textTransform: 'uppercase',
            fontWeight: 'bold',
          }}
          onClick={handleCreate}
        >
          CREATE {voucherType.toLowerCase()}
        </Typography>
      )}
    </Box>
  );
};

export default VoucherHeaderActions;