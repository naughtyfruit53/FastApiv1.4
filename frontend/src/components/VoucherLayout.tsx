// frontend/src/components/VoucherLayout.tsx
// Enhanced VoucherLayout component with comprehensive UI improvements
import React from 'react';
import { Container, Grid, Paper, Box, Typography, Button, Pagination } from '@mui/material';
import { getVoucherStyles } from '../utils/voucherUtils';

interface VoucherLayoutProps {
  voucherType: string;
  voucherTitle?: string;
  indexContent: React.ReactNode;
  formContent: React.ReactNode;
  onShowAll?: () => void;
  showAllButton?: boolean;
  // Enhanced pagination props
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    totalItems: number;
  };
  // Additional props for modal functionality
  showModal?: boolean;
  onCloseModal?: () => void;
  modalContent?: React.ReactNode;
  // Center alignment control
  centerAligned?: boolean;
}

const VoucherLayout: React.FC<VoucherLayoutProps> = ({
  voucherType,
  voucherTitle,
  indexContent,
  formContent,
  onShowAll,
  showAllButton = true,
  pagination,
  showModal = false,
  onCloseModal,
  modalContent,
  centerAligned = true
}) => {
  const voucherStyles = getVoucherStyles();
  
  return (
    <>
      <Container maxWidth="xl" sx={centerAligned ? voucherStyles.voucherContainer : {}}>
        {/* Main Title */}
        {voucherTitle && (
          <Typography 
            variant="h4" 
            sx={{
              ...voucherStyles.voucherTitle,
              mb: 3,
              fontSize: '1.5rem'
            }}
          >
            {voucherTitle}
          </Typography>
        )}
        
        <Grid container spacing={2}>
          {/* Index Panel - approximately 40% */}
          <Grid size={{ xs: 12, md: 5, lg: 5 }}>
            <Paper sx={{ 
              p: 2,
              height: 'fit-content',
              ...(centerAligned && {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center'
              })
            }}>
              <Box 
                display="flex" 
                justifyContent="space-between" 
                alignItems="center" 
                mb={1}
                sx={centerAligned ? { width: '100%' } : {}}
              >
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontSize: 18, 
                    fontWeight: 'bold', 
                    textAlign: 'center', 
                    flex: 1,
                    ...voucherStyles.centerText
                  }}
                >
                  {voucherType}
                </Typography>
                {showAllButton && (
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={onShowAll}
                    sx={{ ml: 1 }}
                  >
                    Show All
                  </Button>
                )}
              </Box>
              
              {/* Index Content with center alignment */}
              <Box sx={centerAligned ? { width: '100%' } : {}}>
                {indexContent}
              </Box>
              
              {/* Pagination for index if provided */}
              {pagination && (
                <Box sx={voucherStyles.paginationContainer}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                      Page {pagination.currentPage} of {pagination.totalPages} 
                      ({pagination.totalItems} total items)
                    </Typography>
                    <Pagination
                      count={pagination.totalPages}
                      page={pagination.currentPage}
                      onChange={(_, page) => pagination.onPageChange(page)}
                      size="small"
                      color="primary"
                      showFirstButton
                      showLastButton
                    />
                  </Box>
                </Box>
              )}
            </Paper>
          </Grid>

          {/* Form Panel - approximately 60% */}
          <Grid size={{ xs: 12, md: 7, lg: 7 }}>
            <Paper sx={{ 
              p: 2,
              ...(centerAligned && voucherStyles.formContainer)
            }}>
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