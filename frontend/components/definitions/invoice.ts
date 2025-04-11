/**
 * Enum representing the urgency levels for invoices
 * OVERDUE: Past due date requiring immediate action
 * CRITICAL: Requires attention within 24 hours
 * HIGH: Important, handle within a week
 * MEDIUM: Moderate importance, handle within two weeks
 * LOW: Low priority, can be handled when convenient
 */

export enum UrgencyLevel {
  OVERDUE = 'OVERDUE',
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

export type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';
export type InvoiceStatus = 'overdue' | 'pending' | 'paid';

export interface Urgency {
  level: UrgencyLevel;
  display_name: string;
  color_code: string;
  is_manual?: boolean;
}

export const URGENCY_COLORS = {
  overdue: '#8B0000',
  critical: '#FF0000',
  high: '#FFA500',
  medium: '#FFD700',
  low: '#008000',
  default: '#D3D3D3',
};

export const URGENCY_LEVELS: Urgency[] = [
  {
    level: UrgencyLevel.OVERDUE,
    display_name: 'Overdue',
    color_code: URGENCY_COLORS.overdue,
  },
  {
    level: UrgencyLevel.CRITICAL,
    display_name: 'Critical',
    color_code: URGENCY_COLORS.critical,
  },
  {
    level: UrgencyLevel.HIGH,
    display_name: 'High',
    color_code: URGENCY_COLORS.high,
  },
  {
    level: UrgencyLevel.MEDIUM,
    display_name: 'Medium',
    color_code: URGENCY_COLORS.medium,
  },
  {
    level: UrgencyLevel.LOW,
    display_name: 'Low',
    color_code: URGENCY_COLORS.low,
  },
];

export const DEFAULT_URGENCY: Urgency = {
  level: UrgencyLevel.LOW,
  display_name: 'Not Available',
  color_code: '#D3D3D3',
  is_manual: false,
};

export const STATUS_COLORS: Record<InvoiceStatus, string> = {
  overdue: 'text-green-600',
  pending: 'text-red-500',
  paid: 'text-yellow-600',
};

export interface Invoice {
  invoice_id: number;
  invoice_number: string;
  amount: number;
  date: string;
  supplier_name: string;
  status: InvoiceStatus;
  urgency: Urgency;
  change?: string;
}
