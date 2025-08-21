import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useForm, useFieldArray } from 'react-hook-form';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Grid, 
  IconButton, 
  Alert, 
  CircularProgress, 
  Container, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Autocomplete, 
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { 
  Add, 
  Remove,
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

interface MaterialReceiptItem {
  product_id: number;
  quantity: number;
  unit: string;
  unit_price: number;
  received_quantity?: number;
  accepted_quantity?: number;
  rejected_quantity?: number;
  batch_number?: string;
  lot_number?: string;
  expiry_date?: string;
  warehouse_location?: string;
  bin_location?: string;
  quality_status?: string;
  inspection_remarks?: string;
  notes?: string;
  total_amount: number;
}

interface MaterialReceiptVoucher {
  id?: number;
  voucher_number: string;
  date: string;
  manufacturing_order_id?: number;
  source_type: string;
  source_reference?: string;
  received_from_department?: string;
  received_from_employee?: string;
  received_by_employee?: string;
  receipt_time?: string;
  inspection_required: boolean;
  inspection_status: string;
  inspector_name?: string;
  inspection_date?: string;
  inspection_remarks?: string;
  condition_on_receipt?: string;
  notes?: string;
  status: string;
  total_amount: number;
  items: MaterialReceiptItem[];
}

const defaultValues: Partial<MaterialReceiptVoucher> = {
  voucher_number: '',
  date: new Date().toISOString().split('T')[0],
  source_type: 'return',
  inspection_required: false,
  inspection_status: 'pending',
  status: 'draft',
  total_amount: 0,
  items: []
};

const sourceTypeOptions = [
  { value: 'return', label: 'Material Return' },
  { value: 'purchase', label: 'Purchase Receipt' },
  { value: 'transfer', label: 'Transfer Receipt' }
];

const inspectionStatusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'passed', label: 'Passed' },
  { value: 'failed', label: 'Failed' },
  { value: 'partial', label: 'Partial' }
];

const qualityStatusOptions = [
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'hold', label: 'Hold' }
];

export default function MaterialReceiptVoucher() {
  const router = useRouter();
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<MaterialReceiptVoucher>({
    defaultValues
  });

  const {
    fields: itemFields,
    append: appendItem,
    remove: removeItem
  } = useFieldArray({
    control,
    name: 'items'
  });

  // Fetch vouchers list
  const { data: voucherList, isLoading } = useQuery({
    queryKey: ['material-receipt-vouchers'],
    queryFn: () => api.get('/material-receipt-vouchers').then(res => res.data),
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch specific voucher
  const { data: voucherData, isFetching } = useQuery({
    queryKey: ['material-receipt-voucher', selectedId],
    queryFn: () => api.get(`/material-receipt-vouchers/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextMaterialReceiptNumber'],
    queryFn: () => api.get('/material-receipt-vouchers/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedVouchers = voucherList ? [...voucherList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestVouchers = sortedVouchers.slice(0, 10);
  const productOptions = productList || [];
  const manufacturingOrderOptions = manufacturingOrders || [];

  useEffect(() => {
    if (mode === 'create' && nextVoucherNumber) {
      setValue('voucher_number', nextVoucherNumber);
    } else if (voucherData) {
      reset(voucherData);
    } else if (mode === 'create') {
      reset(defaultValues);
    }
  }, [voucherData, mode, reset, nextVoucherNumber, setValue]);

  // Calculate totals
  useEffect(() => {
    const items = watch('items') || [];
    const total = items.reduce((sum, item) => sum + (item.total_amount || 0), 0);
    setValue('total_amount', total);
  }, [watch('items'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: MaterialReceiptVoucher) => api.post('/material-receipt-vouchers', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating material receipt voucher:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: MaterialReceiptVoucher }) => 
      api.put(`/material-receipt-vouchers/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating material receipt voucher:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/material-receipt-vouchers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] });
      if (selectedId) {
        setSelectedId(null);
        setMode('create');
        reset(defaultValues);
      }
    }
  });

  const onSubmit = (data: MaterialReceiptVoucher) => {
    if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (voucher: MaterialReceiptVoucher) => {
    setSelectedId(voucher.id!);
    setMode('edit');
  };

  const handleView = (voucher: MaterialReceiptVoucher) => {
    setSelectedId(voucher.id!);
    setMode('view');
  };

  const handleDelete = (voucherId: number) => {
    if (window.confirm('Are you sure you want to delete this voucher?')) {
      deleteMutation.mutate(voucherId);
    }
  };

  const handleCancel = () => {
    setMode('create');
    setSelectedId(null);
    reset(defaultValues);
  };

  const addItem = () => {
    appendItem({
      product_id: 0,
      quantity: 0,
      unit: '',
      unit_price: 0,
      received_quantity: 0,
      accepted_quantity: 0,
      rejected_quantity: 0,
      total_amount: 0
    });
  };

  const updateItemTotal = (index: number) => {
    const items = watch('items');
    const item = items[index];
    if (item) {
      const total = item.quantity * item.unit_price;
      setValue(`items.${index}.total_amount`, total);
    }
  };

  if (isLoading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" component="h1" gutterBottom>
        Material Receipt Vouchers
      </Typography>

      <Grid container spacing={3}>
        {/* Voucher List - Left Side */}
        <Grid size={12} md={5}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Vouchers</Typography>
                <VoucherHeaderActions 
                  onRefresh={() => queryClient.invalidateQueries({ queryKey: ['material-receipt-vouchers'] })}
                />
              </Box>
              
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Voucher No.</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Source Type</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {latestVouchers.map((voucher, index) => (
                      <TableRow key={voucher.id}>
                        <TableCell>{voucher.voucher_number}</TableCell>
                        <TableCell>{new Date(voucher.date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={voucher.source_type} 
                            size="small"
                            color={voucher.source_type === 'return' ? 'warning' : 'default'}
                          />
                        </TableCell>
                        <TableCell>₹{voucher.total_amount?.toFixed(2)}</TableCell>
                        <TableCell>
                          <Chip 
                            label={voucher.status} 
                            color={voucher.status === 'approved' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <VoucherContextMenu
                            voucher={voucher}
                            voucherType="Material Receipt"
                            onView={() => handleView(voucher)}
                            onEdit={() => handleEdit(voucher)}
                            onDelete={() => handleDelete(voucher.id!)}
                            canEdit={voucher.status !== 'approved'}
                            canDelete={voucher.status !== 'approved'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Voucher Form - Right Side */}
        <Grid size={12} md={7}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  {mode === 'create' && 'Create Material Receipt Voucher'}
                  {mode === 'edit' && 'Edit Material Receipt Voucher'}
                  {mode === 'view' && 'View Material Receipt Voucher'}
                </Typography>
                {mode !== 'create' && (
                  <Button 
                    variant="outlined" 
                    onClick={handleCancel}
                    startIcon={<Cancel />}
                  >
                    Cancel
                  </Button>
                )}
              </Box>

              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Basic Details */}
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Voucher Number"
                      {...control.register('voucher_number')}
                      fullWidth
                      disabled
                      value={watch('voucher_number')}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Date"
                      type="date"
                      {...control.register('date')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Source Type</InputLabel>
                      <Select
                        value={watch('source_type')}
                        onChange={(e) => setValue('source_type', e.target.value)}
                        disabled={mode === 'view'}
                      >
                        {sourceTypeOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Source Reference"
                      {...control.register('source_reference')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Autocomplete
                      options={manufacturingOrderOptions}
                      getOptionLabel={(option) => option.voucher_number || ''}
                      value={manufacturingOrderOptions.find(mo => mo.id === watch('manufacturing_order_id')) || null}
                      onChange={(_, newValue) => setValue('manufacturing_order_id', newValue?.id || undefined)}
                      renderInput={(params) => (
                        <TextField {...params} label="Manufacturing Order (Optional)" />
                      )}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Receipt Time"
                      type="datetime-local"
                      {...control.register('receipt_time')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Receipt Details */}
                <Typography variant="h6" gutterBottom>Receipt Details</Typography>
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Received From Department"
                      {...control.register('received_from_department')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Received From Employee"
                      {...control.register('received_from_employee')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Received By Employee"
                      {...control.register('received_by_employee')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Condition on Receipt"
                      {...control.register('condition_on_receipt')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Inspection Details */}
                <Typography variant="h6" gutterBottom>Inspection Details</Typography>
                <Grid container spacing={2} mb={3}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={watch('inspection_required')}
                          onChange={(e) => setValue('inspection_required', e.target.checked)}
                          disabled={mode === 'view'}
                        />
                      }
                      label="Inspection Required"
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <FormControl fullWidth>
                      <InputLabel>Inspection Status</InputLabel>
                      <Select
                        value={watch('inspection_status')}
                        onChange={(e) => setValue('inspection_status', e.target.value)}
                        disabled={mode === 'view'}
                      >
                        {inspectionStatusOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Inspector Name"
                      {...control.register('inspector_name')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Inspection Date"
                      type="datetime-local"
                      {...control.register('inspection_date')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={12}>
                    <TextField
                      label="Inspection Remarks"
                      {...control.register('inspection_remarks')}
                      fullWidth
                      multiline
                      rows={2}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Items */}
                <Typography variant="h6" gutterBottom>Material Items</Typography>
                {mode !== 'view' && (
                  <Box mb={2}>
                    <Button
                      variant="outlined"
                      onClick={addItem}
                      startIcon={<Add />}
                    >
                      Add Item
                    </Button>
                  </Box>
                )}

                <TableContainer component={Paper} sx={{ mb: 3 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Qty</TableCell>
                        <TableCell>Unit</TableCell>
                        <TableCell>Rate</TableCell>
                        <TableCell>Received</TableCell>
                        <TableCell>Accepted</TableCell>
                        <TableCell>Rejected</TableCell>
                        <TableCell>Batch</TableCell>
                        <TableCell>Quality</TableCell>
                        <TableCell>Amount</TableCell>
                        {mode !== 'view' && <TableCell>Actions</TableCell>}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {itemFields.map((field, index) => (
                        <TableRow key={field.id}>
                          <TableCell>
                            <Autocomplete
                              options={productOptions}
                              getOptionLabel={(option) => option.name || ''}
                              value={productOptions.find(p => p.id === watch(`items.${index}.product_id`)) || null}
                              onChange={(_, newValue) => {
                                setValue(`items.${index}.product_id`, newValue?.id || 0);
                                setValue(`items.${index}.unit`, newValue?.unit || '');
                                setValue(`items.${index}.unit_price`, newValue?.price || 0);
                                updateItemTotal(index);
                              }}
                              renderInput={(params) => (
                                <TextField {...params} size="small" />
                              )}
                              disabled={mode === 'view'}
                              sx={{ minWidth: 150 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`items.${index}.quantity`)}
                              onChange={(e) => {
                                setValue(`items.${index}.quantity`, parseFloat(e.target.value) || 0);
                                updateItemTotal(index);
                              }}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={watch(`items.${index}.unit`)}
                              onChange={(e) => setValue(`items.${index}.unit`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 70 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`items.${index}.unit_price`)}
                              onChange={(e) => {
                                setValue(`items.${index}.unit_price`, parseFloat(e.target.value) || 0);
                                updateItemTotal(index);
                              }}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`items.${index}.received_quantity`)}
                              onChange={(e) => setValue(`items.${index}.received_quantity`, parseFloat(e.target.value) || 0)}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`items.${index}.accepted_quantity`)}
                              onChange={(e) => setValue(`items.${index}.accepted_quantity`, parseFloat(e.target.value) || 0)}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              type="number"
                              size="small"
                              value={watch(`items.${index}.rejected_quantity`)}
                              onChange={(e) => setValue(`items.${index}.rejected_quantity`, parseFloat(e.target.value) || 0)}
                              disabled={mode === 'view'}
                              sx={{ width: 80 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              value={watch(`items.${index}.batch_number`)}
                              onChange={(e) => setValue(`items.${index}.batch_number`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 100 }}
                            />
                          </TableCell>
                          <TableCell>
                            <Select
                              size="small"
                              value={watch(`items.${index}.quality_status`) || ''}
                              onChange={(e) => setValue(`items.${index}.quality_status`, e.target.value)}
                              disabled={mode === 'view'}
                              sx={{ width: 100 }}
                            >
                              {qualityStatusOptions.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                  {option.label}
                                </MenuItem>
                              ))}
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ₹{(watch(`items.${index}.total_amount`) || 0).toFixed(2)}
                            </Typography>
                          </TableCell>
                          {mode !== 'view' && (
                            <TableCell>
                              <IconButton
                                onClick={() => removeItem(index)}
                                size="small"
                                color="error"
                              >
                                <Remove />
                              </IconButton>
                            </TableCell>
                          )}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Notes */}
                <Grid container spacing={2} mb={3}>
                  <Grid size={12}>
                    <TextField
                      label="Notes"
                      {...control.register('notes')}
                      fullWidth
                      multiline
                      rows={3}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Total Amount */}
                <Box display="flex" justifyContent="flex-end" mb={3}>
                  <Typography variant="h6">
                    Total Amount: ₹{(watch('total_amount') || 0).toFixed(2)}
                  </Typography>
                </Box>

                {/* Action Buttons */}
                {mode !== 'view' && (
                  <Box mt={3} display="flex" gap={2}>
                    <Button
                      type="submit"
                      variant="contained"
                      color="primary"
                      disabled={createMutation.isPending || updateMutation.isPending}
                      startIcon={<Save />}
                    >
                      {mode === 'edit' ? 'Update' : 'Create'} Voucher
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={handleCancel}
                      startIcon={<Cancel />}
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </form>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}