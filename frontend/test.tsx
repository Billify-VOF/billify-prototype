'use client';
import React, { useState, useEffect } from 'react';
import { Menu, Upload, Settings, Receipt, Wallet, Unlock } from '@/components/ui/icons';
import { Dialog, DialogTrigger, DialogContent } from '@/components/ui/dialog';
import { Card, CardContent } from '@/components/ui/card';
import { InvoiceData, InvoiceUploadResult } from '@/components/InvoiceUploadResult';
import SearchComponent from '@/components/SearchComponent';
import { dummySearchResults, SearchItemResult } from '@/components/types';
import SearchResultItem from '@/components/SearchResultItem';
import NotificationBell from '@/components/NotificationBell';
import { INVOICES_DATA, STATUS_COLORS, UploadStatus } from '@/components/definitions/invoice';
import { generatePontoOAuthUrl } from '@/lib/utils';

//import components
import LeftBar from './components/leftBar';
import TopBar from './components/topBar';

const BillifyDashboard = () => {
  // Add state for file upload
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [uploadedInvoiceData, setUploadedInvoiceData] = useState<any>(null);
  const [isFileTypeInvalid, setIsFileTypeInvalid] = useState<boolean>(false);
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [searchResult, setSearchResult] = useState<SearchItemResult[]>([]);
  const [invoiceData, setInvoiceData] = useState<InvoiceData>();

  // Reset all states when dialog is closed
  const handleDialogOpenChange = (open: boolean) => {
    setIsDialogOpen(open);
    if (!open) {
      // Reset all states when dialog is closed
      setSelectedFile(null);
      setUploadStatus('idle');
      setErrorMessage('');
      setUploadedInvoiceData(null);
      setIsFileTypeInvalid(false);
    }
  };

  useEffect(() => {
    if (!isDialogOpen) {
      setUploadedInvoiceData(null);
    }
  }, [isDialogOpen]);

  //Add file handling functions
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (uploadedInvoiceData) {
      alert('You cannot select a new file while previewing an invoice.');
      return;
    }

    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf' || file.size > 5 * 1024 * 1024) {
        setUploadStatus('error');
        alert('Please select a valid PDF file smaller than 5MB.');
        return;
      }
      setSelectedFile(file);
      setIsFileTypeInvalid(false);
    } else {
      setUploadStatus('error');
      setIsFileTypeInvalid(true);
      alert('Please select a PDF file');
    }
  };

  // Add function to handle file upload
  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus('uploading');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/invoices/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log('Server response:', data);

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to upload file');
      }

      console.log('PARENT TEST - Upload successful, setting data:', data);
      setUploadStatus('success');
      setSelectedFile(null);
      setUploadedInvoiceData(data); // Store the entire response
      setIsDialogOpen(true); // Open the combined dialog
    } catch (error) {
      console.error('Upload error details:', error);
      setUploadStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Failed to upload file');
    }
  };

  // Add function to handle file upload
  const confirmUpload = async () => {
    if (!invoiceData) return;
    setUploadStatus('uploading');
    setErrorMessage('');

    try {
      const response = await fetch('/api/invoices/confirm', {
        method: 'POST',
        body: JSON.stringify(invoiceData),
      });

      const data = await response.json();
      console.log('Server response:', data);

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to upload file');
      }

      setUploadStatus('success');
      // Close the dialog or show success message
      setIsDialogOpen(false);
    } catch (error) {
      console.error('Upload error details:', error);
      setUploadStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Failed to confirm invoice');
    }
  };

  // Sample data
  const financialData = {
    cashSaldo: 25000,
    incomingInvoices: 15000,
    outgoingInvoices: 8000,
    btwSaldo: 3500,
  };

  const onSearch = async (query: string) => {
    // TODO: Implement search functionality
    setSearchResult([...dummySearchResults]);
    console.log('Search query: ', query);
  };

  const onPontoConnect = async () => {
    const oauthUrl = await generatePontoOAuthUrl();
    window.open(oauthUrl);
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Left Sidebar */}

      <LeftBar />

      {/* Main Content */}
      <div className="flex-1">
        <TopBar />

        <div className="my-2 flex items-center justify-between bg-gray-50">
         
          <SearchComponent
            onSearch={onSearch}
            renderItem={(item) => {
              return <SearchResultItem item={item} onClick={() => { }} />;
            }}
            results={searchResult}
          />
        
          <NotificationBell className="w-fit" />
        </div>

        {/* Top Metrics Grid */}
        <div className="mb-6 grid grid-cols-4 gap-6">
          <MetricCard title="Cash Saldo" value={financialData.cashSaldo} />
          <MetricCard title="Incoming Invoices" value={financialData.incomingInvoices} />
          <MetricCard title="Outgoing Invoices" value={financialData.outgoingInvoices} />
          <MetricCard title="BTW Saldo" value={financialData.btwSaldo} />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-2 gap-6">
          {/* Cash Flow Analysis */}
          <Card>
            <CardContent className="p-6">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-xl font-bold">Cash Flow Analysis</h2>
                <div className="text-blue-600">↗</div>
              </div>
              <div className="flex h-64 items-center justify-center text-gray-400">Chart Area</div>
            </CardContent>
          </Card>

          {/* Outstanding Invoices */}
          <Card>
            <CardContent className="p-6">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-xl font-bold">Outstanding Invoices</h2>
                <div className="flex gap-3">
                  <button className="rounded-lg bg-gray-100 px-4 py-2 text-sm">Filter</button>
                  {/* Combined Dialog */}
                  <Dialog open={isDialogOpen} onOpenChange={handleDialogOpenChange}>
                    <DialogTrigger asChild>
                      <button
                        className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white"
                        disabled={isDialogOpen}
                      >
                        <Upload className="h-4 w-4" />
                        Upload
                      </button>
                    </DialogTrigger>
                    <DialogContent
                      className={`border bg-white shadow-xl ${!uploadedInvoiceData
                        ? selectedFile
                          ? 'h-[180px] w-[300px] p-3'
                          : 'h-[140px] w-[300px] p-3'
                        : 'h-[600px] w-[1000px] p-6'
                        } resize-none overflow-auto`}
                      onInteractOutside={(e) => e.preventDefault()} // Prevent closing on outside clicks
                    >
                      {!uploadedInvoiceData && (
                        <div className="space-y-4">
                          <h2 className="mb-2 text-lg font-semibold">Upload Invoice</h2>
                          <div
                            className={`border-2 ${isFileTypeInvalid ? 'border-red-500' : 'border-dashed border-gray-200'} rounded-lg p-4 text-center`}
                          >
                            <input
                              type="file"
                              accept=".pdf"
                              onChange={handleFileSelect}
                              className="hidden"
                              id="file-upload"
                            />
                            <label
                              htmlFor="file-upload"
                              className="mx-auto block max-w-[250px] cursor-pointer truncate text-blue-600 hover:text-blue-700"
                            >
                              {selectedFile ? selectedFile.name : 'Click to select a PDF file'}
                            </label>
                          </div>

                          {/* Progress Bar */}
                          {uploadStatus === 'uploading' && (
                            <div className="h-2 w-full rounded-full bg-gray-200">
                              <div
                                className="h-2 rounded-full bg-blue-600 transition-all duration-300"
                                style={{
                                  width: '100%',
                                  animation: 'progress 1s ease-in-out infinite',
                                }}
                              />
                            </div>
                          )}

                          {selectedFile && uploadStatus === 'idle' && (
                            <button
                              onClick={handleUpload}
                              className="w-full rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                              disabled={(uploadStatus as UploadStatus) === 'uploading'}
                              type="button"
                              aria-label="Upload Invoice"
                            >
                              Upload Invoice
                            </button>
                          )}
                          {uploadStatus === 'error' && errorMessage && (
                            <p className="mt-2 text-sm text-red-600">{errorMessage}</p>
                          )}
                        </div>
                      )}
                      {uploadedInvoiceData && (
                        <div className="flex h-full flex-col">
                          <h2 className="mb-4 text-lg font-semibold">Invoice Preview</h2>
                          <div className="flex flex-1 gap-6 overflow-hidden">
                            <InvoiceUploadResult
                              result={uploadedInvoiceData}
                              onChange={(invoiceData) => {
                                setInvoiceData(invoiceData);
                              }}
                            />
                          </div>
                          <button
                            className="mt-4 w-full rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700"
                            disabled={uploadStatus === 'uploading' || !invoiceData}
                            type="button"
                            aria-label="Confirm Upload"
                            onClick={confirmUpload}
                          >
                            Confirm Upload
                          </button>
                        </div>
                      )}
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              <div className="space-y-4">
                {INVOICES_DATA.map((invoice) => {
                  return (
                    <div
                      key={invoice.invoice_number}
                      className="flex items-center justify-between rounded-lg bg-white p-4"
                    >
                      <div>
                        <div className="font-semibold">Invoice #{invoice.invoice_number}</div>
                        <div className="text-sm text-gray-500">Due: {invoice.date}</div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className={`rounded-full px-3 py-1 ${STATUS_COLORS[invoice.status]}`}>
                          €{invoice.amount}
                        </span>
                        <input type="checkbox" className="h-5 w-5 rounded border-gray-300" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: number;
}

const MetricCard = ({ title, value }: MetricCardProps) => (
  <Card>
    <CardContent className="p-6">
      <h3 className="mb-2 text-sm text-gray-500">{title}</h3>
      <p className="text-2xl font-bold">€{value.toLocaleString('en-US')}</p>
    </CardContent>
  </Card>
);

export default BillifyDashboard;
