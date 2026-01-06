"""
Unit Tests for Context Loader (app/llm/context_loader.py)

Tests YAML loading, validation, and context retrieval
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from app.llm.context_loader import ContextLoader, get_context_loader
from app.utils.exceptions import ContextLoadError


class TestContextLoaderInitialization:
    """Test ContextLoader initialization"""

    def test_context_loader_initialization_with_path(self):
        """Test ContextLoader initializes with provided path"""
        loader = ContextLoader(context_file_path="custom/path/model.yaml")

        assert loader.context_file_path == "custom/path/model.yaml"
        assert loader.context == {}
        assert loader._loaded is False

    def test_context_loader_initialization_default_path(self, mock_settings):
        """Test ContextLoader initializes with default path from settings"""
        with patch('app.llm.context_loader.settings', mock_settings):
            loader = ContextLoader()

            assert loader.context_file_path == mock_settings.CONTEXT_FILE_PATH
            assert loader.context == {}
            assert loader._loaded is False


class TestContextLoaderLoad:
    """Test context loading from YAML file"""

    def test_load_yaml_success(self, tmp_path):
        """Test successful loading of valid YAML file"""
        # Create a temporary YAML file
        yaml_content = {
            'version': '2.0',
            'metrics': {
                'exposure': {
                    'total_exposure': {
                        'description': 'Total account balance',
                        'formula': 'SUM(account_balance_eop)'
                    }
                }
            },
            'dimensions': {
                'product': {
                    'column': 'product_name',
                    'levels': ['Mortgage', 'Auto Loan', 'Credit Card']
                }
            }
        }

        yaml_file = tmp_path / "test_model.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        # Load context
        loader = ContextLoader(context_file_path=str(yaml_file))
        context = loader.load()

        assert context is not None
        assert context['version'] == '2.0'
        assert 'metrics' in context
        assert 'dimensions' in context
        assert loader._loaded is True

    def test_load_yaml_file_not_found(self):
        """Test that ContextLoadError is raised if file doesn't exist"""
        loader = ContextLoader(context_file_path="nonexistent/file.yaml")

        with pytest.raises(ContextLoadError) as exc_info:
            loader.load()

        assert "Context file not found" in str(exc_info.value)

    def test_load_yaml_invalid_yaml_syntax(self, tmp_path):
        """Test that ContextLoadError is raised for invalid YAML syntax"""
        # Create an invalid YAML file
        yaml_file = tmp_path / "invalid.yaml"
        with open(yaml_file, 'w') as f:
            f.write("invalid: yaml: syntax:\n  - unclosed [bracket")

        loader = ContextLoader(context_file_path=str(yaml_file))

        with pytest.raises(ContextLoadError) as exc_info:
            loader.load()

        assert "Failed to parse YAML" in str(exc_info.value)

    def test_load_yaml_empty_file(self, tmp_path):
        """Test loading empty YAML file"""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        loader = ContextLoader(context_file_path=str(yaml_file))

        with pytest.raises(ContextLoadError):
            loader.load()

    def test_load_yaml_missing_required_sections(self, tmp_path):
        """Test that ContextLoadError is raised if required sections are missing"""
        # Create YAML without required 'metrics' section
        yaml_content = {
            'version': '2.0',
            'dimensions': {}
        }

        yaml_file = tmp_path / "missing_metrics.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))

        with pytest.raises(ContextLoadError) as exc_info:
            loader.load()

        assert "Missing required sections" in str(exc_info.value)
        assert "metrics" in str(exc_info.value)


class TestContextValidation:
    """Test context structure validation"""

    def test_validate_structure_success(self, tmp_path):
        """Test validation passes with required sections"""
        yaml_content = {
            'metrics': {
                'exposure': {}
            }
        }

        yaml_file = tmp_path / "valid.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        # Should not raise
        context = loader.load()
        assert 'metrics' in context

    def test_validate_structure_missing_metrics(self, tmp_path):
        """Test validation fails when 'metrics' section is missing"""
        yaml_content = {
            'dimensions': {},
            'version': '2.0'
        }

        yaml_file = tmp_path / "no_metrics.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))

        with pytest.raises(ContextLoadError) as exc_info:
            loader.load()

        assert "metrics" in str(exc_info.value).lower()


class TestContextRetrieval:
    """Test retrieving metrics, dimensions, and relationships"""

    @pytest.fixture
    def loaded_context_loader(self, tmp_path):
        """Create a ContextLoader with test data"""
        yaml_content = {
            'metrics': {
                'exposure': {
                    'total_exposure': {
                        'description': 'Total balance',
                        'formula': 'SUM(balance)',
                        'synonyms': ['balance', 'outstanding amount']
                    },
                    'delinquent_exposure': {
                        'description': 'Delinquent balance',
                        'formula': 'SUM(delinquent_balance)'
                    }
                },
                'delinquency': {
                    'delinquency_rate': {
                        'description': 'Delinquency rate',
                        'formula': 'delinquent / total * 100'
                    }
                }
            },
            'dimensions': {
                'product': {
                    'column': 'product_name',
                    'levels': ['Mortgage', 'Auto Loan', 'Credit Card']
                },
                'region': {
                    'column': 'region_name',
                    'levels': ['Northeast', 'Southeast', 'Midwest', 'West']
                }
            },
            'relationships': {
                'exposure_to_delinquency': 'Delinquent exposure is subset of total exposure'
            },
            'business_rules': [
                'Delinquency rate must be between 0 and 100',
                'Total exposure must be positive'
            ]
        }

        yaml_file = tmp_path / "test.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        loader.load()
        return loader

    def test_get_metrics(self, loaded_context_loader):
        """Test retrieving all metrics"""
        metrics = loaded_context_loader.get_metrics()

        assert 'exposure' in metrics
        assert 'delinquency' in metrics
        assert 'total_exposure' in metrics['exposure']
        assert 'delinquency_rate' in metrics['delinquency']

    def test_get_dimensions(self, loaded_context_loader):
        """Test retrieving all dimensions"""
        dimensions = loaded_context_loader.get_dimensions()

        assert 'product' in dimensions
        assert 'region' in dimensions
        assert dimensions['product']['column'] == 'product_name'

    def test_get_relationships(self, loaded_context_loader):
        """Test retrieving relationships"""
        relationships = loaded_context_loader.get_relationships()

        assert 'exposure_to_delinquency' in relationships

    def test_get_business_rules(self, loaded_context_loader):
        """Test retrieving business rules"""
        rules = loaded_context_loader.get_business_rules()

        assert isinstance(rules, list)
        assert len(rules) == 2
        assert 'Delinquency rate must be between 0 and 100' in rules

    def test_get_metric_by_name(self, loaded_context_loader):
        """Test retrieving a specific metric by name"""
        metric = loaded_context_loader.get_metric_by_name('total_exposure')

        assert metric is not None
        assert metric['name'] == 'total_exposure'
        assert metric['category'] == 'exposure'
        assert 'description' in metric

    def test_get_metric_by_name_case_insensitive(self, loaded_context_loader):
        """Test metric retrieval is case-insensitive"""
        metric1 = loaded_context_loader.get_metric_by_name('TOTAL_EXPOSURE')
        metric2 = loaded_context_loader.get_metric_by_name('total_exposure')
        metric3 = loaded_context_loader.get_metric_by_name('Total_Exposure')

        assert metric1 is not None
        assert metric2 is not None
        assert metric3 is not None
        assert metric1['name'] == metric2['name'] == metric3['name']

    def test_get_metric_by_name_not_found(self, loaded_context_loader):
        """Test that None is returned for non-existent metric"""
        metric = loaded_context_loader.get_metric_by_name('nonexistent_metric')

        assert metric is None

    def test_get_dimension_by_name(self, loaded_context_loader):
        """Test retrieving a specific dimension by name"""
        dimension = loaded_context_loader.get_dimension_by_name('product')

        assert dimension is not None
        assert dimension['name'] == 'product'
        assert dimension['column'] == 'product_name'

    def test_get_dimension_by_name_case_insensitive(self, loaded_context_loader):
        """Test dimension retrieval is case-insensitive"""
        dim1 = loaded_context_loader.get_dimension_by_name('PRODUCT')
        dim2 = loaded_context_loader.get_dimension_by_name('product')

        assert dim1 is not None
        assert dim2 is not None
        assert dim1['name'] == dim2['name']

    def test_get_dimension_by_name_not_found(self, loaded_context_loader):
        """Test that None is returned for non-existent dimension"""
        dimension = loaded_context_loader.get_dimension_by_name('nonexistent_dimension')

        assert dimension is None


class TestMetricSearch:
    """Test metric search functionality"""

    @pytest.fixture
    def search_context_loader(self, tmp_path):
        """Create a ContextLoader for search tests"""
        yaml_content = {
            'metrics': {
                'exposure': {
                    'total_exposure': {
                        'description': 'Total outstanding balance',
                        'formula': 'SUM(balance)',
                        'synonyms': ['balance', 'outstanding amount', 'principal']
                    },
                    'past_due_exposure': {
                        'description': 'Past due amount',
                        'formula': 'SUM(past_due)',
                        'synonyms': ['delinquent', 'overdue']
                    }
                }
            }
        }

        yaml_file = tmp_path / "search.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        loader.load()
        return loader

    def test_search_metrics_by_name(self, search_context_loader):
        """Test searching metrics by name"""
        results = search_context_loader.search_metrics_by_synonym('exposure')

        assert len(results) >= 2
        assert any(m['name'] == 'total_exposure' for m in results)
        assert any(m['name'] == 'past_due_exposure' for m in results)

    def test_search_metrics_by_synonym(self, search_context_loader):
        """Test searching metrics by synonym"""
        results = search_context_loader.search_metrics_by_synonym('balance')

        assert len(results) >= 1
        assert any(m['name'] == 'total_exposure' for m in results)

    def test_search_metrics_by_description(self, search_context_loader):
        """Test searching metrics by description"""
        results = search_context_loader.search_metrics_by_synonym('outstanding')

        assert len(results) >= 1
        assert any(m['name'] == 'total_exposure' for m in results)

    def test_search_metrics_case_insensitive(self, search_context_loader):
        """Test that search is case-insensitive"""
        results1 = search_context_loader.search_metrics_by_synonym('EXPOSURE')
        results2 = search_context_loader.search_metrics_by_synonym('exposure')

        assert len(results1) == len(results2)

    def test_search_metrics_no_matches(self, search_context_loader):
        """Test search returns empty list when no matches"""
        results = search_context_loader.search_metrics_by_synonym('xyz_nonexistent')

        assert results == []


class TestContextFormatting:
    """Test context formatting for LLM"""

    def test_get_context_for_llm(self, sample_semantic_context):
        """Test getting formatted context string for LLM"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(sample_semantic_context)
            temp_path = f.name

        try:
            loader = ContextLoader(context_file_path=temp_path)
            context_str = loader.get_context_for_llm()

            assert isinstance(context_str, str)
            assert 'version' in context_str
            assert 'metrics' in context_str
            assert 'dimensions' in context_str
        finally:
            Path(temp_path).unlink()

    def test_get_compact_context(self, sample_semantic_context):
        """Test getting compact context with just metric/dimension names"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(sample_semantic_context)
            temp_path = f.name

        try:
            loader = ContextLoader(context_file_path=temp_path)
            compact = loader.get_compact_context()

            assert isinstance(compact, str)
            assert '# Available Metrics' in compact
            assert '# Available Dimensions' in compact
            # Check for metric category names (as defined in test fixture)
            assert 'exposure' in compact or 'delinquency' in compact
            assert 'product' in compact
        finally:
            Path(temp_path).unlink()


class TestLazyLoading:
    """Test lazy loading behavior"""

    def test_lazy_loading_on_get_metrics(self, tmp_path):
        """Test that context is loaded lazily when get_metrics is called"""
        yaml_content = {'metrics': {'exposure': {}}}
        yaml_file = tmp_path / "lazy.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        assert loader._loaded is False

        # First call should trigger load
        metrics = loader.get_metrics()
        assert loader._loaded is True
        assert metrics is not None

    def test_lazy_loading_on_get_dimensions(self, tmp_path):
        """Test lazy loading on get_dimensions"""
        yaml_content = {'metrics': {}, 'dimensions': {}}
        yaml_file = tmp_path / "lazy.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        assert loader._loaded is False

        dimensions = loader.get_dimensions()
        assert loader._loaded is True

    def test_lazy_loading_on_get_context_for_llm(self, sample_semantic_context):
        """Test lazy loading on get_context_for_llm"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(sample_semantic_context)
            temp_path = f.name

        try:
            loader = ContextLoader(context_file_path=temp_path)
            assert loader._loaded is False

            context_str = loader.get_context_for_llm()
            assert loader._loaded is True
            assert context_str is not None
        finally:
            Path(temp_path).unlink()


class TestReload:
    """Test context reload functionality"""

    def test_reload_forces_fresh_load(self, tmp_path):
        """Test that reload forces a fresh load from file"""
        yaml_content = {'metrics': {'exposure': {}}}
        yaml_file = tmp_path / "reload.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        loader.load()
        assert loader._loaded is True

        # Modify the file
        yaml_content['metrics']['new_metric'] = {}
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        # Reload should pick up changes
        new_context = loader.reload()
        assert 'new_metric' in new_context['metrics']

    def test_reload_resets_loaded_flag(self, tmp_path):
        """Test that reload resets the _loaded flag"""
        yaml_content = {'metrics': {}}
        yaml_file = tmp_path / "reload.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(yaml_content, f)

        loader = ContextLoader(context_file_path=str(yaml_file))
        loader.load()
        assert loader._loaded is True

        # During reload, flag should be reset and then set again
        loader.reload()
        assert loader._loaded is True


class TestSingletonPattern:
    """Test get_context_loader singleton pattern"""

    def test_get_context_loader_returns_instance(self):
        """Test that get_context_loader returns a ContextLoader instance"""
        loader = get_context_loader()

        assert isinstance(loader, ContextLoader)

    def test_get_context_loader_returns_same_instance(self):
        """Test that get_context_loader returns the same instance (singleton)"""
        loader1 = get_context_loader()
        loader2 = get_context_loader()

        assert loader1 is loader2

    def test_singleton_preserves_state(self):
        """Test that singleton preserves state across calls"""
        # Reset the global singleton
        import app.llm.context_loader as cl_module
        cl_module._context_loader = None

        loader1 = get_context_loader()
        loader1.context = {'test': 'data'}

        loader2 = get_context_loader()
        assert loader2.context == {'test': 'data'}

        # Clean up
        cl_module._context_loader = None
