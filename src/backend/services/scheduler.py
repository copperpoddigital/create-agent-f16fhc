#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler service for the Freight Price Movement Agent.

Manages the scheduling and coordination of recurring tasks including data imports,
analyses, report generation, and system maintenance. Provides a centralized
interface for configuring and managing scheduled operations.
"""

import json
from datetime import datetime
from typing import Optional, Dict, List, Any

import celery  # version ^5.2.7
from celery import schedules  # version ^5.2.7

from ..core.config import settings  # Access configuration settings for scheduler
from ..core.logging import get_logger  # Configure logging for scheduler service
from ..tasks.worker import celery_app  # Celery application instance for task scheduling
from ..tasks.data_import import import_data_from_source_async, import_data_batch_async  # Schedule data import tasks
from ..tasks.analysis import run_analysis, run_analysis_with_time_period, run_batch_analysis  # Schedule analysis tasks
from ..tasks.cleanup import cleanup_expired_analysis_results, archive_old_audit_logs, purge_archived_audit_logs, cleanup_old_analysis_results, optimize_database, schedule_cleanup_tasks  # Schedule cleanup tasks

# Initialize logger
logger = get_logger(__name__)


def initialize_scheduler() -> None:
    """
    Initializes the scheduler with default scheduled tasks.
    """
    logger.info("Initializing scheduler with default scheduled tasks")

    # Configure default scheduled tasks for data import, analysis, cleanup, and reporting
    # Example: schedule_data_import(source_config, schedule_type, interval_seconds, crontab)
    # Example: schedule_analysis(analysis_parameters, schedule_type, interval_seconds, crontab)
    # Example: schedule_system_maintenance()
    # Example: schedule_report_processing()

    # Register the scheduled tasks with Celery Beat
    # This is handled by Celery Beat configuration, no explicit registration needed here

    logger.info("Scheduler initialized successfully")


def schedule_data_import(source_config: Dict, schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None) -> Dict:
    """
    Schedules a recurring data import task.

    Args:
        source_config: Data source configuration
        schedule_type: Schedule type ('interval' or 'crontab')
        interval_seconds: Interval in seconds (for 'interval' schedule)
        crontab: Crontab expression (for 'crontab' schedule)

    Returns:
        Scheduling result with task ID and schedule information
    """
    # Validate the source configuration
    # Validate the schedule parameters based on schedule_type
    validate_schedule_params(schedule_type, interval_seconds, crontab)

    # Create a unique task name for this scheduled import
    task_name = f"import_data_from_source_{source_config['name']}"

    # Configure the schedule based on schedule_type (interval or crontab)
    if schedule_type == "interval":
        schedule = create_interval_schedule(interval_seconds)
    elif schedule_type == "crontab":
        schedule = create_crontab_schedule(crontab)
    else:
        raise ValueError("Invalid schedule type")

    # Register the scheduled task with Celery Beat
    celery_app.add_periodic_task(schedule, import_data_from_source_async.s(source_config), name=task_name)

    # Return a dictionary with task ID and schedule information
    result = {"task_name": task_name, "schedule_type": schedule_type, "interval_seconds": interval_seconds, "crontab": crontab}

    # Log the successful scheduling of the data import task
    logger.info(f"Scheduled data import task: {task_name} with schedule: {schedule_type}")
    return result


def schedule_batch_data_import(source_configs: List[Dict], schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None) -> Dict:
    """
    Schedules a recurring batch data import task.

    Args:
        source_configs: List of data source configurations
        schedule_type: Schedule type ('interval' or 'crontab')
        interval_seconds: Interval in seconds (for 'interval' schedule)
        crontab: Crontab expression (for 'crontab' schedule)

    Returns:
        Scheduling result with task ID and schedule information
    """
    # Validate each source configuration in the list
    # Validate the schedule parameters based on schedule_type
    validate_schedule_params(schedule_type, interval_seconds, crontab)

    # Create a unique task name for this scheduled batch import
    task_name = f"import_data_batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Configure the schedule based on schedule_type (interval or crontab)
    if schedule_type == "interval":
        schedule = create_interval_schedule(interval_seconds)
    elif schedule_type == "crontab":
        schedule = create_crontab_schedule(crontab)
    else:
        raise ValueError("Invalid schedule type")

    # Register the scheduled task with Celery Beat
    celery_app.add_periodic_task(schedule, import_data_batch_async.s(source_configs), name=task_name)

    # Return a dictionary with task ID and schedule information
    result = {"task_name": task_name, "schedule_type": schedule_type, "interval_seconds": interval_seconds, "crontab": crontab}

    # Log the successful scheduling of the batch data import task
    logger.info(f"Scheduled batch data import task: {task_name} with schedule: {schedule_type}")
    return result


def schedule_analysis(analysis_parameters: Dict, schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None, created_by: Optional[str] = None) -> Dict:
    """
    Schedules a recurring analysis task.

    Args:
        analysis_parameters: Analysis parameters
        schedule_type: Schedule type ('interval' or 'crontab')
        interval_seconds: Interval in seconds (for 'interval' schedule)
        crontab: Crontab expression (for 'crontab' schedule)
        created_by: Optional user ID

    Returns:
        Scheduling result with task ID and schedule information
    """
    # Validate the analysis parameters
    # Validate the schedule parameters based on schedule_type
    validate_schedule_params(schedule_type, interval_seconds, crontab)

    # Create a unique task name for this scheduled analysis
    task_name = f"run_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Configure the schedule based on schedule_type (interval or crontab)
    if schedule_type == "interval":
        schedule = create_interval_schedule(interval_seconds)
    elif schedule_type == "crontab":
        schedule = create_crontab_schedule(crontab)
    else:
        raise ValueError("Invalid schedule type")

    # Register the scheduled task with Celery Beat
    celery_app.add_periodic_task(schedule, run_analysis.s(analysis_parameters, created_by), name=task_name)

    # Return a dictionary with task ID and schedule information
    result = {"task_name": task_name, "schedule_type": schedule_type, "interval_seconds": interval_seconds, "crontab": crontab}

    # Log the successful scheduling of the analysis task
    logger.info(f"Scheduled analysis task: {task_name} with schedule: {schedule_type}")
    return result


def schedule_analysis_with_time_period(time_period_id: str, filters: Dict, schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None, created_by: Optional[str] = None) -> Dict:
    """
    Schedules a recurring analysis task with a specific time period.

    Args:
        time_period_id: ID of the time period
        filters: Filters to apply to the analysis
        schedule_type: Schedule type ('interval' or 'crontab')
        interval_seconds: Interval in seconds (for 'interval' schedule)
        crontab: Crontab expression (for 'crontab' schedule)
        created_by: Optional user ID

    Returns:
        Scheduling result with task ID and schedule information
    """
    # Validate the time period ID and filters
    # Validate the schedule parameters based on schedule_type
    validate_schedule_params(schedule_type, interval_seconds, crontab)

    # Create a unique task name for this scheduled analysis
    task_name = f"run_analysis_time_period_{time_period_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Configure the schedule based on schedule_type (interval or crontab)
    if schedule_type == "interval":
        schedule = create_interval_schedule(interval_seconds)
    elif schedule_type == "crontab":
        schedule = create_crontab_schedule(crontab)
    else:
        raise ValueError("Invalid schedule type")

    # Register the scheduled task with Celery Beat
    celery_app.add_periodic_task(schedule, run_analysis_with_time_period.s(time_period_id, filters, created_by), name=task_name)

    # Return a dictionary with task ID and schedule information
    result = {"task_name": task_name, "schedule_type": schedule_type, "interval_seconds": interval_seconds, "crontab": crontab}

    # Log the successful scheduling of the analysis task
    logger.info(f"Scheduled analysis task with time period: {time_period_id}, task_name: {task_name}, schedule: {schedule_type}")
    return result


def schedule_batch_analysis(time_period_ids: List[str], filters: Dict, schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None, created_by: Optional[str] = None) -> Dict:
    """
    Schedules a recurring batch analysis task for multiple time periods.

    Args:
        time_period_ids: List of time period IDs
        filters: Filters to apply to the analysis
        schedule_type: Schedule type ('interval' or 'crontab')
        interval_seconds: Interval in seconds (for 'interval' schedule)
        crontab: Crontab expression (for 'crontab' schedule)
        created_by: Optional user ID

    Returns:
        Scheduling result with task ID and schedule information
    """
    # Validate the time period IDs and filters
    # Validate the schedule parameters based on schedule_type
    validate_schedule_params(schedule_type, interval_seconds, crontab)

    # Create a unique task name for this scheduled batch analysis
    task_name = f"run_batch_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Configure the schedule based on schedule_type (interval or crontab)
    if schedule_type == "interval":
        schedule = create_interval_schedule(interval_seconds)
    elif schedule_type == "crontab":
        schedule = create_crontab_schedule(crontab)
    else:
        raise ValueError("Invalid schedule type")

    # Register the scheduled task with Celery Beat
    celery_app.add_periodic_task(schedule, run_batch_analysis.s(time_period_ids, filters, created_by), name=task_name)

    # Return a dictionary with task ID and schedule information
    result = {"task_name": task_name, "schedule_type": schedule_type, "interval_seconds": interval_seconds, "crontab": crontab}

    # Log the successful scheduling of the batch analysis task
    logger.info(f"Scheduled batch analysis task: {task_name} with schedule: {schedule_type}")
    return result


def schedule_system_maintenance() -> Dict:
    """
    Schedules system maintenance tasks including cleanup and optimization.

    Returns:
        Scheduling result with task IDs and schedule information
    """
    # Configure scheduled tasks for expired analysis results cleanup (hourly)
    cleanup_expired_analysis_results_task_name = "cleanup_expired_analysis_results_hourly"
    celery_app.add_periodic_task(schedules.crontab(minute=0, hour="*"), cleanup_expired_analysis_results.s(), name=cleanup_expired_analysis_results_task_name)

    # Configure scheduled tasks for old analysis results cleanup (weekly)
    cleanup_old_analysis_results_task_name = "cleanup_old_analysis_results_weekly"
    celery_app.add_periodic_task(schedules.crontab(minute=0, hour=3, day_of_week=0), cleanup_old_analysis_results.s(), name=cleanup_old_analysis_results_task_name)

    # Configure scheduled tasks for audit log archival (daily)
    archive_old_audit_logs_task_name = "archive_old_audit_logs_daily"
    celery_app.add_periodic_task(schedules.crontab(minute=0, hour=2), archive_old_audit_logs.s(), name=archive_old_audit_logs_task_name)

    # Configure scheduled tasks for archived audit log purging (monthly)
    purge_archived_audit_logs_task_name = "purge_archived_audit_logs_monthly"
    celery_app.add_periodic_task(schedules.crontab(minute=0, hour=4, day_of_month=1), purge_archived_audit_logs.s(), name=purge_archived_audit_logs_task_name)

    # Configure scheduled tasks for database optimization (weekly during off-peak hours)
    optimize_database_task_name = "optimize_database_weekly"
    celery_app.add_periodic_task(schedules.crontab(minute=0, hour=5, day_of_week=0), optimize_database.s(), name=optimize_database_task_name)

    # Return a dictionary with all scheduled maintenance tasks
    result = {
        "cleanup_expired_analysis_results": cleanup_expired_analysis_results_task_name,
        "cleanup_old_analysis_results": cleanup_old_analysis_results_task_name,
        "archive_old_audit_logs": archive_old_audit_logs_task_name,
        "purge_archived_audit_logs": purge_archived_audit_logs_task_name,
        "optimize_database": optimize_database_task_name
    }

    # Log the successful scheduling of system maintenance tasks
    logger.info(f"Scheduled system maintenance tasks: {result}")
    return result


def schedule_report_processing() -> Dict:
    """
    Schedules the processing of scheduled reports.

    Returns:
        Scheduling result with task ID and schedule information
    """
    # Create a schedule task for processing scheduled reports to run every 15 minutes using the string task name 'tasks.reporting.process_scheduled_reports'
    process_scheduled_reports_task_name = "process_scheduled_reports_every_15_minutes"
    celery_app.add_periodic_task(schedules.crontab(minute="*/15"), "tasks.reporting.process_scheduled_reports", name=process_scheduled_reports_task_name)

    # Create a schedule task for cleaning up old reports to run weekly using the string task name 'tasks.reporting.cleanup_old_reports'
    cleanup_old_reports_task_name = "cleanup_old_reports_weekly"
    celery_app.add_periodic_task(schedules.crontab(minute=0, hour=1, day_of_week=0), "tasks.reporting.cleanup_old_reports", name=cleanup_old_reports_task_name)

    # Return a dictionary with the scheduled report processing tasks
    result = {
        "process_scheduled_reports": process_scheduled_reports_task_name,
        "cleanup_old_reports": cleanup_old_reports_task_name
    }

    # Log the successful scheduling of report processing tasks
    logger.info(f"Scheduled report processing tasks: {result}")
    return result


def get_scheduled_tasks() -> Dict:
    """
    Retrieves all currently scheduled tasks.

    Returns:
        Dictionary of all scheduled tasks with their schedules
    """
    # Retrieve the current schedule from Celery Beat
    scheduled_tasks = celery_app.control.inspect().scheduled()

    # Format the schedule information into a user-friendly dictionary
    formatted_schedule = {}
    for worker, tasks in scheduled_tasks.items():
        formatted_schedule[worker] = []
        for task in tasks:
            formatted_schedule[worker].append({
                "name": task["name"],
                "task": task["task"],
                "args": task["args"],
                "kwargs": task["kwargs"],
                "options": task["options"]
            })

    # Log the retrieval of scheduled tasks
    logger.info("Retrieved scheduled tasks")

    # Return the dictionary of scheduled tasks
    return formatted_schedule


def remove_scheduled_task(task_name: str) -> bool:
    """
    Removes a scheduled task by its name.

    Args:
        task_name: Name of the task to remove

    Returns:
        True if task was removed, False if not found
    """
    # Check if the task exists in the current schedule
    scheduled_tasks = celery_app.control.inspect().scheduled()
    task_found = False

    for worker, tasks in scheduled_tasks.items():
        for task in tasks:
            if task["name"] == task_name:
                task_found = True
                break
        if task_found:
            break

    if not task_found:
        logger.warning(f"Task not found in schedule: {task_name}")
        return False

    # If found, remove the task from the schedule
    celery_app.control.revoke(task_name, terminate=True)

    # Log the removal of the scheduled task
    logger.info(f"Removed scheduled task: {task_name}")

    # Return True if task was removed, False if not found
    return True


def update_scheduled_task(task_name: str, schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None) -> Dict:
    """
    Updates the schedule of an existing task.

    Args:
        task_name: Name of the task to update
        schedule_type: New schedule type ('interval' or 'crontab')
        interval_seconds: New interval in seconds (for 'interval' schedule)
        crontab: New crontab expression (for 'crontab' schedule)

    Returns:
        Updated task schedule information
    """
    # Check if the task exists in the current schedule
    # Validate the new schedule parameters based on schedule_type
    validate_schedule_params(schedule_type, interval_seconds, crontab)

    # Remove the existing task
    remove_scheduled_task(task_name)

    # Create the appropriate schedule object based on schedule_type
    if schedule_type == "interval":
        schedule = create_interval_schedule(interval_seconds)
    elif schedule_type == "crontab":
        schedule = create_crontab_schedule(crontab)
    else:
        raise ValueError("Invalid schedule type")

    # Register the updated task with Celery Beat
    celery_app.add_periodic_task(schedule, task_name, name=task_name)

    # Log the update of the scheduled task
    logger.info(f"Updated scheduled task: {task_name} with schedule: {schedule_type}")

    # Return the updated task schedule information
    return {"task_name": task_name, "schedule_type": schedule_type, "interval_seconds": interval_seconds, "crontab": crontab}


def create_interval_schedule(seconds: int) -> celery.schedules.schedule:
    """
    Creates an interval-based schedule.

    Args:
        seconds: Interval in seconds

    Returns:
        Celery interval schedule
    """
    # Validate that seconds is a positive integer
    if not isinstance(seconds, int) or seconds <= 0:
        raise ValueError("Interval seconds must be a positive integer")

    # Create and return a celery.schedules.schedule.every(seconds) object
    return schedules.schedule(timedelta(seconds=seconds))


def create_crontab_schedule(crontab_string: str) -> celery.schedules.crontab:
    """
    Creates a crontab-based schedule.

    Args:
        crontab_string: Crontab expression

    Returns:
        Celery crontab schedule
    """
    # Parse the crontab string into minute, hour, day_of_week, day_of_month, month_of_year components
    try:
        minute, hour, day_of_week, day_of_month, month_of_year = crontab_string.split()
    except ValueError:
        raise ValueError("Invalid crontab format. Must be 'minute hour day_of_week day_of_month month_of_year'")

    # Validate each component according to crontab rules
    # Create and return a celery.schedules.crontab object with the parsed components
    return schedules.crontab(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month, month_of_year=month_of_year)


def validate_schedule_params(schedule_type: str, interval_seconds: Optional[int] = None, crontab: Optional[str] = None) -> bool:
    """
    Validates schedule parameters based on schedule type.

    Args:
        schedule_type: Schedule type ('interval' or 'crontab')
        interval_seconds: Interval in seconds (for 'interval' schedule)
        crontab: Crontab expression (for 'crontab' schedule)

    Returns:
        True if parameters are valid, raises ValueError otherwise
    """
    # Check if schedule_type is one of 'interval' or 'crontab'
    if schedule_type not in ["interval", "crontab"]:
        raise ValueError("Schedule type must be 'interval' or 'crontab'")

    # If schedule_type is 'interval', validate that interval_seconds is provided and positive
    if schedule_type == "interval":
        if not isinstance(interval_seconds, int) or interval_seconds <= 0:
            raise ValueError("Interval seconds must be a positive integer for 'interval' schedule")

    # If schedule_type is 'crontab', validate that crontab is provided and properly formatted
    if schedule_type == "crontab":
        if not isinstance(crontab, str) or len(crontab.split()) != 5:
            raise ValueError("Crontab expression must be a string with 5 components (minute hour day_of_week day_of_month month_of_year) for 'crontab' schedule")

    # Return True if validation passes, raise ValueError with specific message otherwise
    return True