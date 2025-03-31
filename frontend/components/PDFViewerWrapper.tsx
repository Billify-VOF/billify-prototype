"use client";

import dynamic from "next/dynamic";
import React, { useState, useRef, useEffect } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PDFViewer = ({ filePath }: { filePath: string }) => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [scale, setScale] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [startPosition, setStartPosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  console.log('TEST LOG - PDFViewerWrapper rendered with:', filePath);

  useEffect(() => {
    const container = containerRef.current;

    if (!container) return;

    const handleWheelEvent = (e: WheelEvent) => {
      if (scale > 1) {
        e.preventDefault();
        e.stopPropagation();
        setPosition((prev) => ({
          x: prev.x - e.deltaX,
          y: prev.y - e.deltaY,
        }));
      }
    };

    container.addEventListener("wheel", handleWheelEvent, { passive: false });

    return () => container.removeEventListener("wheel", handleWheelEvent);
  }, [scale]);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setError(null);
  }

  const zoomIn = () => setScale((prev) => Math.min(prev + 0.2, 2));
  const zoomOut = () => setScale((prev) => Math.max(prev - 0.2, 0.5));
  const resetZoom = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (scale > 1 && e.button === 0) {
      // Left click
      setIsDragging(true);
      setStartPosition({
        x: e.clientX - position.x,
        y: e.clientY - position.y,
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && scale > 1) {
      const newX = e.clientX - startPosition.x;
      const newY = e.clientY - startPosition.y;

      setPosition({ x: newX, y: newY });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  if (error) {
    return (
      <div className="pdf-viewer rounded-lg border bg-red-50 p-4 text-red-600">
        <p>Failed to load PDF: {error}</p>
        <p className="mt-2 text-sm">File path: {filePath}</p>
      </div>
    );
  }

  // Use the Django backend URL (port 8000)
  const pdfUrl = `http://localhost:8000/api/invoices/preview/${filePath}/`;

  console.log("Attempting to load PDF from:", pdfUrl);

  return (
    <div className="pdf-viewer flex h-full flex-col overflow-hidden rounded-lg border bg-gray-50 p-4">
      {filePath && (
        <div className="mb-2 flex justify-end gap-2">
          <button
            onClick={zoomOut}
            className="rounded bg-gray-200 px-2 py-1 text-gray-700 hover:bg-gray-300"
            title="Zoom Out"
          >
            -
          </button>
          <button
            onClick={resetZoom}
            className="rounded bg-gray-200 px-2 py-1 text-gray-700 hover:bg-gray-300"
            title="Reset Zoom"
          >
            {Math.round(scale * 100)}%
          </button>
          <button
            onClick={zoomIn}
            className="rounded bg-gray-200 px-2 py-1 text-gray-700 hover:bg-gray-300"
            title="Zoom In"
          >
            +
          </button>
        </div>
      )}
      <div
        ref={containerRef}
        className={`relative flex flex-1 flex-col overflow-hidden ${!filePath && 'rounded-lg border border-dashed border-gray-300'}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          cursor: filePath ? (isDragging ? 'grabbing' : scale > 1 ? 'grab' : 'default') : 'default',
          touchAction: 'none',
          WebkitOverflowScrolling: 'touch',
        }}
      >
        {!filePath ? (
          <div className="p-4 text-center text-gray-500">
            <p className="text-sm">Click to select a PDF file</p>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-auto">
              <div
                style={{
                  transform: `translate(${position.x}px, ${position.y}px)`,
                  transition: isDragging ? 'none' : 'transform 0.1s',
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <Document
                  file={pdfUrl}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={(error) => {
                    console.error("PDF Load Error:", error);
                    setError(error.message);
                  }}
                  loading={<div className="text-gray-500">Loading PDF...</div>}
                >
                  <Page
                    pageNumber={pageNumber}
                    width={400}
                    scale={scale}
                    renderTextLayer={true}
                    renderAnnotationLayer={true}
                    loading={
                      <div className="text-gray-500">Loading page...</div>
                    }
                  />
                </Document>
              </div>
            </div>
            {numPages && numPages > 1 && (
              <div className="flex flex-shrink-0 items-center justify-between border-t border-gray-200 bg-white p-4">
                <button
                  onClick={() => setPageNumber((prev) => Math.max(prev - 1, 1))}
                  disabled={pageNumber <= 1}
                  className="rounded bg-blue-600 px-3 py-1 text-white disabled:opacity-50"
                >
                  Previous
                </button>
                <span>
                  Page {pageNumber} of {numPages}
                </span>
                <button
                  onClick={() => setPageNumber((prev) => Math.min(prev + 1, numPages))}
                  disabled={pageNumber >= numPages}
                  className="rounded bg-blue-600 px-3 py-1 text-white disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export const PDFViewerWrapper = dynamic(() => Promise.resolve(PDFViewer), {
  ssr: false,
  loading: () => (
    <div className="pdf-viewer rounded-lg border bg-gray-50 p-4">Loading PDF viewer...</div>
  ),
});
