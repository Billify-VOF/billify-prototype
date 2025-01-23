"use client"

import React, { useState, useEffect } from 'react';
import { PDFViewerWrapper } from './PDFViewerWrapper';
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { DayPicker } from "react-day-picker";
import "react-day-picker/dist/style.css";

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
  const [open, setOpen] = useState(false);
  
  // Log whenever component renders
  console.log('Current date state:', date);

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

  useEffect(() => {
    // Log whenever date changes
    console.log('Date state changed to:', date);
  }, [date]);

  useEffect(() => {
    console.log('InvoiceData state changed:', invoiceData);
  }, [invoiceData]);

  console.log('Popover open state:', open);

  const handleAmountChange = (value: string) => {
    const regex = /^\d*\.?\d{0,2}$/;
    if (regex.test(value) || value === '') {
      setInvoiceData(prev => ({ ...prev, amount: value }));
    }
  };

  const handleDateSelect = (newDate: Date | undefined) => {
    if (newDate) {
      // Log before updating state
      console.log('Selecting new date:', newDate);
      setDate(newDate);
      setInvoiceData(prev => {
        const formattedDate = format(newDate, 'yyyy-MM-dd');
        // Log the formatted date
        console.log('Formatted date:', formattedDate);
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
              onChange={(e) => handleAmountChange(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Date:</label>
            <Popover 
              open={open} 
              onOpenChange={(isOpen) => {
                console.log('Popover state changing to:', isOpen);
                setOpen(isOpen);  // Simplify this to always update
              }}
              modal={true}  // Make it modal to prevent outside interference
            >
              <PopoverTrigger asChild>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-full justify-start text-left font-normal border border-gray-300 hover:bg-gray-50 mt-1",
                    !date && "text-muted-foreground"
                  )}
                  onClick={() => {
                    console.log('Button clicked, setting open to true');
                    setOpen(true);
                  }}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {date ? format(date, "PPP") : <span>Pick a date</span>}
                </Button>
              </PopoverTrigger>
              <PopoverContent 
                className="w-auto p-0 bg-white" 
                align="start"
                side="bottom"
                sideOffset={5}
                onEscapeKeyDown={(e) => {
                  // Allow Escape to close
                  setOpen(false);
                }}
                onPointerDownOutside={(e) => {
                  // Allow clicking outside to close
                  setOpen(false);
                }}
                onFocusOutside={(e) => {
                  // Allow focus loss to close
                  setOpen(false);
                }}
                onInteractOutside={(e) => {
                  // Allow outside interaction to close
                  setOpen(false);
                }}
              >
                <div className="p-0" onClick={(e) => e.stopPropagation()}>
                  <DayPicker
                    mode="single"
                    selected={date}
                    onSelect={(selectedDate) => {
                      console.log('DayPicker onSelect triggered', selectedDate);
                      if (selectedDate) {
                        handleDateSelect(selectedDate);
                        setOpen(false);  // Close the popover after selection
                      }
                    }}
                    defaultMonth={date || new Date()}
                    className="p-3"
                    showOutsideDays={true}
                    fixedWeeks={true}
                    captionLayout="dropdown"
                    disabled={{
                      before: new Date(1900, 0, 1),
                      after: new Date(2100, 11, 31)
                    }}
                    modifiersClassNames={{
                      selected: 'bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground',
                      today: 'bg-accent text-accent-foreground hover:bg-accent hover:text-accent-foreground'
                    }}
                    required
                  />
                </div>
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
