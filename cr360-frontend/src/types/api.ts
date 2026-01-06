// API Types matching backend schemas

export interface ClarificationQuestion {
  question_id: string;
  question_text: string;
  options: string[];
}

export interface Clarification {
  question_id: string;
  selected_option: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  query: string;
  conversation_id?: string;
  conversation_history?: Message[];
  check_ambiguity?: boolean;
  session_id?: string;
  clarifications?: Clarification[];
}

export interface QueryResult {
  sql: string;
  explanation: string;
  results: Record<string, any>[];
  metrics_used: string[];
  visualization_hint: 'bar' | 'line' | 'table' | 'horizontal_bar' | 'pie' | 'scatter';
  row_count: number;
}

export interface ChatSuccessResponse {
  success: true;
  query: string;
  conversation_id: string;
  result: QueryResult;
  processing_time_ms: number;
}

export interface AmbiguityResponse {
  success: false;
  query: string;
  is_ambiguous: true;
  reasons: string[];
  suggestions: string[];
  questions: ClarificationQuestion[];
  timestamp: string;
}

export interface ErrorResponse {
  success: false;
  error: string;
  error_type: string;
  details?: any;
  timestamp: string;
}

export type ChatResponse = ChatSuccessResponse | AmbiguityResponse | ErrorResponse;

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  components: {
    database: 'up' | 'down';
    context_loader: 'up' | 'down';
    llm: 'configured' | 'not_configured';
  };
}
