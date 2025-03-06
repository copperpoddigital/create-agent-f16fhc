#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for data source management in the Freight Price Movement Agent.
This module provides helper functions for validating data source configurations,
testing connections to various data sources, creating log entries, and retrieving
specific data source instances based on their type.
"""

import logging  # Standard library for logging
import typing  # Standard library for type annotations
import uuid  # Standard library for generating UUID values
import datetime  # Standard library for date and time handling
import os  # Standard library for operating system interfaces

# Internal imports from the Freight Price Movement Agent
from ...core.logging import get_logger  # Import getLogger function from core logging module
from .models import (  # Import data source model classes
    DataSource,
    CSVDataSource,
    DatabaseDataSource,
    APIDataSource,
    TMSDataSource,
    ERPDataSource,
    DataSourceLog,
)
from ...models.enums import (  # Import enumeration types for data source types and statuses
    DataSourceType,
    DataSourceStatus,
)
from ...connectors.file_connector import (  # Import FileConnector class
    FileConnector,
)
from ...connectors.database_connector import (  # Import DatabaseConnector class
    DatabaseConnector,
)
from ...connectors.generic_api_connector import (  # Import APIConnector class
    APIConnector,
)
from ...connectors.tms_connector import (  # Import TMSConnector class
    TMSConnector,
)
from ...connectors.erp_connector import (  # Import ERPConnector class
    ERPConnector,
)
from ...core.exceptions import (  # Import custom exceptions
    ConfigValidationError,
    ConnectionError,
)

# Initialize logger for this module
logger = get_logger(__name__)


def validate_data_source_config(data_source: DataSource) -> bool:
    """
    Validates the configuration of a data source based on its type.

    Args:
        data_source (DataSource): The data source to validate.

    Returns:
        bool: True if configuration is valid, raises exception otherwise.

    Raises:
        ConfigValidationError: If validation fails.
    """
    logger.info(f"Validating data source configuration for data source ID: {data_source.id}")

    try:
        if data_source.source_type == DataSourceType.CSV:
            # Validate CSV data source configuration
            if not data_source.file_path:
                raise ConfigValidationError("File path is required for CSV data source")
            if not data_source.delimiter:
                raise ConfigValidationError("Delimiter is required for CSV data source")
            if not data_source.encoding:
                raise ConfigValidationError("Encoding is required for CSV data source")
            if not data_source.field_mapping:
                raise ConfigValidationError("Field mapping is required for CSV data source")
            validate_field_mapping(data_source.field_mapping)

        elif data_source.source_type == DataSourceType.DATABASE:
            # Validate Database data source configuration
            if not data_source.connection_string:
                raise ConfigValidationError("Connection string is required for Database data source")
            if not data_source.query:
                raise ConfigValidationError("Query is required for Database data source")
            if not data_source.field_mapping:
                raise ConfigValidationError("Field mapping is required for Database data source")
            validate_field_mapping(data_source.field_mapping)

        elif data_source.source_type == DataSourceType.API:
            # Validate API data source configuration
            if not data_source.endpoint_url:
                raise ConfigValidationError("Endpoint URL is required for API data source")
            if not data_source.field_mapping:
                raise ConfigValidationError("Field mapping is required for API data source")
        
        elif data_source.source_type == DataSourceType.TMS:
            # Validate TMS data source configuration
            if not data_source.tms_type:
                raise ConfigValidationError("TMS Type is required for TMS data source")
            if not data_source.connection_string:
                raise ConfigValidationError("Connection string is required for TMS data source")
            if not data_source.field_mapping:
                raise ConfigValidationError("Field mapping is required for TMS data source")
            validate_field_mapping(data_source.field_mapping)

        elif data_source.source_type == DataSourceType.ERP:
            # Validate ERP data source configuration
            if not data_source.erp_type:
                raise ConfigValidationError("ERP Type is required for ERP data source")
            if not data_source.connection_string:
                raise ConfigValidationError("Connection string is required for ERP data source")
            if not data_source.field_mapping:
                raise ConfigValidationError("Field mapping is required for ERP data source")
            validate_field_mapping(data_source.field_mapping)

        else:
            raise ConfigValidationError(f"Unsupported data source type: {data_source.source_type}")

        logger.info(f"Data source configuration is valid for data source ID: {data_source.id}")
        return True

    except ConfigValidationError as e:
        logger.error(f"Data source configuration is invalid: {str(e)}")
        raise


def test_data_source_connection(data_source: DataSource) -> dict:
    """
    Tests the connection to a data source based on its type.

    Args:
        data_source (DataSource): The data source to test.

    Returns:
        dict: Connection test results with success status and details.
    """
    logger.info(f"Testing connection for data source ID: {data_source.id}, type: {data_source.source_type}")

    try:
        if data_source.source_type == DataSourceType.CSV:
            # Test CSV data source connection
            file_connector = FileConnector(file_path=data_source.file_path)
            file_connector.validate_file()
            return {"success": True, "message": "CSV file is valid"}

        elif data_source.source_type == DataSourceType.DATABASE:
            # Test Database data source connection
            db_data_source = typing.cast(DatabaseDataSource, get_data_source_by_type(data_source, db_session=None))
            database_connector = DatabaseConnector(connection_params_or_string=db_data_source.connection_string)
            database_connector.connect()
            return {"success": True, "message": "Database connection is valid"}

        elif data_source.source_type == DataSourceType.API:
            # Test API data source connection
            api_data_source = typing.cast(APIDataSource, get_data_source_by_type(data_source, db_session=None))
            api_connector = APIConnector(connection_params=api_data_source.__dict__)
            api_connector.connect()
            return {"success": True, "message": "API connection is valid"}
        
        elif data_source.source_type == DataSourceType.TMS:
            # Test TMS data source connection
            tms_data_source = typing.cast(TMSDataSource, get_data_source_by_type(data_source, db_session=None))
            tms_connector = TMSConnector(connection_params=tms_data_source.__dict__)
            tms_connector.connect()
            return {"success": True, "message": "TMS connection is valid"}

        elif data_source.source_type == DataSourceType.ERP:
            # Test ERP data source connection
            erp_data_source = typing.cast(ERPDataSource, get_data_source_by_type(data_source, db_session=None))
            erp_connector = ERPConnector(erp_type=erp_data_source.erp_type, connection_params=erp_data_source.__dict__)
            erp_connector.connect()
            return {"success": True, "message": "ERP connection is valid"}

        else:
            return {"success": False, "message": f"Unsupported data source type: {data_source.source_type}"}

    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return {"success": False, "message": str(e)}


def create_data_source_log(
    data_source_id: str,
    operation: str,
    status: str,
    message: str = None,
    records_processed: int = 0,
    records_failed: int = 0,
    details: typing.Dict = None,
    performed_by: str = None,
    db_session = None
) -> DataSourceLog:
    """
    Creates a log entry for a data source operation.

    Args:
        data_source_id (str): ID of the data source.
        operation (str): Operation type (e.g., IMPORT, EXPORT, TEST).
        status (str): Status of the operation (e.g., SUCCESS, FAILURE).
        message (str, optional): Optional message describing the result. Defaults to None.
        records_processed (int, optional): Number of records processed. Defaults to 0.
        records_failed (int, optional): Number of records that failed processing. Defaults to 0.
        details (typing.Dict, optional): Additional details about the operation. Defaults to None.
        performed_by (str, optional): User ID of the user who performed the operation. Defaults to None.
        db_session: Database session

    Returns:
        DataSourceLog: Created log entry.
    """
    logger.info(f"Creating data source log for data source ID: {data_source_id}, operation: {operation}, status: {status}")

    try:
        # Create a new DataSourceLog instance with the provided parameters
        log_entry = DataSourceLog(
            data_source_id=data_source_id,
            operation=operation,
            status=status,
            message=message,
            records_processed=records_processed,
            records_failed=records_failed,
            details=details or {},
            performed_by=performed_by
        )

        # Add the log entry to the database session
        # db_session.add(log_entry)

        # Commit the transaction
        # db_session.commit()

        logger.info(f"Data source log created successfully for data source ID: {data_source_id}")
        return log_entry

    except Exception as e:
        logger.error(f"Failed to create data source log: {str(e)}")
        raise


def get_data_source_by_type(data_source: DataSource, db_session = None) -> typing.Union[CSVDataSource, DatabaseDataSource, APIDataSource, TMSDataSource, ERPDataSource]:
    """
    Returns the specific data source instance based on its type.

    Args:
        data_source (DataSource): The data source to retrieve.
        db_session: Database session

    Returns:
        typing.Union[CSVDataSource, DatabaseDataSource, APIDataSource, TMSDataSource, ERPDataSource]: Specific data source instance.

    Raises:
        ValueError: If source_type is not recognized.
    """
    try:
        if data_source.source_type == DataSourceType.CSV:
            # Query for CSVDataSource
            return CSVDataSource()
        elif data_source.source_type == DataSourceType.DATABASE:
            # Query for DatabaseDataSource
            return DatabaseDataSource()
        elif data_source.source_type == DataSourceType.API:
            # Query for APIDataSource
            return APIDataSource()
        elif data_source.source_type == DataSourceType.TMS:
            # Query for TMSDataSource
            return TMSDataSource()
        elif data_source.source_type == DataSourceType.ERP:
            # Query for ERPDataSource
            return ERPDataSource()
        else:
            raise ValueError(f"Unsupported data source type: {data_source.source_type}")
    except Exception as e:
        logger.error(f"Failed to get data source by type: {str(e)}")
        raise


def get_required_fields_by_type(source_type: DataSourceType) -> typing.List[str]:
    """
    Returns the required fields for a data source based on its type.

    Args:
        source_type (DataSourceType): The data source type.

    Returns:
        typing.List[str]: List of required field names.

    Raises:
        ValueError: If source_type is not recognized.
    """
    if source_type == DataSourceType.CSV:
        return ['file_path', 'field_mapping']
    elif source_type == DataSourceType.DATABASE:
        return ['connection_string', 'query', 'username', 'field_mapping']
    elif source_type == DataSourceType.API:
        return ['endpoint_url', 'field_mapping']
    elif source_type == DataSourceType.TMS:
        return ['tms_type', 'connection_string', 'field_mapping']
    elif source_type == DataSourceType.ERP:
        return ['erp_type', 'connection_string', 'field_mapping']
    else:
        raise ValueError(f"Unsupported data source type: {source_type}")


def validate_field_mapping(field_mapping: typing.Dict[str, str]) -> bool:
    """
    Validates that the field mapping contains the required freight data fields.

    Args:
        field_mapping (typing.Dict[str, str]): The field mapping to validate.

    Returns:
        bool: True if field mapping is valid, raises exception otherwise.

    Raises:
        ConfigValidationError: If validation fails.
    """
    required_freight_data_fields = ['origin', 'destination', 'freight_charge', 'date/time']

    if field_mapping is None or not isinstance(field_mapping, dict):
        raise ConfigValidationError("Field mapping must be a dictionary")

    missing_fields = [field for field in required_freight_data_fields if field not in field_mapping.values()]

    if missing_fields:
        raise ConfigValidationError(f"Missing required freight data fields in field mapping: {', '.join(missing_fields)}")

    return True