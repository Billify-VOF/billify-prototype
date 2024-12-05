import { NextResponse } from 'next/server'

export async function POST(request: Request) {
    try {
        console.log('API route hit - starting file upload process')
        
        const formData = await request.formData();
        console.log('Form data received:', formData)
        const file = formData.get('file') as File;
        console.log('File extracted from form data:', file)

        // For testing, just log the file details
        console.log('Received file:', {
            name: file.name,
            size: file.size,
            type: file.type
        })

        // Simulate a delay
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Return a success response
        console.log('Sending success response')
        return NextResponse.json({ 
            success: true,
            message: 'File received successfully' 
        })
    } catch (error) {
        console.error('Upload error details:', {
            error: error instanceof Error ? error.message : 'Unknown error',
            stack: error instanceof Error ? error.stack : undefined
        })
        return NextResponse.json({ 
            success: false,
            message: 'Failed to upload file' 
        }, { status: 500 })
    }
}