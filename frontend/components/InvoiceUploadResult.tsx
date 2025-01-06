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
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4 max-w-[90vw] max-h-[80vh]">
          <div className="space-y-4">
            <div className="space-y-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">Invoice Number:</label>
                <input
                  type="text"
                  value={invoiceData.invoice_number}
                  onChange={(e) => setInvoiceData(prev => ({ ...prev, invoice_number: e.target.value }))}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Amount:</label>
                <div className="relative mt-1">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-500">€</span>
                  <input
                    type="text"
                    value={invoiceData.amount}
                    onChange={(e) => handleAmountChange(e.target.value)}
                    placeholder="0.00"
                    className="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Date:</label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      type="button"
                      variant={"outline"}
                      className={cn(
                        "w-full justify-start text-left font-normal border border-gray-300 hover:bg-gray-50",
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
          </div>
          <div>
            <PDFViewerWrapper filePath={result.invoice?.file_path || ''} />
          </div>
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
