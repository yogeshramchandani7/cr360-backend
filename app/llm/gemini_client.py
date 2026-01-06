"""
Gemini LLM Client for CR360

Handles all interactions with Google Gemini API for:
- Text-to-SQL generation
- Query understanding
- Insight generation
- Investigation hypothesis generation
"""

import google.generativeai as genai
from typing import Optional, Dict, Any, List
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import LLMError

logger = get_logger(__name__)


class GeminiClient:
    """Client for Google Gemini API interactions"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key (defaults to settings.GOOGLE_API_KEY)
            model_name: Model name (defaults to settings.LLM_MODEL)
            temperature: Sampling temperature (defaults to settings.LLM_TEMPERATURE)
            max_tokens: Max output tokens (defaults to settings.LLM_MAX_TOKENS)
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model_name = model_name or settings.LLM_MODEL
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS

        # Configure the API
        genai.configure(api_key=self.api_key)

        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens,
            }
        )

        logger.info(
            "gemini_client_initialized",
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Gemini

        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            **kwargs: Additional generation config overrides

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails
        """
        try:
            logger.info(
                "generating_llm_response",
                prompt_length=len(prompt),
                has_system_instruction=system_instruction is not None
            )

            # Build generation config with overrides
            generation_config = {
                'temperature': self.temperature,
                'max_output_tokens': self.max_tokens,
                **kwargs
            }

            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            else:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=generation_config
                )

            # Generate response
            response = model.generate_content(prompt)

            if not response or not response.text:
                raise LLMError("Empty response from Gemini API")

            logger.info(
                "llm_response_generated",
                response_length=len(response.text)
            )

            return response.text

        except Exception as e:
            logger.error("llm_generation_error", error=str(e))
            raise LLMError(f"Failed to generate response: {e}")

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text with additional context

        Args:
            prompt: User prompt
            context: Additional context (e.g., semantic model, conversation history)
            system_instruction: Optional system instruction
            **kwargs: Additional generation config overrides

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails
        """
        # Combine context and prompt
        full_prompt = f"""Context:
{context}

---

User Query:
{prompt}
"""

        return await self.generate(
            prompt=full_prompt,
            system_instruction=system_instruction,
            **kwargs
        )

    async def generate_sql(
        self,
        natural_language_query: str,
        semantic_context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL from natural language query

        Args:
            natural_language_query: User's natural language query
            semantic_context: YAML semantic model context
            conversation_history: Optional conversation history

        Returns:
            Dict with 'sql', 'explanation', and 'metrics_used'

        Raises:
            LLMError: If SQL generation fails
        """
        try:
            # Build system instruction with two-tier routing
            system_instruction = """You are a SQL expert for credit risk analytics with TWO-TIER query routing capability.

DATABASE SCHEMA (Two Tables):

1. `accounts` table - Account-level granular data (1,141 rows)
   - Use for: Breakdowns, GROUP BY queries, account filters, drill-downs
   - Primary key: (account_id, as_of_date)
   - Key columns: product_code, region_code, customer_segment, adjusted_eop_balance, days_past_due

2. `computed_metrics` table - Pre-aggregated portfolio metrics (8 rows, one per quarter)
   - Use for: Portfolio totals, complex ratios, pre-calculated metrics
   - Primary key: as_of_date
   - Key columns: total_outstanding_balance, delinquency_rate_30_plus, net_charge_off_rate, ecl_coverage_ratio

CRITICAL ROUTING RULES:

✅ Use `computed_metrics` when:
  - Query asks for "total", "overall", "portfolio-level" metric
  - Complex calculations like NCO rate, ECL coverage (annualization is error-prone)
  - No breakdown by product/region/segment needed
  - Example: "What is the total delinquency rate?"

✅ Use `accounts` when:
  - Query needs GROUP BY (by product, region, segment, vintage)
  - Account-level filters (credit score ranges, customer_id, DPD buckets)
  - Drill-downs and breakdowns
  - Example: "What is the delinquency rate BY PRODUCT?"

IMPORTANT SQL PATTERNS:

Pattern 1 - Portfolio Total (use computed_metrics):
```sql
SELECT delinquency_rate_30_plus
FROM computed_metrics
WHERE as_of_date = (SELECT MAX(as_of_date) FROM computed_metrics)
```

Pattern 2 - Breakdown by Dimension (use accounts):
```sql
SELECT
  product_code,
  SUM(CASE WHEN days_past_due >= 30 THEN adjusted_eop_balance ELSE 0 END) /
  NULLIF(SUM(adjusted_eop_balance), 0) * 100 as delinquency_rate
FROM accounts
WHERE as_of_date = (SELECT MAX(as_of_date) FROM accounts)
GROUP BY product_code
ORDER BY delinquency_rate DESC
```

Pattern 3 - Account-Level Query (use accounts):
```sql
SELECT account_id, customer_id, current_credit_score, adjusted_eop_balance
FROM accounts
WHERE product_code = 'AUTO' AND current_credit_score < 650
  AND as_of_date = (SELECT MAX(as_of_date) FROM accounts)
ORDER BY adjusted_eop_balance DESC
LIMIT 100
```

CRITICAL PostgreSQL constraints:
- If using GROUP BY, every non-aggregated column in SELECT/ORDER BY MUST be in GROUP BY
- For simple portfolio totals with no dimensions, use computed_metrics (no GROUP BY needed)
- For "latest" date filtering, use WHERE with MAX() subquery, NOT ORDER BY + LIMIT
- Always use NULLIF(SUM(denominator), 0) for rate calculations to avoid division by zero

NEVER calculate complex ratios from accounts table if available in computed_metrics.
ALWAYS validate which table to use before generating SQL.

Output format:
```sql
[Your SQL query here]
```

Explanation: [Brief explanation including which table you chose and why]

Metrics used: [List of metrics from semantic model]
"""

            # Build prompt with conversation history
            prompt_parts = []

            if conversation_history:
                prompt_parts.append("Previous conversation:")
                for turn in conversation_history[-3:]:  # Last 3 turns
                    prompt_parts.append(f"User: {turn.get('user', '')}")
                    prompt_parts.append(f"Assistant: {turn.get('assistant', '')}")
                prompt_parts.append("")

            prompt_parts.append(f"Current query: {natural_language_query}")

            prompt = "\n".join(prompt_parts)

            # Generate SQL
            response = await self.generate_with_context(
                prompt=prompt,
                context=semantic_context,
                system_instruction=system_instruction,
                temperature=0.1  # Low temperature for SQL generation
            )

            # Parse response
            sql, explanation, metrics = self._parse_sql_response(response)

            logger.info(
                "sql_generated",
                query_length=len(natural_language_query),
                sql_length=len(sql),
                metrics_count=len(metrics)
            )

            return {
                'sql': sql,
                'explanation': explanation,
                'metrics_used': metrics
            }

        except Exception as e:
            logger.error("sql_generation_error", error=str(e))
            raise LLMError(f"Failed to generate SQL: {e}")

    def _parse_sql_response(self, response: str) -> tuple[str, str, List[str]]:
        """
        Parse SQL generation response

        Args:
            response: Raw LLM response

        Returns:
            Tuple of (sql, explanation, metrics_used)
        """
        sql = ""
        explanation = ""
        metrics = []

        # Extract SQL from code blocks
        if "```sql" in response:
            sql_start = response.find("```sql") + 6
            sql_end = response.find("```", sql_start)
            sql = response[sql_start:sql_end].strip()
        elif "```" in response:
            sql_start = response.find("```") + 3
            sql_end = response.find("```", sql_start)
            sql = response[sql_start:sql_end].strip()

        # Extract explanation
        if "Explanation:" in response:
            exp_start = response.find("Explanation:") + 12
            exp_end = response.find("Metrics used:", exp_start)
            if exp_end == -1:
                exp_end = len(response)
            explanation = response[exp_start:exp_end].strip()

        # Extract metrics
        if "Metrics used:" in response:
            metrics_start = response.find("Metrics used:") + 13
            metrics_text = response[metrics_start:].strip()
            # Parse comma or newline separated list, handle bullet points (-, *)
            metrics = [m.strip().lstrip('-*').strip() for m in metrics_text.replace('\n', ',').split(',') if m.strip()]

        return sql, explanation, metrics

    async def detect_ambiguity(
        self,
        natural_language_query: str,
        semantic_context: str
    ) -> Dict[str, Any]:
        """
        Detect if a query is ambiguous and suggest clarifications

        Args:
            natural_language_query: User's query
            semantic_context: Semantic model context

        Returns:
            Dict with 'is_ambiguous', 'reasons', 'suggestions', and 'questions'
        """
        system_instruction = """You are an expert at detecting ambiguous queries in credit risk analytics.

Analyze the user's query and determine if it's ambiguous based on:
1. Multiple possible metric interpretations
2. Missing time period
3. Missing aggregation level (product, region, etc.)
4. Unclear comparison dimensions

Output format (IMPORTANT: Include BOTH old format for backward compatibility AND new structured questions):

Ambiguous: [Yes/No]

Reasons:
- [Reason 1]
- [Reason 2]

Suggestions:
- [Suggestion 1]
- [Suggestion 2]

Questions:
[
  {
    "question_id": "unique_id_1",
    "question_text": "What type of charge-off do you mean?",
    "options": ["Gross charge-off", "Net charge-off"]
  },
  {
    "question_id": "unique_id_2",
    "question_text": "Which time period?",
    "options": ["Latest quarter", "Q4 2024", "Q3 2024", "All quarters"]
  }
]

CRITICAL RULES FOR QUESTIONS:
1. question_id should be short, snake_case identifier (e.g., "charge_off_type", "time_period", "balance_type", "metric_type")
2. question_text should be a clear question ending with "?"
3. options should be 2-5 concrete choices the user can select
4. Each question should resolve ONE ambiguity
5. If query has multiple ambiguities, create multiple questions
6. Options should be mutually exclusive within each question
7. Use JSON array format exactly as shown above
8. Common question IDs to use:
   - charge_off_type: for gross vs net charge-off
   - balance_type: for outstanding vs original balance
   - time_period: for missing quarters/dates
   - metric_type: for unclear metric selection
   - aggregation_level: for product, region, account level
"""

        prompt = f"User query: {natural_language_query}"

        response = await self.generate_with_context(
            prompt=prompt,
            context=semantic_context,
            system_instruction=system_instruction,
            temperature=0.2
        )

        # Parse response using new method
        return self._parse_ambiguity_response(response)

    def _parse_ambiguity_response(self, response: str) -> Dict[str, Any]:
        """
        Parse ambiguity detection response

        Args:
            response: Raw LLM response

        Returns:
            Dict with 'is_ambiguous', 'reasons', 'suggestions', and 'questions'
        """
        import json
        import re

        is_ambiguous = "Ambiguous: Yes" in response
        reasons = []
        suggestions = []
        questions = []

        # Parse reasons (existing logic)
        if "Reasons:" in response:
            reasons_start = response.find("Reasons:") + 8
            # Find next section (Suggestions or Questions)
            reasons_end = response.find("Suggestions:", reasons_start)
            if reasons_end == -1:
                reasons_end = response.find("Questions:", reasons_start)
            if reasons_end == -1:
                reasons_end = len(response)
            reasons_text = response[reasons_start:reasons_end].strip()
            reasons = [r.strip('- ').strip() for r in reasons_text.split('\n') if r.strip()]

        # Parse suggestions (existing logic)
        if "Suggestions:" in response:
            suggestions_start = response.find("Suggestions:") + 12
            # Find next section (Questions)
            suggestions_end = response.find("Questions:", suggestions_start)
            if suggestions_end == -1:
                suggestions_end = len(response)
            suggestions_text = response[suggestions_start:suggestions_end].strip()
            suggestions = [s.strip('- ').strip() for s in suggestions_text.split('\n') if s.strip()]

        # Parse questions (NEW - robust JSON extraction)
        if "Questions:" in response:
            try:
                questions_start = response.find("Questions:") + 10
                questions_text = response[questions_start:].strip()

                # Extract JSON array (handle markdown code blocks)
                json_match = re.search(r'\[[\s\S]*\]', questions_text)
                if json_match:
                    json_str = json_match.group(0)
                    questions = json.loads(json_str)

                    # Validate question structure
                    for q in questions:
                        if not all(key in q for key in ['question_id', 'question_text', 'options']):
                            logger.warning(
                                "invalid_question_structure",
                                question=q
                            )
                            questions = []  # Fallback to empty if invalid
                            break
                        if not isinstance(q['options'], list) or len(q['options']) < 2:
                            logger.warning(
                                "invalid_question_options",
                                question_id=q.get('question_id')
                            )
                            questions = []
                            break
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(
                    "failed_to_parse_questions",
                    error=str(e),
                    questions_text=questions_text[:200] if 'questions_text' in locals() else ''
                )
                questions = []  # Graceful fallback

        return {
            'is_ambiguous': is_ambiguous,
            'reasons': reasons,
            'suggestions': suggestions,
            'questions': questions  # NEW field
        }

    def augment_query_with_clarifications(
        self,
        original_query: str,
        clarifications: List[Dict[str, str]]
    ) -> str:
        """
        Augment original query with clarification selections

        Args:
            original_query: Original ambiguous query
            clarifications: List of {question_id, selected_option} dicts

        Returns:
            Augmented query string

        Example:
            original_query = "What is the charge-off rate?"
            clarifications = [
                {"question_id": "charge_off_type", "selected_option": "Net charge-off"},
                {"question_id": "time_period", "selected_option": "Q4 2024"}
            ]
            returns: "What is the charge-off rate? [User clarifications: charge_off_type='Net charge-off', time_period='Q4 2024']"
        """
        if not clarifications:
            return original_query

        # Build clarification context
        clarification_text = "\n".join([
            f"- For '{c['question_id']}': User selected '{c['selected_option']}'"
            for c in clarifications
        ])

        augmented = f"""{original_query}

[Clarifications provided by user:
{clarification_text}
]"""

        logger.info(
            "query_augmented_with_clarifications",
            original_query=original_query,
            clarification_count=len(clarifications),
            augmented_query=augmented
        )

        return augmented


# Global singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Get the global Gemini client instance (singleton pattern)

    Returns:
        GeminiClient instance
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
