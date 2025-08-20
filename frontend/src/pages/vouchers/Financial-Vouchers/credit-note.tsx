// Credit Note Page - Sales voucher type
import React from 'react';
import { useRouter } from 'next/router';
import { Box, Button, TextField, Typography, Grid, IconButton, Alert, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Switch, FormControlLabel, Modal } from '@mui/material';
import { Add, Remove, Visibility, Edit } from '@mui/icons-material';
import AddCustomerModal from '../../../components/AddCustomerModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherLayout from '../../../components/VoucherLayout';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import BalanceDisplay from '../../../components/BalanceDisplay';
import StockDisplay from '../../../components/StockDisplay';
import ProductAutocomplete from '../../../components/ProductAutocomplete';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, GST_SLABS } from '../../../utils/voucherUtils';

const CreditNotePage: React.FC = () => {
  const router = useRouter();
  const config = getVoucherConfig('credit-note');
  const {
    // State
    mode,
    setMode,
    isLoading,
    showAddCustomerModal,
    setShowAddCustomerModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    addCustomerLoading,
    setAddCustomerLoading,
    addProductLoading,
    setAddProductLoading,
    addShippingLoading,
    setAddShippingLoading,
    addingItemIndex,
    setAddingItemIndex,
    showFullModal,
    contextMenu,
    useDifferentShipping,
    setUseDifferentShipping,
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
    errors,
    fields,
    append,
    remove,

    // Data
    voucherList,
    customerList,
    productList,
    sortedVouchers,
    latestVouchers,
    computedItems,
    totalAmount,

    // Mutations
    createMutation,
    updateMutation,

    // Event handlers
    handleCreate,
    handleEdit,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleDeleteVoucher,
    handlePrintVoucher,
    handleEmailVoucher,
    handleAddCustomer,
    handleAddProduct,
    selectedId
  } = useVoucherPage(config);

  if (isLoading) {
    return (
      <Container maxWidth="xl">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  const filter = createFilterOptions<any>();
  const customerOptions = customerList || [];
  const productOptions = productList || [];

  return (
    <VoucherLayout
      voucherType="Credit Notes"
      onShowAll={handleModalOpen}
      indexContent={
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Credit Note #</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {latestVouchers.map((voucher: any) => (
                <TableRow 
                  key={voucher.id}
                  onContextMenu={(e) => handleContextMenu(e, voucher)}
                  style={{ cursor: 'context-menu' }}
                >
                  <TableCell>{voucher.voucher_number}</TableCell>
                  <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                  <TableCell>{customerList?.find((c: any) => c.id === voucher.customer_id)?.name || ''}</TableCell>
                  <TableCell align="right" sx={{ pr: 0 }}>
                    <VoucherContextMenu
                      voucher={voucher}
                      voucherType="Credit Note"
                      onView={handleView}
                      onEdit={handleEdit}
                      onDelete={handleDeleteVoucher}
                      onPrint={() => handlePrintVoucher(voucher.id, voucher.voucher_number)}
                      onEmail={handleEmailVoucher}
                      showKebab={true}
                      open={false}
                      onClose={() => {}}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      }
      formContent={
        <Box>
          <VoucherHeaderActions
            mode={mode}
            setMode={setMode}
            isViewMode={mode === 'view'}
            currentId={selectedId || undefined}
          />
          <form onSubmit={handleSubmit(handleSubmitForm)}>
            <Grid container spacing={0.5}>
              <Grid size={4}>
                <Tooltip title={mode === 'create' ? 'Auto-generated on save' : ''} arrow>
                  <TextField
                    fullWidth
                    label="Credit Note Number"
                    {...control.register('voucher_number')}
                    disabled={mode === 'create' || mode === 'view'}
                    InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                    inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                    size="small"
                    sx={{ '& .MuiInputBase-root': { height: 27 } }}
                  />
                </Tooltip>
              </Grid>
              <Grid size={4}>
                <TextField
                  fullWidth
                  label="Date"
                  type="date"
                  {...control.register('date', { required: true })}
                  error={!!errors.date}
                  helperText={errors.date ? 'Required' : ''}
                  disabled={mode === 'view'}
                  InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                  inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              </Grid>
              <Grid size={4}>
                <Autocomplete
                  options={customerOptions}
                  getOptionLabel={(option) => option.name || ''}
                  value={customerOptions.find((opt: any) => opt.id === watch('customer_id')) || null}
                  onChange={(_, newValue) => {
                    if (newValue && newValue.id === -1) {
                      handleAddCustomer();
                    } else {
                      setValue('customer_id', newValue ? newValue.id : null);
                    }
                  }}
                  filterOptions={(options, params) => {
                    const filtered = filter(options, params);
                    if (params.inputValue !== '') {
                      filtered.unshift({ id: -1, name: `Add "${params.inputValue}"` });
                    }
                    return filtered;
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Customer"
                      error={!!errors.customer_id}
                      helperText={errors.customer_id ? 'Required' : ''}
                      InputLabelProps={{ shrink: true, style: { fontSize: 10, textAlign: 'center' } }}
                      inputProps={{ ...params.inputProps, style: { fontSize: 12, textAlign: 'center' } }}
                      size="small"
                      sx={{ '& .MuiInputBase-root': { height: 27 } }}
                    />
                  )}
                  disabled={mode === 'view'}
                />
              </Grid>
              
              <Grid size={12}>
                <TextField
                  fullWidth
                  label="Reason for Credit Note"
                  {...control.register('notes')}
                  multiline
                  rows={2}
                  disabled={mode === 'view'}
                  InputLabelProps={{ shrink: true, style: { fontSize: 10 } }}
                  inputProps={{ style: { fontSize: 12 } }}
                  size="small"
                />
              </Grid>

              {/* Total Amount */}
              <Grid size={6}>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  {...control.register('total_amount', { valueAsNumber: true })}
                  disabled={mode === 'view'}
                  InputLabelProps={{ shrink: true, style: { fontSize: 10 } }}
                  inputProps={{ style: { fontSize: 12, textAlign: 'center' } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              </Grid>

              <Grid size={6}>
                <TextField
                  fullWidth
                  label="Amount in Words"
                  value={getAmountInWords(watch('total_amount') || 0)}
                  disabled
                  InputLabelProps={{ shrink: true, style: { fontSize: 10 } }}
                  inputProps={{ style: { fontSize: 12 } }}
                  size="small"
                  sx={{ '& .MuiInputBase-root': { height: 27 } }}
                />
              </Grid>
              
              {/* Action buttons */}
              <Grid size={12}>
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  {mode !== 'view' && (
                    <Button 
                      type="submit" 
                      variant="contained" 
                      color="success" 
                      disabled={createMutation.isPending || updateMutation.isPending}
                      sx={{ fontSize: 10 }}
                    >
                      Save
                    </Button>
                  )}
                  <Button 
                    variant="contained" 
                    color="error" 
                    onClick={() => router.push('/dashboard')} 
                    sx={{ fontSize: 10 }}
                  >
                    Cancel
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Box>
      }
    />
  );
};

export default CreditNotePage;