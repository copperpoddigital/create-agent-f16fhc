# src/backend/api/reports/utils.py
"""Utility functions for the reports module of the Freight Price Movement Agent.
This file provides helper functions for report generation, validation, file management, and scheduled report processing.
"""

import os  # standard library
import uuid  # standard library
import datetime  # standard library
import typing  # standard library
import shutil  # standard library

import sqlalchemy  # package_version: 1.4.x
from sqlalchemy.orm import Session  # package_version: 1.4.x
import fastapi  # package_version: 0.95.x
from fastapi import HTTPException, status  # package_version: 0.95.x
import pydantic  # package_version: 1.10.x
from pydantic import ValidationError  # package_version: 1.10.x

from src.backend.core.config import settings  # Access configuration settings for report storage and retention
from src.backend.core.db import db  # Database session for ORM operations
from src.backend.core.logging import logger  # Logging utility for report operations
from src.backend.core.exceptions import AnalysisException  # Exception handling for analysis operations
from src.backend.models.enums import ReportFormat  # Enum for report format types
from src.backend.models.enums import ReportStatus  # Enum for report status tracking
from src.backend.models.enums import ScheduleFrequency  # Enum for report scheduling frequency
from src.backend.services.analysis_engine import AnalysisEngine  # Engine for performing freight price analysis
from src.backend.services.presentation import PresentationService  # Service for formatting and delivering analysis results
from src.backend.services.notifications import NotificationService  # Service for sending notifications about report execution
from src.backend.models.report import Report  # Import the Report model

REPORT_FILE_EXTENSION_MAP = {
    ReportFormat.JSON: 'json',
    ReportFormat.CSV: 'csv',
    ReportFormat.TEXT: 'txt'
}


def generate_report(report: Report, user_id: typing.Optional[str] = None, execution_id: typing.Optional[str] = None) -> str:
    """
    Generates a report file based on the report configuration and saves it to the file system.

    Args:
        report (Report): The report object containing configuration details.
        user_id (typing.Optional[str], optional): The ID of the user generating the report. Defaults to None.
        execution_id (typing.Optional[str], optional): The ID of the report execution. Defaults to None.

    Returns:
        str: Path to the generated report file.
    """
    logger.info(f"Starting report generation for report ID: {report.id}, execution ID: {execution_id}")

    try:
        # Create the report storage directory if it doesn't exist
        report_dir = create_report_directory()

        # Initialize the analysis engine
        analysis_engine = AnalysisEngine()

        # Retrieve the analysis result using the report's analysis_result_id
        analysis_result = analysis_engine.get_analysis_result(report.analysis_id)
        if not analysis_result:
            raise AnalysisException(f"Analysis result not found: {report.analysis_id}")

        # Initialize the presentation service
        presentation_service = PresentationService(analysis_engine=analysis_engine)

        # Format the analysis result according to the report's format
        formatted_result = presentation_service.format_result(
            analysis_id=report.analysis_id,
            output_format=report.format,
            include_visualization=report.include_visualization
        )

        # Generate a unique filename for the report
        file_extension = REPORT_FILE_EXTENSION_MAP.get(report.format)
        if not file_extension:
            raise ValueError(f"Unsupported report format: {report.format}")

        filename = f"{report.id}"
        if execution_id:
            filename += f"_{execution_id}"
        filename += f".{file_extension}"

        # Construct the full path to the report file
        file_path = os.path.join(report_dir, filename)

        # Export the formatted result to a file
        with open(file_path, "w") as f:
            f.write(formatted_result["output"])

        # Update the report's file_path attribute
        with db.session() as session:
            db_report = session.query(Report).get(report.id)
            if db_report:
                db_report.file_path = file_path
                db_report.last_generated_at = datetime.datetime.utcnow()
                session.commit()
            else:
                logger.error(f"Report with ID {report.id} not found in the database.")
                raise ValueError(f"Report with ID {report.id} not found in the database.")

        logger.info(f"Successfully generated report file: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        raise


def delete_report_file(report: Report) -> bool:
    """
    Deletes a report file from the file system.

    Args:
        report (Report): The report object.

    Returns:
        bool: True if file was deleted, False otherwise.
    """
    try:
        # Check if the report has a file_path attribute
        if not hasattr(report, 'file_path'):
            logger.warning(f"Report object does not have a file_path attribute.")
            return False

        # If file_path is None, return False (nothing to delete)
        if report.file_path is None:
            logger.info(f"Report {report.id} has no file_path, nothing to delete.")
            return False

        # Construct the full path to the report file
        file_path = report.file_path

        # Check if the file exists
        if os.path.exists(file_path):
            # If the file exists, delete it and return True
            os.remove(file_path)
            logger.info(f"Deleted report file: {file_path}")
            return True
        else:
            # If the file doesn't exist, log a warning and return False
            logger.warning(f"Report file not found, cannot delete: {file_path}")
            return False

    except Exception as e:
        logger.error(f"Error deleting report file: {str(e)}", exc_info=True)
        return False


def get_due_scheduled_reports(current_time: typing.Optional[datetime.datetime] = None) -> typing.List[dict]:
    """
    Retrieves scheduled reports that are due for execution.

    Args:
        current_time (typing.Optional[datetime.datetime], optional): The current time. Defaults to None.

    Returns:
        typing.List[dict]: List of scheduled reports due for execution.
    """
    try:
        # If current_time is not provided, use the current UTC time
        if current_time is None:
            current_time = datetime.datetime.utcnow()

        # Query the database for scheduled reports where next_run_at <= current_time and active is True
        with db.session() as session:
            due_reports = session.query(Report).filter(
                Report.scheduled == True,
                Report.schedule_frequency != None,
                Report.next_run_at <= current_time,
                Report.active == True
            ).all()

        # Filter out reports with status other than PENDING or COMPLETED
        due_reports = [report for report in due_reports]

        logger.info(f"Found {len(due_reports)} scheduled reports due for execution.")
        return [report.to_dict() for report in due_reports]

    except Exception as e:
        logger.error(f"Error retrieving due scheduled reports: {str(e)}", exc_info=True)
        return []


def update_scheduled_report_status(scheduled_report_id: str, status: ReportStatus, error_message: typing.Optional[str] = None) -> bool:
    """
    Updates the status of a scheduled report after execution.

    Args:
        scheduled_report_id (str): The ID of the scheduled report.
        status (ReportStatus): The new status of the report.
        error_message (typing.Optional[str], optional): An error message if the report failed. Defaults to None.

    Returns:
        bool: True if update was successful, False otherwise.
    """
    try:
        # Query the database for the scheduled report with the given ID
        with db.session() as session:
            report = session.query(Report).get(scheduled_report_id)

            # If the report is not found, log an error and return False
            if report is None:
                logger.error(f"Scheduled report not found: {scheduled_report_id}")
                return False

            # Update the report's status to the provided status
            report.status = status

            # If error_message is provided, store it in the report's metadata
            if error_message:
                report.error_message = error_message

            # Update the report's last_run_at timestamp to the current time
            report.last_generated_at = datetime.datetime.utcnow()

            # Calculate and update the next_run_at timestamp based on the schedule frequency
            if report.schedule_frequency:
                if report.schedule_frequency == ScheduleFrequency.DAILY:
                    report.next_run_at = report.last_generated_at + datetime.timedelta(days=1)
                elif report.schedule_frequency == ScheduleFrequency.WEEKLY:
                    report.next_run_at = report.last_generated_at + datetime.timedelta(weeks=1)
                elif report.schedule_frequency == ScheduleFrequency.MONTHLY:
                    # Calculate the next month
                    next_month = report.last_generated_at.month % 12 + 1
                    next_year = report.last_generated_at.year + (report.last_generated_at.month // 12)
                    report.next_run_at = report.last_generated_at.replace(year=next_year, month=next_month, day=1)
                else:
                    logger.warning(f"Unsupported schedule frequency: {report.schedule_frequency}")
                    report.next_run_at = None

            # Commit the changes to the database
            session.commit()

        logger.info(f"Updated scheduled report {scheduled_report_id} status to {status}.")
        return True

    except Exception as e:
        logger.error(f"Error updating scheduled report status: {str(e)}", exc_info=True)
        return False


def send_report_notification(report: Report, execution_id: str, status: ReportStatus, output_location: typing.Optional[str] = None, error_message: typing.Optional[str] = None) -> bool:
    """
    Sends a notification about a report execution.

    Args:
        report (Report): The report object.
        execution_id (str): The ID of the report execution.
        status (ReportStatus): The status of the report execution.
        output_location (typing.Optional[str], optional): The location of the report output. Defaults to None.
        error_message (typing.Optional[str], optional): An error message if the report failed. Defaults to None.

    Returns:
        bool: True if notification was sent, False otherwise.
    """
    try:
        # Check if the report has notification settings
        if not report.scheduled:
            logger.debug(f"Report {report.id} is not scheduled, skipping notification.")
            return False

        # Prepare the notification content based on the report status
        if status == ReportStatus.COMPLETED:
            title = f"Report '{report.name}' Generated Successfully"
            message = f"Report '{report.name}' was generated successfully at {datetime.datetime.utcnow().isoformat()}."
            if output_location:
                message += f" Output location: {output_location}"
        elif status == ReportStatus.FAILED:
            title = f"Report '{report.name}' Generation Failed"
            message = f"Report '{report.name}' generation failed at {datetime.datetime.utcnow().isoformat()}."
            if error_message:
                message += f" Error: {error_message}"
        else:
            logger.warning(f"Unsupported report status for notification: {status}")
            return False

        # Use the NotificationService to send the notification
        notification_service = NotificationService()
        sent = notification_service.send_notification(
            user=report.created_by,
            title=title,
            message=message,
            notification_type="report_generation",  # Replace with appropriate enum
            priority="high",  # Replace with appropriate enum
            data={"report_id": str(report.id), "execution_id": execution_id, "status": status.name}
        )

        if sent:
            logger.info(f"Report execution notification sent for report {report.id}.")
            return True
        else:
            logger.error(f"Failed to send report execution notification for report {report.id}.")
            return False

    except Exception as e:
        logger.error(f"Error sending report notification: {str(e)}", exc_info=True)
        return False


def validate_report_parameters(parameters: dict) -> bool:
    """
    Validates report parameters against required schema.

    Args:
        parameters (dict): The report parameters to validate.

    Returns:
        bool: True if parameters are valid, False otherwise.
    """
    # Placeholder for validation logic
    return True


def validate_report_filters(filters: dict) -> bool:
    """
    Validates report filters against required schema.

    Args:
        filters (dict): The report filters to validate.

    Returns:
        bool: True if filters are valid, False otherwise.
    """
    # Placeholder for validation logic
    return True


def clean_old_report_files(retention_days: typing.Optional[int] = None) -> int:
    """
    Removes report files that exceed the retention period.

    Args:
        retention_days (typing.Optional[int], optional): The number of days to retain report files. Defaults to None.

    Returns:
        int: Number of files deleted.
    """
    deleted_files_count = 0
    try:
        # If retention_days is not provided, use the configured REPORT_RETENTION_DAYS
        if retention_days is None:
            retention_days = settings.REPORT_RETENTION_DAYS

        # Calculate the cutoff date based on the current date and retention period
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=retention_days)

        # Scan the report storage directory for files
        report_dir = create_report_directory()
        for filename in os.listdir(report_dir):
            file_path = os.path.join(report_dir, filename)

            # Check if it's a file and not a directory
            if os.path.isfile(file_path):
                # Get the file's last modification time
                file_modified_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(file_path))

                # Delete files older than the cutoff date
                if file_modified_time < cutoff_date:
                    os.remove(file_path)
                    deleted_files_count += 1
                    logger.info(f"Deleted old report file: {file_path}")

        logger.info(f"Cleaned up {deleted_files_count} old report files.")
        return deleted_files_count

    except Exception as e:
        logger.error(f"Error cleaning up old report files: {str(e)}", exc_info=True)
        return deleted_files_count


def get_report_file_path(report_id: str, format: ReportFormat, execution_id: typing.Optional[str] = None) -> str:
    """
    Constructs the file path for a report based on its format and ID.

    Args:
        report_id (str): The ID of the report.
        format (ReportFormat): The format of the report.
        execution_id (typing.Optional[str], optional): The ID of the report execution. Defaults to None.

    Returns:
        str: Full path to the report file.
    """
    try:
        # Get the file extension for the specified format from REPORT_FILE_EXTENSION_MAP
        file_extension = REPORT_FILE_EXTENSION_MAP.get(format)
        if not file_extension:
            raise ValueError(f"Unsupported report format: {format}")

        # Create a filename using report_id and execution_id if provided
        filename = f"{report_id}"
        if execution_id:
            filename += f"_{execution_id}"
        filename += f".{file_extension}"

        # Construct the full path using REPORT_STORAGE_PATH and the filename
        report_dir = create_report_directory()
        file_path = os.path.join(report_dir, filename)

        return file_path

    except Exception as e:
        logger.error(f"Error getting report file path: {str(e)}", exc_info=True)
        raise


def create_report_directory() -> str:
    """
    Creates the directory for storing report files if it doesn't exist.

    Returns:
        str: Path to the report directory.
    """
    try:
        # Get the configured REPORT_STORAGE_PATH
        report_storage_path = settings.REPORT_STORAGE_PATH

        # Check if the directory exists
        if not os.path.exists(report_storage_path):
            # If it doesn't exist, create it with appropriate permissions
            os.makedirs(report_storage_path, exist_ok=True)
            logger.info(f"Created report storage directory: {report_storage_path}")

        return report_storage_path

    except Exception as e:
        logger.error(f"Error creating report directory: {str(e)}", exc_info=True)
        raise