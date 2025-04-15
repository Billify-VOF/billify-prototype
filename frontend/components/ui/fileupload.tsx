import React, { useState } from 'react';
//import axios from 'axios';
import { InvoiceUploadResult, UploadResult } from '@/components/invoice/InvoiceUploadResult';

const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<{
    status: 'idle' | 'uploading' | 'complete';
    result: UploadResult | null;
  }>({
    status: 'idle',
    result: null,
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploadState({ status: 'uploading', result: null });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/invoices/upload/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      setUploadState({
        status: 'complete',
        result: data,
      });

      // If successful, clear the file selection
      if (data.status === 'success') {
        setFile(null);
      }
    } catch (error) {
      console.log('Error: ', error);
      setUploadState({
        status: 'complete',
        result: {
          status: 'error',
          error: 'Upload failed',
          detail: 'An unexpected error occurred',
        },
      });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="file-input"
        />

        <button
          onClick={handleUpload}
          disabled={!file || uploadState.status === 'uploading'}
          className="btn btn-primary"
        >
          {uploadState.status === 'uploading' ? 'Uploading...' : 'Upload Invoice'}
        </button>
      </div>

      {uploadState.status === 'complete' && (
        <InvoiceUploadResult
          result={uploadState.result}
          onChange={() => setUploadState({ status: 'idle', result: null })}
        />
      )}
    </div>
  );
};

export default FileUpload;
