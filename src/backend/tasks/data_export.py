"""
Implements asynchronous tasks for exporting analysis results to various formats.
This module provides Celery tasks that handle the export of freight price movement
analysis results to JSON, CSV, and text formats, with optional file storage capabilities.
"""

import os  # File path operations and environment variables
import typing  # Type annotations for better code documentation
import datetime  # Date and time handling for file naming and timestamps

import boto3  # version: ^1.26.0 # AWS S3 integration for file storage

from .worker import celery_app  # Celery application instance for task registration
from ..core.logging import logger  # Logging functionality for export tasks
from ..core.db import session_scope  # Database session context manager
from ..services.analysis_engine import AnalysisEngine  # Retrieve analysis results for export
from ..services.presentation import PresentationService  # Format and export analysis results
from ..models.enums import OutputFormat  # Enumeration of supported output formats

# Global variables for default export directory and S3 configuration
DEFAULT_EXPORT_DIR = os.environ.get('EXPORT_DIR', '/tmp/exports')
S3_BUCKET = os.environ.get('S3_BUCKET', None)
S3_PREFIX = os.environ.get('S3_PREFIX', 'exports')


@celery_app.task(name='export_analysis_result', bind=True, max_retries=3)
def export_analysis_result(self, analysis_id: str,
                           output_format: typing.Optional[str] = None,
                           file_path: typing.Optional[str] = None,
                           include_visualization: typing.Optional[bool] = False,
                           upload_to_s3: typing.Optional[bool] = False) -> dict:
    """
    Celery task that exports an analysis result to the specified format and location.

    Args:
        analysis_id: The ID of the analysis result to export.
        output_format: The desired output format (JSON, CSV, TEXT). Defaults to JSON.
        file_path: The file path to save the exported result. If None, a default path is generated.
        include_visualization: Whether to include visualizations in the export.
        upload_to_s3: Whether to upload the exported file to Amazon S3.

    Returns:
        A dictionary with export result information including file path and status.
    """
    logger.info(f"Starting export of analysis result {analysis_id} to {output_format or 'JSON'}")

    try:
        # Validate the analysis_id parameter
        if not analysis_id:
            raise ValueError("analysis_id must be provided")

        # If output_format is provided as string, convert it to OutputFormat enum
        if output_format:
            try:
                output_format_enum = OutputFormat[output_format.upper()]
            except KeyError:
                raise ValueError(f"Invalid output format: {output_format}")
        # If output_format is not provided, default to JSON
        else:
            output_format_enum = OutputFormat.JSON

        # Create a database session using session_scope
        with session_scope() as session:
            # Initialize AnalysisEngine and PresentationService
            analysis_engine = AnalysisEngine()
            presentation_service = PresentationService(analysis_engine=analysis_engine)

            # Retrieve the analysis result using AnalysisEngine.get_analysis_result()
            analysis_result = analysis_engine.get_analysis_result(analysis_id)

            # If analysis result is not found, log error and raise exception
            if not analysis_result:
                logger.error(f"Analysis result not found: {analysis_id}")
                raise ValueError(f"Analysis result not found: {analysis_id}")

            # If file_path is not provided, generate a default path based on analysis_id and format
            if not file_path:
                file_path = generate_default_file_path(analysis_id, output_format_enum)

            # Ensure the export directory exists
            ensure_export_dir_exists(os.path.dirname(file_path))

            # Use PresentationService.format_result() to format the result to the file
            formatted_result = presentation_service.format_result(
                analysis_id=analysis_id,
                output_format=output_format_enum,
                include_visualization=include_visualization
            )

            # Write the formatted result to the file
            with open(file_path, "w") as f:
                f.write(str(formatted_result["output"]))

            s3_path = None
            # If upload_to_s3 is True and S3_BUCKET is configured, upload the file to S3
            if upload_to_s3:
                s3_path = upload_to_s3(file_path)

            # Log the successful export operation
            logger.info(f"Successfully exported analysis result {analysis_id} to {file_path}")

            # Return a dictionary with export information (file_path, s3_path if applicable, success status)
            return {
                "file_path": file_path,
                "s3_path": s3_path,
                "success": True
            }

    except Exception as e:
        # Log errors, and retry the task if appropriate
        logger.error(f"Error exporting analysis result {analysis_id}: {e}", exc_info=True)
        # Retry the task if max_retries is not exceeded
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task export_analysis_result for analysis {analysis_id} (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
        else:
            logger.error(f"Max retries exceeded for task export_analysis_result for analysis {analysis_id}")
            return {
                "file_path": file_path,
                "s3_path": None,
                "success": False,
                "error": str(e)
            }


def generate_default_file_path(analysis_id: str, output_format: OutputFormat) -> str:
    """
    Generates a default file path for an exported analysis result.

    Args:
        analysis_id: The ID of the analysis result.
        output_format: The desired output format (JSON, CSV, TEXT).

    Returns:
        The generated file path.
    """
    # Create a timestamp string in the format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Determine the file extension based on output_format (json, csv, txt)
    if output_format == OutputFormat.JSON:
        file_extension = "json"
    elif output_format == OutputFormat.CSV:
        file_extension = "csv"
    elif output_format == OutputFormat.TEXT:
        file_extension = "txt"
    else:
        file_extension = "txt"  # Default to txt if format is not recognized

    # Construct the filename using analysis_id, timestamp, and extension
    filename = f"analysis_result_{analysis_id}_{timestamp}.{file_extension}"

    # Ensure the export directory exists
    export_dir = ensure_export_dir_exists()

    # Join the export directory with the filename
    file_path = os.path.join(export_dir, filename)

    # Return the complete file path
    return file_path


def ensure_export_dir_exists(export_dir: typing.Optional[str] = None) -> str:
    """
    Ensures that the export directory exists, creating it if necessary.

    Args:
        export_dir: The export directory path. If None, DEFAULT_EXPORT_DIR is used.

    Returns:
        The path to the export directory.
    """
    # If export_dir is not provided, use DEFAULT_EXPORT_DIR
    export_dir = export_dir or DEFAULT_EXPORT_DIR

    # Check if the directory exists
    if not os.path.exists(export_dir):
        # If not, create the directory with appropriate permissions
        os.makedirs(export_dir, exist_ok=True)
        logger.info(f"Created export directory: {export_dir}")

    # Return the path to the export directory
    return export_dir


def upload_to_s3(file_path: str, bucket: typing.Optional[str] = None,
                 prefix: typing.Optional[str] = None) -> typing.Optional[str]:
    """
    Uploads an exported file to Amazon S3.

    Args:
        file_path: The path to the file to upload.
        bucket: The S3 bucket name. If None, S3_BUCKET is used.
        prefix: The S3 key prefix. If None, S3_PREFIX is used.

    Returns:
        The S3 object URL if successful, None otherwise.
    """
    # If bucket is not provided, use S3_BUCKET
    bucket = bucket or S3_BUCKET

    # If prefix is not provided, use S3_PREFIX
    prefix = prefix or S3_PREFIX

    # If bucket is None, log warning and return None
    if not bucket:
        logger.warning("S3_BUCKET is not configured. Skipping S3 upload.")
        return None

    # Extract the filename from the file_path
    filename = os.path.basename(file_path)

    # Construct the S3 key by joining prefix and filename
    s3_key = f"{prefix}/{filename}"

    try:
        # Initialize boto3 S3 client
        s3_client = boto3.client('s3')

        # Determine content type based on file extension
        content_type = 'application/json'  # Default
        if filename.endswith('.csv'):
            content_type = 'text/csv'
        elif filename.endswith('.txt'):
            content_type = 'text/plain'

        # Upload the file to S3 with appropriate content type
        with open(file_path, 'rb') as f:
            s3_client.upload_fileobj(f, bucket, s3_key, ExtraArgs={'ContentType': content_type})

        # Generate and return the S3 object URL
        s3_url = f"https://{bucket}.s3.amazonaws.com/{s3_key}"
        logger.info(f"Successfully uploaded {file_path} to S3: {s3_url}")
        return s3_url

    except Exception as e:
        logger.error(f"Error uploading {file_path} to S3: {e}", exc_info=True)
        return None