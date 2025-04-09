import { BACKEND_API_URL } from '@/constants/api';
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {

    const formData = await request.formData();

    const backendResponse = await fetch(
      `${BACKEND_API_URL}/api/ponto/login/`,
      {
        method: 'POST',
        body: formData,
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

    // Format the response to match the expected structure
    return NextResponse.json({
      status: 'success',
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      expires_in: data.expires_in,
    });
  } catch (error) {
    console.error('Request error details:', error);

    return NextResponse.json(
      {
        status: 'error',
        error: 'Failed to request initial token',
        detail: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 },
    );
  }
}
