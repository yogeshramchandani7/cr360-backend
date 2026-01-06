"""
Chat API Routes

Endpoints for natural language querying and conversation
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import uuid
import time
from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    QueryResult,
    AmbiguityResponse,
    ErrorResponse
)
from app.query.text_to_sql import get_text_to_sql_engine
from app.utils.logger import get_logger
from app.utils.exceptions import (
    AmbiguousQueryError,
    SQLGenerationError,
    SQLValidationError,
    SQLExecutionError
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        200: {"model": ChatResponse},
        400: {"model": AmbiguityResponse},
        500: {"model": ErrorResponse}
    },
    summary="Process natural language query",
    description="Convert natural language to SQL, execute, and return results"
)
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Process a natural language query and return results

    Args:
        request: Chat request with query and optional conversation history

    Returns:
        ChatResponse with query results or error

    Raises:
        HTTPException: For various error conditions
    """
    start_time = time.time()

    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())

    logger.info(
        "chat_request_received",
        query=request.query,
        conversation_id=conversation_id,
        has_history=request.conversation_history is not None
    )

    try:
        # Get Text-to-SQL engine
        engine = get_text_to_sql_engine()

        # Convert conversation history to simple dict format
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {
                    'user': msg.content if msg.role == 'user' else '',
                    'assistant': msg.content if msg.role == 'assistant' else ''
                }
                for msg in request.conversation_history
            ]

        # NEW: Augment query with clarifications if provided
        query_to_process = request.query
        should_check_ambiguity = request.check_ambiguity

        if request.clarifications:
            logger.info(
                "processing_query_with_clarifications",
                conversation_id=conversation_id,
                clarification_count=len(request.clarifications)
            )

            # Get LLM client for query augmentation
            from app.llm.gemini_client import get_gemini_client
            llm_client = get_gemini_client()

            # Convert Pydantic models to dicts
            clarification_dicts = [
                {
                    'question_id': c.question_id,
                    'selected_option': c.selected_option
                }
                for c in request.clarifications
            ]

            # Augment the query
            query_to_process = llm_client.augment_query_with_clarifications(
                request.query,
                clarification_dicts
            )

            # Skip ambiguity check for clarified queries
            should_check_ambiguity = False

        # Process query
        result = await engine.process_query(
            natural_language_query=query_to_process,
            conversation_history=conversation_history,
            check_ambiguity=should_check_ambiguity
        )

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Build response
        response = ChatResponse(
            success=True,
            query=request.query,
            conversation_id=conversation_id,
            result=QueryResult(
                sql=result['sql'],
                explanation=result['explanation'],
                results=result['results'],
                metrics_used=result['metrics_used'],
                visualization_hint=result['visualization_hint'],
                row_count=len(result['results'])
            ),
            processing_time_ms=processing_time_ms
        )

        logger.info(
            "chat_request_completed",
            conversation_id=conversation_id,
            rows_returned=len(result['results']),
            processing_time_ms=processing_time_ms
        )

        return response.model_dump()

    except AmbiguousQueryError as e:
        logger.warning(
            "ambiguous_query",
            conversation_id=conversation_id,
            suggestions=e.options,
            questions_count=len(e.questions)
        )

        response = AmbiguityResponse(
            query=request.query,
            reasons=[str(e)],
            suggestions=e.options or [],
            questions=e.questions or []
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.model_dump(mode='json')
        )

    except (SQLGenerationError, SQLValidationError) as e:
        logger.error(
            "sql_error",
            conversation_id=conversation_id,
            error=str(e),
            error_type=type(e).__name__
        )

        response = ErrorResponse(
            error=str(e),
            error_type=type(e).__name__
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.model_dump(mode='json')
        )

    except SQLExecutionError as e:
        logger.error(
            "sql_execution_error",
            conversation_id=conversation_id,
            error=str(e)
        )

        response = ErrorResponse(
            error="Failed to execute query. Please try rephrasing your question.",
            error_type="SQLExecutionError",
            details={"original_error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.model_dump(mode='json')
        )

    except Exception as e:
        logger.error(
            "unexpected_error",
            conversation_id=conversation_id,
            error=str(e)
        )

        response = ErrorResponse(
            error="An unexpected error occurred. Please try again.",
            error_type="InternalError",
            details={"error": str(e)}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response.model_dump(mode='json')
        )
