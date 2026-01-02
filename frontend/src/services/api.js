// API service for chatbot functionality
const API_BASE_URL = typeof process !== 'undefined' && process.env ? process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1' : 'http://localhost:8000/api/v1';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async chat(query, selectedText = null, contextOverride = false, sessionId = null) {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          selected_text: selectedText || null,
          context_override: contextOverride,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Chat API call failed:', error);
      throw error;
    }
  }

  // Streaming chat method for real-time responses
  async streamChat(query, selectedText = null, contextOverride = false, sessionId = null, onMessage, onError) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          selected_text: selectedText || null,
          context_override: contextOverride,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        if (onError) onError(error);
        throw error;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete JSON objects from the stream
          const lines = buffer.split('\n');
          buffer = lines.pop(); // Keep the incomplete line in the buffer

          for (const line of lines) {
            if (line.trim()) {
              try {
                const data = JSON.parse(line);
                if (data.type === 'content') {
                  onMessage(data.content);
                } else if (data.type === 'sources') {
                  onMessage({ sources: data.sources });
                } else if (data.type === 'error') {
                  const error = new Error(data.message);
                  if (onError) onError(error);
                  throw error;
                }
              } catch (e) {
                console.error('Error parsing stream data:', e);
                // Continue processing other lines
              }
            }
          }
        }

        // Process any remaining data in the buffer
        if (buffer.trim()) {
          try {
            const data = JSON.parse(buffer);
            if (data.type === 'content') {
              onMessage(data.content);
            } else if (data.type === 'sources') {
              onMessage({ sources: data.sources });
            }
          } catch (e) {
            console.error('Error parsing final stream data:', e);
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      console.error('Stream chat API call failed:', error);
      if (onError) onError(error);
      throw error;
    }
  }


  async ingest(sourcePath, chunkSize = 1000, overlap = 200) {
    try {
      const response = await fetch(`${this.baseUrl}/ingest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_path: sourcePath,
          chunk_size: chunkSize,
          overlap: overlap,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Ingest API call failed:', error);
      throw error;
    }
  }

  async health() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      return { status: 'unhealthy', details: { error: error.message } };
    }
  }

  async query(question, selectedText = null) {
    try {
      const response = await fetch(`${this.baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          selected_text: selectedText || null
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Query API call failed:', error);
      throw error;
    }
  }
}

export default new ApiService();