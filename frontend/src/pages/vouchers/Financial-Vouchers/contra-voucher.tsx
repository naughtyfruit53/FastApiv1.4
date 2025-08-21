import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, InputAdornment, Tooltip, Modal, Autocomplete, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Visibility, Edit } from '@mui/icons-material';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig } from '../../../utils/voucherUtils';

const ContraVoucher: React.FC = () => {
  const config = getVoucherConfig('contra-voucher');
  const {
    // State
    mode,
    setMode,
    isLoading,
    showFullModal,
    contextMenu,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,

    // Form
    control,
    handleSubmit,
    watch,
    errors,

    // Data
    voucherList,
    sortedVouchers,
    latestVouchers,

    // Mutations
    createMutation,
    updateMutation,

    // Event handlers
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu: handleContextMenuClose,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    getAmountInWords,

    // Utilities
    isViewMode,
  } = useVoucherPage(config);

  const totalAmountValue = watch('total_amount');

  // Account options - this could be moved to a shared utility if used across vouchers
  const accountOptions = [
    'Cash',
    'Bank Account - SBI', 
    'Bank Account - HDFC',
    'Bank Account - ICICI',
    'Bank Account - Axis',
    'Petty Cash',
    'Fixed Deposit',
    'Savings Account',
    'Current Account'
  ];

  // Custom submit handler for contra voucher validation
  const onSubmit = (data: any) => {
    if (data.from_account === data.to_account) {
      alert('From Account and To Account cannot be the same');
      return;
    }
    handleSubmitForm(data);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Contra Vouchers</Typography>
              <VoucherHeaderActions
                onCreate={handleCreate}
                onSearch={handleModalOpen}
                voucherType="Contra Voucher"
              />
            </Box>

            {isLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Sr.</TableCell>
                      <TableCell>Voucher #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sortedVouchers?.map((voucher: any, index: number) => (
                      <TableRow 
                        key={voucher.id} 
                        hover
                        onContextMenu={(e) => handleContextMenu(e, voucher)}
                        sx={{ cursor: 'context-menu' }}
                      >
                        <TableCell>{index + 1}</TableCell>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                        <TableCell>₹{voucher.total_amount?.toFixed(2) || '0.00'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Right side - Voucher Form */}
        <Grid size={12} md={8}>
          <Paper sx={{ p: 3, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Contra Voucher
            </Typography>

            {(createMutation.isPending || updateMutation.isPending) && (
              <Box display="flex" justifyContent="center" my={2}>
                <CircularProgress />
              </Box>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 3 }}>
              <Grid container spacing={3}>
          <Grid size={6}>
            <TextField
              {...control.register('voucher_number')}
              label="Voucher Number"
              fullWidth
              disabled={true}
              InputProps={{
                readOnly: true,
              }}
            />
          </Grid>
          <Grid size={6}>
            <TextField
              {...control.register('date')}
              label="Date"
              type="date"
              fullWidth
              disabled={isViewMode}
              InputLabelProps={{
                shrink: true,
              }}
              error={!!errors.date}
              helperText={errors.date?.message}
            />
          </Grid>

          <Grid size={6}>
            <Autocomplete
              options={accountOptions}
              value={watch('from_account') || ''}
              onChange={(_, newValue) => setValue('from_account', newValue || '')}
              disabled={isViewMode}
              freeSolo
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="From Account"
                  error={!!errors.from_account}
                  helperText={errors.from_account?.message}
                />
              )}
            />
          </Grid>

          <Grid size={6}>
            <Autocomplete
              options={accountOptions}
              value={watch('to_account') || ''}
              onChange={(_, newValue) => setValue('to_account', newValue || '')}
              disabled={isViewMode}
              freeSolo
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="To Account"
                  error={!!errors.to_account}
                  helperText={errors.to_account?.message}
                />
              )}
            />
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('total_amount', {
                required: 'Amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' }
              })}
              label="Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.total_amount}
              helperText={errors.total_amount?.message}
              InputProps={{
                inputProps: { step: "0.01" }
              }}
            />
          </Grid>

          <Grid size={12}>
            <TextField
              {...control.register('notes')}
              label="Notes"
              multiline
              rows={3}
              fullWidth
              disabled={isViewMode}
              error={!!errors.notes}
              helperText={errors.notes?.message}
            />
          </Grid>

          {totalAmountValue > 0 && (
            <Grid size={12}>
              <Typography variant="body2" color="textSecondary">
                Amount in Words: {getAmountInWords(totalAmountValue)}
              </Typography>
            </Grid>
          )}

          <Grid size={12}>
            <Box display="flex" gap={2}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                disabled={isViewMode || createMutation.isPending || updateMutation.isPending}
              >
                {mode === 'create' ? 'Create' : 'Update'} Contra Voucher
              </Button>
              <Button
                variant="outlined"
                onClick={handleCreate}
              >
                Clear
              </Button>
              {!isViewMode && (
                <Button
                  variant="outlined"
                  onClick={() => handleGeneratePDF()}
                  disabled={!watch('voucher_number')}
                >
                  Generate PDF
                </Button>
              )}
            </Box>
          </Grid>
        </Grid>
      </Box>
          </Paper>
        </Grid>
      </Grid>

      <VoucherContextMenu
        voucherType="Contra Voucher"
        contextMenu={contextMenu}
        onClose={handleContextMenuClose}
        onEdit={(id) => {
          handleEdit(id);
          handleContextMenuClose();
        }}
        onView={(id) => {
          handleView(id);
          handleContextMenuClose();
        }}
        onDelete={(id) => {
          handleDelete(id);
          handleContextMenuClose();
        }}
      />

      <Modal
        open={showFullModal}
        onClose={handleModalClose}
        aria-labelledby="voucher-list-modal"
      >
        <Box sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '90%',
          maxWidth: 1200,
          bgcolor: 'background.paper',
          border: '2px solid #000',
          boxShadow: 24,
          p: 4,
          maxHeight: '90vh',
          overflow: 'auto'
        }}>
          <Typography variant="h6" component="h2" gutterBottom>
            Contra Vouchers
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid size={4}>
              <TextField
                fullWidth
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid size={3}>
              <TextField
                fullWidth
                label="From Date"
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Grid>
            <Grid size={3}>
              <TextField
                fullWidth
                label="To Date"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Grid>
            <Grid size={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleSearch}
                size="small"
              >
                Filter
              </Button>
            </Grid>
          </Grid>

          <Box sx={{ height: 400, overflow: 'auto' }}>
            {(filteredVouchers.length > 0 ? filteredVouchers : sortedVouchers).map((voucher: any) => (
              <Box
                key={voucher.id}
                sx={{
                  p: 2,
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  mb: 1,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'grey.50' }
                }}
                onContextMenu={(e) => handleContextMenu(e, voucher)}
              >
                <Grid container spacing={2} alignItems="center">
                  <Grid size={2}>
                    <Typography variant="body2" fontWeight="bold">
                      {voucher.voucher_number}
                    </Typography>
                  </Grid>
                  <Grid size={2}>
                    <Typography variant="body2">
                      {new Date(voucher.date).toLocaleDateString()}
                    </Typography>
                  </Grid>
                  <Grid size={3}>
                    <Typography variant="body2" noWrap>
                      {voucher.from_account}
                    </Typography>
                  </Grid>
                  <Grid size={3}>
                    <Typography variant="body2" noWrap>
                      {voucher.to_account}
                    </Typography>
                  </Grid>
                  <Grid size={1}>
                    <Typography variant="body2" fontWeight="bold">
                      ₹{voucher.total_amount?.toFixed(2)}
                    </Typography>
                  </Grid>
                  <Grid size={1}>
                    <Box display="flex" gap={1}>
                      <Tooltip title="View">
                        <Button
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleView(voucher);
                            handleModalClose();
                          }}
                        >
                          <Visibility fontSize="small" />
                        </Button>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <Button
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEdit(voucher);
                            handleModalClose();
                          }}
                        >
                          <Edit fontSize="small" />
                        </Button>
                      </Tooltip>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            ))}
          </Box>
        </Box>
      </Modal>
    </Container>
  );
};

export default ContraVoucher;