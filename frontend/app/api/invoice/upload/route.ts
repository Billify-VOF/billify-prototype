import { NextResponse } from 'next/server'

export async function POST(request: Request) {
    try {
        console.log('API route hit - starting file upload process')
        
        const formData = await request.formData();
        const file = formData.get('file') as File;

        // Create a new FormData to send to backend
        const backendFormData = new FormData();
        backendFormData.append('file', file);

        // Forward to Django backend
        const backendResponse = await fetch('http://localhost:8000/api/invoice/upload', {
            method: 'POST',
            body: backendFormData,
            credentials: 'include'
        });

        const data = await backendResponse.json();
        console.log('Backend response:', data);

        if (!backendResponse.ok) {
            throw new Error(data.detail || 'Backend processing failed');
        }

        // Return the backend response
        return NextResponse.json(data);

    } catch (error) {
        console.error('Upload error details:', {
            error: error instanceof Error ? error.message : 'Unknown error',
            stack: error instanceof Error ? error.stack : undefined
        });
        return NextResponse.json({ 
            success: false,
            error: 'Failed to process file',
            detail: error instanceof Error ? error.message : 'Unknown error'
        }, { status: 500 });
    }
}