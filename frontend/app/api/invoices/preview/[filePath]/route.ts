import { NextRequest, NextResponse } from 'next/server';

export async function GET(_: NextRequest, { params }: { params: { filePath: string } }) {
  try {
    const filePath = params.filePath;
    console.log('Fetching PDF preview for:', filePath);

    // Forward the request to the Django backend
    const response = await fetch(`http://localhost:8000/api/invoices/preview/${filePath}`, {
      credentials: 'include',
      headers: {
        Accept: 'application/pdf',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      console.error('PDF fetch failed:', response.status, await response.text());
      throw new Error('Failed to fetch PDF file');
    }

    // Get the PDF file as a blob
    const blob = await response.blob();
    console.log('PDF blob received:', blob.size, 'bytes');

    // Return the PDF with appropriate headers
    return new NextResponse(blob, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `inline; filename="${filePath}"`,
      },
    });
  } catch (error) {
    console.error('Error fetching PDF:', error);
    return NextResponse.json({ error: 'Failed to fetch PDF file' }, { status: 500 });
  }
}
