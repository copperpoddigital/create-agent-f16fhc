"""
Initialization module for the tasks package in the Freight Price Movement Agent.
Exports task functions from various task modules and provides a unified interface for asynchronous background processing of data ingestion, analysis, reporting, and maintenance operations.
"""

from .worker import celery_app  # Celery application instance for task registration and execution
from .data_import import import_data_from_source, import_data_from_file, import_data_from_database, schedule_recurring_import  # Import data ingestion tasks
from .analysis import run_analysis, get_analysis, compare_periods, run_analysis_batch  # Import analysis tasks
from .data_export import export_analysis_result  # Import data export tasks
from .reporting import generate_report, run_scheduled_report, batch_generate_reports, check_scheduled_reports, cleanup_report_executions  # Import reporting tasks
from .cleanup import cleanup_expired_data  # Import data cleanup tasks

__all__ = [
    "celery_app",
    "import_data_from_source",
    "import_data_from_file",
    "import_data_from_database",
    "schedule_recurring_import",
    "run_analysis",
    "get_analysis",
    "compare_periods",
    "run_analysis_batch",
    "export_analysis_result",
    "generate_report",
    "run_scheduled_report",
    "batch_generate_reports",
    "check_scheduled_reports",
    "cleanup_report_executions",
    "cleanup_expired_data",
]