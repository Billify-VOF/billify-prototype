import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    console.log('API route hit - starting file upload process');

    const formData = await request.formData();
    const file = formData.get('file') as File;

    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const backendResponse = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invoices/upload/`,
      {
        method: 'POST',
        body: backendFormData,
      },
    );

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      // Handle backend error response
      return NextResponse.json(
        {
          status: 'error',
          message: data.message || 'Backend processing failed',
          detail: data.detail || 'Unknown error',
        },
        { status: backendResponse.status },
      );
    }

    // Format date properly to ensure it's in ISO format
    let formattedDate = 'N/A';
    if (data.invoice_data?.date) {
      // Try to parse and format the date properly
      try {
        // If it's a Python datetime or date object, it might be in YYYY-MM-DD format already
        // If not, we need to ensure it's a valid ISO string
        if (typeof data.invoice_data.date === 'string') {
          // If it's already in ISO format (YYYY-MM-DD), use it directly
          if (/^\d{4}-\d{2}-\d{2}$/.test(data.invoice_data.date)) {
            formattedDate = data.invoice_data.date;
          } else {
            // Otherwise, try to parse and re-format it
            const parsedDate = new Date(data.invoice_data.date);
            if (!isNaN(parsedDate.getTime())) {
              formattedDate = parsedDate.toISOString().split('T')[0]; // YYYY-MM-DD format
            }
          }
        }
      } catch (error) {
        console.warn('Error formatting date:', error);
      }
    }

    // Check if invoice_data exists to avoid TypeError
    if (!data.invoice_data) {
      return NextResponse.json({
        status: 'success',
        message: data.message,
        invoice: data.invoice,
        invoice_data: {
          invoice_number: 'Unknown',
          amount: '0.00',
          date: '',
          supplier_name: 'Unknown',
          urgency: null,
        },
      });
    }

    // Format the response to match the expected structure
    return NextResponse.json({
      status: 'success',
      message: data.message,
      invoice: data.invoice,
      invoice_data: {
        invoice_number: data.invoice_data.invoice_number,
        amount: data.invoice_data.amount,
        date: formattedDate,
        supplier_name: data.invoice_data.supplier_name,
        urgency: data.invoice_data.urgency,
      },
    });
  } catch (error) {
    console.error('Upload error details:', error);

    return NextResponse.json(
      {
        status: 'error',
        error: 'Failed to process file',
        detail: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 },
    );
  }
}
