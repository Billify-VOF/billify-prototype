import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: Request) {
    try {
        const formData = await request.formData();
        
        // Forward the request to Django backend
        const response = await fetch(`${BACKEND_URL}/api/invoices/upload/`, {
            method: 'POST',
            body: formData,
            // Include any auth headers if needed
            headers: {
                // Remove the default content-type as it's set automatically with FormData
                ...(request.headers as any),
            },
        });

        const data = await response.json();

        // Forward the response status
        return NextResponse.json(data, { status: response.status });
        
    } catch (error) {
        console.error('Upload error:', error);
        return NextResponse.json({ 
            error: 'Failed to upload file',
            detail: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}