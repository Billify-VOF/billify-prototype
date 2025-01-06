'use client';

import React, { useState, useRef } from 'react';
import { Document, Page } from 'react-pdf';
import { pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import dynamic from 'next/dynamic';

// Initialize PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

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
  
  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setError(null);
  }

  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 2));
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5));
  const resetZoom = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (scale > 1) {
      setIsDragging(true);
      setStartPosition({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && containerRef.current) {
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
      <div className="pdf-viewer border rounded-lg bg-red-50 p-4 text-red-600">
        <p>Failed to load PDF: {error}</p>
        <p className="text-sm mt-2">File path: {filePath}</p>
      </div>
    );
  }

  // Use the Django backend URL (port 8000)
  const pdfUrl = `http://localhost:8000/api/invoices/preview/${filePath}/`;
  console.log('Attempting to load PDF from:', pdfUrl);

  return (
    <div className="pdf-viewer border rounded-lg bg-gray-50 p-4">
      <div className="flex justify-end gap-2 mb-2">
        <button
          onClick={zoomOut}
          className="px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          title="Zoom Out"
        >
          -
        </button>
        <button
          onClick={resetZoom}
          className="px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          title="Reset Zoom"
        >
          {Math.round(scale * 100)}%
        </button>
        <button
          onClick={zoomIn}
          className="px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          title="Zoom In"
        >
          +
        </button>
      </div>
      <div 
        ref={containerRef}
        className="h-[400px] overflow-hidden relative"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default' }}
      >
        <div 
          style={{ 
            transform: `translate(${position.x}px, ${position.y}px)`,
            transition: isDragging ? 'none' : 'transform 0.1s',
          }}
        >
          <Document
            file={pdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(error) => {
              console.error('PDF Load Error:', error);
              setError(error.message);
            }}
            loading={<div className="text-gray-500">Loading PDF...</div>}
          >
            <Page 
              pageNumber={pageNumber} 
              width={300}
              scale={scale}
              renderTextLayer={false}
              renderAnnotationLayer={false}
              loading={<div className="text-gray-500">Loading page...</div>}
            />
          </Document>
          {numPages && numPages > 1 && (
            <div className="flex justify-between items-center mt-4">
              <button
                onClick={() => setPageNumber(prev => Math.max(prev - 1, 1))}
                disabled={pageNumber <= 1}
                className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span>
                Page {pageNumber} of {numPages}
              </span>
              <button
                onClick={() => setPageNumber(prev => Math.min(prev + 1, numPages))}
                disabled={pageNumber >= numPages}
                className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const PDFViewerWrapper = dynamic(
  () => Promise.resolve(PDFViewer),
  {
    ssr: false,
    loading: () => <div className="pdf-viewer border rounded-lg bg-gray-50 p-4">Loading PDF viewer...</div>
  }
); 