import React, { useState } from 'react';
import axios from 'axios';

interface UploadState {
  progress: number;
  error: string | null;
  success: boolean;
}

const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>({
    progress: 0,
    error: null,
    success: false
  });

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Reset state when new file is selected
      setUploadState({ progress: 0, error: null, success: false });
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setUploadState(prev => ({ ...prev, error: 'Please select a file' }));
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/invoices/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 100)
          );
          setUploadState(prev => ({ ...prev, progress }));
        },
      });

      setUploadState(prev => ({ ...prev, success: true, error: null }));
      // Handle successful response
      console.log('Upload successful:', response.data);
    } catch (error) {
      setUploadState(prev => ({
        ...prev,
        error: 'Upload failed. Please try again.',
        success: false
      }));
      console.error('Upload error:', error);
    }
  };

  return (
    <div className="upload-container">
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="file-input"
      />
      
      <button 
        onClick={handleUpload}
        disabled={!file || uploadState.progress > 0}
        className="upload-button"
      >
        Upload Invoice
      </button>

      {/* Progress indicator */}
      {uploadState.progress > 0 && uploadState.progress < 100 && (
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${uploadState.progress}%` }}
          />
          <span>{uploadState.progress}%</span>
        </div>
      )}

      {/* Success message */}
      {uploadState.success && (
        <div className="success-message">
          File uploaded successfully!
        </div>
      )}

      {/* Error message */}
      {uploadState.error && (
        <div className="error-message">
          {uploadState.error}
        </div>
      )}
    </div>
  );
};

export default FileUpload;