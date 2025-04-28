import { useState, useRef } from 'react';
import { uploadPDF } from '../../services/api';
import '../../App.css';

export default function FileUpload({ onUploadSuccess }: { onUploadSuccess: (sessionId: string) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    const sessionId = `session-${Date.now()}`;
    
    try {
      await uploadPDF(file, sessionId);
      onUploadSuccess(sessionId);
    } catch (error) {
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="file-upload-container">
      <div 
        className="drop-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          setFile(e.dataTransfer.files[0]);
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        {file ? (
          <p>Selected: {file.name}</p>
        ) : (
          <p>Drag & drop a PDF here, or click to select</p>
        )}
        <input
          type="file"
          ref={fileInputRef}
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          hidden
        />
      </div>
      <button 
        onClick={handleUpload}
        disabled={!file || isUploading}
      >
        {isUploading ? 'Uploading...' : 'Start Chat'}
      </button>
    </div>
  );
}