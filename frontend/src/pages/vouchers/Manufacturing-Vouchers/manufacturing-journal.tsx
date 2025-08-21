// @ts-nocheck
// Manufacturing vouchers are on hold and not included in current scope
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
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  Add, 
  Remove,
  Visibility, 
  Edit, 
  Delete, 
  Save,
  Cancel,
  ExpandMore
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../../lib/api';
import { getProducts } from '../../../services/masterService';
import VoucherContextMenu from '../../../components/VoucherContextMenu';
import VoucherHeaderActions from '../../../components/VoucherHeaderActions';

interface ManufacturingJournalFinishedProduct {
  product_id: number;
  quantity: number;
  unit: string;
  unit_cost: number;
  quality_grade?: string;
  batch_number?: string;
  lot_number?: string;
}

interface ManufacturingJournalMaterial {
  product_id: number;
  quantity_consumed: number;
  unit: string;
  unit_cost: number;
  batch_number?: string;
  lot_number?: string;
}

interface ManufacturingJournalByproduct {
  product_id: number;
  quantity: number;
  unit: string;
  unit_value: number;
  batch_number?: string;
  condition?: string;
}

interface ManufacturingJournalVoucher {
  id?: number;
  voucher_number: string;
  date: string;
  manufacturing_order_id: number;
  bom_id: number;
  date_of_manufacture: string;
  shift?: string;
  operator?: string;
  supervisor?: string;
  machine_used?: string;
  finished_quantity: number;
  scrap_quantity: number;
  rework_quantity: number;
  byproduct_quantity: number;
  material_cost: number;
  labor_cost: number;
  overhead_cost: number;
  quality_grade?: string;
  quality_remarks?: string;
  narration?: string;
  notes?: string;
  status: string;
  finished_products: ManufacturingJournalFinishedProduct[];
  consumed_materials: ManufacturingJournalMaterial[];
  byproducts: ManufacturingJournalByproduct[];
}

const defaultValues: Partial<ManufacturingJournalVoucher> = {
  voucher_number: '',
  date: new Date().toISOString().split('T')[0],
  date_of_manufacture: new Date().toISOString().split('T')[0],
  finished_quantity: 0,
  scrap_quantity: 0,
  rework_quantity: 0,
  byproduct_quantity: 0,
  material_cost: 0,
  labor_cost: 0,
  overhead_cost: 0,
  status: 'draft',
  finished_products: [],
  consumed_materials: [],
  byproducts: []
};

export default function ManufacturingJournalVoucher() {
  const router = useRouter();
  const [mode, setMode] = useState<'create' | 'edit' | 'view'>('create');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const queryClient = useQueryClient();

  const { control, handleSubmit, watch, setValue, reset, formState: { errors } } = useForm<ManufacturingJournalVoucher>({
    defaultValues
  });

  const {
    fields: finishedProductFields,
    append: appendFinishedProduct,
    remove: removeFinishedProduct
  } = useFieldArray({
    control,
    name: 'finished_products'
  });

  const {
    fields: materialFields,
    append: appendMaterial,
    remove: removeMaterial
  } = useFieldArray({
    control,
    name: 'consumed_materials'
  });

  const {
    fields: byproductFields,
    append: appendByproduct,
    remove: removeByproduct
  } = useFieldArray({
    control,
    name: 'byproducts'
  });

  // Fetch vouchers list
  const { data: voucherList, isLoading } = useQuery({
    queryKey: ['manufacturing-journal-vouchers'],
    queryFn: () => api.get('/manufacturing-journal-vouchers').then(res => res.data),
  });

  // Fetch manufacturing orders
  const { data: manufacturingOrders } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: () => api.get('/manufacturing-orders').then(res => res.data),
  });

  // Fetch BOMs
  const { data: bomList } = useQuery({
    queryKey: ['boms'],
    queryFn: () => api.get('/boms').then(res => res.data),
  });

  // Fetch products
  const { data: productList } = useQuery({
    queryKey: ['products'],
    queryFn: getProducts
  });

  // Fetch specific voucher
  const { data: voucherData, isFetching } = useQuery({
    queryKey: ['manufacturing-journal-voucher', selectedId],
    queryFn: () => api.get(`/manufacturing-journal-vouchers/${selectedId}`).then(res => res.data),
    enabled: !!selectedId
  });

  // Fetch next voucher number
  const { data: nextVoucherNumber, refetch: refetchNextNumber } = useQuery({
    queryKey: ['nextManufacturingJournalNumber'],
    queryFn: () => api.get('/manufacturing-journal-vouchers/next-number').then(res => res.data),
    enabled: mode === 'create',
  });

  const sortedVouchers = voucherList ? [...voucherList].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  ) : [];

  const latestVouchers = sortedVouchers.slice(0, 10);
  const productOptions = productList || [];
  const manufacturingOrderOptions = manufacturingOrders || [];
  const bomOptions = bomList || [];

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
    const materialCost = watch('material_cost') || 0;
    const laborCost = watch('labor_cost') || 0;
    const overheadCost = watch('overhead_cost') || 0;
    const totalCost = materialCost + laborCost + overheadCost;
    setValue('total_amount', totalCost);
  }, [watch('material_cost'), watch('labor_cost'), watch('overhead_cost'), setValue]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: ManufacturingJournalVoucher) => api.post('/manufacturing-journal-vouchers', data),
    onSuccess: async () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-journal-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue('voucher_number', newNextNumber);
    },
    onError: (error: any) => {
      console.error('Error creating manufacturing journal voucher:', error);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ManufacturingJournalVoucher }) => 
      api.put(`/manufacturing-journal-vouchers/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-journal-vouchers'] });
      setMode('create');
      setSelectedId(null);
      reset(defaultValues);
    },
    onError: (error: any) => {
      console.error('Error updating manufacturing journal voucher:', error);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/manufacturing-journal-vouchers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manufacturing-journal-vouchers'] });
      if (selectedId) {
        setSelectedId(null);
        setMode('create');
        reset(defaultValues);
      }
    }
  });

  const onSubmit = (data: ManufacturingJournalVoucher) => {
    if (mode === 'edit' && selectedId) {
      updateMutation.mutate({ id: selectedId, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (voucher: ManufacturingJournalVoucher) => {
    setSelectedId(voucher.id!);
    setMode('edit');
  };

  const handleView = (voucher: ManufacturingJournalVoucher) => {
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
        Manufacturing Journal Vouchers
      </Typography>

      <Grid container spacing={3}>
        {/* Voucher List - Left Side */}
        <Grid size={12} md={5}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Vouchers</Typography>
                <VoucherHeaderActions 
                  onRefresh={() => queryClient.invalidateQueries({ queryKey: ['manufacturing-journal-vouchers'] })}
                />
              </Box>
              
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Voucher No.</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>MO No.</TableCell>
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
                        <TableCell>{voucher.manufacturing_order?.voucher_number}</TableCell>
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
                            voucherType="Manufacturing Journal"
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
                  {mode === 'create' && 'Create Manufacturing Journal Voucher'}
                  {mode === 'edit' && 'Edit Manufacturing Journal Voucher'}
                  {mode === 'view' && 'View Manufacturing Journal Voucher'}
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
                    <Autocomplete
                      options={manufacturingOrderOptions}
                      getOptionLabel={(option) => option.voucher_number || ''}
                      value={manufacturingOrderOptions.find(mo => mo.id === watch('manufacturing_order_id')) || null}
                      onChange={(_, newValue) => {
                        setValue('manufacturing_order_id', newValue?.id || 0);
                        if (newValue?.bom_id) {
                          setValue('bom_id', newValue.bom_id);
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Manufacturing Order" required />
                      )}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Autocomplete
                      options={bomOptions}
                      getOptionLabel={(option) => option.bom_name || ''}
                      value={bomOptions.find(bom => bom.id === watch('bom_id')) || null}
                      onChange={(_, newValue) => setValue('bom_id', newValue?.id || 0)}
                      renderInput={(params) => (
                        <TextField {...params} label="BOM" required />
                      )}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Date of Manufacture"
                      type="datetime-local"
                      {...control.register('date_of_manufacture')}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Shift"
                      {...control.register('shift')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Operator"
                      {...control.register('operator')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Supervisor"
                      {...control.register('supervisor')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Machine Used"
                      {...control.register('machine_used')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

                {/* Production Quantities */}
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Production Quantities</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid size={12} sm={3}>
                        <TextField
                          label="Finished Quantity"
                          type="number"
                          {...control.register('finished_quantity', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={12} sm={3}>
                        <TextField
                          label="Scrap Quantity"
                          type="number"
                          {...control.register('scrap_quantity', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={12} sm={3}>
                        <TextField
                          label="Rework Quantity"
                          type="number"
                          {...control.register('rework_quantity', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={12} sm={3}>
                        <TextField
                          label="Byproduct Quantity"
                          type="number"
                          {...control.register('byproduct_quantity', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

                {/* Cost Allocation */}
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="h6">Cost Allocation</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, sm: 4 }}>
                        <TextField
                          label="Material Cost"
                          type="number"
                          {...control.register('material_cost', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={{ xs: 12, sm: 4 }}>
                        <TextField
                          label="Labor Cost"
                          type="number"
                          {...control.register('labor_cost', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                      <Grid size={{ xs: 12, sm: 4 }}>
                        <TextField
                          label="Overhead Cost"
                          type="number"
                          {...control.register('overhead_cost', { valueAsNumber: true })}
                          fullWidth
                          disabled={mode === 'view'}
                        />
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

                {/* Quality Information */}
                <Grid container spacing={2} mt={2}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <TextField
                      label="Quality Grade"
                      {...control.register('quality_grade')}
                      fullWidth
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={12}>
                    <TextField
                      label="Quality Remarks"
                      {...control.register('quality_remarks')}
                      fullWidth
                      multiline
                      rows={2}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={12}>
                    <TextField
                      label="Narration"
                      {...control.register('narration')}
                      fullWidth
                      multiline
                      rows={3}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                  <Grid size={12}>
                    <TextField
                      label="Notes"
                      {...control.register('notes')}
                      fullWidth
                      multiline
                      rows={2}
                      disabled={mode === 'view'}
                    />
                  </Grid>
                </Grid>

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