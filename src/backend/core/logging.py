#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core logging module for the Freight Price Movement Agent.

This module provides standardized logging functionality across all application
components with structured log formatting, configurable log levels, and
integration with monitoring systems.
"""

import logging
import sys
import os
import json
import datetime
import traceback
from typing import Optional, Dict, Any, cast

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from pythonjsonlogger import jsonlogger

from .config import settings

# Default log level and format if not specified in settings
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Mapping of string log levels to logging constants
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Cache of logger instances to avoid creating multiple loggers for the same module
_loggers = {}


class JsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom log formatter that outputs logs in JSON format.
    
    This formatter extends the pythonjsonlogger.JsonFormatter to provide
    structured JSON logging with application-specific context and formatting.
    """
    
    def __init__(self, fmt: Optional[str] = None, json_default=None, json_indent=None):
        """
        Initializes the JsonFormatter.
        
        Args:
            fmt: Log format string
            json_default: Function for serializing objects that aren't serializable by default
            json_indent: Number of spaces to indent JSON output (None for compact output)
        """
        if not fmt:
            fmt = '%(timestamp)s %(level)s %(name)s %(message)s'
        super(JsonFormatter, self).__init__(fmt=fmt, json_default=json_default, json_indent=json_indent)
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record as a JSON string.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON formatted log string
        """
        # Call the base format method
        log_record = super(JsonFormatter, self).format(record)
        
        # Convert to dict if it's a string (depending on the jsonlogger version)
        if isinstance(log_record, str):
            try:
                log_record = json.loads(log_record)
            except json.JSONDecodeError:
                # If we can't parse as JSON, return the original string
                return log_record
        
        # Process the log record
        return json.dumps(self.process_log_record(log_record))
    
    def process_log_record(self, log_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a log record to prepare it for JSON formatting.
        
        Args:
            log_record: The log record as a dictionary
            
        Returns:
            Processed log record
        """
        # Use the format_log_record function to structure the record
        return format_log_record(log_record)


class SentryHandler(logging.Handler):
    """
    Custom log handler that forwards logs to Sentry.
    
    This handler sends log records to Sentry with appropriate severity levels
    and additional context from the log record.
    """
    
    def __init__(self, level: int = logging.ERROR):
        """
        Initializes the SentryHandler.
        
        Args:
            level: Minimum log level to forward to Sentry (default: ERROR)
        """
        super(SentryHandler, self).__init__(level)
    
    def emit(self, record: logging.LogRecord) -> None:
        """
        Sends the log record to Sentry.
        
        Args:
            record: The log record to send
        """
        if not self.filter(record):
            return
        
        try:
            # Skip if Sentry SDK is not initialized
            if not sentry_sdk.Hub.current.client:
                return
            
            # Extract exception info if present
            exc_info = record.exc_info
            
            # Prepare extra data from record
            extra = {
                'logger': record.name,
                'level': record.levelname,
            }
            
            # Add any additional data from the record
            if hasattr(record, 'data') and isinstance(record.data, dict):
                extra.update(record.data)
            
            # Map logging levels to Sentry levels
            level = 'error'
            if record.levelno >= logging.CRITICAL:
                level = 'fatal'
            elif record.levelno >= logging.ERROR:
                level = 'error'
            elif record.levelno >= logging.WARNING:
                level = 'warning'
            elif record.levelno >= logging.INFO:
                level = 'info'
            elif record.levelno >= logging.DEBUG:
                level = 'debug'
            
            # Send to Sentry
            sentry_sdk.capture_event({
                'message': record.getMessage(),
                'level': level,
                'extra': extra,
                'exception': exc_info[1] if exc_info else None,
            })
            
        except Exception:
            self.handleError(record)


def setup_logging() -> None:
    """
    Initializes the logging system with appropriate configuration.
    
    This function sets up the root logger with the appropriate log level,
    handlers, and formatters based on the application settings.
    """
    # Get log level from settings
    log_level = get_log_level(settings.LOG_LEVEL)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler for all environments
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    
    # Determine formatter based on settings
    if settings.LOG_FORMAT.lower() == 'json':
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(settings.LOG_FORMAT or DEFAULT_LOG_FORMAT)
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler in production environment
    if settings.ENV.lower() == 'production':
        # Ensure logs directory exists
        log_dir = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(os.path.join(log_dir, f'{settings.APP_NAME.lower().replace(" ", "_")}.log'))
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        configure_sentry(settings.SENTRY_DSN, settings.ENV, settings.APP_NAME)
        
        # Add Sentry handler
        sentry_handler = SentryHandler(level=logging.ERROR)
        root_logger.addHandler(sentry_handler)
    
    # Set log levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('alembic').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(f"Logging initialized at {log_level} level for {settings.APP_NAME} in {settings.ENV} environment")


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance for the specified module.
    
    Args:
        name: Name of the module or component
        
    Returns:
        Configured logger instance
    """
    # Check if logger already exists in cache
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = logging.getLogger(name)
    
    # Cache logger for future use
    _loggers[name] = logger
    
    return logger


def log_exception(exception: Exception, module_name: Optional[str] = None, 
                  context: Optional[str] = None, extra_data: Optional[dict] = None) -> None:
    """
    Logs an exception with detailed information and context.
    
    Args:
        exception: The exception to log
        module_name: Name of the module where the exception occurred
        context: Additional context information about the exception
        extra_data: Additional data to include in the log
    """
    # If module_name is not provided, try to get it from the caller's frame
    if not module_name:
        frame = traceback.extract_stack()[-2]
        module_name = frame.name
    
    # Get logger for the module
    logger = get_logger(module_name)
    
    # Prepare exception information
    exc_type = type(exception).__name__
    exc_msg = str(exception)
    exc_traceback = traceback.format_exc()
    
    # Prepare log message
    log_msg = f"Exception: {exc_type}: {exc_msg}"
    if context:
        log_msg = f"{context}: {log_msg}"
    
    # Prepare extra data
    log_data = {
        'exception_type': exc_type,
        'exception_message': exc_msg,
        'traceback': exc_traceback,
    }
    
    # Add any extra data provided
    if extra_data:
        log_data.update(extra_data)
    
    # Log the exception
    logger.error(log_msg, extra={'data': log_data}, exc_info=True)


def format_log_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats a log record into a structured dictionary.
    
    Args:
        record: The log record to format
        
    Returns:
        Formatted log record
    """
    # Create a copy of the record to avoid modifying the original
    formatted_record = record.copy()
    
    # Add application context
    formatted_record['app'] = settings.APP_NAME
    formatted_record['env'] = settings.ENV
    
    # Add ISO format timestamp if not present
    if 'timestamp' not in formatted_record:
        formatted_record['timestamp'] = datetime.datetime.now().isoformat()
    
    # Extract and format exception info if present
    if 'exc_info' in formatted_record and formatted_record['exc_info']:
        exc_info = formatted_record.pop('exc_info')
        formatted_record['exception'] = {
            'type': exc_info[0].__name__ if exc_info[0] else None,
            'message': str(exc_info[1]) if exc_info[1] else None,
            'traceback': traceback.format_tb(exc_info[2]) if exc_info[2] else None,
        }
    
    # Add any extra fields from the record
    if 'data' in formatted_record and isinstance(formatted_record['data'], dict):
        extra_data = formatted_record.pop('data')
        for key, value in extra_data.items():
            if key not in formatted_record:
                formatted_record[key] = value
    
    return formatted_record


def configure_sentry(dsn: str, environment: str, app_name: str) -> None:
    """
    Configures Sentry integration for error tracking.
    
    Args:
        dsn: Sentry DSN
        environment: Environment name (development, staging, production)
        app_name: Application name
    """
    # Set up the logging integration
    logging_integration = LoggingIntegration(
        level=logging.INFO,  # Capture INFO and above as breadcrumbs
        event_level=logging.ERROR  # Send ERROR and above as events
    )
    
    # Initialize Sentry SDK
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=f"{app_name}@{getattr(settings, 'APP_VERSION', '1.0.0')}",
        integrations=[logging_integration],
        # Set traces sample rate based on environment
        traces_sample_rate=1.0 if environment.lower() == 'development' else 0.1,
        # Add app context
        defaults={
            'tags': {
                'app': app_name,
                'env': environment,
            }
        }
    )
    
    # Log successful Sentry initialization
    logging.getLogger(__name__).info(f"Sentry initialized for {app_name} in {environment} environment")


def get_log_level(level_name: str) -> int:
    """
    Converts a string log level to the corresponding logging constant.
    
    Args:
        level_name: String representation of the log level
        
    Returns:
        Logging level constant
    """
    # Convert to uppercase to avoid case sensitivity issues
    level_upper = level_name.upper()
    
    # Return the corresponding level or default if not found
    return LOG_LEVELS.get(level_upper, DEFAULT_LOG_LEVEL)