"""
Celery worker configuration module for the Freight Price Movement Agent.

This module defines and configures the Celery application instance used for
asynchronous task processing, including data ingestion, analysis, and reporting tasks.
"""

import os
import logging
from celery import Celery
from kombu.serialization import register

from ..core.config import settings
from ..core.exceptions import ApplicationException

# Set up logger for worker tasks
logger = logging.getLogger(__name__)

def register_serializers():
    """
    Registers custom serializers for Celery message serialization.
    
    This ensures consistent serialization across the application and worker processes.
    """
    # JSON serialization is already built into Celery
    # This function is a placeholder for registering any custom serializers
    # that might be needed in the future
    pass

def configure_celery(app):
    """
    Configures Celery application with appropriate settings.
    
    Args:
        app: The Celery application instance to configure
        
    Returns:
        The configured Celery application
    """
    # Configure broker and backend
    app.conf.broker_url = settings.REDIS_URL
    app.conf.result_backend = settings.REDIS_URL
    
    # Set serializers
    app.conf.task_serializer = 'json'
    app.conf.result_serializer = 'json'
    app.conf.accept_content = ['json']
    
    # Configure task execution
    app.conf.task_acks_late = True  # Tasks are acknowledged after execution for reliability
    app.conf.worker_prefetch_multiplier = 1  # Prefetch just one task at a time for fair distribution
    
    # Configure task routing for different task types
    app.conf.task_routes = {
        'tasks.data_ingestion.*': {'queue': 'data_ingestion'},
        'tasks.analysis.*': {'queue': 'analysis'},
        'tasks.reporting.*': {'queue': 'reporting'},
        'tasks.integration.*': {'queue': 'integration'},
    }
    
    # Set task time limits
    app.conf.task_time_limit = 3600  # Hard limit: 1 hour
    app.conf.task_soft_time_limit = 3000  # Soft limit: 50 minutes
    
    # Configure retry settings with exponential backoff
    app.conf.task_default_retry_delay = 60  # 1 minute initial delay
    app.conf.task_max_retries = 5  # Retry up to 5 times
    
    return app

def init_celery():
    """
    Initializes and configures the Celery application.
    
    Returns:
        Initialized Celery application
    """
    # Create Celery application
    app = Celery(settings.APP_NAME)
    
    # Register custom serializers
    register_serializers()
    
    # Configure the Celery application
    app = configure_celery(app)
    
    # Set up task error handlers
    app.conf.task_on_failure = task_failure_handler
    
    logger.info(f"Celery initialized with broker: {app.conf.broker_url} in {settings.ENV} environment")
    return app

def task_failure_handler(task, exc, task_id, args, kwargs, einfo):
    """
    Handles task failures and logs appropriate information.
    
    Args:
        task: The task object
        exc: The exception raised
        task_id: The task ID
        args: Task positional arguments
        kwargs: Task keyword arguments
        einfo: Exception information object
    """
    task_name = task.name if hasattr(task, 'name') else str(task)
    
    logger.error(
        f"Task failed: {task_id} {task_name} - {exc.__class__.__name__}: {str(exc)}"
    )
    
    # Provide additional details for application-specific exceptions
    if isinstance(exc, ApplicationException):
        logger.error(f"Exception details: {exc.details}")
        if exc.original_exception:
            logger.error(f"Original exception: {str(exc.original_exception)}")
    
    # Log traceback if available
    if einfo and hasattr(einfo, 'traceback'):
        logger.error(f"Traceback: {einfo.traceback}")

# Initialize the Celery application
celery_app = init_celery()