import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const json = await request.json();

    const backendResponse = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invoices/confirm/`,
      {
        method: "POST",
        body: json,
      }
    );

    const data = await backendResponse.json();

    return NextResponse.json({
      status: "success",
      data: data,
    });
  } catch (error) {
    console.error("Upload error details:", error);

    return NextResponse.json(
      {
        status: "error",
        error: "Failed to process data",
      },
      { status: 500 }
    );
  }
}
