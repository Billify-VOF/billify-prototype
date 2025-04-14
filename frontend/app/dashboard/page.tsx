'use client';
import React, { Suspense, useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { Dialog, DialogTrigger, DialogContent } from '@/components/ui/dialog';
import { Card, CardContent } from '@/components/ui/card';
import { InvoiceData, InvoiceUploadResult } from '@/components/InvoiceUploadResult';
import { dummySearchResults, SearchItemResult } from '@/components/types';
import { STATUS_COLORS, UploadStatus } from '@/components/definitions/invoice';
import { generatePontoOAuthUrl } from '@/lib/utils';
import { ArrowUpRight, ArrowDownLeft } from 'lucide-react';
import { Filter, Upload } from 'lucide-react';
import { useAuth } from '@/lib/auth/AuthContext';
import { getDisplayName } from '@/lib/utils/userUtils';

//import components
import LeftBar from '../../components/layout/LeftBar';
import TopBar from '../../components/layout/TopBar';
import CashFlowChart from '../../components/dashboard/CashFlowChart';
import AnalysisSection from '../../components/dashboard/AnalysisSection';
import { Ponto_Connect_2_Options } from '@/constants/api';

interface ExtendedInvoiceData extends InvoiceData {
  temp_file_path?: string;
}

const BillifyDashboard = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DashboardContent />
    </Suspense>
  );
};

const DashboardContent = () => {
  const searchParams = useSearchParams();
  const { user } = useAuth();
  // Add state for file upload
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [uploadedInvoiceData, setUploadedInvoiceData] = useState<any>(null);
  const [isFileTypeInvalid, setIsFileTypeInvalid] = useState<boolean>(false);
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [searchResult, setSearchResult] = useState<SearchItemResult[]>([]);
  const [invoiceData, setInvoiceData] = useState<ExtendedInvoiceData>();
  const [invoices, setInvoices] = useState<InvoiceData[]>([]);
  const [isFilterDropdownOpen, setIsFilterDropdownOpen] = useState<boolean>(false);
  const [filters, setFilters] = useState<{ dueDate?: string; status?: string }>({});
  const [nextPageUrl, setNextPageUrl] = useState<string | null>(null);

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

  const requestAccessToken = useCallback(async () => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    if (code && state && Ponto_Connect_2_Options.REDIRECT_URI) {
      const payload = new FormData();
      payload.append('code', code);
      payload.append('state', state);
      payload.append('redirect_uri', Ponto_Connect_2_Options.REDIRECT_URI!);
      try {
        await fetch('/api/ponto/auth', {
          method: 'POST',
          body: payload,
        });
      } catch (error) {
        console.log('Error while requesting access token: ', error);
      }
    }
  }, [searchParams]);

  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      requestAccessToken();
      hasFetched.current = true; // Prevents duplicate execution
    }
  }, [requestAccessToken]);

  // Fetch invoices with pagination
  const fetchInvoices = async (url: string | null) => {
    if (!url) return;

    try {
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
          "Access-Control-Allow-Origin": "*" 
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch invoices');
      }

      const data = await response.json();
      setInvoices((prev) => (url.includes('page=1') ? data.results : [...prev, ...data.results])); // Use `results` for invoices
      setNextPageUrl(data.next); // Update `next` link
    } catch (error) {
      console.error('Error fetching invoices:', error);
    }
  };

  useEffect(() => {
    const initialUrl = process.env.NEXT_PUBLIC_BACKEND_URL
      ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invoices/?page=1`
      : null;

    if (initialUrl) {
      fetchInvoices(initialUrl);
    } else {
      console.error('NEXT_PUBLIC_BACKEND_URL is not defined');
    }
  }, [filters]);

  // Ensure NEXT_PUBLIC_BACKEND_URL is defined during build
  if (!process.env.NEXT_PUBLIC_BACKEND_URL) {
    console.error(
      'Error: NEXT_PUBLIC_BACKEND_URL is not defined. Please set it in your environment variables.',
    );
  }

  // Load more invoices when scrolling
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight + 50 && nextPageUrl) {
      // Add a small buffer (50px) to ensure the fetch is triggered slightly before reaching the bottom
      fetchInvoices(nextPageUrl); // Fetch next page using `next` link
    }
  };

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
    formData.append('token', `Bearer ${localStorage.getItem('token') || ''}`);

    try {
      const response = await fetch('/api/invoices/upload', {
        method: 'POST',
        body: formData,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
          "Access-Control-Allow-Origin": "*" 
        },
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
    if (!invoiceData || !process.env.NEXT_PUBLIC_BACKEND_URL) {
      console.error('Missing invoice data or NEXT_PUBLIC_BACKEND_URL');
      return;
    }

    setUploadStatus('uploading');
    setErrorMessage('');
    invoiceData['invoice_id'] = uploadedInvoiceData['invoice']['id'];
    invoiceData['id'] = uploadedInvoiceData['invoice']['id'];
    invoiceData['due_date'] = uploadedInvoiceData['invoice']['date'];
    invoiceData['temp_file_path'] = uploadedInvoiceData['invoice']['file_path']; // No type error now

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invoices/${uploadedInvoiceData['invoice']['id']}/confirm/`,
        {
          method: 'POST',
          body: JSON.stringify(invoiceData),
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
            "Access-Control-Allow-Origin": "*" 
          },
        },
      );

      const data = await response.json();
      console.log('Server response:', data);

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to upload file');
      }

      setUploadStatus('success');
      setIsDialogOpen(false);

      const initialUrl = process.env.NEXT_PUBLIC_BACKEND_URL
        ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invoices/?page=1`
        : null;

      if (initialUrl) {
        fetchInvoices(initialUrl);
      }
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

  const percentData = {
    cashSaldo: 5.25,
    incomingInvoices: 1.25,
    outgoingInvoices: 5.25,
    btwSaldo: 1.25,
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
      <LeftBar onPontoConnect={onPontoConnect} />
      <div className="flex w-full flex-col">
        <TopBar onSearch={onSearch} searchResult={searchResult} />

        <div className="flex-1 p-5">
          <h1 className="text-2xl font-bold">
            {`Hi${getDisplayName(user) !== 'User' ? `, ${getDisplayName(user)}` : ''}!`}
          </h1>
          <h6 className="mt-3 text-gray-500">
            Here is the finance analysis for your business since January 2024
          </h6>

          {/* Top Metrics Grid */}
          <div className="my-3 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              title="Cash Saldo"
              value={financialData.cashSaldo}
              percent={percentData.cashSaldo}
            />
            <MetricCard
              title="Incoming Invoices"
              value={financialData.incomingInvoices}
              percent={percentData.incomingInvoices}
            />
            <MetricCard
              title="Outgoing Invoices"
              value={financialData.outgoingInvoices}
              percent={percentData.outgoingInvoices}
            />
            <MetricCard
              title="BTW Saldo"
              value={financialData.btwSaldo}
              percent={percentData.btwSaldo}
            />
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Cash Flow Analysis */}
            <Card>
              <CashFlowChart />
            </Card>

            {/* Outstanding Invoices */}
            <Card>
              <CardContent className="p-6">
                <div className="mb-6 flex items-center justify-between">
                  <h2 className="text-xl font-bold">Outstanding Invoices</h2>
                  <div className="flex gap-3">
                    {/* Combined Dialog */}
                    <Dialog open={isDialogOpen} onOpenChange={handleDialogOpenChange}>
                      <DialogTrigger asChild>
                        <div className="flex cursor-pointer items-center justify-center rounded-full bg-gray-200 p-2">
                          <Upload size={20} />
                        </div>
                      </DialogTrigger>
                      <DialogContent
                        className={`border bg-white shadow-xl ${
                          !uploadedInvoiceData
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
                    <div className="relative">
                      <div
                        className="flex cursor-pointer items-center justify-center rounded-full bg-gray-200 p-2"
                        onClick={() => setIsFilterDropdownOpen(!isFilterDropdownOpen)}
                      >
                        <Filter size={20} />
                      </div>
                      {isFilterDropdownOpen && (
                        <div className="absolute right-0 z-10 mt-2 w-64 rounded-lg border bg-white p-4 shadow-lg">
                          <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">
                              Due Date
                            </label>
                            <input
                              type="date"
                              className="mt-1 w-full rounded-lg border-gray-300 px-4 py-2"
                              value={filters.dueDate || ''}
                              onChange={(e) =>
                                setFilters((prev) => ({ ...prev, dueDate: e.target.value }))
                              }
                            />
                          </div>
                          <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700">
                              Status
                            </label>
                            <select
                              className="mt-1 w-full rounded-lg border-gray-300 px-4 py-2"
                              value={filters.status || ''}
                              onChange={(e) =>
                                setFilters((prev) => ({ ...prev, status: e.target.value }))
                              }
                            >
                              <option value="">All Statuses</option>
                              <option value="pending">Pending</option>
                              <option value="paid">Paid</option>
                              <option value="overdue">Overdue</option>
                            </select>
                          </div>
                          <div className="flex justify-between">
                            <button
                              className="rounded-lg bg-gray-100 px-4 py-2 text-sm"
                              onClick={() => {
                                setFilters({});
                                setIsFilterDropdownOpen(false);
                              }}
                            >
                              Clear
                            </button>
                            <button
                              className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white"
                              onClick={() => setIsFilterDropdownOpen(false)}
                            >
                              Apply
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div
                  className="space-y-4 overflow-auto" // Ensure the container is scrollable
                  onScroll={handleScroll}
                >
                  {invoices.map((invoice) => {
                    return (
                      <div
                        key={invoice.id}
                        className="flex items-center justify-between rounded-lg bg-gray-100 p-4"
                      >
                        <div className="flex flex-row items-center gap-x-5">
                          <input type="checkbox" className="h-5 w-5 rounded border-gray-300" />
                          <div className="flex flex-col">
                            <div className="font-semibold">Invoice #{invoice.invoice_number}</div>
                            <div className="text-sm text-gray-500">Due: {invoice.date}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span
                            className={`rounded-full px-3 py-1 font-medium ${
                              STATUS_COLORS[invoice.status as keyof typeof STATUS_COLORS]
                            }`}
                          >
                            ${invoice.amount}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="mt-5">
            <Card>
              <AnalysisSection />
            </Card>
          </div>
        </div>
      </div>

      {/* Main Content */}
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: number;
  percent: number;
}

const MetricCard = ({ title, value, percent }: MetricCardProps) => {
  const isPositive = title === 'Cash Saldo';
  const ArrowIcon = isPositive ? ArrowUpRight : ArrowDownLeft;
  const colorClass = isPositive ? 'text-green-500' : 'text-red-500';

  return (
    <Card>
      <CardContent className="px-6 py-3">
        <h3 className="text-sm text-gray-500">{title}</h3>
        <p className="text-2xl font-bold">€{value.toLocaleString('en-US')}</p>
        <div className="mt-3 flex flex-row items-center gap-x-2">
          <ArrowIcon size={20} className={colorClass} />
          <p className="text-gray-500">{percent}% since last month</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default BillifyDashboard;
