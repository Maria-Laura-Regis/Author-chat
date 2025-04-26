import { useState, useRef } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [sessionId] = useState(`session-${Date.now()}`);
  const [messages, setMessages] = useState<Array<{sender: string, text: string}>>([]);
  const [input, setInput] = useState('');
  const fileInput = useRef<HTMLInputElement>(null);

  const uploadPDF = async () => {
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      const res = await axios.post('http://localhost:5000/upload', formData);
      setMessages(prev => [...prev, 
        { sender: 'system', text: `Uploaded ${file.name} (${res.data.pages} pages)` }
      ]);
    } catch (err) {
      setMessages(prev => [...prev, 
        { sender: 'error', text: 'Upload failed' }
      ]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    setInput('');
    
    try {
      const res = await axios.post('http://localhost:5000/chat', {
        session_id: sessionId,
        message: input
      });
      setMessages(prev => [...prev, { sender: 'ai', text: res.data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'error', text: 'Chat failed' }]);
    }
  };

  return (
    <div className="app">
      <h1>Chat with Authors</h1>
      
      <div className="upload-section">
        <input 
          type="file" 
          ref={fileInput}
          onChange={e => setFile(e.target.files?.[0] || null)} 
          accept=".pdf"
        />
        <button onClick={uploadPDF}>Upload PDF</button>
      </div>
      
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask the author..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;