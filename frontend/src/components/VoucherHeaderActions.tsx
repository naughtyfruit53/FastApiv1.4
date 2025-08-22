// frontend/src/components/VoucherHeaderActions.tsx
'use client';

import React from 'react';
import { Box, Button } from '@mui/material';
import { Add as AddIcon, Edit as EditIcon, PictureAsPdf as PdfIcon } from '@mui/icons-material';
import { useRouter } from 'next/navigation';

interface VoucherHeaderActionsProps {
  mode: 'create' | 'edit' | 'view';
  voucherType: string; // e.g., 'Purchase Order', 'Sales Voucher', etc.
  voucherRoute: string; // The base route for this voucher type
  currentId?: number; // Current voucher ID (for edit route)
  onGeneratePDF?: () => void;
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
  onGeneratePDF,
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

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {mode === 'view' && (
        <>
          <Button 
            variant="contained" 
            color="success" 
            startIcon={<AddIcon />}
            onClick={handleCreate}
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Create {voucherType.toLowerCase()}
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<EditIcon />}
            onClick={handleEdit}
            sx={{ fontSize: 12, textTransform: 'uppercase' }}
          >
            Edit {voucherType.toLowerCase()}
          </Button>
        </>
      )}
      {mode === 'edit' && (
        <Button 
          variant="contained" 
          color="success" 
          startIcon={<AddIcon />}
          onClick={handleCreate}
          sx={{ fontSize: 12, textTransform: 'uppercase' }}
        >
          Create {voucherType.toLowerCase()}
        </Button>
      )}
      {(mode === 'view' || mode === 'edit') && onGeneratePDF && (
        <Button 
          variant="contained" 
          color="secondary" 
          startIcon={<PdfIcon />}
          onClick={onGeneratePDF}
          sx={{ fontSize: 12, textTransform: 'uppercase' }}
        >
          Generate PDF
        </Button>
      )}
      {mode !== 'view' && (
        <Button form="voucherForm" type="submit" variant="contained" color="success" sx={{ fontSize: 12 }}>
          Save
        </Button>
      )}
    </Box>
  );
};

export default VoucherHeaderActions;