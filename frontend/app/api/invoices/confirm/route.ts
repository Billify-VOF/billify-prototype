import { NextResponse } from 'next/server'

export async function POST(request: Request) {
    try {
        const json = await request.json()
        console.log("API route hit - starting invoice confirmation process", json);
        
        
        const backendResponse = await fetch('http://localhost:8000/api/invoices/confirm/', {
            method: 'POST',
            body: json,
            credentials: 'include'
        });

        const contentType = backendResponse.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            const data = await backendResponse.json();
            console.log('Backend response:', data);

            if (!backendResponse.ok) {
                throw new Error(data.detail || 'An unexpected error occurred while processing your invoice.');
            }

            return NextResponse.json({
                status: 'success',
                data: data,
            });
        } else {
            throw new Error('Unexpected response format');
        }

    } catch (error) {
        console.error('Upload error details:', {
            error: error instanceof Error ? error.message : 'Unknown error',
            stack: error instanceof Error ? error.stack : undefined
        });
        return NextResponse.json({ 
            status: 'error',
            error: 'Failed to process data',
            detail: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}
