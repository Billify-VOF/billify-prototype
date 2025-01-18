"use client"

import React, { useState, useEffect } from 'react';
import { PDFViewerWrapper } from './PDFViewerWrapper';
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

interface InvoiceData {
  invoice_number: string;
  amount: string;
  date: string;
  supplier_name?: string;
}

interface Invoice {
  id: string;
  status: string;
  file_path: string;
  updated: boolean;
}

export interface UploadResult {
  status: 'success' | 'error';
  message?: string;
  error?: string;
  detail?: string;
  invoice?: Invoice;
  invoice_data?: InvoiceData;
}

interface Props {
  result: UploadResult;
}

export function InvoiceUploadResult({ result }: Props) {
  const [invoiceData, setInvoiceData] = useState<InvoiceData>({
    invoice_number: '',
    amount: '',
    date: '',
    supplier_name: ''
  });
  const [date, setDate] = useState<Date | undefined>(undefined);

  useEffect(() => {
    if (result?.invoice_data) {
      setInvoiceData({
        invoice_number: result.invoice_data.invoice_number || '',
        amount: result.invoice_data.amount || '',
        date: result.invoice_data.date || '',
        supplier_name: result.invoice_data.supplier_name || ''
      });
      if (result.invoice_data.date) {
        setDate(new Date(result.invoice_data.date));
      }
    }
  }, [result]);

  const handleAmountChange = (value: string) => {
    const regex = /^\d*\.?\d{0,2}$/;
    if (regex.test(value) || value === '') {
      setInvoiceData(prev => ({ ...prev, amount: value }));
    }
  };

  const handleDateSelect = (newDate: Date | undefined) => {
    if (newDate) {
      setDate(newDate);
      setInvoiceData(prev => {
        const formattedDate = format(newDate, 'yyyy-MM-dd');
        return {
          ...prev,
          date: formattedDate
        };
      });
    }
  };

  if (!result || !result.status) {
    return null;
  }

  if (result.status === 'success') {
    return (
      <div className="flex w-full h-full gap-6">
        <div className="w-1/3 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Invoice Number:</label>
            <input
              type="text"
              value={invoiceData.invoice_number}
              onChange={(e) => setInvoiceData({ ...invoiceData, invoice_number: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Amount:</label>
            <input
              type="text"
              value={invoiceData.amount}
              onChange={(e) => setInvoiceData({ ...invoiceData, amount: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date:</label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-full justify-start text-left font-normal border border-gray-300 hover:bg-gray-50 mt-1",
                    !date && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0 bg-white" align="start">
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={handleDateSelect}
                  initialFocus
                  className="rounded-md border"
                />
              </PopoverContent>
            </Popover>
          </div>
        </div>

        <div className="w-2/3 h-full">
          <PDFViewerWrapper filePath={result.invoice?.file_path || ''} />
        </div>
      </div>
    );
  }

  return (
    <div className="text-red-600">
      <p>Error: {result.error}</p>
      {result.detail && <p className="text-sm mt-1">{result.detail}</p>}
    </div>
  );
}
