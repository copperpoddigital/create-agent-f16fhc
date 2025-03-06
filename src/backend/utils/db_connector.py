#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database connector utility for the Freight Price Movement Agent.

This module provides a standardized interface for database connections,
query execution, and error handling, with optimized support for PostgreSQL
with TimescaleDB for time-series freight data analysis.
"""

import os
import re
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager

import psycopg2  # version: 2.9.5
import psycopg2.extras
import pandas as pd  # version: 1.5.0
import sqlalchemy  # version: 1.4.40
from sqlalchemy import create_engine

from ..core.logging import get_logger
from ..core.exceptions import DataSourceException, ConfigurationException
from ..core.utils import Timer

# Configure module logger
logger = get_logger(__name__)

# Default query timeout in seconds
DEFAULT_TIMEOUT = 30


def create_connection_string(connection_params: Dict[str, Any], db_type: str = "postgresql") -> str:
    """
    Creates a database connection string from connection parameters.

    Args:
        connection_params: Dictionary containing connection parameters
        db_type: Database type (postgresql, sqlite, etc.)

    Returns:
        Database connection string

    Raises:
        ConfigurationException: If required parameters are missing or invalid
    """
    try:
        # Validate connection parameters
        if not isinstance(connection_params, dict):
            raise ValueError("Connection parameters must be a dictionary")

        # PostgreSQL connection string
        if db_type.lower() == "postgresql":
            required_params = ["host", "port", "database", "username", "password"]
            for param in required_params:
                if param not in connection_params:
                    raise ValueError(f"Missing required parameter: {param}")

            host = connection_params["host"]
            port = connection_params["port"]
            database = connection_params["database"]
            username = connection_params["username"]
            password = connection_params["password"]
            
            # Extract optional parameters
            sslmode = connection_params.get("sslmode", "prefer")
            application_name = connection_params.get("application_name", "FreightPriceMovementAgent")
            
            # Build connection string
            conn_str = (
                f"postgresql://{username}:{password}@{host}:{port}/{database}"
                f"?sslmode={sslmode}&application_name={application_name}"
            )
            
            return conn_str
            
        # SQLite connection string
        elif db_type.lower() == "sqlite":
            if "database" not in connection_params:
                raise ValueError("Missing required parameter: database")
                
            database = connection_params["database"]
            return f"sqlite:///{database}"
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
            
    except Exception as e:
        error_msg = f"Failed to create connection string: {str(e)}"
        logger.error(error_msg)
        raise ConfigurationException(error_msg, original_exception=e)


def parse_connection_string(connection_string: str) -> Dict[str, Any]:
    """
    Parses a database connection string into component parts.
    
    Args:
        connection_string: Database connection string
        
    Returns:
        Dictionary of connection parameters
        
    Raises:
        ConfigurationException: If connection string is invalid
    """
    try:
        if not connection_string:
            raise ValueError("Connection string cannot be empty")
            
        # Determine database type from connection string
        if connection_string.startswith("postgresql://"):
            db_type = "postgresql"
            # Parse PostgreSQL connection string
            # Format: postgresql://username:password@host:port/database?param1=value1
            pattern = r"postgresql://(?P<username>[^:]+):(?P<password>[^@]+)@(?P<host>[^:/]+):(?P<port>\d+)/(?P<database>[^?]+)(?:\?(?P<params>.+))?"
            match = re.match(pattern, connection_string)
            
            if not match:
                raise ValueError("Invalid PostgreSQL connection string format")
                
            params = {
                "db_type": db_type,
                "host": match.group("host"),
                "port": int(match.group("port")),
                "database": match.group("database"),
                "username": match.group("username"),
                "password": match.group("password")
            }
            
            # Parse additional parameters if present
            if match.group("params"):
                for param_pair in match.group("params").split("&"):
                    if "=" in param_pair:
                        key, value = param_pair.split("=", 1)
                        params[key] = value
            
            return params
            
        elif connection_string.startswith("sqlite:///"):
            # Parse SQLite connection string
            # Format: sqlite:///path/to/database.db
            db_type = "sqlite"
            database_path = connection_string[10:]  # Remove "sqlite:///"
            
            return {
                "db_type": db_type,
                "database": database_path
            }
            
        else:
            raise ValueError(f"Unsupported connection string format: {connection_string}")
            
    except Exception as e:
        error_msg = f"Failed to parse connection string: {str(e)}"
        logger.error(error_msg)
        raise ConfigurationException(error_msg, original_exception=e)


class DatabaseConnection:
    """
    Base class for database connections with common functionality.
    
    This class provides the core database operations, including connection
    management, query execution, and result formatting.
    """
    
    def __init__(self, connection_params_or_string: Union[Dict[str, Any], str], db_type: str = "postgresql"):
        """
        Initializes a new DatabaseConnection instance.
        
        Args:
            connection_params_or_string: Dictionary with connection parameters or connection string
            db_type: Database type (postgresql, sqlite, etc.)
            
        Raises:
            ConfigurationException: If connection parameters are invalid
        """
        self.connection_string = None
        self.connection_params = None
        self.connection = None
        self.connected = False
        self.db_type = db_type.lower()
        
        # Process connection parameters
        if isinstance(connection_params_or_string, str):
            self.connection_string = connection_params_or_string
            try:
                self.connection_params = parse_connection_string(connection_params_or_string)
                self.db_type = self.connection_params.get("db_type", db_type).lower()
            except Exception as e:
                logger.warning(f"Could not parse connection string: {str(e)}")
        elif isinstance(connection_params_or_string, dict):
            self.connection_params = connection_params_or_string
            try:
                self.connection_string = create_connection_string(connection_params_or_string, db_type)
            except Exception as e:
                logger.warning(f"Could not create connection string: {str(e)}")
        else:
            error_msg = "connection_params_or_string must be either a dictionary or a string"
            logger.error(error_msg)
            raise ConfigurationException(error_msg)
            
        logger.debug(f"Initialized {self.__class__.__name__} for {self.db_type} database")
        
    def connect(self) -> bool:
        """
        Establishes a connection to the database.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            DataSourceException: If connection fails
        """
        if self.connected:
            logger.debug("Already connected to database")
            return True
            
        try:
            with Timer("Database connection"):
                if self.db_type == "postgresql":
                    if self.connection_params:
                        # Connect using parameters
                        self.connection = psycopg2.connect(
                            host=self.connection_params.get("host"),
                            port=self.connection_params.get("port"),
                            dbname=self.connection_params.get("database"),
                            user=self.connection_params.get("username"),
                            password=self.connection_params.get("password"),
                            sslmode=self.connection_params.get("sslmode", "prefer"),
                            application_name=self.connection_params.get("application_name", "FreightPriceMovementAgent")
                        )
                    else:
                        # Connect using connection string
                        self.connection = psycopg2.connect(self.connection_string)
                        
                elif self.db_type == "sqlite":
                    if self.connection_params:
                        self.connection = sqlite3.connect(self.connection_params.get("database"))
                    else:
                        # Extract database path from connection string
                        db_path = self.connection_string.replace("sqlite:///", "")
                        self.connection = sqlite3.connect(db_path)
                else:
                    raise ValueError(f"Unsupported database type: {self.db_type}")
                
            self.connected = True
            logger.info(f"Successfully connected to {self.db_type} database")
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to database: {str(e)}"
            logger.error(error_msg)
            self.connected = False
            raise DataSourceException(error_msg, original_exception=e)
            
    def disconnect(self) -> bool:
        """
        Closes the database connection.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        if not self.connected or not self.connection:
            logger.debug("Not connected to database")
            return True
            
        try:
            self.connection.close()
            self.connected = False
            logger.info("Disconnected from database")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from database: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None, timeout: Optional[int] = None) -> List[Dict]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        
        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            timeout: Query timeout in seconds
            
        Returns:
            Query results as a list of dictionaries
            
        Raises:
            DataSourceException: If query execution fails
        """
        # Ensure we have a connection
        if not self.connected:
            self.connect()
            
        # Set default timeout if not provided
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
            
        try:
            with Timer(f"Query execution: {query[:60]}..."):
                cursor = self.connection.cursor()
                
                # Set timeout if supported
                if self.db_type == "postgresql":
                    cursor.execute(f"SET statement_timeout = {timeout * 1000}")
                
                # Execute query with parameters if provided
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                # Fetch results
                rows = cursor.fetchall()
                
                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Convert to list of dictionaries
                results = [dict(zip(columns, row)) for row in rows]
                
                cursor.close()
                
                logger.debug(f"Query executed successfully, returned {len(results)} rows")
                return results
                
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}\nQuery: {query}\nParams: {params}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def execute_query_df(self, query: str, params: Optional[Dict] = None, timeout: Optional[int] = None) -> pd.DataFrame:
        """
        Executes a SQL query and returns the results as a pandas DataFrame.
        
        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            timeout: Query timeout in seconds
            
        Returns:
            Query results as a pandas DataFrame
            
        Raises:
            DataSourceException: If query execution fails
        """
        # Ensure we have a connection
        if not self.connected:
            self.connect()
            
        # Set default timeout if not provided
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
            
        try:
            with Timer(f"DataFrame query execution: {query[:60]}..."):
                # Use SQLAlchemy for pandas integration
                engine = create_engine(self.connection_string)
                
                # Execute query with parameters if provided
                if params:
                    df = pd.read_sql(query, engine, params=params)
                else:
                    df = pd.read_sql(query, engine)
                    
                logger.debug(f"Query executed successfully, returned DataFrame with {len(df)} rows")
                return df
                
        except Exception as e:
            error_msg = f"Error executing query as DataFrame: {str(e)}\nQuery: {query}\nParams: {params}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)
    
    def get_table_schema(self, table_name: str, schema_name: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieves schema information for a database table.
        
        Args:
            table_name: Name of the table
            schema_name: Optional schema name (for PostgreSQL)
            
        Returns:
            Table schema information as a DataFrame
            
        Raises:
            DataSourceException: If schema retrieval fails
        """
        # Ensure we have a connection
        if not self.connected:
            self.connect()
            
        try:
            if self.db_type == "postgresql":
                schema = schema_name or "public"
                query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %(table_name)s AND table_schema = %(schema_name)s
                ORDER BY ordinal_position
                """
                params = {"table_name": table_name, "schema_name": schema}
                
                return self.execute_query_df(query, params)
                
            elif self.db_type == "sqlite":
                query = f"PRAGMA table_info({table_name})"
                
                # Execute directly as SQLite doesn't support parameterized PRAGMA
                df = pd.read_sql(query, sqlite3.connect(self.connection_params.get("database")))
                # Rename columns to match PostgreSQL output format
                df = df.rename(columns={
                    "name": "column_name",
                    "type": "data_type",
                    "notnull": "is_nullable",
                    "dflt_value": "column_default"
                })
                # Convert notnull (0/1) to 'YES'/'NO' for is_nullable
                df["is_nullable"] = df["is_nullable"].apply(lambda x: "NO" if x == 1 else "YES")
                
                return df
                
            else:
                raise ValueError(f"Table schema retrieval not implemented for {self.db_type}")
                
        except Exception as e:
            error_msg = f"Error retrieving table schema: {str(e)}\nTable: {table_name}"
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


class PostgreSQLConnection(DatabaseConnection):
    """
    Specialized connection class for PostgreSQL databases.
    
    This class extends the base DatabaseConnection with PostgreSQL-specific
    optimizations, including TimescaleDB support for time-series data.
    """
    
    def __init__(self, connection_params_or_string: Union[Dict[str, Any], str]):
        """
        Initializes a new PostgreSQLConnection instance.
        
        Args:
            connection_params_or_string: Dictionary with connection parameters or connection string
        """
        super().__init__(connection_params_or_string, db_type="postgresql")
    
    def connect(self) -> bool:
        """
        Establishes a connection to PostgreSQL database with optimized settings.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            DataSourceException: If connection fails
        """
        if self.connected:
            logger.debug("Already connected to PostgreSQL database")
            return True
            
        try:
            with Timer("PostgreSQL connection"):
                if self.connection_params:
                    # Connect using parameters
                    self.connection = psycopg2.connect(
                        host=self.connection_params.get("host"),
                        port=self.connection_params.get("port"),
                        dbname=self.connection_params.get("database"),
                        user=self.connection_params.get("username"),
                        password=self.connection_params.get("password"),
                        sslmode=self.connection_params.get("sslmode", "prefer"),
                        application_name=self.connection_params.get("application_name", "FreightPriceMovementAgent")
                    )
                else:
                    # Connect using connection string
                    self.connection = psycopg2.connect(self.connection_string)
                
                # Configure connection for best performance with TimescaleDB
                self.connection.autocommit = True
                
                # Set timezone to UTC for consistent timestamp handling
                cursor = self.connection.cursor()
                cursor.execute("SET timezone = 'UTC'")
                
                # Optimize settings for bulk operations
                cursor.execute("SET work_mem = '64MB'")
                
                # Close cursor
                cursor.close()
                
            self.connected = True
            logger.info("Successfully connected to PostgreSQL database")
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to PostgreSQL database: {str(e)}"
            logger.error(error_msg)
            self.connected = False
            raise DataSourceException(error_msg, original_exception=e)
    
    def execute_query(self, query: str, params: Optional[Dict] = None, timeout: Optional[int] = None) -> List[Dict]:
        """
        Executes a SQL query on PostgreSQL with specific optimizations.
        
        Args:
            query: SQL query to execute
            params: Query parameters for parameterized queries
            timeout: Query timeout in seconds
            
        Returns:
            Query results as a list of dictionaries
            
        Raises:
            DataSourceException: If query execution fails
        """
        # Ensure we have a connection
        if not self.connected:
            self.connect()
            
        # Set default timeout if not provided
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
            
        try:
            with Timer(f"PostgreSQL query execution: {query[:60]}..."):
                # Use DictCursor for easier dictionary access
                cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                # Set timeout
                cursor.execute(f"SET statement_timeout = {timeout * 1000}")
                
                # Execute query with parameters if provided
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                    
                # Fetch results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = [dict(row) for row in rows]
                
                cursor.close()
                
                logger.debug(f"Query executed successfully, returned {len(results)} rows")
                return results
                
        except Exception as e:
            error_msg = f"Error executing PostgreSQL query: {str(e)}\nQuery: {query}\nParams: {params}"
            logger.error(error_msg)
            raise DataSourceException(error_msg, original_exception=e)


class SQLiteConnection(DatabaseConnection):
    """
    Specialized connection class for SQLite databases.
    
    This class extends the base DatabaseConnection with SQLite-specific
    optimizations and handling.
    """
    
    def __init__(self, connection_params_or_string: Union[Dict[str, Any], str]):
        """
        Initializes a new SQLiteConnection instance.
        
        Args:
            connection_params_or_string: Dictionary with connection parameters or connection string
        """
        super().__init__(connection_params_or_string, db_type="sqlite")
    
    def connect(self) -> bool:
        """
        Establishes a connection to SQLite database with optimized settings.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            DataSourceException: If connection fails
        """
        if self.connected:
            logger.debug("Already connected to SQLite database")
            return True
            
        try:
            with Timer("SQLite connection"):
                if self.connection_params:
                    # Connect using parameters
                    db_path = self.connection_params.get("database")
                    self.connection = sqlite3.connect(db_path)
                else:
                    # Extract database path from connection string
                    db_path = self.connection_string.replace("sqlite:///", "")
                    self.connection = sqlite3.connect(db_path)
                
                # Set row factory to return dictionaries
                self.connection.row_factory = sqlite3.Row
                
                # Enable foreign keys
                cursor = self.connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.close()
                
            self.connected = True
            logger.info(f"Successfully connected to SQLite database: {db_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to SQLite database: {str(e)}"
            logger.error(error_msg)
            self.connected = False
            raise DataSourceException(error_msg, original_exception=e)