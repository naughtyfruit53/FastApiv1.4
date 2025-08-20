// Purchase Order Page - Refactored using shared DRY logic  
import React from 'react';
import { Box, Button, TextField, Typography, Grid, IconButton, Alert, CircularProgress, Container, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Autocomplete, createFilterOptions, InputAdornment, Tooltip, Switch, FormControlLabel, Modal } from '@mui/material';
import { Add, Remove, Visibility, Edit } from '@mui/icons-material';
import AddVendorModal from '../../../components/AddVendorModal';
import AddProductModal from '../../../components/AddProductModal';
import AddShippingAddressModal from '../../../components/AddShippingAddressModal';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';
import ProductAutocomplete from '../../../components/ProductAutocomplete';
import { useVoucherPage } from '../../../hooks/useVoucherPage';
import { getVoucherConfig, numberToWords, GST_SLABS } from '../../../utils/voucherUtils';

const PurchaseOrderPage: React.FC = () => {
  const config = getVoucherConfig('purchase-order');
  const {
    // State
    mode,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    addVendorLoading,
    setAddVendorLoading,
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
    vendorList,
    productList,
    sortedVouchers,
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,

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
    handleAddProduct,
    handleAddShipping,
  } = useVoucherPage(config);

  const nameFilter = createFilterOptions();

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Grid container spacing={3}>
        {/* Left side - Voucher List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Purchase Orders</Typography>
              <VoucherHeaderActions
                onCreate={handleCreate}
                onSearch={handleModalOpen}
                voucherType="Purchase Order"
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
                      <TableCell>PO #</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Total</TableCell>
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
                        <TableCell>{voucher.vendor?.name || 'N/A'}</TableCell>
                        <TableCell>{voucher.status || 'draft'}</TableCell>
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
              {mode === 'create' ? 'Create' : mode === 'edit' ? 'Edit' : 'View'} Purchase Order
            </Typography>

            <form onSubmit={handleSubmit(handleSubmitForm)} className="space-y-4">
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    {...control.register('voucher_number')}
                    label="PO Number"
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
                    options={vendorList || []}
                    getOptionLabel={(option: any) => option?.name || ''}
                    value={vendorList?.find((vendor: any) => vendor.id === watch('vendor_id')) || null}
                    onChange={(_, value: any) => setValue('vendor_id', value?.id || null)}
                    filterOptions={nameFilter}
                    disabled={mode === 'view'}
                    renderInput={(params) => (
                      <TextField 
                        {...params} 
                        label="Vendor" 
                        error={!!errors.vendor_id}
                        helperText={errors.vendor_id?.message}
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
                    {...control.register('payment_terms')}
                    label="Payment Terms"
                    fullWidth
                    disabled={mode === 'view'}
                    error={!!errors.payment_terms}
                    helperText={errors.payment_terms?.message}
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

                {/* Shipping Address Toggle */}
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useDifferentShipping}
                        onChange={(e) => setUseDifferentShipping(e.target.checked)}
                        disabled={mode === 'view'}
                      />
                    }
                    label="Use different shipping address"
                  />
                </Grid>

                {/* Items Section */}
                <Grid item xs={12}>
                  <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="subtitle1">Items</Typography>
                    {mode !== 'view' && (
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => append({ 
                          product_id: null, 
                          hsn_code: '', 
                          quantity: 0, 
                          unit: '', 
                          unit_price: 0, 
                          original_unit_price: 0, 
                          discount_percentage: 0, 
                          discount_amount: 0, 
                          taxable_amount: 0, 
                          gst_rate: 0, 
                          cgst_amount: 0, 
                          sgst_amount: 0, 
                          igst_amount: 0, 
                          total_amount: 0 
                        })}
                        startIcon={<Add />}
                      >
                        Add Item
                      </Button>
                    )}
                  </Box>

                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Product</TableCell>
                          <TableCell>HSN</TableCell>
                          <TableCell>Qty</TableCell>
                          <TableCell>Unit</TableCell>
                          <TableCell>Rate</TableCell>
                          <TableCell>Disc%</TableCell>
                          <TableCell>GST%</TableCell>
                          <TableCell>Amount</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {fields.map((field, index) => (
                          <TableRow key={field.id}>
                            <TableCell>
                              <ProductAutocomplete
                                value={productList?.find((p: any) => p.id === watch(`items.${index}.product_id`)) || null}
                                onChange={(product: any) => {
                                  setValue(`items.${index}.product_id`, product?.id || null);
                                  if (product) {
                                    setValue(`items.${index}.hsn_code`, product.hsn_code || '');
                                    setValue(`items.${index}.unit`, product.unit || '');
                                    setValue(`items.${index}.unit_price`, product.selling_price || 0);
                                    setValue(`items.${index}.original_unit_price`, product.selling_price || 0);
                                    setValue(`items.${index}.gst_rate`, product.gst_rate || 0);
                                  }
                                }}
                                disabled={mode === 'view'}
                                onAddNew={() => {
                                  setAddingItemIndex(index);
                                  handleAddProduct();
                                }}
                                error={!!errors.items?.[index]?.product_id}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.hsn_code`)}
                                size="small"
                                disabled={mode === 'view'}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.quantity`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 70 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.unit`)}
                                size="small"
                                disabled={mode === 'view'}
                                sx={{ width: 60 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.unit_price`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 80 }}
                              />
                            </TableCell>
                            <TableCell>
                              <TextField
                                {...control.register(`items.${index}.discount_percentage`, { valueAsNumber: true })}
                                size="small"
                                type="number"
                                disabled={mode === 'view'}
                                sx={{ width: 60 }}
                              />
                            </TableCell>
                            <TableCell>
                              <Autocomplete
                                options={GST_SLABS}
                                value={watch(`items.${index}.gst_rate`) || 0}
                                onChange={(_, value) => setValue(`items.${index}.gst_rate`, value || 0)}
                                disabled={mode === 'view'}
                                renderInput={(params) => (
                                  <TextField
                                    {...params}
                                    size="small"
                                    sx={{ width: 70 }}
                                  />
                                )}
                              />
                            </TableCell>
                            <TableCell>
                              ₹{(computedItems[index]?.total_amount || 0).toFixed(2)}
                            </TableCell>
                            <TableCell>
                              {mode !== 'view' && (
                                <IconButton
                                  size="small"
                                  onClick={() => remove(index)}
                                  disabled={fields.length === 1}
                                >
                                  <Remove fontSize="small" />
                                </IconButton>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    {...control.register('notes')}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={2}
                    disabled={mode === 'view'}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2">Subtotal: ₹{totalSubtotal.toFixed(2)}</Typography>
                        <Typography variant="body2">GST: ₹{totalGst.toFixed(2)}</Typography>
                        <Typography variant="h6">Total: ₹{totalAmount.toFixed(2)}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        {totalAmount > 0 && (
                          <Typography variant="body2" color="textSecondary">
                            Amount in words: {numberToWords(totalAmount)}
                          </Typography>
                        )}
                      </Grid>
                    </Grid>
                  </Box>
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
                        disabled={!watch('voucher_number')}
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

      {/* Add Product Modal */}
      <AddProductModal
        open={showAddProductModal}
        onClose={() => setShowAddProductModal(false)}
        onAdd={handleAddProduct}
        loading={addProductLoading}
      />

      {/* Add Shipping Address Modal */}
      <AddShippingAddressModal
        open={showShippingModal}
        onClose={() => setShowShippingModal(false)}
        onAdd={handleAddShipping}
        loading={addShippingLoading}
      />

      {/* Context Menu */}
      {contextMenu !== null && (
        <VoucherContextMenu
          voucher={contextMenu.voucher}
          voucherType="Purchase Order"
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
            maxWidth: 1000,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" gutterBottom>
            Search Purchase Orders
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <TextField
                label="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                fullWidth
                placeholder="PO number, vendor, notes..."
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
                  <TableCell>PO #</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Vendor</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Total</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredVouchers.map((voucher: any) => (
                  <TableRow key={voucher.id}>
                    <TableCell>{voucher.voucher_number}</TableCell>
                    <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                    <TableCell>{voucher.vendor?.name || 'N/A'}</TableCell>
                    <TableCell>{voucher.status || 'draft'}</TableCell>
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

export default PurchaseOrderPage;