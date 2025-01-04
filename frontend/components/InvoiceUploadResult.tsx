import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface InvoiceData {
  invoice_number: string;
  amount: string;
  date: string;
  supplier_name?: string;
}

export interface UploadResult {
  status: 'success' | 'error';
  message?: string;
  error?: string;
  detail?: string;
  file_path?: string;
  invoice_data?: InvoiceData;
}

interface Props {
  result: UploadResult | null;
  onClose: () => void;
}

export const InvoiceUploadResult: React.FC<Props> = ({ result, onClose }) => {
  if (!result) return null;

  if (result.status === 'error') {
    return (
      <Alert variant="destructive">
        <AlertTitle className="text-lg font-bold">Upload Failed</AlertTitle>
        <AlertDescription>
          {result.error}: {result.detail}
        </AlertDescription>
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
        >
          ×
        </button>
      </Alert>
    );
  }

  console.log('Upload Result Data:', result);

  return (
    <Alert className="bg-green-50">
      <AlertTitle className="text-lg font-bold">Upload Successful</AlertTitle>
      <AlertDescription>
        <div className="mt-4">
          <h4 className="font-semibold">Extracted Invoice Data:</h4>
          <div className="mt-2 space-y-2">
            <p><span className="font-medium">Invoice Number:</span> {result.invoice_data?.invoice_number || 'N/A'}</p>
            <p><span className="font-medium">Amount:</span> €{result.invoice_data?.amount || '0'}</p>
            <p><span className="font-medium">Date:</span> {result.invoice_data?.date || 'N/A'}</p>
            {result.invoice_data?.supplier_name && (
              <p><span className="font-medium">Supplier:</span> {result.invoice_data.supplier_name}</p>
            )}
          </div>
        </div>
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
        >
          ×
        </button>
      </AlertDescription>
    </Alert>
  );
};
