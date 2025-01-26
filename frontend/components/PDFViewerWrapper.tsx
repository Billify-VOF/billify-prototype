'use client';

import React, { useState, useRef, useEffect } from 'react';
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
  
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheelEvent = (e: WheelEvent) => {
      if (scale > 1) {
        e.preventDefault();
        e.stopPropagation();
        setPosition(prev => ({
          x: prev.x - e.deltaX,
          y: prev.y - e.deltaY
        }));
      }
    };

    container.addEventListener('wheel', handleWheelEvent, { passive: false });
    return () => container.removeEventListener('wheel', handleWheelEvent);
  }, [scale]);

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
    if (scale > 1 && e.button === 0) { // Left click
      setIsDragging(true);
      setStartPosition({
        x: e.clientX - position.x,
        y: e.clientY - position.y
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
    <div className="pdf-viewer h-full flex flex-col border rounded-lg bg-gray-50 p-4 overflow-hidden">
      {filePath && (
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
      )}
      <div 
        ref={containerRef}
        className={`flex-1 relative overflow-hidden flex flex-col ${!filePath && 'border border-dashed border-gray-300 rounded-lg'}`}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ 
          cursor: filePath ? (isDragging ? 'grabbing' : (scale > 1 ? 'grab' : 'default')) : 'default',
          touchAction: 'none',
          WebkitOverflowScrolling: 'touch'
        }}
      >
        {!filePath ? (
          <div className="text-gray-500 text-center p-4">
            <p className="text-sm">Click to select a PDF file</p>
          </div>
        ) : (
          <div 
            style={{ 
              transform: `translate(${position.x}px, ${position.y}px)`,
              transition: isDragging ? 'none' : 'transform 0.1s',
              width: '100%',
              height: '100%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center'
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
                width={400}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                loading={<div className="text-gray-500">Loading page...</div>}
              />
            </Document>
            {numPages && numPages > 1 && (
              <div className="flex-shrink-0 flex justify-between items-center p-4 bg-white bg-opacity-90">
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
        )}
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
