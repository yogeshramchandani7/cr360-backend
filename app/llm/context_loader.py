"""
Context Loader for CR360 Semantic Model

Loads and manages the YAML-based semantic model containing:
- Metric definitions and taxonomies
- Dimension hierarchies
- Business relationships and rules
- Synonyms for NLP matching
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import ContextLoadError

logger = get_logger(__name__)


class ContextLoader:
    """Loads and manages the semantic model context"""

    def __init__(self, context_file_path: Optional[str] = None):
        """
        Initialize context loader

        Args:
            context_file_path: Path to YAML semantic model file.
                              Defaults to settings.CONTEXT_FILE_PATH
        """
        self.context_file_path = context_file_path or settings.CONTEXT_FILE_PATH
        self.context: Dict[str, Any] = {}
        self._loaded = False

    def load(self) -> Dict[str, Any]:
        """
        Load the semantic model from YAML file

        Returns:
            Dict containing the full semantic model

        Raises:
            ContextLoadError: If file not found or invalid YAML
        """
        try:
            logger.info("loading_context", path=self.context_file_path)

            context_path = Path(self.context_file_path)

            if not context_path.exists():
                raise ContextLoadError(
                    f"Context file not found: {self.context_file_path}"
                )

            with open(context_path, 'r', encoding='utf-8') as f:
                self.context = yaml.safe_load(f)

            # Validate required sections
            self._validate_structure()

            self._loaded = True

            logger.info(
                "context_loaded_successfully",
                metrics_count=len(self.get_metrics()),
                dimensions_count=len(self.get_dimensions())
            )

            return self.context

        except yaml.YAMLError as e:
            logger.error("yaml_parse_error", error=str(e))
            raise ContextLoadError(f"Failed to parse YAML: {e}")
        except Exception as e:
            logger.error("context_load_error", error=str(e))
            raise ContextLoadError(f"Failed to load context: {e}")

    def _validate_structure(self) -> None:
        """
        Validate that required sections exist in the semantic model

        Raises:
            ContextLoadError: If required sections are missing
        """
        required_sections = ['metrics']
        missing = [s for s in required_sections if s not in self.context]

        if missing:
            raise ContextLoadError(
                f"Missing required sections in semantic model: {missing}"
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics from the semantic model"""
        if not self._loaded:
            self.load()
        return self.context.get('metrics', {})

    def get_dimensions(self) -> Dict[str, Any]:
        """Get all dimensions from the semantic model"""
        if not self._loaded:
            self.load()
        return self.context.get('dimensions', {})

    def get_relationships(self) -> Dict[str, Any]:
        """Get business relationships from the semantic model"""
        if not self._loaded:
            self.load()
        return self.context.get('relationships', {})

    def get_business_rules(self) -> List[str]:
        """Get business rules from the semantic model"""
        if not self._loaded:
            self.load()
        return self.context.get('business_rules', [])

    def get_metric_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific metric by name

        Args:
            name: Metric name (case-insensitive)

        Returns:
            Metric definition or None if not found
        """
        metrics = self.get_metrics()

        # Search in all metric categories
        for category, category_metrics in metrics.items():
            if isinstance(category_metrics, dict):
                for metric_name, metric_def in category_metrics.items():
                    if metric_name.lower() == name.lower():
                        return {**metric_def, 'name': metric_name, 'category': category}

        return None

    def get_dimension_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific dimension by name

        Args:
            name: Dimension name (case-insensitive)

        Returns:
            Dimension definition or None if not found
        """
        dimensions = self.get_dimensions()

        for dim_name, dim_def in dimensions.items():
            if dim_name.lower() == name.lower():
                return {**dim_def, 'name': dim_name}

        return None

    def search_metrics_by_synonym(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for metrics by synonym or description

        Args:
            query: Search term

        Returns:
            List of matching metric definitions
        """
        query_lower = query.lower()
        matches = []
        metrics = self.get_metrics()

        for category, category_metrics in metrics.items():
            if isinstance(category_metrics, dict):
                for metric_name, metric_def in category_metrics.items():
                    # Check name
                    if query_lower in metric_name.lower():
                        matches.append({**metric_def, 'name': metric_name, 'category': category})
                        continue

                    # Check synonyms
                    synonyms = metric_def.get('synonyms', [])
                    if any(query_lower in syn.lower() for syn in synonyms):
                        matches.append({**metric_def, 'name': metric_name, 'category': category})
                        continue

                    # Check description
                    description = metric_def.get('description', '')
                    if query_lower in description.lower():
                        matches.append({**metric_def, 'name': metric_name, 'category': category})

        return matches

    def get_context_for_llm(self) -> str:
        """
        Get formatted context string for LLM prompts

        Returns:
            Formatted string with full semantic model
        """
        if not self._loaded:
            self.load()

        # Convert YAML back to string for LLM consumption
        return yaml.dump(self.context, default_flow_style=False, sort_keys=False)

    def get_compact_context(self) -> str:
        """
        Get a compact version of the context with just metric/dimension names
        Useful for lightweight prompts

        Returns:
            Compact string listing available metrics and dimensions
        """
        if not self._loaded:
            self.load()

        output = ["# Available Metrics\n"]
        metrics = self.get_metrics()
        for category, category_metrics in metrics.items():
            output.append(f"\n## {category}")
            if isinstance(category_metrics, dict):
                for metric_name in category_metrics.keys():
                    output.append(f"  - {metric_name}")

        output.append("\n\n# Available Dimensions\n")
        dimensions = self.get_dimensions()
        for dim_name, dim_def in dimensions.items():
            levels = dim_def.get('levels', [])
            output.append(f"  - {dim_name}: {', '.join(levels)}")

        return '\n'.join(output)

    def reload(self) -> Dict[str, Any]:
        """
        Force reload of the context from file

        Returns:
            Reloaded context
        """
        self._loaded = False
        self.context = {}
        return self.load()


# Global singleton instance
_context_loader: Optional[ContextLoader] = None


def get_context_loader() -> ContextLoader:
    """
    Get the global context loader instance (singleton pattern)

    Returns:
        ContextLoader instance
    """
    global _context_loader
    if _context_loader is None:
        _context_loader = ContextLoader()
    return _context_loader
