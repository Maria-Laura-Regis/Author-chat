import axios from 'axios';

const API_URL = 'http://localhost:5000';

interface ChatResponse {
  reply: string;
  success?: boolean;
  error?: string;
}

export const uploadPDF = (file: File, sessionId: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);
  return axios.post(`${API_URL}/upload`, formData);
};

export const chatWithAuthor = async (sessionId: string, message: string): Promise<ChatResponse> => {
  try {
    const response = await axios.post(`${API_URL}/chat`, { 
      session_id: sessionId, 
      message 
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      return {
        reply: error.response?.data?.error || "Network error occurred",
        success: false
      };
    }
    return {
      reply: "An unexpected error occurred",
      success: false
    };
  }
};