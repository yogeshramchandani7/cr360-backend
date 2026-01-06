"""
Unit Tests for Logger (app/utils/logger.py)

Tests logger initialization and configuration
"""

import pytest
import logging
from unittest.mock import patch, Mock
from app.utils.logger import get_logger, configure_logging


class TestGetLogger:
    """Test get_logger function"""

    @patch('app.utils.logger.structlog.get_logger')
    def test_get_logger_returns_logger(self, mock_get_logger):
        """Test that get_logger returns a logger instance"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger = get_logger("test_module")

        mock_get_logger.assert_called_once_with("test_module")
        assert logger is mock_logger

    @patch('app.utils.logger.structlog.get_logger')
    def test_get_logger_with_name(self, mock_get_logger):
        """Test get_logger with specific name"""
        logger = get_logger("custom.module.name")

        mock_get_logger.assert_called_once_with("custom.module.name")

    @patch('app.utils.logger.structlog.get_logger')
    def test_get_logger_default_name(self, mock_get_logger):
        """Test get_logger with default name"""
        logger = get_logger()

        mock_get_logger.assert_called_once()


class TestConfigureLogging:
    """Test configure_logging function"""

    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.logging.basicConfig')
    def test_configure_logging_info_level(self, mock_basic_config, mock_structlog_configure):
        """Test configuring logging at INFO level"""
        configure_logging(log_level="INFO")

        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == logging.INFO

        mock_structlog_configure.assert_called_once()

    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.logging.basicConfig')
    def test_configure_logging_debug_level(self, mock_basic_config, mock_structlog_configure):
        """Test configuring logging at DEBUG level"""
        configure_logging(log_level="DEBUG")

        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == logging.DEBUG

    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.logging.basicConfig')
    def test_configure_logging_warning_level(self, mock_basic_config, mock_structlog_configure):
        """Test configuring logging at WARNING level"""
        configure_logging(log_level="WARNING")

        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == logging.WARNING

    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.logging.basicConfig')
    def test_configure_logging_error_level(self, mock_basic_config, mock_structlog_configure):
        """Test configuring logging at ERROR level"""
        configure_logging(log_level="ERROR")

        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == logging.ERROR

    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.logging.basicConfig')
    def test_configure_logging_structlog_configured(self, mock_basic_config, mock_structlog_configure):
        """Test that structlog is configured with processors"""
        configure_logging(log_level="INFO")

        mock_structlog_configure.assert_called_once()
        call_args = mock_structlog_configure.call_args[1]

        assert 'processors' in call_args
        assert 'wrapper_class' in call_args
        assert 'context_class' in call_args
        assert 'logger_factory' in call_args

    @patch('app.utils.logger.structlog.configure')
    @patch('app.utils.logger.logging.basicConfig')
    def test_configure_logging_case_insensitive(self, mock_basic_config, mock_structlog_configure):
        """Test that log level is case insensitive"""
        configure_logging(log_level="info")

        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == logging.INFO

        configure_logging(log_level="DeBuG")
        call_args = mock_basic_config.call_args[1]
        assert call_args['level'] == logging.DEBUG
