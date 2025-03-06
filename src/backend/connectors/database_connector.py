#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Connector module for database interactions in the Freight Price Movement Agent.

This module provides a standardized interface for connecting to and querying
relational databases, particularly PostgreSQL with TimescaleDB extension for
time-series freight pricing data.
"""

import logging
from typing import Any, Dict, List, Optional, Union, Tuple

import pandas as pd  # version: 1.5.0
import sqlalchemy  # version: 1.4.40

from ..core.config import settings
from ..core.exceptions import DataSourceException, ConfigurationException
from ..utils.db_connector import DatabaseConnection
from ..core.utils import Timer

# Configure logger
logger = logging.getLogger(__name__)

# Default query timeout in seconds
DEFAULT_QUERY_TIMEOUT = 30  # Default database query timeout in seconds


def validate_connection_params(connection_params: Dict) -> bool:
    """
    Validates that the connection parameters contain all required fields.
    
    Args:
        connection_params: Dictionary containing connection parameters
        
    Returns:
        True if parameters are valid, raises exception otherwise
        
    Raises:
        ConfigurationException: If required parameters are missing
    """
    if not isinstance(connection_params, dict):
        raise ConfigurationException("Connection parameters must be a dictionary")
    
    required_fields = ['host', 'port', 'database', 'username', 'password']
    missing_fields = [field for field in required_fields if field not in connection_params]
    
    if missing_fields:
        raise ConfigurationException(
            f"Missing required connection parameters: {', '.join(missing_fields)}"
        )
    
    return True


def build_query_with_filters(base_query: str, filters: Dict) -> Tuple[str, Dict]:
    """
    Builds a SQL query with WHERE clauses based on filter criteria.
    
    Args:
        base_query: Base SQL query without WHERE clause
        filters: Dictionary of filter conditions
        
    Returns:
        Tuple of (modified query string, parameters dictionary)
        
    Raises:
        DataSourceException: If query construction fails
    """
    if not filters:
        return base_query, {}
    
    try:
        where_clauses = []
        params = {}
        
        for field, value in filters.items():
            # Handle different filter types based on value
            if isinstance(value, dict):
                # Complex filter with operator
                operator = value.get('operator', '=')
                filter_value = value.get('value')
                
                # Skip if value is None, unless it's an IS NULL operation
                if filter_value is None and operator.upper() != 'IS NULL':
                    continue
                
                # Handle different operators
                if operator.upper() in ('IN', 'NOT IN'):
                    if not filter_value or not isinstance(filter_value, (list, tuple)):
                        continue
                    param_name = f"{field}_param"
                    where_clauses.append(f"{field} {operator} (:{param_name})")
                    params[param_name] = filter_value
                elif operator.upper() in ('IS NULL', 'IS NOT NULL'):
                    where_clauses.append(f"{field} {operator}")
                elif operator.upper() in ('BETWEEN', 'NOT BETWEEN'):
                    if not filter_value or not isinstance(filter_value, (list, tuple)) or len(filter_value) != 2:
                        continue
                    param_name1 = f"{field}_param1"
                    param_name2 = f"{field}_param2"
                    where_clauses.append(f"{field} {operator} :{param_name1} AND :{param_name2}")
                    params[param_name1] = filter_value[0]
                    params[param_name2] = filter_value[1]
                elif operator.upper() in ('LIKE', 'ILIKE', 'NOT LIKE', 'NOT ILIKE'):
                    param_name = f"{field}_param"
                    where_clauses.append(f"{field} {operator} :{param_name}")
                    params[param_name] = f"%{filter_value}%" if '%' not in str(filter_value) else filter_value
                else:
                    # Standard comparison operators
                    param_name = f"{field}_param"
                    where_clauses.append(f"{field} {operator} :{param_name}")
                    params[param_name] = filter_value
            else:
                # Simple equality filter
                # Skip if value is None
                if value is None:
                    continue
                    
                param_name = f"{field}_param"
                where_clauses.append(f"{field} = :{param_name}")
                params[param_name] = value
        
        if where_clauses:
            query = f"{base_query} WHERE {' AND '.join(where_clauses)}"
            return query, params
        else:
            return base_query, {}
            
    except Exception as e:
        raise DataSourceException(f"Error building query with filters: {str(e)}", original_exception=e)


def format_query_results(results: List, include_metadata: bool = False) -> Dict:
    """
    Formats database query results into a standardized structure.
    
    Args:
        results: Raw query results
        include_metadata: Whether to include additional metadata
        
    Returns:
        Standardized query results with optional metadata
        
    Raises:
        DataSourceException: If result formatting fails
    """
    try:
        formatted_results = {
            'data': results,
            'count': len(results)
        }
        
        if include_metadata:
            import datetime
            formatted_results['metadata'] = {
                'timestamp': datetime.datetime.now().isoformat(),
                'row_count': len(results)
            }
            
        return formatted_results
    except Exception as e:
        raise DataSourceException(f"Error formatting query results: {str(e)}", original_exception=e)


class DatabaseConnector:
    """
    Class for connecting to and querying relational databases for freight pricing data.
    """
    
    def __init__(self, connection_params: Optional[Dict] = None, 
                 database_url: Optional[str] = None,
                 database_type: str = 'postgresql'):
        """
        Initializes a new DatabaseConnector instance.
        
        Args:
            connection_params: Optional dictionary with connection parameters
            database_url: Optional database connection URL
            database_type: Database type (e.g., 'postgresql')
            
        Raises:
            ConfigurationException: If connection configuration is invalid
        """
        self.db_connection = None
        self.connected = False
        self.database_type = database_type
        
        # Determine connection parameters
        if connection_params:
            validate_connection_params(connection_params)
            self.connection_params = connection_params
        elif database_url:
            self.connection_params = {'url': database_url}
        else:
            self.connection_params = settings.get_database_connection_parameters()
            
        logger.info(f"Initialized {self.__class__.__name__} for {self.database_type} database")
    
    def connect(self) -> bool:
        """
        Establishes a connection to the database.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            DataSourceException: If connection fails
        """
        try:
            if self.connected and self.db_connection:
                logger.debug("Already connected to database")
                return True
                
            # Create database connection
            self.db_connection = DatabaseConnection(self.connection_params)
            self.connected = self.db_connection.connect()
            
            if self.connected:
                logger.info(f"Successfully connected to {self.database_type} database")
            else:
                logger.error("Failed to connect to database")
                
            return self.connected
        
        except Exception as e:
            self.connected = False
            error_msg = f"Error connecting to database: {str(e)}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def disconnect(self) -> bool:
        """
        Closes the database connection.
        
        Returns:
            True if disconnection successful
        """
        if not self.connected or not self.db_connection:
            return True
            
        try:
            self.db_connection.disconnect()
            self.connected = False
            logger.info("Disconnected from database")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from database: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None, 
                     timeout: Optional[int] = None) -> List:
        """
        Executes a SQL query and returns the results.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            timeout: Optional query timeout in seconds
            
        Returns:
            Query results as a list of dictionaries
            
        Raises:
            DataSourceException: If query execution fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        # Set default timeout if not provided
        if timeout is None:
            timeout = DEFAULT_QUERY_TIMEOUT
            
        try:
            with Timer(f"Query execution: {query[:50]}..."):
                results = self.db_connection.execute_query(query, params, timeout)
                return results
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}\nQuery: {query}\nParams: {params}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def execute_query_df(self, query: str, params: Optional[Dict] = None, 
                        timeout: Optional[int] = None) -> pd.DataFrame:
        """
        Executes a SQL query and returns the results as a pandas DataFrame.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            timeout: Optional query timeout in seconds
            
        Returns:
            Query results as a DataFrame
            
        Raises:
            DataSourceException: If query execution fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        # Set default timeout if not provided
        if timeout is None:
            timeout = DEFAULT_QUERY_TIMEOUT
            
        try:
            with Timer(f"DataFrame query execution: {query[:50]}..."):
                df = self.db_connection.execute_query_df(query, params, timeout)
                return df
        except Exception as e:
            error_msg = f"Error executing query as DataFrame: {str(e)}\nQuery: {query}\nParams: {params}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def fetch_freight_data(self, filters: Optional[Dict] = None, 
                          sort_by: Optional[str] = None,
                          desc: Optional[bool] = False,
                          limit: Optional[int] = None) -> pd.DataFrame:
        """
        Fetches freight pricing data from the database.
        
        Args:
            filters: Optional filtering criteria
            sort_by: Optional column to sort by
            desc: Whether to sort in descending order
            limit: Maximum number of rows to return
            
        Returns:
            Freight pricing data as a DataFrame
            
        Raises:
            DataSourceException: If data retrieval fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        try:
            # Build base query
            base_query = """
            SELECT *
            FROM freight_data
            """
            
            # Apply filters if provided
            query, params = build_query_with_filters(base_query, filters or {})
            
            # Apply sorting if requested
            if sort_by:
                direction = "DESC" if desc else "ASC"
                query = f"{query} ORDER BY {sort_by} {direction}"
                
            # Apply limit if provided
            if limit and limit > 0:
                query = f"{query} LIMIT {limit}"
                
            # Execute query and return as DataFrame
            return self.execute_query_df(query, params)
            
        except Exception as e:
            error_msg = f"Error fetching freight data: {str(e)}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def get_table_schema(self, table_name: str, schema_name: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves schema information for a database table.
        
        Args:
            table_name: Name of the table
            schema_name: Optional schema name
            
        Returns:
            Table schema information
            
        Raises:
            DataSourceException: If schema retrieval fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        try:
            return self.db_connection.get_table_schema(table_name, schema_name)
        except Exception as e:
            error_msg = f"Error retrieving table schema: {str(e)}\nTable: {table_name}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def test_query(self, query: str, params: Optional[Dict] = None) -> bool:
        """
        Tests a query without executing it to validate syntax and structure.
        
        Args:
            query: SQL query to test
            params: Optional query parameters
            
        Returns:
            True if query is valid, raises exception otherwise
            
        Raises:
            DataSourceException: If query validation fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        try:
            # This will validate the query syntax without executing it
            # Implementation may vary based on database type
            if self.database_type == 'postgresql':
                # For PostgreSQL, we can use EXPLAIN
                test_query = f"EXPLAIN {query}"
                self.execute_query(test_query, params, timeout=5)
            else:
                # Generic approach - just prepare the query
                # This might execute the query depending on the driver
                self.execute_query(f"/* TEST QUERY */ {query} LIMIT 0", params, timeout=5)
                
            return True
        except Exception as e:
            error_msg = f"Query validation failed: {str(e)}\nQuery: {query}\nParams: {params}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def __enter__(self):
        """Context manager entry point."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.disconnect()
        logger.debug("Database connection context exited")


class PostgreSQLConnector(DatabaseConnector):
    """
    Specialized connector for PostgreSQL databases with TimescaleDB support.
    """
    
    def __init__(self, connection_params: Optional[Dict] = None, 
                 database_url: Optional[str] = None):
        """
        Initializes a new PostgreSQLConnector instance.
        
        Args:
            connection_params: Optional dictionary with connection parameters
            database_url: Optional database connection URL
        """
        super().__init__(connection_params, database_url, database_type='postgresql')
    
    def get_time_series_data(self, time_column: str, start_date: str, end_date: str,
                            interval: str, filters: Optional[Dict] = None) -> pd.DataFrame:
        """
        Fetches time-series freight pricing data with TimescaleDB optimizations.
        
        Args:
            time_column: Column name for time series
            start_date: Start date for time range
            end_date: End date for time range
            interval: Time bucket interval (e.g., '1 day', '1 week')
            filters: Optional filtering criteria
            
        Returns:
            Time-series freight pricing data
            
        Raises:
            DataSourceException: If data retrieval fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        try:
            # Build base query with time_bucket function from TimescaleDB
            base_query = f"""
            SELECT 
                time_bucket('{interval}', {time_column}) AS time_bucket,
                AVG(freight_charge) AS avg_freight_charge,
                MIN(freight_charge) AS min_freight_charge,
                MAX(freight_charge) AS max_freight_charge,
                COUNT(*) AS record_count
            FROM freight_data
            WHERE {time_column} BETWEEN :start_date AND :end_date
            """
            
            # Apply additional filters
            if filters:
                filter_query, filter_params = build_query_with_filters("", filters)
                if filter_query and filter_query.strip():
                    # Remove "WHERE" from filter_query as we already have a WHERE clause
                    filter_conditions = filter_query.replace("WHERE", "").strip()
                    if filter_conditions:
                        base_query = f"{base_query} AND {filter_conditions}"
                params = {**filter_params, 'start_date': start_date, 'end_date': end_date}
            else:
                params = {'start_date': start_date, 'end_date': end_date}
                
            # Add group by clause
            query = f"{base_query} GROUP BY time_bucket ORDER BY time_bucket"
            
            # Execute query and return as DataFrame
            return self.execute_query_df(query, params)
            
        except Exception as e:
            error_msg = f"Error fetching time-series data: {str(e)}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def get_aggregated_data(self, group_by_columns: List[str], 
                          aggregate_columns: List[str],
                          filters: Optional[Dict] = None) -> pd.DataFrame:
        """
        Fetches aggregated freight pricing data with specified grouping.
        
        Args:
            group_by_columns: Columns to group by
            aggregate_columns: Columns to aggregate
            filters: Optional filtering criteria
            
        Returns:
            Aggregated freight pricing data
            
        Raises:
            DataSourceException: If data retrieval fails
        """
        # Ensure connection is established
        if not self.connected:
            self.connect()
            
        try:
            # Validate inputs
            if not group_by_columns or not aggregate_columns:
                raise ValueError("Group by columns and aggregate columns must be provided")
                
            # Build select clause with group by columns and aggregations
            select_items = []
            
            # Add group by columns to select
            for col in group_by_columns:
                select_items.append(col)
                
            # Add aggregate functions for each aggregate column
            for col in aggregate_columns:
                select_items.append(f"AVG({col}) AS avg_{col}")
                select_items.append(f"MIN({col}) AS min_{col}")
                select_items.append(f"MAX({col}) AS max_{col}")
                select_items.append(f"SUM({col}) AS sum_{col}")
                
            # Build count expression
            select_items.append("COUNT(*) AS record_count")
            
            # Build base query
            base_query = f"""
            SELECT {', '.join(select_items)}
            FROM freight_data
            """
            
            # Apply filters if provided
            query, params = build_query_with_filters(base_query, filters or {})
            
            # Add group by clause
            query = f"{query} GROUP BY {', '.join(group_by_columns)}"
            
            # Execute query and return as DataFrame
            return self.execute_query_df(query, params)
            
        except Exception as e:
            error_msg = f"Error fetching aggregated data: {str(e)}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)