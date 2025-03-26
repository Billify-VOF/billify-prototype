export enum UrgencyLevel {
  OVERDUE = "OVERDUE",
  CRITICAL = "CRITICAL",
  HIGH = "HIGH",
  MEDIUM = "MEDIUM",
  LOW = "LOW",
}

export type UploadStatus = "idle" | "uploading" | "success" | "error";
export type InvoiceStatus = "overdue" | "pending" | "paid";

export interface Urgency {
  level: UrgencyLevel;
  display_name: string;
  color_code: string;
  is_manual?: boolean;
}

export const URGENCY_LEVELS: Urgency[] = [
  {
    level: UrgencyLevel.OVERDUE,
    display_name: "Overdue",
    color_code: "#8B0000",
  },
  {
    level: UrgencyLevel.CRITICAL,
    display_name: "Critical",
    color_code: "#FF0000",
  },
  { level: UrgencyLevel.HIGH, display_name: "High", color_code: "#FFA500" },
  { level: UrgencyLevel.MEDIUM, display_name: "Medium", color_code: "#FFD700" },
  { level: UrgencyLevel.LOW, display_name: "Low", color_code: "#008000" },
];

export const DEFAULT_URGENCY: Urgency = {
  level: "NA",
  display_name: "Not Available",
  color_code: "#D3D3D3",
  is_manual: false,
};

export const STATUS_COLORS: Record<InvoiceStatus, string> = {
  overdue: "bg-red-100 text-red-800",
  pending: "bg-yellow-100 text-yellow-800",
  paid: "bg-green-100 text-green-800",
};

export const INVOICES_DATA = [
  {
    invoice_id: 1,
    invoice_number: "INV-001",
    amount: "1000.00",
    date: "2025-03-10",
    supplier_name: "Supplier A",
    status: "pending",
    urgency: { ...URGENCY_LEVELS[0], is_manual: false },
  },
  {
    invoice_id: 2,
    invoice_number: "INV-002",
    amount: "500.00",
    date: "2025-03-15",
    supplier_name: "Supplier B",
    status: "paid",
    urgency: { ...URGENCY_LEVELS[1], is_manual: false },
  },
  {
    invoice_id: 3,
    invoice_number: "INV-003",
    amount: "750.00",
    date: "2025-03-20",
    supplier_name: "Supplier C",
    status: "overdue",
    urgency: { ...URGENCY_LEVELS[2], is_manual: true },
  },
];
