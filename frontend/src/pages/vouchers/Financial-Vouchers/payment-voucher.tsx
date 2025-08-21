import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Grid, CircularProgress, Container, Autocomplete, InputAdornment, Tooltip, Modal, FormControl, InputLabel, Select, MenuItem, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Add, Visibility, Edit } from '@mui/icons-material';
import EntitySelector from '../../../components/EntitySelector';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import VoucherListModal from '../../../components/VoucherListModal';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, getVoucherStyles, parseRateField, formatRateField } from '../../../utils/voucherUtils';
import { useReferenceOptions } from '../../../utils/nameRefUtils';

const PaymentVoucher: React.FC = () => {
  const config = getVoucherConfig('payment-voucher');
  const voucherStyles = getVoucherStyles();
  
  const {
    // State
    mode,
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
    setValue,
    reset,
    errors,

    // Data
    voucherList,
    vendorList,
    customerList,
    sortedVouchers,

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
    refreshMasterData,
    getAmountInWords,

    // Utilities
    isViewMode,
  } = useVoucherPage(config);

  // Handle voucher click to load details
  const handleVoucherClick = (voucher: any) => {
    // Load the selected voucher into the form
    reset(voucher);
    // Set the form with the voucher data
    Object.keys(voucher).forEach(key => {
      setValue(key, voucher[key]);
    });
  };

  // Payment voucher specific state
  const [selectedModule, setSelectedModule] = useState<'Vendor' | 'Customer' | null>(null);
  
  const totalAmountValue = watch('total_amount');
  const selectedEntity = watch('entity'); // Now using entity instead of name_id/name_type

  // Get reference options including unpaid vouchers for the selected entity
  const referenceOptions = useReferenceOptions(
    selectedEntity?.id || null, 
    selectedEntity?.type || null
  );

  // Payment methods for payment vouchers
  const paymentMethods = [
    'Cash',
    'Bank Transfer',
    'Cheque',
    'Credit Card',
    'Debit Card',
    'Online Payment',
    'UPI',
    'Net Banking'
  ];

  // Handle entity creation success
  const handleEntityCreated = (newEntity: any) => {
    setValue('entity', {
      id: newEntity.id,
      name: newEntity.name,
      type: newEntity.type || 'Customer', // Default type
      value: newEntity.id,
      label: newEntity.name
    });
    refreshMasterData();
  };

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List (40%) */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Paper sx={{ p: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Payment Vouchers</Typography>
              <Button variant="outlined" size="small" onClick={handleModalOpen}>
                Show All
              </Button>
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
                      <TableCell>Party</TableCell>
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
                        <TableCell>
                          {voucher.entity?.name || 
                           (voucher.name_type === 'Vendor' 
                            ? vendorList?.find((v: any) => v.id === voucher.name_id)?.name 
                            : customerList?.find((c: any) => c.id === voucher.name_id)?.name) || 'N/A'}
                        </TableCell>
                        <TableCell>₹{voucher.total_amount?.toFixed(2) || '0.00'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Right side - Voucher Form (60%) */}
        <Grid size={12} md={7}>
          <Paper sx={{ p: 3, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Payment Voucher
            </Typography>

            {(createMutation.isPending || updateMutation.isPending) && (
              <Box display="flex" justifyContent="center" my={2}>
                <CircularProgress />
              </Box>
            )}

            <Box 
              component="form" 
              onSubmit={handleSubmit(handleSubmitForm)} 
              sx={{ 
                mt: 3,
                ...voucherStyles.formContainer
              }}
            >
              <Grid container spacing={3}>
          <Grid size={6}>
            <TextField
              {...control.register('voucher_number')}
              label="Voucher Number"
              fullWidth
              disabled={true}
              sx={voucherStyles.centerField}
              InputProps={{
                readOnly: true,
                style: { textAlign: 'center', fontWeight: 'bold' }
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
              sx={voucherStyles.centerField}
              InputLabelProps={{
                shrink: true,
              }}
              inputProps={{ style: { textAlign: 'center' } }}
              error={!!errors.date}
              helperText={errors.date?.message}
            />
          </Grid>

          <Grid size={6}>
            <EntitySelector
              name="entity"
              control={control}
              label="Party Name"
              required
              entityTypes={['Customer', 'Vendor']}
              allowTypeSelection={true}
              onEntityCreated={handleEntityCreated}
              disabled={isViewMode}
              error={!!errors.entity}
              helperText={errors.entity?.message}
            />
          </Grid>

          <Grid size={6}>
            <FormControl fullWidth disabled={isViewMode}>
              <InputLabel>Payment Method</InputLabel>
              <Select
                {...control.register('payment_method')}
                value={watch('payment_method') || ''}
                onChange={(e) => setValue('payment_method', e.target.value)}
                error={!!errors.payment_method}
              >
                {paymentMethods.map((method) => (
                  <MenuItem key={method} value={method}>
                    {method}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={6}>
            <Autocomplete
              freeSolo
              options={referenceOptions}
              value={watch('reference') || ''}
              onChange={(_, newValue) => setValue('reference', newValue || '')}
              disabled={isViewMode}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Reference"
                  error={!!errors.reference}
                  helperText={errors.reference?.message}
                />
              )}
            />
          </Grid>

          <Grid size={6}>
            <TextField
              {...control.register('total_amount', {
                required: 'Amount is required',
                min: { value: 0.01, message: 'Amount must be greater than 0' },
                setValueAs: (value) => parseRateField(value)
              })}
              label="Amount"
              type="number"
              fullWidth
              disabled={isViewMode}
              error={!!errors.total_amount}
              helperText={errors.total_amount?.message}
              sx={{
                ...voucherStyles.rateField,
                ...voucherStyles.centerField
              }}
              InputProps={{
                inputProps: { 
                  step: "0.01",
                  style: { textAlign: 'center' }
                }
              }}
              onChange={(e) => {
                const value = parseRateField(e.target.value);
                setValue('total_amount', value);
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
                {mode === 'create' ? 'Create' : 'Update'} Payment Voucher
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

      {/* Add Vendor Modal */}
      <VoucherContextMenu
        voucherType="Payment Voucher"
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

      {/* Voucher List Modal */}
      <VoucherListModal
        open={showFullModal}
        onClose={handleModalClose}
        voucherType="Payment Vouchers"
        vouchers={sortedVouchers || []}
        onVoucherClick={handleVoucherClick}
        onEdit={handleEdit}
        onView={handleView}
        onDelete={handleDelete}
        onGeneratePDF={handleGeneratePDF}
        customerList={customerList}
        vendorList={vendorList}
      />
    </Container>
  );
};

export default PaymentVoucher;
