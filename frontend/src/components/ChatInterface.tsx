import { useState, useEffect, useRef } from 'react';
import { chatWithAuthor } from '..//services/api';

type Message = {
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
};

export default function ChatInterface({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage: Message = {
      sender: 'user',
      text: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await chatWithAuthor(sessionId, input);
      const aiMessage: Message = {
        sender: 'ai',
        text: response.reply,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        sender: 'ai',
        text: "Sorry, I couldn't process your request.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            <div className="message-content">
              <span className="sender">{msg.sender === 'user' ? 'You' : 'Author'}</span>
              <p>{msg.text}</p>
              <small>{msg.timestamp.toLocaleTimeString()}</small>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask the author..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}