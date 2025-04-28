import { useState, useRef } from 'react';
import { uploadPDF } from '../services/api';

export default function FileUpload({ onUpload }: { onUpload: (sessionId: string) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    const sessionId = `session-${Date.now()}`;
    try {
      await uploadPDF(file, sessionId);
      onUpload(sessionId);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  };

  return (
    <div className="upload-container">
      <input 
        type="file" 
        ref={fileInput}
        accept=".pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button onClick={handleUpload}>Upload PDF</button>
    </div>
  );
}