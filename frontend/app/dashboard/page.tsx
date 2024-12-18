"use client"
import React, { useState } from 'react'
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

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

const BillifyDashboard = () => {
    // Add state for file upload
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
    const [errorMessage, setErrorMessage] = useState<string>('');
    const [uploadedInvoiceData, setUploadedInvoiceData] = useState<any>(null);

    //Add file handling functions
    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (file && file.type === 'application/pdf') {
            setSelectedFile(file)
        } else {
            setUploadStatus('error')
            alert('Please select a PDF file')
        }
    }

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

        setUploadStatus('success');
        setSelectedFile(null);
        setUploadedInvoiceData(data.invoice_data);  // Store the received data

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
  
    return (
      <div className="flex min-h-screen">
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
                    <Dialog>
                      <DialogTrigger asChild>
                        <button className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white flex items-center gap-2">
                          <Upload className="w-4 h-4" />
                          Upload
                        </button>
                      </DialogTrigger>
                      <DialogContent>
                        <div className="space-y-4">
                          <h3 className="text-lg font-semibold">Upload Invoice</h3>
                          <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 text-center">
                            <input
                              type="file"
                              accept=".pdf"
                              onChange={handleFileSelect}
                              className="hidden"
                              id="file-upload"
                            />
                            <label
                              htmlFor="file-upload"
                              className="cursor-pointer text-blue-600 hover:text-blue-700"
                            >
                              {selectedFile ? selectedFile.name : 'Click to select a PDF file'}
                            </label>
                          </div>
                          
                          {/* Progress Bar */}
                          {uploadStatus === 'uploading' && (
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div 
                                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
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
                            >
                              Upload Invoice
                            </button>
                          )}
                          
                          {/* Use InvoiceUploadResult component for success/error states */}
                          {uploadStatus === 'success' && (
                            <InvoiceUploadResult 
                              result={{
                                status: 'success',
                                invoice_data: uploadedInvoiceData || {
                                  invoice_number: '',
                                  amount: '0',
                                  date: '',
                                  supplier_name: ''
                                }
                              }}
                              onClose={() => setUploadStatus('idle')}
                            />
                          )}
                          
                          {uploadStatus === 'error' && (
                            <InvoiceUploadResult 
                              result={{
                                status: 'error',
                                error: 'Upload failed',
                                detail: errorMessage
                              }}
                              onClose={() => setUploadStatus('idle')}
                            />
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                    
                  </div>
                </div>
                
                <div className="space-y-4">
                  {invoices.map(invoice => {
                    const statusColors = {
                      urgent: 'bg-red-50 text-red-700',
                      warning: 'bg-orange-50 text-orange-700',
                      safe: 'bg-green-50 text-green-700'
                    };
  
                    return (
                      <div key={invoice.id} className="flex items-center justify-between p-4 bg-white rounded-lg">
                        <div>
                          <div className="font-semibold">Invoice #{invoice.id}</div>
                          <div className="text-gray-500 text-sm">Due: {invoice.dueDate}</div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={`px-3 py-1 rounded-full ${statusColors[invoice.status]}`}>
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
  
  // Helper component for metric cards
  const MetricCard = ({ title, value }) => (
    <Card>
      <CardContent className="p-6">
        <h3 className="text-gray-500 text-sm mb-2">{title}</h3>
        <p className="text-2xl font-bold">€{value.toLocaleString()}</p>
      </CardContent>
    </Card>
  );
  
  export default BillifyDashboard;