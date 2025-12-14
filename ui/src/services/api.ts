/**
 * API Service for Nepal Government RAG Assistant
 * Handles all backend API communications
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface QueryRequest {
  query: string;
  top_k?: number;
  use_hybrid?: boolean;
  use_reranker?: boolean;
  session_id?: string;
}

export interface QueryResponse {
  answer: string;
  sources?: Array<{
    content: string;
    metadata: Record<string, any>;
    score: number;
  }>;
  session_id: string;
}

export interface UploadResponse {
  message: string;
  filename: string;
  chunks: number;
}

export interface StatsResponse {
  total_documents: number;
  total_chunks?: number;
  last_updated?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
}

/**
 * Query the RAG system
 */
export async function queryRAG(request: QueryRequest): Promise<QueryResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: request.query,
        top_k: request.top_k || 5,
        use_hybrid: request.use_hybrid !== false,
        use_reranker: request.use_reranker || false,
        session_id: request.session_id || generateSessionId(),
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error querying RAG:', error);
    throw error;
  }
}

/**
 * Upload a document
 */
export async function uploadDocument(file: File): Promise<UploadResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
}

/**
 * Get system statistics
 */
export async function getStats(): Promise<StatsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`);

    if (!response.ok) {
      throw new Error(`Failed to get stats: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting stats:', error);
    throw error;
  }
}

/**
 * Check backend health
 */
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
}

/**
 * Get list of documents
 */
export async function getDocuments(): Promise<any[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/documents`);

    if (!response.ok) {
      throw new Error(`Failed to get documents: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting documents:', error);
    throw error;
  }
}

/**
 * Generate a session ID
 */
function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Store session ID in localStorage
 */
export function getOrCreateSessionId(): string {
  let sessionId = localStorage.getItem('nepal_rag_session_id');
  
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('nepal_rag_session_id', sessionId);
  }
  
  return sessionId;
}
