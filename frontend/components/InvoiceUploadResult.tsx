import React, { useState } from 'react';
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
  const [editableData, setEditableData] = useState<InvoiceData | null>(result?.invoice_data || null);

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

  const handleInputChange = (field: keyof InvoiceData, value: string) => {
    setEditableData((prevData) => ({
      ...prevData,
      [field]: value,
    }));
  };

  const handleSave = () => {
    // Handle save logic here, e.g., send updated data to the backend
    console.log('Saved data:', editableData);
    onClose();
  };

  console.log('Upload Result Data:', result);

  return (
    <Alert className="bg-green-50">
      <AlertTitle className="text-lg font-bold">Upload Successful</AlertTitle>
      <AlertDescription>
        <div className="mt-4">
          <h4 className="font-semibold">Extracted Invoice Data:</h4>
          <div className="mt-2 space-y-2">
            <div>
              <label className="font-medium">Invoice Number:</label>
              <input
                type="text"
                value={editableData?.invoice_number || ''}
                onChange={(e) => handleInputChange('invoice_number', e.target.value)}
                className="ml-2 p-1 border rounded"
              />
            </div>
            <div>
              <label className="font-medium">Amount:</label>
              <input
                type="text"
                value={editableData?.amount || ''}
                onChange={(e) => handleInputChange('amount', e.target.value)}
                className="ml-2 p-1 border rounded"
              />
            </div>
            <div>
              <label className="font-medium">Date:</label>
              <input
                type="text"
                value={editableData?.date || ''}
                onChange={(e) => handleInputChange('date', e.target.value)}
                className="ml-2 p-1 border rounded"
              />
            </div>
            {editableData?.supplier_name && (
              <div>
                <label className="font-medium">Supplier:</label>
                <input
                  type="text"
                  value={editableData.supplier_name}
                  onChange={(e) => handleInputChange('supplier_name', e.target.value)}
                  className="ml-2 p-1 border rounded"
                />
              </div>
            )}
          </div>
        </div>
        <button
          onClick={handleSave}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Save
        </button>
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
