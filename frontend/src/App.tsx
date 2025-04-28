import { useState } from 'react';
import FileUpload from './components/FileUpload/FileUpload';
import Chat from './components/ChatInterface';
import './App.css';

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  return (
    <div className="app-container">
      <header>
        <h1>Chat with Authors</h1>
        <p>Upload a book to chat with its author's style</p>
      </header>

      <main>
        {!sessionId ? (
          <FileUpload 
            onUploadSuccess={(id) => {
              setSessionId(id);
              setIsProcessing(false);
            }}
          />
        ) : (
          <Chat sessionId={sessionId} />
        )}
      </main>

      {isProcessing && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>Analyzing your document...</p>
        </div>
      )}
    </div>
  );
}