/**
 * API Client for CR360 Backend
 * Handles all communication with the FastAPI backend
 */

import { logger } from '../utils/logger';
import type {
  ChatRequest,
  ChatResponse,
  HealthStatus,
  Clarification,
} from '../types/api';

// Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    logger.info('API Client initialized', { baseUrl });
  }

  /**
   * Generic fetch wrapper with logging and error handling
   */
  private async fetch<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    logger.apiRequest(options.method || 'GET', url, options.body);

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      const data = await response.json();

      logger.apiResponse(url, response.status, data);

      // For chat endpoint, 400 responses can be valid (ambiguity, validation errors)
      // FastAPI wraps error responses in a "detail" field, so extract it
      if (!response.ok && endpoint === `/api/${API_VERSION}/chat`) {
        // Return the detail field which contains the actual response
        return (data.detail || data) as T;
      }

      if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return data as T;
    } catch (error) {
      logger.apiError(url, error);
      throw error;
    }
  }

  /**
   * Health check endpoint
   */
  async checkHealth(): Promise<HealthStatus> {
    logger.debug('Checking backend health');
    return this.fetch<HealthStatus>('/health');
  }

  /**
   * Main chat endpoint - send query and get results
   */
  async sendQuery(request: ChatRequest): Promise<ChatResponse> {
    logger.info('Sending query to backend', {
      query: request.query,
      conversationId: request.conversation_id,
      checkAmbiguity: request.check_ambiguity,
    });

    const response = await this.fetch<ChatResponse>(`/api/${API_VERSION}/chat`, {
      method: 'POST',
      body: JSON.stringify(request),
    });

    // Log the response type for debugging
    if (response.success) {
      logger.info('Query successful', {
        conversationId: response.conversation_id,
        rowCount: response.result.row_count,
        processingTimeMs: response.processing_time_ms,
        visualizationHint: response.result.visualization_hint,
      });
    } else {
      logger.warn('Query failed or ambiguous', {
        errorType: response.error_type,
        message: response.message,
      });
    }

    return response;
  }

  /**
   * Send a query with conversation history
   */
  async sendQueryWithHistory(
    query: string,
    conversationId?: string,
    conversationHistory?: ChatRequest['conversation_history'],
    checkAmbiguity: boolean = true,
    clarifications?: Clarification[]
  ): Promise<ChatResponse> {
    return this.sendQuery({
      query,
      conversation_id: conversationId,
      conversation_history: conversationHistory,
      check_ambiguity: checkAmbiguity,
      clarifications,
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
