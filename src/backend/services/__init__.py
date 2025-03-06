"""
Initialization module for the services package that exports all service classes and functions for the Freight Price Movement Agent.
This module provides a centralized access point to all service components including analysis, data ingestion, presentation, integration, and error handling services.
"""

from .analysis_engine import AnalysisEngine  # Core service for performing freight price movement analysis
from .data_ingestion import DataIngestionService, DataIngestionResult  # Service for data collection and ingestion from multiple sources
from .presentation import PresentationService  # Service for formatting and delivering analysis results
from .integration import IntegrationService, DataSourceType  # Service for managing connections to external systems
from .error_handling import ErrorHandler, with_retry, circuit_breaker, safe_execute  # Error handling and resilience patterns

__all__ = [
    "AnalysisEngine",
    "DataIngestionService",
    "DataIngestionResult",
    "PresentationService",
    "IntegrationService",
    "DataSourceType",
    "ErrorHandler",
    "with_retry",
    "circuit_breaker",
    "safe_execute",
]