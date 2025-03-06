#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core service module for data ingestion in the Freight Price Movement Agent.
Provides functionality to collect, validate, normalize, and store freight pricing data from multiple sources
including CSV files, databases, APIs, TMS and ERP systems.
"""

import os
import uuid
import pandas  # version ^1.5.0
from datetime import datetime
from typing import Dict, List, Optional, Union

from ..core.config import settings  # Access application configuration settings
from ..core.logging import get_logger  # Configure logging for the data ingestion service
from ..core.exceptions import DataSourceException, ValidationException  # Handle data source and validation exceptions
from ..core.db import get_db, session_scope  # Database session management
from ..connectors.file_connector import FileConnector, CSVConnector  # Connect to and process file-based data sources
from ..connectors.database_connector import DatabaseConnector  # Connect to and query database data sources
from ..connectors.tms_connector import create_tms_connector  # Create appropriate TMS connector based on TMS type
from ..connectors.erp_connector import create_erp_connector  # Create appropriate ERP connector based on ERP type
from ..models.freight_data import FreightData  # ORM model for freight pricing data
from ..utils.validators import validate_freight_data, validate_data_source_config  # Validate freight data and data source configurations
from .error_handling import retry, circuit_breaker, with_error_handling  # Error handling and resilience patterns

# Initialize logger
logger = get_logger(__name__)


def create_data_source_connector(data_source_config: Dict) -> Union[FileConnector, CSVConnector, DatabaseConnector]:
    """
    Factory function to create the appropriate data source connector based on source type

    Args:
        data_source_config (dict): Data source configuration

    Returns:
        object: Appropriate connector instance for the data source
    """
    try:
        # Validate data source configuration
        validate_data_source_config(data_source_config)

        # Extract source_type from configuration
        source_type = data_source_config['source_type'].upper()

        # Create and return appropriate connector based on source_type
        if source_type == 'FILE':
            file_path = data_source_config['file_path']
            return FileConnector(file_path, data_source_config)
        elif source_type == 'CSV':
            file_path = data_source_config['file_path']
            return CSVConnector(file_path, data_source_config)
        elif source_type == 'DATABASE':
            connection_string = data_source_config['connection_string']
            return DatabaseConnector(connection_string, database_type=data_source_config.get('database_type', 'postgresql'))
        elif source_type == 'TMS':
            return create_tms_connector(data_source_config)
        elif source_type == 'ERP':
            return create_erp_connector(data_source_config['erp_type'], data_source_config)
        elif source_type == 'API':
            # Assuming a GenericAPIConnector can handle this
            from ..connectors.generic_api_connector import GenericAPIConnector
            return GenericAPIConnector(data_source_config)
        else:
            raise DataSourceException(f"Unsupported source type: {source_type}")

        logger.info(f"Created connector for source type: {source_type}")

    except DataSourceException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating data source connector: {str(e)}", exc_info=True)
        raise DataSourceException(f"Failed to create data source connector: {str(e)}")


@retry(max_attempts=3, exceptions_to_retry=[DataSourceException])
@circuit_breaker(failure_threshold=5)
def ingest_data_from_source(data_source_config: Dict, query_params: Optional[Dict] = None) -> Dict:
    """
    Ingests data from a specified data source into the system

    Args:
        data_source_config (dict): Data source configuration
        query_params (typing.Optional[dict]): Optional query parameters

    Returns:
        dict: Ingestion result with statistics and status
    """
    try:
        # Create appropriate connector using create_data_source_connector
        connector = create_data_source_connector(data_source_config)

        # Fetch data from the source using connector.fetch_freight_data
        data = connector.fetch_freight_data(query_params)

        # Validate the fetched data using validate_freight_data
        # validate_freight_data(data)

        # Store the data in the database using store_freight_data
        result = store_freight_data(data, data_source_config.get('name'))

        # Log ingestion statistics (record count, validation results)
        logger.info(f"Data ingestion completed successfully from {data_source_config['name']}")

        # Return ingestion result with statistics and status
        return result

    except DataSourceException as e:
        logger.error(f"Data ingestion failed from {data_source_config['name']}: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Data ingestion failed from {data_source_config['name']}: {str(e)}", exc_info=True)
        raise DataSourceException(f"Data ingestion failed: {str(e)}")


@with_error_handling(context='Storing freight data')
def store_freight_data(data: pandas.DataFrame, source_system: Optional[str] = None) -> Dict:
    """
    Stores validated freight data in the database

    Args:
        data (pandas.DataFrame): Validated freight data
        source_system (typing.Optional[str]): Source system identifier

    Returns:
        dict: Storage result with record count and status
    """
    # Validate that data is a pandas DataFrame and not empty
    if not isinstance(data, pandas.DataFrame) or data.empty:
        raise ValidationException("Data must be a non-empty pandas DataFrame")

    # Ensure required columns are present
    required_columns = ['record_date', 'origin', 'destination', 'carrier', 'freight_charge', 'currency_code', 'transport_mode']
    if not all(col in data.columns for col in required_columns):
        raise ValidationException(f"Missing required columns in DataFrame: {required_columns}")

    # Convert DataFrame to list of dictionaries
    data_list = data.to_dict(orient='records')

    # Use session_scope to manage database transaction
    with session_scope() as db:
        # Create FreightData objects from the dictionaries
        freight_data_objects = [FreightData(**item) for item in data_list]

        # Add FreightData objects to the session
        db.add_all(freight_data_objects)

        # Commit the transaction
        db.commit()

    # Log successful storage with record count
    record_count = len(freight_data_objects)
    logger.info(f"Successfully stored {record_count} freight data records in the database")

    # Return storage result with record count and status
    return {"status": "success", "record_count": record_count}


def validate_and_transform_data(data: pandas.DataFrame, field_mapping: Optional[Dict] = None) -> pandas.DataFrame:
    """
    Validates and transforms raw data to match the required format

    Args:
        data (pandas.DataFrame): Raw data
        field_mapping (typing.Optional[dict]): Optional field mapping

    Returns:
        pandas.DataFrame: Validated and transformed data
    """
    # Validate that data is a pandas DataFrame and not empty
    if not isinstance(data, pandas.DataFrame) or data.empty:
        raise ValidationException("Data must be a non-empty pandas DataFrame")

    # Apply field mapping if provided to standardize column names
    if field_mapping:
        data = data.rename(columns=field_mapping)

    # Validate required fields are present
    required_fields = ['record_date', 'origin', 'destination', 'carrier', 'freight_charge', 'currency_code', 'transport_mode']
    if not all(col in data.columns for col in required_fields):
        raise ValidationException(f"Missing required columns: {required_fields}")

    # Convert data types to appropriate formats (dates, numeric values)
    # Apply data quality checks and flag potential issues
    # Remove or handle invalid records based on validation rules
    # Log validation results including any issues found

    # Return the validated and transformed DataFrame
    return data


def get_data_source_status(data_source_config: Dict) -> Dict:
    """
    Checks the status and availability of a data source

    Args:
        data_source_config (dict): Data source configuration

    Returns:
        dict: Status information including availability and metadata
    """
    # Create appropriate connector using create_data_source_connector
    # Test connection to the data source
    # Gather metadata about the data source (record count, last update)
    # Return status information with availability flag and metadata
    # Handle connection failures with appropriate error messages
    return {}


def schedule_data_ingestion(data_source_config: Dict, schedule: str, query_params: Optional[Dict] = None) -> Dict:
    """
    Schedules a data ingestion job for periodic execution

    Args:
        data_source_config (dict): Data source configuration
        schedule (str): Schedule
        query_params (typing.Optional[dict]): Optional query parameters

    Returns:
        dict: Scheduling result with job ID and status
    """
    # Validate data source configuration
    # Validate schedule format (cron expression or interval)
    # Create a scheduled job in the task scheduler
    # Store job configuration for future execution
    # Return scheduling result with job ID and status
    # Handle scheduling failures with appropriate error messages
    return {}


class DataIngestionService:
    """
    Service class that manages data ingestion from various sources
    """

    def __init__(self):
        """
        Initializes the DataIngestionService
        """
        # Initialize logger
        self.logger = get_logger(__name__)

        # Initialize empty dictionaries for data sources and scheduled jobs
        self._data_sources: Dict = {}
        self._scheduled_jobs: Dict = {}

        # Load any previously configured data sources from storage
        # TODO: Implement loading from persistent storage
        self.logger.info("DataIngestionService initialized")

    def register_data_source(self, name: str, config: Dict) -> str:
        """
        Registers a new data source configuration

        Args:
            name (str): Data source name
            config (dict): Data source configuration

        Returns:
            str: Data source ID
        """
        try:
            # Validate data source configuration
            validate_data_source_config(config)

            # Generate a unique ID for the data source
            data_source_id = str(uuid.uuid4())

            # Store the configuration with name and ID
            self._data_sources[data_source_id] = {"name": name, "config": config}

            # Test the connection to verify configuration
            # TODO: Implement connection testing

            # Log successful registration
            self.logger.info(f"Data source '{name}' registered with ID: {data_source_id}")

            # Return the data source ID
            return data_source_id

        except Exception as e:
            self.logger.error(f"Failed to register data source '{name}': {str(e)}", exc_info=True)
            raise

    def get_data_source(self, identifier: Union[str, Dict]) -> Dict:
        """
        Retrieves a data source configuration by ID or name

        Args:
            identifier (typing.Union[str, dict]): Data source ID or name

        Returns:
            dict: Data source configuration
        """
        try:
            if isinstance(identifier, str):
                # Look up by ID
                if identifier in self._data_sources:
                    return self._data_sources[identifier]
                else:
                    # Look up by name
                    for ds_id, ds in self._data_sources.items():
                        if ds['name'] == identifier:
                            return ds
                    raise DataSourceException(f"Data source with ID or name '{identifier}' not found")
            elif isinstance(identifier, Dict):
                # Use it directly as configuration
                return identifier
            else:
                raise DataSourceException(f"Invalid identifier type: {type(identifier)}")
        except Exception as e:
            self.logger.error(f"Failed to get data source '{identifier}': {str(e)}", exc_info=True)
            raise

    def ingest_data(self, data_source: Union[str, Dict], query_params: Optional[Dict] = None) -> Dict:
        """
        Ingests data from a registered or provided data source

        Args:
            data_source (typing.Union[str, dict]): Data source ID or configuration
            query_params (typing.Optional[dict]): Optional query parameters

        Returns:
            dict: Ingestion result with statistics and status
        """
        try:
            # Get data source configuration using get_data_source
            data_source_config = self.get_data_source(data_source)

            # Call ingest_data_from_source with the configuration
            result = ingest_data_from_source(data_source_config['config'], query_params)

            # Log ingestion result
            self.logger.info(f"Data ingestion completed for data source: {data_source}")

            # Return the ingestion result
            return result

        except Exception as e:
            self.logger.error(f"Data ingestion failed for data source '{data_source}': {str(e)}", exc_info=True)
            raise

    def schedule_ingestion(self, data_source: Union[str, Dict], schedule: str, query_params: Optional[Dict] = None) -> Dict:
        """
        Schedules periodic ingestion from a data source

        Args:
            data_source (typing.Union[str, dict]): Data source ID or configuration
            schedule (str): Schedule
            query_params (typing.Optional[dict]): Optional query parameters

        Returns:
            dict: Scheduling result with job ID and status
        """
        try:
            # Get data source configuration using get_data_source
            data_source_config = self.get_data_source(data_source)

            # Call schedule_data_ingestion with configuration and schedule
            result = schedule_data_ingestion(data_source_config['config'], schedule, query_params)

            # Store the scheduled job information
            # TODO: Implement job storage

            # Log scheduling result
            self.logger.info(f"Data ingestion scheduled for data source: {data_source}")

            # Return the scheduling result
            return result

        except Exception as e:
            self.logger.error(f"Data ingestion scheduling failed for data source '{data_source}': {str(e)}", exc_info=True)
            raise

    def cancel_scheduled_ingestion(self, job_id: str) -> bool:
        """
        Cancels a scheduled ingestion job

        Args:
            job_id (str): Job ID

        Returns:
            bool: True if cancellation successful, False otherwise
        """
        try:
            # Check if job_id exists in _scheduled_jobs
            if job_id not in self._scheduled_jobs:
                self.logger.warning(f"Scheduled job with ID '{job_id}' not found")
                return False

            # Remove the job from the task scheduler
            # TODO: Implement task scheduler removal

            # Remove the job from _scheduled_jobs
            del self._scheduled_jobs[job_id]

            # Log cancellation result
            self.logger.info(f"Scheduled job with ID '{job_id}' cancelled successfully")

            # Return True if successful, False otherwise
            return True

        except Exception as e:
            self.logger.error(f"Failed to cancel scheduled job with ID '{job_id}': {str(e)}", exc_info=True)
            return False

    def list_data_sources(self) -> List:
        """
        Lists all registered data sources

        Returns:
            list: List of data source configurations
        """
        # Return a list of all data sources in _data_sources
        # Include basic metadata but exclude sensitive information
        data_sources = []
        for ds_id, ds in self._data_sources.items():
            data_sources.append({
                "id": ds_id,
                "name": ds["name"],
                "source_type": ds["config"]["source_type"],
                "description": ds["config"]["description"]
            })
        return data_sources

    def list_scheduled_jobs(self) -> List:
        """
        Lists all scheduled ingestion jobs

        Returns:
            list: List of scheduled job information
        """
        # Return a list of all jobs in _scheduled_jobs
        # Include job ID, data source, schedule, and status
        return []

    def update_data_source(self, source_id: str, updated_config: Dict) -> Dict:
        """
        Updates an existing data source configuration

        Args:
            source_id (str): Data source ID
            updated_config (dict): Updated configuration

        Returns:
            dict: Updated data source configuration
        """
        try:
            # Check if source_id exists in _data_sources
            if source_id not in self._data_sources:
                raise DataSourceException(f"Data source with ID '{source_id}' not found")

            # Validate updated configuration
            validate_data_source_config(updated_config)

            # Merge updated configuration with existing one
            existing_config = self._data_sources[source_id]["config"]
            merged_config = {**existing_config, **updated_config}

            # Test the connection with updated configuration
            # TODO: Implement connection testing

            # Update the stored configuration
            self._data_sources[source_id]["config"] = merged_config

            # Log update result
            self.logger.info(f"Data source with ID '{source_id}' updated successfully")

            # Return the updated configuration
            return merged_config

        except Exception as e:
            self.logger.error(f"Failed to update data source with ID '{source_id}': {str(e)}", exc_info=True)
            raise

    def delete_data_source(self, source_id: str) -> bool:
        """
        Deletes a registered data source

        Args:
            source_id (str): Data source ID

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # Check if source_id exists in _data_sources
            if source_id not in self._data_sources:
                self.logger.warning(f"Data source with ID '{source_id}' not found")
                return False

            # Cancel any scheduled jobs for this data source
            # TODO: Implement job cancellation

            # Remove the data source from _data_sources
            del self._data_sources[source_id]

            # Log deletion result
            self.logger.info(f"Data source with ID '{source_id}' deleted successfully")

            # Return True if successful, False otherwise
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete data source with ID '{source_id}': {str(e)}", exc_info=True)
            return False

    def preview_data(self, data_source: Union[str, Dict], query_params: Optional[Dict] = None, limit: Optional[int] = 10) -> pandas.DataFrame:
        """
        Previews data from a data source without storing it

        Args:
            data_source (typing.Union[str, dict]): Data source ID or configuration
            query_params (typing.Optional[dict]): Optional query parameters
            limit (typing.Optional[int]): Limit

        Returns:
            pandas.DataFrame: Preview of the data
        """
        try:
            # Get data source configuration using get_data_source
            data_source_config = self.get_data_source(data_source)

            # Create appropriate connector
            connector = create_data_source_connector(data_source_config['config'])

            # Fetch limited data from the source
            # Apply validation and transformation
            df = connector.fetch_freight_data(query_params)

            # Return the preview data without storing it
            return df.head(limit)

        except Exception as e:
            self.logger.error(f"Failed to preview data from data source '{data_source}': {str(e)}", exc_info=True)
            raise


class DataIngestionResult:
    """
    Class representing the result of a data ingestion operation
    """

    def __init__(self, success: bool, total_records: int, valid_records: Optional[int] = None,
                 invalid_records: Optional[int] = None, errors: Optional[List] = None,
                 warnings: Optional[List] = None, source_type: Optional[str] = None, source_name: Optional[str] = None):
        """
        Initializes a new DataIngestionResult

        Args:
            success (bool): Success flag
            total_records (int): Total records count
            valid_records (typing.Optional[int]): Valid records count
            invalid_records (typing.Optional[int]): Invalid records count
            errors (typing.Optional[list]): Errors list
            warnings (typing.Optional[list]): Warnings list
            source_type (typing.Optional[str]): Source type
            source_name (typing.Optional[str]): Source name
        """
        self.success = success
        self.total_records = total_records
        self.valid_records = valid_records if valid_records is not None else total_records
        self.invalid_records = invalid_records if invalid_records is not None else 0
        self.errors = errors if errors is not None else []
        self.warnings = warnings if warnings is not None else []
        self.timestamp = datetime.utcnow()
        self.source_type = source_type
        self.source_name = source_name

    def to_dict(self) -> Dict:
        """
        Converts the result to a dictionary

        Returns:
            dict: Dictionary representation of the result
        """
        return {
            "success": self.success,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat(),
            "source_type": self.source_type,
            "source_name": self.source_name
        }

    def add_error(self, error_message: str, error_details: Optional[Dict] = None) -> None:
        """
        Adds an error to the result

        Args:
            error_message (str): Error message
            error_details (typing.Optional[dict]): Error details
        """
        self.errors.append({"message": error_message, "details": error_details})
        self.invalid_records += 1
        self.success = False

    def add_warning(self, warning_message: str, warning_details: Optional[Dict] = None) -> None:
        """
        Adds a warning to the result

        Args:
            warning_message (str): Warning message
            warning_details (typing.Optional[dict]): Warning details
        """
        self.warnings.append({"message": warning_message, "details": warning_details})

    def summary(self) -> str:
        """
        Returns a summary of the ingestion result

        Returns:
            str: Summary string
        """
        return (
            f"Ingestion Summary: Success={self.success}, "
            f"Total Records={self.total_records}, "
            f"Valid Records={self.valid_records}, "
            f"Invalid Records={self.invalid_records}, "
            f"Errors={len(self.errors)}, "
            f"Warnings={len(self.warnings)}"
        )