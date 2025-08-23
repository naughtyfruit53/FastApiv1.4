// frontend/src/services/dispatchService.ts

import api from '../lib/api';

export interface DispatchOrderStatus {
  PENDING: 'pending';
  IN_TRANSIT: 'in_transit';
  DELIVERED: 'delivered';
  CANCELLED: 'cancelled';
}

export interface DispatchItemStatus {
  PENDING: 'pending';
  PACKED: 'packed';
  DISPATCHED: 'dispatched';
  DELIVERED: 'delivered';
}

export interface InstallationJobStatus {
  SCHEDULED: 'scheduled';
  IN_PROGRESS: 'in_progress';
  COMPLETED: 'completed';
  CANCELLED: 'cancelled';
  RESCHEDULED: 'rescheduled';
}

export interface InstallationJobPriority {
  LOW: 'low';
  MEDIUM: 'medium';
  HIGH: 'high';
  URGENT: 'urgent';
}

// DispatchItem interfaces
export interface DispatchItemBase {
  product_id: number;
  quantity: number;
  unit: string;
  description?: string | null;
  serial_numbers?: string | null;
  batch_numbers?: string | null;
  status: keyof DispatchItemStatus;
}

export interface DispatchItemCreate extends DispatchItemBase {}

export interface DispatchItemUpdate extends Partial<DispatchItemBase> {}

export interface DispatchItemInDB extends DispatchItemBase {
  id: number;
  dispatch_order_id: number;
  created_at: string;
  updated_at?: string | null;
}

// DispatchOrder interfaces
export interface DispatchOrderBase {
  customer_id: number;
  ticket_id?: number | null;
  status: keyof DispatchOrderStatus;
  dispatch_date?: string | null;
  expected_delivery_date?: string | null;
  actual_delivery_date?: string | null;
  delivery_address: string;
  delivery_contact_person?: string | null;
  delivery_contact_number?: string | null;
  notes?: string | null;
  tracking_number?: string | null;
  courier_name?: string | null;
}

export interface DispatchOrderCreate extends DispatchOrderBase {
  items: DispatchItemCreate[];
}

export interface DispatchOrderUpdate extends Partial<Omit<DispatchOrderBase, 'items'>> {}

export interface DispatchOrderInDB extends DispatchOrderBase {
  id: number;
  organization_id: number;
  order_number: string;
  created_by_id?: number | null;
  updated_by_id?: number | null;
  items: DispatchItemInDB[];
  created_at: string;
  updated_at?: string | null;
}

// InstallationJob interfaces
export interface InstallationJobBase {
  customer_id: number;
  ticket_id?: number | null;
  status: keyof InstallationJobStatus;
  priority: keyof InstallationJobPriority;
  scheduled_date?: string | null;
  estimated_duration_hours?: number | null;
  installation_address: string;
  contact_person?: string | null;
  contact_number?: string | null;
  installation_notes?: string | null;
  assigned_technician_id?: number | null;
}

export interface InstallationJobCreate extends InstallationJobBase {
  dispatch_order_id: number;
}

export interface InstallationJobUpdate extends Partial<InstallationJobBase> {
  actual_start_time?: string | null;
  actual_end_time?: string | null;
  completion_notes?: string | null;
  customer_feedback?: string | null;
  customer_rating?: number | null;
}

export interface InstallationJobInDB extends InstallationJobBase {
  id: number;
  organization_id: number;
  job_number: string;
  dispatch_order_id: number;
  actual_start_time?: string | null;
  actual_end_time?: string | null;
  completion_notes?: string | null;
  customer_feedback?: string | null;
  customer_rating?: number | null;
  created_by_id?: number | null;
  updated_by_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

// Installation Schedule Prompt
export interface InstallationSchedulePromptResponse {
  create_installation_schedule: boolean;
  installation_job?: InstallationJobCreate | null;
}

// Filter interfaces
export interface DispatchOrderFilter {
  status?: keyof DispatchOrderStatus;
  customer_id?: number;
  ticket_id?: number;
  from_date?: string;
  to_date?: string;
}

export interface InstallationJobFilter {
  status?: keyof InstallationJobStatus;
  priority?: keyof InstallationJobPriority;
  customer_id?: number;
  assigned_technician_id?: number;
  dispatch_order_id?: number;
  from_date?: string;
  to_date?: string;
}

export const dispatchService = {
  // Dispatch Order endpoints
  getDispatchOrders: async (params: {
    skip?: number;
    limit?: number;
    filter?: DispatchOrderFilter;
  } = {}): Promise<DispatchOrderInDB[]> => {
    try {
      console.log('[DispatchService] Fetching dispatch orders with params:', params);
      
      const queryParams = new URLSearchParams();
      if (params.skip) queryParams.append('skip', params.skip.toString());
      if (params.limit) queryParams.append('limit', params.limit.toString());
      
      // Add filter parameters
      if (params.filter) {
        Object.entries(params.filter).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, value.toString());
          }
        });
      }
      
      const response = await api.get(`/dispatch/orders?${queryParams.toString()}`);
      console.log('[DispatchService] Successfully fetched dispatch orders');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error fetching dispatch orders:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch dispatch orders');
    }
  },

  getDispatchOrder: async (orderId: number): Promise<DispatchOrderInDB> => {
    try {
      console.log('[DispatchService] Fetching dispatch order:', orderId);
      const response = await api.get(`/dispatch/orders/${orderId}`);
      console.log('[DispatchService] Successfully fetched dispatch order');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error fetching dispatch order:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch dispatch order');
    }
  },

  createDispatchOrder: async (orderData: DispatchOrderCreate): Promise<DispatchOrderInDB> => {
    try {
      console.log('[DispatchService] Creating dispatch order:', orderData);
      const response = await api.post('/dispatch/orders', orderData);
      console.log('[DispatchService] Successfully created dispatch order');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error creating dispatch order:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create dispatch order');
    }
  },

  updateDispatchOrder: async (orderId: number, orderData: DispatchOrderUpdate): Promise<DispatchOrderInDB> => {
    try {
      console.log('[DispatchService] Updating dispatch order:', orderId, orderData);
      const response = await api.put(`/dispatch/orders/${orderId}`, orderData);
      console.log('[DispatchService] Successfully updated dispatch order');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error updating dispatch order:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update dispatch order');
    }
  },

  deleteDispatchOrder: async (orderId: number): Promise<void> => {
    try {
      console.log('[DispatchService] Deleting dispatch order:', orderId);
      await api.delete(`/dispatch/orders/${orderId}`);
      console.log('[DispatchService] Successfully deleted dispatch order');
    } catch (error: any) {
      console.error('[DispatchService] Error deleting dispatch order:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete dispatch order');
    }
  },

  // Installation Job endpoints
  getInstallationJobs: async (params: {
    skip?: number;
    limit?: number;
    filter?: InstallationJobFilter;
  } = {}): Promise<InstallationJobInDB[]> => {
    try {
      console.log('[DispatchService] Fetching installation jobs with params:', params);
      
      const queryParams = new URLSearchParams();
      if (params.skip) queryParams.append('skip', params.skip.toString());
      if (params.limit) queryParams.append('limit', params.limit.toString());
      
      // Add filter parameters
      if (params.filter) {
        Object.entries(params.filter).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            queryParams.append(key, value.toString());
          }
        });
      }
      
      const response = await api.get(`/dispatch/installation-jobs?${queryParams.toString()}`);
      console.log('[DispatchService] Successfully fetched installation jobs');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error fetching installation jobs:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch installation jobs');
    }
  },

  getInstallationJob: async (jobId: number): Promise<InstallationJobInDB> => {
    try {
      console.log('[DispatchService] Fetching installation job:', jobId);
      const response = await api.get(`/dispatch/installation-jobs/${jobId}`);
      console.log('[DispatchService] Successfully fetched installation job');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error fetching installation job:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch installation job');
    }
  },

  createInstallationJob: async (jobData: InstallationJobCreate): Promise<InstallationJobInDB> => {
    try {
      console.log('[DispatchService] Creating installation job:', jobData);
      const response = await api.post('/dispatch/installation-jobs', jobData);
      console.log('[DispatchService] Successfully created installation job');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error creating installation job:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create installation job');
    }
  },

  updateInstallationJob: async (jobId: number, jobData: InstallationJobUpdate): Promise<InstallationJobInDB> => {
    try {
      console.log('[DispatchService] Updating installation job:', jobId, jobData);
      const response = await api.put(`/dispatch/installation-jobs/${jobId}`, jobData);
      console.log('[DispatchService] Successfully updated installation job');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error updating installation job:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update installation job');
    }
  },

  deleteInstallationJob: async (jobId: number): Promise<void> => {
    try {
      console.log('[DispatchService] Deleting installation job:', jobId);
      await api.delete(`/dispatch/installation-jobs/${jobId}`);
      console.log('[DispatchService] Successfully deleted installation job');
    } catch (error: any) {
      console.error('[DispatchService] Error deleting installation job:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete installation job');
    }
  },

  // Installation Schedule Prompt
  handleInstallationSchedulePrompt: async (responseData: InstallationSchedulePromptResponse): Promise<InstallationJobInDB> => {
    try {
      console.log('[DispatchService] Handling installation schedule prompt:', responseData);
      const response = await api.post('/dispatch/installation-schedule-prompt', responseData);
      console.log('[DispatchService] Successfully handled installation schedule prompt');
      return response.data;
    } catch (error: any) {
      console.error('[DispatchService] Error handling installation schedule prompt:', error);
      throw new Error(error.response?.data?.detail || 'Failed to handle installation schedule prompt');
    }
  }
};