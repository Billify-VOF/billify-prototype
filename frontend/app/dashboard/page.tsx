"use client"
import React, { useState, useEffect } from 'react'
import {
  Menu,
  Upload,
  Settings,
  Receipt,
  Wallet,
} from '@/components/ui/icons'
import { Dialog, DialogTrigger, DialogContent } from '@/components/ui/dialog'
import { Card, CardContent } from '@/components/ui/card'
import { InvoiceUploadResult } from '@/components/InvoiceUploadResult'
import SearchComponent from '@/components/SearchComponent'
import { dummySearchResults, SearchItemResult } from '@/components/types'
import SearchResultItem from '@/components/SearchResultItem'
import NotificationBell from '@/components/NotificationBell'

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';
type InvoiceStatus = 'urgent' | 'warning' | 'safe';

const statusColors: Record<InvoiceStatus, string> = {
  urgent: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  safe: 'bg-green-100 text-green-800'
};

const BillifyDashboard = () => {
    // Add state for file upload
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
    const [errorMessage, setErrorMessage] = useState<string>('');
    const [uploadedInvoiceData, setUploadedInvoiceData] = useState<any>(null);
    const [isFileTypeInvalid, setIsFileTypeInvalid] = useState<boolean>(false);
    const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
    const [searchResult, setSearchResult] = useState<SearchItemResult[]>([]);

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
      if (isDialogOpen && uploadedInvoiceData) {
        console.log('PARENT TEST - Rendering Dialog with uploadedInvoiceData:', uploadedInvoiceData);
      }
    }, [isDialogOpen, uploadedInvoiceData]);

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

    const uploadUrl = '/api/invoices/upload';  // Define URL separately
    console.log('Attempting upload to:', uploadUrl);  // Log the URL

    // Add function to handle file upload
    const handleUpload = async () => {
      if (!selectedFile) return;

      setUploadStatus('uploading');
      const formData = new FormData();
      formData.append('file', selectedFile);

      try {
        const response = await fetch(uploadUrl, {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });

        const data = await response.json();
        console.log('Server response:', data);

        if (!response.ok) {
          throw new Error(data.detail || data.error || 'Failed to upload file');
        }

        console.log('PARENT TEST - Upload successful, setting data:', data);
        setUploadStatus('success');
        setSelectedFile(null);
        setUploadedInvoiceData(data);  // Store the entire response
        setIsDialogOpen(true);  // Open the combined dialog

      } catch (error) {
        console.error('Upload error details:', error);
        setUploadStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Failed to upload file');
      }
    };

    // Sample data
    const financialData = {
      cashSaldo: 25000,
      incomingInvoices: 15000,
      outgoingInvoices: 8000,
      btwSaldo: 3500
    };
  
    const invoices = [
      { id: 1, amount: 1200, dueDate: '2024-12-01', status: 'urgent' },
      { id: 2, amount: 800, dueDate: '2024-12-10', status: 'warning' },
      { id: 3, amount: 2500, dueDate: '2024-12-25', status: 'safe' }
    ];

    const onSearch = async (query: string) => {
      // Make API call to search for query
      // const response = await fetch(`/api/search?q=${query}`);
      // const data = await response.json();
      // setSearchResult(data);

      setSearchResult([...dummySearchResults]);
    }
  
    return (
      <div className="flex min-h-screen bg-gray-50">
        {/* Left Sidebar */}
        <div className="w-20 bg-white border-r border-gray-200 flex flex-col items-center py-6">
          {/* Logo */}
          <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center text-white text-xl font-bold mb-8">
            B
          </div>
          {/* Navigation Icons */}
          <div className="space-y-6">
            <Menu className="w-6 h-6 text-gray-400" />
            <Receipt className="w-6 h-6 text-gray-400" />
            <Wallet className="w-6 h-6 text-gray-400" />
            <Settings className="w-6 h-6 text-gray-400" />
          </div>
        </div>
  
        {/* Main Content */}
        <div className="flex-1 bg-gray-50 p-8">

        <div className='bg-gray-50  my-2 mb-2 flex justify-between items-center'>
          {/* Top Search Bar */}
            <SearchComponent
              onSearch={onSearch}
              renderItem={(item) => {
                return (
                  <SearchResultItem
                    item={item}
                    onClick={() => {}}
                  />
                );
              }}
              results={searchResult}
            />
          {/* Notification Widget */}
            <NotificationBell className="w-fit" />
          </div>
          
          {/* Top Metrics Grid */}
          <div className="grid grid-cols-4 gap-6 mb-6">
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
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">Cash Flow Analysis</h2>
                  <div className="text-blue-600">↗</div>
                </div>
                <div className="h-64 flex items-center justify-center text-gray-400">
                  Chart Area
                </div>
              </CardContent>
            </Card>
  
            {/* Outstanding Invoices */}
            <Card>
              <CardContent className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">Outstanding Invoices</h2>
                  <div className="flex gap-3">
                    <button className="px-4 py-2 text-sm rounded-lg bg-gray-100">
                      Filter
                    </button>
                    {/* Combined Dialog */}
                    <Dialog open={isDialogOpen} onOpenChange={handleDialogOpenChange}>
                      <DialogTrigger asChild>
                        <button 
                          className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white flex items-center gap-2"
                          disabled={isDialogOpen}
                        >
                          <Upload className="w-4 h-4" />
                          Upload
                        </button>
                      </DialogTrigger>
                      <DialogContent 
                        className={`bg-white border shadow-xl ${
                          !uploadedInvoiceData 
                            ? (selectedFile ? 'w-[300px] h-[180px] p-3' : 'w-[300px] h-[140px] p-3')
                            : 'w-[1000px] h-[600px] p-6'
                        } resize-none overflow-auto`}
                        onInteractOutside={(e) => e.preventDefault()} // Prevent closing on outside clicks
                      >
                        {!uploadedInvoiceData && (
                          <div className="space-y-4">
                            <h2 className="text-lg font-semibold mb-2">Upload Invoice</h2>
                            <div className={`border-2 ${isFileTypeInvalid ? 'border-red-500' : 'border-dashed border-gray-200'} rounded-lg p-4 text-center`}>
                              <input
                                type="file"
                                accept=".pdf"
                                onChange={handleFileSelect}
                                className="hidden"
                                id="file-upload"
                              />
                              <label
                                htmlFor="file-upload"
                                className="cursor-pointer text-blue-600 hover:text-blue-700 block truncate max-w-[250px] mx-auto"
                              >
                                {selectedFile ? selectedFile.name : 'Click to select a PDF file'}
                              </label>
                            </div>
                            
                            {/* Progress Bar */}
                            {uploadStatus === 'uploading' && (
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                  style={{ width: '100%', animation: 'progress 1s ease-in-out infinite' }}
                                />
                              </div>
                            )}
                            
                            {selectedFile && uploadStatus === 'idle' && (
                              <button
                                onClick={handleUpload}
                                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                disabled={(uploadStatus as UploadStatus) === 'uploading'}
                                type="button"
                                aria-label="Upload Invoice"
                              >
                                Upload Invoice
                              </button>
                            )}
                            {uploadStatus === 'error' && errorMessage && (
                              <p className="text-red-600 text-sm mt-2">{errorMessage}</p>
                            )}
                          </div>
                        )}
                        {uploadedInvoiceData && (
                          <div className="h-full flex flex-col">
                            <h2 className="text-lg font-semibold mb-4">Invoice Preview</h2>
                            <div className="flex-1 flex gap-6 overflow-hidden">
                              <InvoiceUploadResult result={uploadedInvoiceData} />
                            </div>
                            <button
                              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 mt-4"
                              disabled={uploadStatus === 'uploading'}
                              type="button"
                              aria-label="Confirm Upload"
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
                  {invoices.map(invoice => {
                    return (
                      <div key={invoice.id} className="flex items-center justify-between p-4 bg-white rounded-lg">
                        <div>
                          <div className="font-semibold">Invoice #{invoice.id}</div>
                          <div className="text-gray-500 text-sm">Due: {invoice.dueDate}</div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={`px-3 py-1 rounded-full ${statusColors[invoice.status as InvoiceStatus]}`}>
                            €{invoice.amount}
                          </span>
                          <input 
                            type="checkbox" 
                            className="h-5 w-5 rounded border-gray-300"
                          />
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
        <h3 className="text-gray-500 text-sm mb-2">{title}</h3>
        <p className="text-2xl font-bold">€{value.toLocaleString('en-US')}</p>
      </CardContent>
    </Card>
  );
  
  export default BillifyDashboard;
