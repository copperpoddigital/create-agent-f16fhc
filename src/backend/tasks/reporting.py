"""
Implements asynchronous background tasks for report generation, scheduling, and delivery in the Freight Price Movement Agent.
This module handles the execution of reports, both on-demand and scheduled, and manages the formatting and delivery of report results.
"""

import os  # version: standard library
from datetime import datetime  # version: standard library
import uuid  # version: standard library
from typing import List, Optional, Dict  # version: standard library

import sqlalchemy.orm  # package_version: ^1.4.40
from celery import Celery  # package_version: ^5.2.7

from .worker import celery_app  # Celery application instance for task registration
from ..core.db import get_db, transaction  # Database session management for task operations
from ..core.logging import get_logger  # Configure logging for report tasks
from ..core.exceptions import ReportNotFoundException, ScheduledReportNotFoundException, ReportExecutionNotFoundException  # Exception handling for report-related operations
from ..api.reports.models import Report, ReportExecution, ScheduledReport  # Database models for reports and related entities
from ..models.enums import ReportStatus, ReportFormat  # Enumeration types for report status and format
from ..services.presentation import PresentationService  # Format and present report results
from ..services.notifications import NotificationService  # Send notifications for completed reports
from ..core.config import settings  # Access configuration settings for report generation

# Initialize logger
logger = get_logger(__name__)


@celery_app.task(name='reporting.generate_report', bind=True, max_retries=3)
def generate_report(self, report_id: str, execution_id: Optional[str] = None, parameters_override: Optional[dict] = None, user_id: Optional[str] = None) -> dict:
    """
    Celery task that generates a report based on a report configuration
    """
    logger.info(f"Starting report generation for report_id: {report_id}, execution_id: {execution_id}, user_id: {user_id}")
    db_session = None
    try:
        # Get a database session using get_db()
        with get_db() as db:
            db_session = db
            # Try to retrieve the report by ID, handle ReportNotFoundException
            report = db_session.query(Report).get(report_id)
            if not report:
                raise ReportNotFoundException(f"Report not found with id: {report_id}")

            # If execution_id is provided, retrieve the existing execution, otherwise create a new one
            if execution_id:
                report_execution = db_session.query(ReportExecution).get(execution_id)
                if not report_execution:
                    raise ReportExecutionNotFoundException(f"ReportExecution not found with id: {execution_id}")
            else:
                report_execution = _create_report_execution(report=report, scheduled_report_id=None, user_id=user_id, db=db_session)
                execution_id = report_execution.id

            # Set execution status to PROCESSING
            report_execution.status = ReportStatus.PROCESSING
            db_session.commit()

            # Apply any parameter overrides to the report parameters
            report_parameters = report.parameters.copy()
            if parameters_override:
                report_parameters.update(parameters_override)

            # Create the output directory if it doesn't exist
            output_dir = settings.REPORT_OUTPUT_DIR
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Generate a unique filename for the report output
            output_path = _get_report_output_path(report=report, execution=report_execution)

            # Initialize the PresentationService
            presentation_service = PresentationService()

            # Try to format and export the report using the appropriate format
            formatted_result = presentation_service.format_result(analysis_id=report.analysis_result_id, output_format=report.format, include_visualization=report.include_visualization)
            with open(output_path, "w") as f:
                f.write(formatted_result["output"])

            # If successful, update the execution status to COMPLETED
            report_execution.output_location = output_path
            report_execution.status = ReportStatus.COMPLETED
            report_execution.complete()
            db_session.commit()

            # Update the report's last_run_at timestamp
            report.update_last_run()
            db_session.commit()

            # If notification settings are configured, send a notification
            _send_report_notification(report=report, execution=report_execution, scheduled_report=None)

            # Log the completion of the report generation
            logger.info(f"Report generation completed successfully for report_id: {report_id}, execution_id: {execution_id}")
            return {"execution_id": execution_id, "status": "COMPLETED", "output_location": output_path}

    except ReportNotFoundException as e:
        logger.error(f"Report not found: {e}", exc_info=True)
        return {"execution_id": execution_id, "status": "FAILED", "error_message": str(e)}
    except ReportExecutionNotFoundException as e:
        logger.error(f"Report Execution not found: {e}", exc_info=True)
        return {"execution_id": execution_id, "status": "FAILED", "error_message": str(e)}
    except Exception as e:
        # If any exception occurs, set execution status to FAILED with error message
        error_message = f"Report generation failed: {str(e)}"
        logger.error(error_message, exc_info=True)
        if db_session and report_execution:
            report_execution.fail(error_message)
            db_session.commit()
        return {"execution_id": execution_id, "status": "FAILED", "error_message": error_message}


@celery_app.task(name='reporting.run_scheduled_report', bind=True, max_retries=3)
def run_scheduled_report(self, scheduled_report_id: str) -> dict:
    """
    Celery task that executes a scheduled report
    """
    logger.info(f"Starting scheduled report execution for scheduled_report_id: {scheduled_report_id}")
    db_session = None
    try:
        # Get a database session using get_db()
        with get_db() as db:
            db_session = db
            # Try to retrieve the scheduled report by ID, handle ScheduledReportNotFoundException
            scheduled_report = db_session.query(ScheduledReport).get(scheduled_report_id)
            if not scheduled_report:
                raise ScheduledReportNotFoundException(f"ScheduledReport not found with id: {scheduled_report_id}")

            # Check if the scheduled report is active, skip if not
            if not scheduled_report.active:
                logger.info(f"Scheduled report is inactive, skipping: {scheduled_report_id}")
                return {"scheduled_report_id": scheduled_report_id, "status": "SKIPPED", "message": "Scheduled report is inactive"}

            # Create a new report execution for this scheduled run
            report_execution = _create_report_execution(report=scheduled_report.report, scheduled_report_id=scheduled_report_id, user_id=scheduled_report.created_by, db=db_session)
            execution_id = report_execution.id

            # Call generate_report task with the report ID and execution ID
            generate_report_result = generate_report.delay(report_id=scheduled_report.report_id, execution_id=execution_id, user_id=scheduled_report.created_by)

            # Update the scheduled report's last_run_at and next_run_at timestamps
            scheduled_report.update_last_run(ReportStatus.PROCESSING)
            db_session.commit()

            # Log the completion of the scheduled report execution
            logger.info(f"Scheduled report execution initiated successfully for scheduled_report_id: {scheduled_report_id}, task_id: {generate_report_result.id}")
            return {"scheduled_report_id": scheduled_report_id, "status": "PENDING", "task_id": generate_report_result.id}

    except ScheduledReportNotFoundException as e:
        logger.error(f"Scheduled report not found: {e}", exc_info=True)
        return {"scheduled_report_id": scheduled_report_id, "status": "FAILED", "error_message": str(e)}
    except Exception as e:
        logger.error(f"Scheduled report execution failed: {str(e)}", exc_info=True)
        return {"scheduled_report_id": scheduled_report_id, "status": "FAILED", "error_message": str(e)}


@celery_app.task(name='reporting.batch_generate_reports', bind=True)
def batch_generate_reports(self, report_ids: List[str], user_id: Optional[str] = None) -> dict:
    """
    Celery task that generates multiple reports in batch
    """
    logger.info(f"Starting batch report generation for report_ids: {report_ids}, user_id: {user_id}")
    results = {}
    try:
        # Initialize results dictionary to track each report's status
        # For each report ID in the list:
        for report_id in report_ids:
            # Call generate_report task asynchronously
            task = generate_report.delay(report_id=report_id, user_id=user_id)
            # Add the task ID to the results dictionary
            results[report_id] = task.id

        # Log the completion of batch report generation initiation
        logger.info(f"Batch report generation initiated successfully for report_ids: {report_ids}")
        return results
    except Exception as e:
        logger.error(f"Batch report generation failed: {str(e)}", exc_info=True)
        return {"status": "FAILED", "error_message": str(e)}


@celery_app.task(name='reporting.check_scheduled_reports', bind=True)
def check_scheduled_reports(self) -> dict:
    """
    Celery task that checks for scheduled reports due to run
    """
    logger.info("Starting scheduled reports check")
    results = {}
    db_session = None
    try:
        # Get a database session using get_db()
        with get_db() as db:
            db_session = db
            # Get current UTC datetime
            now = datetime.utcnow()

            # Query for active scheduled reports with next_run_at <= current time
            scheduled_reports = db_session.query(ScheduledReport).filter(
                ScheduledReport.active == True,
                ScheduledReport.next_run_at <= now
            ).all()

            # Initialize results dictionary to track scheduled reports
            # For each scheduled report due to run:
            for scheduled_report in scheduled_reports:
                # Call run_scheduled_report task asynchronously
                task = run_scheduled_report.delay(scheduled_report_id=scheduled_report.id)
                # Add the task ID to the results dictionary
                results[scheduled_report.id] = task.id

        # Log the completion of scheduled reports check
        logger.info(f"Scheduled reports check completed successfully, initiated {len(results)} reports")
        return results
    except Exception as e:
        logger.error(f"Scheduled reports check failed: {str(e)}", exc_info=True)
        return {"status": "FAILED", "error_message": str(e)}


@celery_app.task(name='reporting.cleanup_report_executions', bind=True)
def cleanup_report_executions(self, days_to_keep: Optional[int] = None) -> dict:
    """
    Celery task that cleans up old report executions
    """
    logger.info("Starting report executions cleanup")
    db_session = None
    try:
        # Get a database session using get_db()
        with get_db() as db:
            db_session = db
            # Set days_to_keep to provided value or default (30)
            days_to_keep = days_to_keep if days_to_keep is not None else 30

            # Calculate the cutoff date (current date - days_to_keep)
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_to_keep)

            # Query for report executions older than the cutoff date
            old_executions = db_session.query(ReportExecution).filter(ReportExecution.created_at < cutoff_date).all()

            # Delete the old executions from the database
            num_deleted = 0
            for execution in old_executions:
                db_session.delete(execution)
                num_deleted += 1
            db_session.commit()

            # Log the number of executions cleaned up
            logger.info(f"Report executions cleanup completed successfully, deleted {num_deleted} executions")
            return {"status": "COMPLETED", "deleted": num_deleted}
    except Exception as e:
        logger.error(f"Report executions cleanup failed: {str(e)}", exc_info=True)
        return {"status": "FAILED", "error_message": str(e)}


def _create_report_execution(report: Report, scheduled_report_id: Optional[str], user_id: Optional[str], db: sqlalchemy.orm.Session) -> ReportExecution:
    """
    Helper function to create a new report execution record
    """
    # Create a new ReportExecution instance
    report_execution = ReportExecution(
        report_id=report.id,
        execution_parameters=report.parameters,
        scheduled_report_id=scheduled_report_id,
        created_by=user_id or report.created_by
    )
    # Add the execution to the database session
    db.add(report_execution)
    db.flush()
    return report_execution


def _get_report_output_path(report: Report, execution: ReportExecution) -> str:
    """
    Helper function to generate the output file path for a report
    """
    # Create the base output directory if it doesn't exist
    output_dir = settings.REPORT_OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate a unique filename based on report ID, execution ID, and timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{report.id}_execution_{execution.id}_{timestamp}"

    # Add appropriate file extension based on report format (.json, .csv, .txt)
    if report.format == ReportFormat.JSON:
        filename += ".json"
    elif report.format == ReportFormat.CSV:
        filename += ".csv"
    elif report.format == ReportFormat.TEXT:
        filename += ".txt"
    else:
        filename += ".unknown"

    # Combine the output directory and filename to create the full path
    output_path = os.path.join(output_dir, filename)
    return output_path


def _send_report_notification(report: Report, execution: ReportExecution, scheduled_report: Optional[ScheduledReport]) -> bool:
    """
    Helper function to send notifications for completed reports
    """
    # Check if notification settings are configured
    if not settings.EMAIL_SENDER or not settings.SMTP_SERVER:
        logger.warning("Notification settings are not configured, skipping notification")
        return False

    # Initialize the NotificationService
    notification_service = NotificationService()

    # Prepare notification data with report and execution details
    title = f"Report '{report.name}' generated successfully"
    message = f"Report '{report.name}' has been generated. View it at: {execution.output_location}"
    data = {
        "report_id": report.id,
        "report_name": report.name,
        "execution_id": execution.id,
        "output_location": execution.output_location
    }

    # If scheduled report is provided, include scheduled report details
    if scheduled_report:
        title = f"Scheduled Report '{report.name}' generated successfully"
        message = f"Scheduled Report '{report.name}' has been generated. View it at: {execution.output_location}"
        data["scheduled_report_id"] = scheduled_report.id

    # Call send_report_notification with the prepared data
    try:
        sent = notification_service.send_notification(
            user=report.created_by,
            title=title,
            message=message,
            notification_type="REPORT",
            priority="INFO",
            data=data
        )
        if sent:
            logger.info(f"Report generation notification sent successfully for report_id: {report.id}, execution_id: {execution.id}")
            return True
        else:
            logger.warning(f"Failed to send report generation notification for report_id: {report.id}, execution_id: {execution.id}")
            return False
    except Exception as e:
        logger.error(f"Error sending report generation notification: {str(e)}", exc_info=True)
        return False