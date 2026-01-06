"""
Unit Tests for Gemini LLM Client (app/llm/gemini_client.py)

Tests LLM API interactions, response parsing, and error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from app.llm.gemini_client import GeminiClient, get_gemini_client
from app.utils.exceptions import LLMError


class TestGeminiClientInitialization:
    """Test GeminiClient initialization"""

    @patch('app.llm.gemini_client.genai')
    def test_gemini_client_initialization_with_params(self, mock_genai):
        """Test GeminiClient initializes with provided parameters"""
        client = GeminiClient(
            api_key="test_key_123",
            model_name="gemini-2.5-flash",
            temperature=0.3,
            max_tokens=4096
        )

        assert client.api_key == "test_key_123"
        assert client.model_name == "gemini-2.5-flash"
        assert client.temperature == 0.3
        assert client.max_tokens == 4096

        # Verify API was configured
        mock_genai.configure.assert_called_once_with(api_key="test_key_123")

    @patch('app.llm.gemini_client.genai')
    @patch('app.llm.gemini_client.settings')
    def test_gemini_client_initialization_defaults(self, mock_settings, mock_genai):
        """Test GeminiClient uses settings defaults"""
        mock_settings.GOOGLE_API_KEY = "settings_key"
        mock_settings.LLM_MODEL = "gemini-2.5-flash"
        mock_settings.LLM_TEMPERATURE = 0.1
        mock_settings.LLM_MAX_TOKENS = 8192

        client = GeminiClient()

        assert client.api_key == "settings_key"
        assert client.model_name == "gemini-2.5-flash"
        assert client.temperature == 0.1
        assert client.max_tokens == 8192

    @patch('app.llm.gemini_client.genai')
    def test_gemini_client_creates_model(self, mock_genai):
        """Test that GeminiClient creates GenerativeModel on init"""
        client = GeminiClient(api_key="test_key")

        mock_genai.GenerativeModel.assert_called()
        assert client.model is not None


class TestResponseParsing:
    """Test _parse_sql_response method"""

    def test_parse_sql_response_with_sql_code_blocks(self):
        """Test parsing SQL from ```sql blocks"""
        response = """```sql
SELECT
    product_name,
    SUM(balance) as total_exposure
FROM account_level_monthly
GROUP BY product_name
```

Explanation: This query aggregates balance by product.

Metrics used: total_exposure"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert "SELECT" in sql
        assert "product_name" in sql
        assert "GROUP BY" in sql
        assert "This query aggregates" in explanation
        assert "total_exposure" in metrics

    def test_parse_sql_response_without_sql_marker(self):
        """Test parsing SQL from plain ``` blocks"""
        response = """```
SELECT * FROM table
```

Explanation: Simple query

Metrics used: all_metrics"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert "SELECT * FROM table" in sql
        assert "Simple query" in explanation

    def test_parse_sql_response_extracts_explanation(self):
        """Test that explanation is extracted correctly"""
        response = """```sql
SELECT 1
```

Explanation: This is a detailed explanation of what the query does.

Metrics used: metric1"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert "detailed explanation" in explanation
        assert "what the query does" in explanation

    def test_parse_sql_response_extracts_metrics_list(self):
        """Test that metrics list is extracted correctly"""
        response = """```sql
SELECT 1
```

Explanation: Test

Metrics used: total_exposure, delinquency_rate, charge_off_rate"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert len(metrics) == 3
        assert "total_exposure" in metrics
        assert "delinquency_rate" in metrics
        assert "charge_off_rate" in metrics

    def test_parse_sql_response_metrics_newline_separated(self):
        """Test parsing metrics from newline-separated list"""
        response = """```sql
SELECT 1
```

Explanation: Test

Metrics used:
- total_exposure
- delinquency_rate
- charge_off_rate"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert len(metrics) == 3
        assert all(m in metrics for m in ["total_exposure", "delinquency_rate", "charge_off_rate"])

    def test_parse_sql_response_incomplete_response(self):
        """Test handling of incomplete response"""
        response = """```sql
SELECT * FROM table
```"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert "SELECT" in sql
        assert explanation == ""  # No explanation section
        assert metrics == []  # No metrics section

    def test_parse_sql_response_no_code_blocks(self):
        """Test handling response without code blocks"""
        response = """This is just plain text without any SQL"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        assert sql == ""
        assert explanation == ""
        assert metrics == []


class TestGenerate:
    """Test generate method"""

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_success(self, mock_genai):
        """Test successful text generation"""
        # Mock the response
        mock_response = Mock()
        mock_response.text = "Generated response text"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.generate(prompt="Test prompt")

        assert result == "Generated response text"
        mock_model.generate_content.assert_called_once_with("Test prompt")

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_with_system_instruction(self, mock_genai):
        """Test generation with system instruction"""
        mock_response = Mock()
        mock_response.text = "Response with system instruction"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.generate(
            prompt="Test prompt",
            system_instruction="You are an SQL expert"
        )

        assert result == "Response with system instruction"
        # Verify GenerativeModel was called with system_instruction
        assert mock_genai.GenerativeModel.call_count >= 2  # Once in __init__, once in generate

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_empty_response(self, mock_genai):
        """Test handling of empty response"""
        mock_response = Mock()
        mock_response.text = None

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")

        with pytest.raises(LLMError) as exc_info:
            await client.generate(prompt="Test prompt")

        assert "Empty response" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_api_failure(self, mock_genai):
        """Test handling of API failures"""
        mock_model = Mock()
        mock_model.generate_content = Mock(side_effect=Exception("API Error"))

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")

        with pytest.raises(LLMError) as exc_info:
            await client.generate(prompt="Test prompt")

        assert "Failed to generate response" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_with_kwargs_overrides(self, mock_genai):
        """Test generation with generation config overrides"""
        mock_response = Mock()
        mock_response.text = "Response"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.generate(
            prompt="Test",
            temperature=0.5,
            max_output_tokens=2048
        )

        assert result == "Response"


class TestGenerateWithContext:
    """Test generate_with_context method"""

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_with_context_combines_prompt(self, mock_genai):
        """Test that context and prompt are combined correctly"""
        mock_response = Mock()
        mock_response.text = "Response"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")

        # Patch the generate method to inspect the combined prompt
        with patch.object(client, 'generate', new=AsyncMock(return_value="Response")) as mock_generate:
            result = await client.generate_with_context(
                prompt="What is total exposure?",
                context="Semantic model context here",
                system_instruction="You are an expert"
            )

            # Check that generate was called with combined prompt
            call_args = mock_generate.call_args
            combined_prompt = call_args[1]['prompt']

            assert "Context:" in combined_prompt
            assert "Semantic model context here" in combined_prompt
            assert "User Query:" in combined_prompt
            assert "What is total exposure?" in combined_prompt


class TestGenerateSQL:
    """Test generate_sql method"""

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_sql_success(self, mock_genai, sample_sql_response):
        """Test successful SQL generation"""
        mock_response = Mock()
        mock_response.text = sample_sql_response

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.generate_sql(
            natural_language_query="What is total exposure by product?",
            semantic_context="YAML context here"
        )

        assert 'sql' in result
        assert 'explanation' in result
        assert 'metrics_used' in result
        assert result['sql'] != ""
        assert isinstance(result['metrics_used'], list)

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_sql_with_conversation_history(self, mock_genai, sample_sql_response):
        """Test SQL generation with conversation history"""
        mock_response = Mock()
        mock_response.text = sample_sql_response

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        conversation_history = [
            {'user': 'What is total exposure?', 'assistant': 'Total is $2.8B'},
            {'user': 'Show by product', 'assistant': 'Here is the breakdown...'}
        ]

        client = GeminiClient(api_key="test")
        result = await client.generate_sql(
            natural_language_query="What about regions?",
            semantic_context="YAML context",
            conversation_history=conversation_history
        )

        assert 'sql' in result
        # Verify the model was called (conversation history was included)
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_sql_parsing_error(self, mock_genai):
        """Test handling of SQL response parsing errors"""
        mock_response = Mock()
        mock_response.text = "Invalid response without SQL"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.generate_sql(
            natural_language_query="Test query",
            semantic_context="Context"
        )

        # Should still return dict with empty/default values
        assert 'sql' in result
        assert 'explanation' in result
        assert 'metrics_used' in result

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_sql_api_error(self, mock_genai):
        """Test handling of API errors during SQL generation"""
        mock_model = Mock()
        mock_model.generate_content = Mock(side_effect=Exception("API Error"))

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")

        with pytest.raises(LLMError) as exc_info:
            await client.generate_sql(
                natural_language_query="Test",
                semantic_context="Context"
            )

        assert "Failed to generate SQL" in str(exc_info.value)


class TestDetectAmbiguity:
    """Test detect_ambiguity method"""

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_detect_ambiguity_is_ambiguous(self, mock_genai, sample_ambiguous_response):
        """Test detecting ambiguous query"""
        mock_response = Mock()
        mock_response.text = sample_ambiguous_response

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.detect_ambiguity(
            natural_language_query="Show me the metrics",
            semantic_context="Context"
        )

        assert result['is_ambiguous'] is True
        assert len(result['reasons']) > 0
        assert len(result['suggestions']) > 0
        assert "Missing time period" in result['reasons'][0]

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_detect_ambiguity_not_ambiguous(self, mock_genai, sample_clear_response):
        """Test detecting non-ambiguous query"""
        mock_response = Mock()
        mock_response.text = sample_clear_response

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.detect_ambiguity(
            natural_language_query="What is total exposure as of latest date?",
            semantic_context="Context"
        )

        assert result['is_ambiguous'] is False
        assert result['reasons'] == [] or len(result['reasons']) == 0
        assert result['suggestions'] == [] or len(result['suggestions']) == 0

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_detect_ambiguity_parsing_error(self, mock_genai):
        """Test handling of ambiguity response parsing errors"""
        mock_response = Mock()
        mock_response.text = "Unparseable response format"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        result = await client.detect_ambiguity(
            natural_language_query="Test",
            semantic_context="Context"
        )

        # Should return default structure even if parsing fails
        assert 'is_ambiguous' in result
        assert 'reasons' in result
        assert 'suggestions' in result
        assert result['is_ambiguous'] is False  # Default when "Ambiguous: Yes" not found


class TestSingletonPattern:
    """Test get_gemini_client singleton pattern"""

    def test_get_gemini_client_returns_instance(self):
        """Test that get_gemini_client returns a GeminiClient instance"""
        # Reset singleton
        import app.llm.gemini_client as gc_module
        gc_module._gemini_client = None

        with patch('app.llm.gemini_client.genai'):
            client = get_gemini_client()
            assert isinstance(client, GeminiClient)

        # Clean up
        gc_module._gemini_client = None

    def test_get_gemini_client_returns_same_instance(self):
        """Test that get_gemini_client returns the same instance (singleton)"""
        # Reset singleton
        import app.llm.gemini_client as gc_module
        gc_module._gemini_client = None

        with patch('app.llm.gemini_client.genai'):
            client1 = get_gemini_client()
            client2 = get_gemini_client()

            assert client1 is client2

        # Clean up
        gc_module._gemini_client = None


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_very_long_prompt(self, mock_genai):
        """Test generation with very long prompt"""
        mock_response = Mock()
        mock_response.text = "Response"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        long_prompt = "a" * 10000

        result = await client.generate(prompt=long_prompt)
        assert result == "Response"

    @pytest.mark.asyncio
    @patch('app.llm.gemini_client.genai')
    async def test_generate_special_characters_in_prompt(self, mock_genai):
        """Test generation with special characters"""
        mock_response = Mock()
        mock_response.text = "Response"

        mock_model = Mock()
        mock_model.generate_content = Mock(return_value=mock_response)

        mock_genai.GenerativeModel.return_value = mock_model

        client = GeminiClient(api_key="test")
        special_prompt = "Test with special chars: é, ñ, 中文, 😀"

        result = await client.generate(prompt=special_prompt)
        assert result == "Response"

    def test_parse_sql_response_multiple_code_blocks(self):
        """Test parsing response with multiple code blocks (uses first)"""
        response = """```sql
SELECT 1 FROM first
```

Some text

```sql
SELECT 2 FROM second
```

Explanation: Test

Metrics used: metric1"""

        client = GeminiClient(api_key="test")
        sql, explanation, metrics = client._parse_sql_response(response)

        # Should extract the first SQL block
        assert "first" in sql
        assert "second" not in sql
