import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    console.log("API route hit - starting file upload process");

    const formData = await request.formData();
    const file = formData.get("file") as File;

    const backendFormData = new FormData();
    backendFormData.append("file", file);

    const backendResponse = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/invoices/upload/`,
      {
        method: "POST",
        body: backendFormData,
      }
    );

    const data = await backendResponse.json();

    // Format the response to match the expected structure
    return NextResponse.json({
      status: "success",
      message: data.message,
      invoice: data.invoice,
      invoice_data: {
        invoice_number: data.invoice_data.invoice_number,
        amount: data.invoice_data.amount,
        date: data.invoice_data.date || "N/A",
        supplier_name: data.invoice_data.supplier_name,
        urgency: data.invoice_data.urgency,
      },
    });
  } catch (error) {
    console.error("Upload error details:", error);

    return NextResponse.json(
      {
        status: "error",
        error: "Failed to process file",
        detail: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
