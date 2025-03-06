#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration service module for the Freight Price Movement Agent. Provides a unified
interface for connecting to and retrieving data from various external systems
including TMS, ERP, databases, and file sources. Manages connection lifecycle,
data transformation, and error handling for all external integrations.
"""

import logging
from typing import Dict, Optional, Tuple
import pandas as pd  # version 1.5.x
from enum import Enum  # standard library
import enum  # standard library

from ..core.logging import getLogger
from ..core.config import settings  # Import application settings
from ..core.exceptions import IntegrationException, DataSourceException
from ..connectors.tms_connector import TMSConnector, create_tms_connector
from ..connectors.erp_connector import ERPConnector, create_erp_connector
from ..connectors.database_connector import DatabaseConnector
from ..connectors.file_connector import FileConnector, CSVConnector
from ..connectors.generic_api_connector import GenericAPIConnector, create_api_connector
from .error_handling import ErrorHandler, with_retry

# Initialize logger
logger = getLogger(__name__)


class IntegrationService:
    """
    Service for managing connections to external systems and retrieving freight pricing data
    """

    def __init__(self):
        """
        Initializes the IntegrationService
        """
        self.error_handler = ErrorHandler()  # Initialize error_handler instance
        self.active_connections = {}  # Initialize active_connections dictionary to track open connections
        logger.info("IntegrationService initialized")  # Log service initialization

    @with_retry(max_retries=3, backoff_factor=1.5)
    def connect_to_source(self, source_type: str, connection_params: Dict,
                          connection_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Establishes a connection to a data source

        Args:
            source_type (str): Type of data source (e.g., 'tms', 'erp', 'database', 'file', 'api')
            connection_params (dict): Dictionary containing connection parameters
            connection_id (Optional[str]): Unique identifier for the connection

        Returns:
            Tuple[bool, str]: Success status and connection ID
        """
        try:
            # Generate a unique connection_id if not provided
            if not connection_id:
                import uuid  # standard library
                connection_id = str(uuid.uuid4())

            # Validate connection parameters for the source type
            validate_connection_params(source_type, connection_params)

            # Create appropriate connector using create_connector function
            connector = create_connector(source_type, connection_params)

            # Attempt to connect to the data source
            if hasattr(connector, 'connect'):
                connector.connect()
            else:
                logger.warning(f"Connector for {source_type} does not have a connect method. Skipping explicit connection.")

            # If successful, store connector in active_connections dictionary
            self.active_connections[connection_id] = connector

            logger.info(f"Successfully connected to {source_type} with connection ID: {connection_id}")
            return True, connection_id

        except Exception as e:
            # Handle exceptions using error_handler
            error_response, _ = self.error_handler.handle_exception(
                e,
                module_name=__name__,
                context=f"Failed to connect to {source_type}"
            )
            logger.error(f"Failed to connect to {source_type}: {error_response['message']}")
            # Return failure status and error message on exception
            return False, error_response['message']

    def disconnect_from_source(self, connection_id: str) -> bool:
        """
        Closes a connection to a data source

        Args:
            connection_id (str): Unique identifier for the connection

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            # Check if connection_id exists in active_connections
            if connection_id in self.active_connections:
                # If exists, retrieve the connector
                connector = self.active_connections[connection_id]

                # Call disconnect method on the connector
                if hasattr(connector, 'disconnect'):
                    connector.disconnect()
                else:
                    logger.warning(f"Connector {type(connector).__name__} does not have a disconnect method. Skipping explicit disconnection.")

                # Remove connection from active_connections dictionary
                del self.active_connections[connection_id]

                logger.info(f"Successfully disconnected from connection ID: {connection_id}")
                return True
            else:
                # If connection_id not found, log warning and return False
                logger.warning(f"Connection ID not found: {connection_id}")
                return False

        except Exception as e:
            # Handle exceptions using error_handler
            error_response, _ = self.error_handler.handle_exception(
                e,
                module_name=__name__,
                context=f"Failed to disconnect from connection ID: {connection_id}"
            )
            logger.error(f"Failed to disconnect from connection ID {connection_id}: {error_response['message']}")
            # Return False on exception
            return False

    @with_retry(max_retries=2, backoff_factor=1.0)
    def fetch_freight_data(self, connection_id: str, query_params: Optional[Dict] = None,
                           field_mapping: Optional[Dict] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from a connected data source

        Args:
            connection_id (str): Unique identifier for the connection
            query_params (Optional[dict]): Parameters to filter the data
            field_mapping (Optional[dict]): Mapping of source fields to target field names
            limit (Optional[int]): Maximum number of records to return

        Returns:
            pandas.DataFrame: Freight pricing data as a DataFrame
        """
        try:
            # Check if connection_id exists in active_connections
            if connection_id in self.active_connections:
                # If exists, retrieve the connector
                connector = self.active_connections[connection_id]

                # Call fetch_freight_data method on the connector with parameters
                data = connector.fetch_freight_data(query_params=query_params, field_mapping=field_mapping, limit=limit)

                # Standardize the returned data format
                if not isinstance(data, pd.DataFrame):
                    raise DataSourceException(f"fetch_freight_data method must return a pandas DataFrame, got {type(data)}")

                # Return the standardized DataFrame
                return data
            else:
                # If connection_id not found, raise DataSourceException
                raise DataSourceException(f"Connection ID not found: {connection_id}")

        except Exception as e:
            # Handle exceptions using error_handler
            error_response, _ = self.error_handler.handle_exception(
                e,
                module_name=__name__,
                context=f"Failed to fetch freight data from connection ID: {connection_id}"
            )
            logger.error(f"Failed to fetch freight data from connection ID {connection_id}: {error_response['message']}")
            # Re-raise exception after handling
            raise

    def get_active_connections(self) -> dict:
        """
        Returns information about all active connections

        Returns:
            dict: Dictionary of active connections with metadata
        """
        try:
            connections_info = {}
            for conn_id, connector in self.active_connections.items():
                source_type = type(connector).__name__
                connection_time = "N/A"  # Placeholder, implement if needed
                status = "Active"  # Assume active if in the dictionary

                connections_info[conn_id] = {
                    "source_type": source_type,
                    "connection_time": connection_time,
                    "status": status
                }

            # Return the connections information dictionary
            return connections_info

        except Exception as e:
            # Handle exceptions using error_handler
            error_response, _ = self.error_handler.handle_exception(
                e,
                module_name=__name__,
                context="Failed to retrieve active connections"
            )
            logger.error(f"Failed to retrieve active connections: {error_response['message']}")
            # Return empty dictionary on exception
            return {}

    def test_connection(self, source_type: str, connection_params: Dict) -> Tuple[bool, str]:
        """
        Tests a connection to a data source without storing it

        Args:
            source_type (str): Type of data source
            connection_params (dict): Connection parameters

        Returns:
            Tuple[bool, str]: Success status and message
        """
        try:
            # Validate connection parameters for the source type
            validate_connection_params(source_type, connection_params)

            # Create appropriate connector using create_connector function
            connector = create_connector(source_type, connection_params)

            # Attempt to connect to the data source
            if hasattr(connector, 'test_connection'):
                result = connector.test_connection()
            else:
                logger.warning(f"Connector for {source_type} does not have a test_connection method. Assuming connection is valid.")
                result = True
            
            if result:
                message = f"Successfully tested connection to {source_type}"
                logger.info(message)
                return True, message
            else:
                message = f"Failed to test connection to {source_type}"
                logger.warning(message)
                return False, message

        except Exception as e:
            # Handle exceptions using error_handler
            error_response, _ = self.error_handler.handle_exception(
                e,
                module_name=__name__,
                context=f"Failed to test connection to {source_type}"
            )
            message = error_response['message']
            logger.error(f"Failed to test connection to {source_type}: {message}")
            # Return failure status and error message on exception
            return False, message

    def close_all_connections(self) -> dict:
        """
        Closes all active connections

        Returns:
            dict: Dictionary with results of each disconnection attempt
        """
        results = {}
        try:
            # Iterate through all active_connections
            for conn_id in list(self.active_connections.keys()):  # Iterate over a copy of the keys
                try:
                    # Call disconnect method on each connector
                    success = self.disconnect_from_source(conn_id)
                    results[conn_id] = {"success": success}
                except Exception as e:
                    # Record success/failure for each connection in results dictionary
                    results[conn_id] = {"success": False, "error": str(e)}
                    logger.error(f"Failed to disconnect from connection ID {conn_id}: {str(e)}")

            # Clear active_connections dictionary
            self.active_connections.clear()

            logger.info(f"All connections closed with results: {results}")
            # Return results dictionary
            return results

        except Exception as e:
            # Handle exceptions using error_handler
            error_response, _ = self.error_handler.handle_exception(
                e,
                module_name=__name__,
                context="Failed to close all connections"
            )
            logger.error(f"Failed to close all connections: {error_response['message']}")
            # Continue with next connection on exception
            return results

    def __del__(self):
        """
        Destructor to ensure all connections are closed when the service is destroyed
        """
        self.close_all_connections()  # Call close_all_connections method
        logger.info("IntegrationService destroyed")  # Log service destruction


class DataSourceType(enum.Enum):
    """
    Enumeration of supported data source types
    """
    TMS = "tms"
    ERP = "erp"
    DATABASE = "database"
    FILE = "file"
    API = "api"


def create_connector(source_type: str, connection_params: Dict):
    """
    Factory function to create the appropriate connector based on source type and parameters

    Args:
        source_type (str): Type of data source
        connection_params (dict): Dictionary containing connection parameters

    Returns:
        DataSourceConnector: An instance of the appropriate connector class
    """
    # Validate that source_type is provided and supported
    if not source_type:
        raise ValueError("Source type must be specified")

    # Validate that connection_params contains required fields for the source type
    validate_connection_params(source_type, connection_params)

    # Create and return the appropriate connector based on source_type
    try:
        if source_type == 'tms':
            # Call create_tms_connector with connection_params
            return create_tms_connector(connection_params)
        elif source_type == 'erp':
            # Call create_erp_connector with connection_params
            return create_erp_connector(connection_params['erp_type'], connection_params)
        elif source_type == 'database':
            # Create a DatabaseConnector instance
            return DatabaseConnector(connection_params)
        elif source_type == 'file':
            # Create a FileConnector or CSVConnector instance
            file_path = connection_params['file_path']
            return CSVConnector(file_path, connection_params)
        elif source_type == 'api':
            # Call create_api_connector with connection_params
            return create_api_connector(connection_params['api_type'], connection_params)
        else:
            # Handle unsupported source types with appropriate error message
            raise ValueError(f"Unsupported source type: {source_type}")
    except Exception as e:
        logger.error(f"Error creating connector for {source_type}: {str(e)}")
        raise

    # Log the connector creation


def validate_connection_params(source_type: str, connection_params: Dict) -> bool:
    """
    Validates that the connection parameters contain all required fields for the given source type

    Args:
        source_type (str): Type of data source
        connection_params (dict): Dictionary containing connection parameters

    Returns:
        bool: True if parameters are valid, raises exception otherwise
    """
    # Check if connection_params is a dictionary
    if not isinstance(connection_params, dict):
        raise ValueError("Connection parameters must be a dictionary")

    # Determine required fields based on source_type
    if source_type == 'tms':
        # Check for tms_type, api_url, etc.
        required_fields = ['tms_type', 'api_url']
    elif source_type == 'erp':
        # Check for erp_type, connection details, etc.
        required_fields = ['erp_type']
    elif source_type == 'database':
        # Check for host, port, database, username, password
        required_fields = ['host', 'port', 'database', 'username', 'password']
    elif source_type == 'file':
        # Check for file_path
        required_fields = ['file_path']
    elif source_type == 'api':
        # Check for api_url, auth_type, etc.
        required_fields = ['api_url']
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

    # Verify that all required fields exist in connection_params
    missing_fields = [field for field in required_fields if field not in connection_params]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    # Return True if all validations pass
    return True


def standardize_data_format(data: pd.DataFrame, field_mapping: Optional[Dict] = None) -> pd.DataFrame:
    """
    Standardizes data format from various sources to a consistent structure

    Args:
        data (pandas.DataFrame): Data from external source
        field_mapping (Optional[dict]): Mapping of source fields to target fields

    Returns:
        pandas.DataFrame: Standardized DataFrame with consistent column names and formats
    """
    try:
        # Check if data is a pandas DataFrame
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")

        # If field_mapping is provided, rename columns according to mapping
        if field_mapping:
            data = data.rename(columns=field_mapping)

        # Ensure required columns exist (origin, destination, freight_charge, date)
        required_columns = ['origin', 'destination', 'freight_charge', 'date']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")

        # Standardize date/time format
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'], errors='coerce')

        # Ensure freight_charge is numeric
        if 'freight_charge' in data.columns:
            data['freight_charge'] = pd.to_numeric(data['freight_charge'], errors='coerce')

        # Add source_system column if not present
        if 'source_system' not in data.columns:
            data['source_system'] = 'unknown'

        # Return the standardized DataFrame
        return data

    except Exception as e:
        logger.error(f"Error standardizing data format: {str(e)}")
        raise