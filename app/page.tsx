'use client';
import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      alert(`Uploaded ${file.name}! Extracted text: ${data.text.slice(0, 50)}...`);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-6">Chat with Authors</h1>
      <form onSubmit={handleUpload} className="space-y-4">
        <input 
          type="file" 
          accept=".pdf,.txt" 
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="border p-2"
        />
        <button 
          type="submit" 
          disabled={isLoading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
        >
          {isLoading ? 'Processing...' : 'Upload Book'}
        </button>
      </form>
    </main>
  );
}