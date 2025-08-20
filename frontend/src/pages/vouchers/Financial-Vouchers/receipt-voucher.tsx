// Receipt Voucher Page - Refactored using shared DRY logic
import React from 'react';
import { Box, Button, TextField, Typography, Grid, Alert, CircularProgress, Container, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Modal, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import { Add, Visibility, Edit } from '@mui/icons-material';
import { Controller } from 'react-hook-form';
import AddVendorModal from '../../../components/AddVendorModal';
import AddCustomerModal from '../../../components/AddCustomerModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords } from '../../../utils/voucherUtils';

const ReceiptVoucher: React.FC = () => {
  const config = getVoucherConfig('receipt-voucher');
  const {
    // State
    mode,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddCustomerModal,
    setShowAddCustomerModal,
    addVendorLoading,
    setAddVendorLoading,
    addCustomerLoading,
    setAddCustomerLoading,
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
    handleAddVendor,
    handleAddCustomer,
  } = useVoucherPage(config);

  // Watch form values
  const watchedValues = watch();
  const totalAmount = watchedValues?.total_amount || 0;

  // Combined name options for autocomplete
  const allNameOptions = [
    ...(vendorList || []).map(v => ({ ...v, type: 'Vendor' })),
    ...(customerList || []).map(c => ({ ...c, type: 'Customer' }))
  ];

  const nameFilter = createFilterOptions();

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Receipt Vouchers</Typography>
              <VoucherHeaderActions
                onCreate={handleCreate}
                onSearch={handleModalOpen}
                voucherType="Receipt Voucher"
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
                        <TableCell>{voucher.vendor?.name || voucher.customer?.name || 'N/A'}</TableCell>
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
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Receipt Voucher
            </Typography>

            <form onSubmit={handleSubmit(handleSubmitForm)} className="space-y-4">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="Voucher Number"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.voucher_number}
                    helperText={errors.voucher_number?.message}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('date')}
                    label="Date"
                    type="date"
                    fullWidth
                    disabled={mode === 'view'}
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.date}
                    helperText={errors.date?.message}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Autocomplete
                    options={allNameOptions}
                    getOptionLabel={(option: any) => option?.name || ''}
                    groupBy={(option: any) => option.type}
                    value={allNameOptions.find((option: any) => 
                      (watchedValues.vendor_id && option.id === watchedValues.vendor_id && option.type === 'Vendor') ||
                      (watchedValues.customer_id && option.id === watchedValues.customer_id && option.type === 'Customer')
                    ) || null}
                    onChange={(_, value: any) => {
                      if (value) {
                        if (value.type === 'Vendor') {
                          setValue('vendor_id', value.id);
                          setValue('customer_id', null);
                        } else {
                          setValue('customer_id', value.id);
                          setValue('vendor_id', null);
                        }
                      } else {
                        setValue('vendor_id', null);
                        setValue('customer_id', null);
                      }
                    }}
                    filterOptions={nameFilter}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField 
                        {...params} 
                        label="Party Name" 
                        error={!!errors.vendor_id || !!errors.customer_id}
                        helperText={errors.vendor_id?.message || errors.customer_id?.message}
                        InputProps={{
                          ...params.InputProps,
                          endAdornment: (
                            <>
                              {params.InputProps.endAdornment}
                              <InputAdornment position="end">
                                <Tooltip title="Add Vendor">
                                  <Button
                                    size="small"
                                    onClick={handleAddVendor}
                                    sx={{ minWidth: 'auto', p: 0.5, mr: 0.5 }}
                                  >
                                    <Add fontSize="small" />
                                  </Button>
                                </Tooltip>
                                <Tooltip title="Add Customer">
                                  <Button
                                    size="small"
                                    onClick={handleAddCustomer}
                                    sx={{ minWidth: 'auto', p: 0.5 }}
                                  >
                                    <Add fontSize="small" />
                                  </Button>
                                </Tooltip>
                              </InputAdornment>
                            </>
                          ),
                        }}
                      />
                    )}
                  />
                </Grid>

                <Grid item xs={6}>
                  <TextField
                    {...control.register('receipt_method')}
                    label="Receipt Method"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.receipt_method}
                    helperText={errors.receipt_method?.message}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('reference')}
                    label="Reference"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.reference}
                    helperText={errors.reference?.message}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    {...control.register('total_amount', { valueAsNumber: true })}
                    label="Total Amount"
                    type="number"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.total_amount}
                    helperText={errors.total_amount?.message}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                      inputProps: { step: "0.01" }
                    }}
                  />
                </Grid>

                {totalAmount > 0 && (
                  <Grid item xs={12}>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      <strong>Amount in words:</strong> {numberToWords(totalAmount)}
                    </Alert>
                  </Grid>
                )}

                <Grid item xs={12}>
                  <TextField
                    {...control.register('notes')}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={3}
                    disabled={mode === 'view'}
                    error={!!errors.notes}
                    helperText={errors.notes?.message}
                  />
                </Grid>

                {mode !== 'view' && (
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                      <Button 
                        variant="outlined" 
                        onClick={handleCreate}
                        disabled={createMutation.isPending || updateMutation.isPending}
                      >
                        Clear
                      </Button>
                      <Button 
                        type="submit" 
                        variant="contained"
                        disabled={createMutation.isPending || updateMutation.isPending}
                      >
                        {createMutation.isPending || updateMutation.isPending ? 
                          <CircularProgress size={20} /> : 
                          (mode === 'create' ? 'Create' : 'Update')
                        }
                      </Button>
                      <Button 
                        variant="outlined" 
                        onClick={() => handleGeneratePDF()}
                        disabled={!watchedValues.voucher_number}
                      >
                        Save as PDF
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </form>
          </Paper>
        </Grid>
      </Grid>

      {/* Add Vendor Modal */}
      <AddVendorModal
        open={showAddVendorModal}
        onClose={() => setShowAddVendorModal(false)}
        onAdd={handleAddVendor}
        loading={addVendorLoading}
      />

      {/* Add Customer Modal */}
      <AddCustomerModal
        open={showAddCustomerModal}
        onClose={() => setShowAddCustomerModal(false)}
        onAdd={handleAddCustomer}
        loading={addCustomerLoading}
      />

      {/* Context Menu */}
      {contextMenu !== null && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType="Receipt Voucher"
          onEdit={handleEdit}
          onView={handleView}
          onDelete={handleDelete}
          onPrint={() => handleGeneratePDF(contextMenu.voucher)}
          onDuplicate={(voucher) => {
            handleCreate();
            setValue('reference', voucher.voucher_number);
          }}
          showKebab={false}
          open={true}
          onClose={handleContextMenuClose}
          anchorReference="anchorPosition"
          anchorPosition={{ top: contextMenu.mouseY, left: contextMenu.mouseX }}
        />
      )}

      {/* Search/Filter Modal */}
      <Modal open={showFullModal} onClose={handleModalClose}>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '90%',
            maxWidth: 800,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Search Receipt Vouchers
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                placeholder="Voucher number, reference, notes..."
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <TextField
                label="From Date"
                type="date"
                value={fromDate}
                onChange={(e) => setFromDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <TextField
                label="To Date"
                type="date"
                value={toDate}
                onChange={(e) => setToDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                onClick={handleSearch}
                fullWidth
                sx={{ height: '56px' }}
              >
                Search
              </Button>
            </Grid>
          </Grid>

          <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Voucher #</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Party</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredVouchers.map((voucher: any) => (
                  <TableRow key={voucher.id}>
                    <TableCell>{voucher.voucher_number}</TableCell>
                    <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                    <TableCell>{voucher.vendor?.name || voucher.customer?.name || 'N/A'}</TableCell>
                    <TableCell>₹{voucher.total_amount?.toFixed(2) || '0.00'}</TableCell>
                    <TableCell>
                      <Button
                        size="small"
                        onClick={() => {
                          handleEdit(voucher);
                          handleModalClose();
                        }}
                        startIcon={<Edit />}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        onClick={() => {
                          handleView(voucher);
                          handleModalClose();
                        }}
                        startIcon={<Visibility />}
                      >
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Modal>
    </Container>
  );
};

export default ReceiptVoucher;