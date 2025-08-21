// frontend/src/components/VoucherLayout.tsx
// Shared VoucherLayout component - 40:60 split ratio (approximated as 5:7 in Grid)
import React from 'react';
import { Container, Grid, Paper, Box, Typography, Button } from '@mui/material';

interface VoucherLayoutProps {
  voucherType: string;
  indexContent: React.ReactNode;
  formContent: React.ReactNode;
  onShowAll?: () => void;
  showAllButton?: boolean;
  // Additional props for modal functionality
  showModal?: boolean;
  onCloseModal?: () => void;
  modalContent?: React.ReactNode;
}

const VoucherLayout: React.FC<VoucherLayoutProps> = ({
  voucherType,
  indexContent,
  formContent,
  onShowAll,
  showAllButton = true,
  showModal = false,
  onCloseModal,
  modalContent
}) => {
  return (
    <>
      <Container maxWidth="xl">
        <Grid container spacing={2}>
          {/* Index Panel - approximately 40% */}
          <Grid size={{ xs: 12, md: 5, lg: 5 }}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="h6" sx={{ fontSize: 18, fontWeight: 'bold', textAlign: 'center', flex: 1 }}>
                  {voucherType}
                </Typography>
                {showAllButton && (
                  <Button variant="outlined" size="small" onClick={onShowAll}>
                    Show All
                  </Button>
                )}
              </Box>
              {indexContent}
            </Paper>
          </Grid>

          {/* Form Panel - approximately 60% */}
          <Grid size={{ xs: 12, md: 7, lg: 7 }}>
            <Paper sx={{ p: 2 }}>
              {formContent}
            </Paper>
          </Grid>
        </Grid>
      </Container>
      
      {/* Modal Content */}
      {modalContent}
    </>
  );
};

export default VoucherLayout;