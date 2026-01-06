"""
API Schemas for Chat Endpoints

Request and response models for the chat interface
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime


class ClarificationQuestion(BaseModel):
    """A single clarification question with multiple choice options"""
    question_id: str = Field(
        ...,
        description="Unique identifier for this question (e.g., 'charge_off_type')",
        pattern=r'^[a-z_]+$'
    )
    question_text: str = Field(
        ...,
        description="The question to ask the user",
        min_length=5,
        max_length=200
    )
    options: List[str] = Field(
        ...,
        description="List of possible answers (2-5 options)",
        min_length=2,
        max_length=5
    )


class Clarification(BaseModel):
    """User's answer to a clarification question"""
    question_id: str = Field(
        ...,
        description="ID of the question being answered",
        pattern=r'^[a-z_]+$'
    )
    selected_option: str = Field(
        ...,
        description="The option selected by the user"
    )


class Message(BaseModel):
    """Single message in a conversation"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(
        ...,
        description="Natural language query from the user",
        min_length=1,
        max_length=1000,
        example="What is the total exposure for Auto loans in the Southeast region?"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for multi-turn conversations"
    )
    conversation_history: Optional[List[Message]] = Field(
        None,
        description="Previous conversation history (last N turns)"
    )
    check_ambiguity: bool = Field(
        True,
        description="Whether to check for query ambiguity before processing"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for tracking"
    )
    clarifications: Optional[List[Clarification]] = Field(
        None,
        description="Clarifications provided by user for an ambiguous query"
    )


class QueryResult(BaseModel):
    """Query result data"""
    sql: str = Field(..., description="Generated SQL query")
    explanation: str = Field(..., description="Plain English explanation of the query")
    results: List[Dict[str, Any]] = Field(..., description="Query results as list of rows")
    metrics_used: List[str] = Field(..., description="List of metrics used in the query")
    visualization_hint: str = Field(
        ...,
        description="Suggested visualization type (bar, line, table, etc.)"
    )
    row_count: int = Field(..., description="Number of rows returned")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    success: bool = Field(..., description="Whether the request was successful")
    query: str = Field(..., description="Original user query")
    conversation_id: str = Field(..., description="Conversation ID")
    result: Optional[QueryResult] = Field(None, description="Query result if successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    suggestions: Optional[List[str]] = Field(
        None,
        description="Suggestions for ambiguous queries"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="Processing time in milliseconds"
    )


class AmbiguityResponse(BaseModel):
    """Response for ambiguous queries"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    success: bool = Field(False, description="Always false for ambiguous queries")
    query: str = Field(..., description="Original user query")
    is_ambiguous: bool = Field(True, description="Always true for this response type")
    reasons: List[str] = Field(..., description="Reasons why the query is ambiguous")
    suggestions: List[str] = Field(..., description="Suggestions to clarify the query")
    questions: List[ClarificationQuestion] = Field(
        default_factory=list,
        description="Structured clarification questions with options"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    status: str = Field(..., description="Service status (healthy/unhealthy)")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    components: Dict[str, str] = Field(
        ...,
        description="Component health status"
    )
