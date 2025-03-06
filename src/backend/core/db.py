"""
Core database module for the Freight Price Movement Agent.

This module provides database connection management, session handling, and
SQLAlchemy configuration. It implements connection pooling, declarative base
setup, and TimescaleDB integration for efficient time-series data storage
and querying.
"""

import contextlib
from typing import Any, Dict, List, Optional, ContextManager, Callable, Union, TypeVar

import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
from sqlalchemy.engine import Engine, Connection

from .config import settings, DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW, get_database_connection_parameters
from .utils import logger
from .exceptions import DatabaseException

# Global variables
engine: Optional[Engine] = None  # SQLAlchemy engine instance, initialized in initialize_db()
SessionLocal: Optional[sessionmaker] = None  # SQLAlchemy session factory, initialized in initialize_db()
Base = declarative_base()  # SQLAlchemy declarative base for ORM models

T = TypeVar('T')  # Type variable for generic function return types


def initialize_db() -> Engine:
    """
    Initializes the database connection and session factory.
    
    Returns:
        SQLAlchemy engine instance
    """
    global engine, SessionLocal
    
    try:
        # Get database connection parameters from settings
        db_params = settings.get_database_connection_parameters()
        
        # Create SQLAlchemy engine with connection parameters and pooling settings
        connection_url = DATABASE_URL
        engine = create_engine(
            connection_url,
            pool_size=DATABASE_POOL_SIZE,
            max_overflow=DATABASE_MAX_OVERFLOW,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections after 30 minutes
            pool_pre_ping=True,  # Check connection validity before using
            connect_args={
                "application_name": "freight_price_movement_agent",
                "options": "-c timezone=UTC"
            }
        )
        
        # Configure engine events for better monitoring and debugging
        configure_engine_events(engine)
        
        # Create session factory bound to the engine
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Log successful database initialization
        logger.info(f"Database initialized successfully: {connection_url}")
        
        return engine
    
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise DatabaseException(f"Database initialization failed: {str(e)}", original_exception=e)


def get_db_engine() -> Engine:
    """
    Returns the database engine, initializing it if necessary.
    
    Returns:
        SQLAlchemy engine instance
    """
    global engine
    
    # Check if engine is already initialized
    if engine is None:
        # If not initialized, call initialize_db()
        engine = initialize_db()
    
    return engine


def get_db() -> ContextManager[Session]:
    """
    Context manager for database sessions.
    
    Yields:
        SQLAlchemy session
    """
    if SessionLocal is None:
        initialize_db()
        
    # Create a new database session using SessionLocal
    db_session = SessionLocal()
    
    try:
        # Yield the session to the caller
        yield db_session
    except Exception as e:
        # Rollback on exception
        db_session.rollback()
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        raise
    finally:
        # Close the session when the context is exited
        db_session.close()


def create_all_tables() -> None:
    """
    Creates all tables defined in the models.
    """
    try:
        # Get database engine using get_db_engine()
        engine = get_db_engine()
        
        # Create all tables defined in Base.metadata
        Base.metadata.create_all(bind=engine)
        
        # Log successful table creation
        logger.info("Database tables created successfully")
    
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}", exc_info=True)
        raise DatabaseException(f"Table creation failed: {str(e)}", original_exception=e)


def setup_timescaledb() -> None:
    """
    Sets up TimescaleDB extensions and features.
    """
    try:
        # Get database engine using get_db_engine()
        engine = get_db_engine()
        
        # Create a connection to execute SQL statements
        with engine.connect() as connection:
            # Execute SQL to create TimescaleDB extension if it doesn't exist
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # Additional TimescaleDB configuration can be added here
            logger.info("TimescaleDB extension enabled successfully")
    
    except Exception as e:
        logger.error(f"Failed to setup TimescaleDB: {str(e)}", exc_info=True)
        raise DatabaseException(f"TimescaleDB setup failed: {str(e)}", original_exception=e)


def configure_engine_events(engine: Engine) -> None:
    """
    Configures event listeners for the SQLAlchemy engine.
    
    Args:
        engine: SQLAlchemy engine instance
    """
    # Add event listener for engine connect events
    event.listen(engine, 'connect', on_connect)
    
    # Add event listener for engine checkout events
    event.listen(engine, 'checkout', on_checkout)
    
    # Add event listener for engine checkin events
    event.listen(engine, 'checkin', on_checkin)
    
    logger.debug("Engine event listeners configured successfully")


def on_connect(dbapi_connection: Connection, connection_record: Any) -> None:
    """
    Event handler for database connection events.
    
    Args:
        dbapi_connection: Database connection
        connection_record: Connection record object
    """
    # Log new database connection
    logger.debug(f"New database connection established: {id(dbapi_connection)}")
    
    # Configure connection parameters
    cursor = dbapi_connection.cursor()
    try:
        # Set timezone to UTC
        cursor.execute("SET timezone TO 'UTC';")
        
        # Set application name for easier identification in database logs
        cursor.execute("SET application_name TO 'freight_price_movement_agent';")
        
        # Additional connection configuration can be added here
        
        cursor.close()
    except Exception as e:
        cursor.close()
        logger.error(f"Error configuring new database connection: {str(e)}", exc_info=True)


def on_checkout(dbapi_connection: Connection, connection_record: Any, connection_proxy: Any) -> None:
    """
    Event handler for connection checkout from pool.
    
    Args:
        dbapi_connection: Database connection
        connection_record: Connection record object
        connection_proxy: Connection proxy object
    """
    # Log connection checkout from pool
    logger.debug(f"Database connection checked out: {id(dbapi_connection)}")
    
    # Verify connection is still valid
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    except Exception as e:
        # Connection is invalid, invalidate it so it gets replaced
        connection_proxy._pool.invalidate(dbapi_connection)
        logger.warning(f"Invalid connection detected during checkout: {str(e)}")
        raise


def on_checkin(dbapi_connection: Connection, connection_record: Any) -> None:
    """
    Event handler for connection checkin to pool.
    
    Args:
        dbapi_connection: Database connection
        connection_record: Connection record object
    """
    # Log connection checkin to pool
    logger.debug(f"Database connection checked in: {id(dbapi_connection)}")
    
    # Reset any session-specific state here if needed
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("RESET ALL;")
        cursor.close()
    except Exception as e:
        logger.error(f"Error resetting connection state during checkin: {str(e)}", exc_info=True)


@contextlib.contextmanager
def session_scope() -> ContextManager[Session]:
    """
    Context manager for database sessions with transaction management.
    
    Yields:
        SQLAlchemy session
    """
    # Create a new database session using SessionLocal
    if SessionLocal is None:
        initialize_db()
        
    session = SessionLocal()
    
    try:
        # Begin a transaction
        session.begin()
        
        # Yield the session to the caller
        yield session
        
        # Commit the transaction if no exceptions occur
        session.commit()
    except Exception as e:
        # Rollback the transaction if an exception occurs
        session.rollback()
        logger.error(f"Transaction error: {str(e)}", exc_info=True)
        raise
    finally:
        # Close the session when the context is exited
        session.close()


class Database:
    """
    Database manager class for centralized database operations.
    """
    
    def __init__(self):
        """
        Initializes the Database manager with engine and session factory.
        """
        # Get database engine using get_db_engine()
        self._engine = get_db_engine()
        
        # Get session factory from SessionLocal
        if SessionLocal is None:
            initialize_db()
        self._session_factory = SessionLocal
    
    def get_session(self) -> Session:
        """
        Creates and returns a new database session.
        
        Returns:
            SQLAlchemy session
        """
        # Create a new session using the session factory
        return self._session_factory()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a raw SQL query.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Query results as a list of dictionaries
        """
        try:
            # Create a connection from the engine
            with self._engine.connect() as connection:
                # Execute the query with parameters
                result = connection.execute(text(query), params or {})
                
                # Fetch all results
                rows = result.fetchall()
                
                # Convert results to dictionaries
                if rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in rows]
                return []
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}", exc_info=True)
            raise DatabaseException(f"Query execution failed: {str(e)}", original_exception=e)
    
    def execute_transaction(self, func: Callable[[Session], T]) -> T:
        """
        Executes a function within a transaction.
        
        Args:
            func: Function to execute with session parameter
            
        Returns:
            Result of the function
        """
        # Create a new session
        session = self.get_session()
        
        try:
            # Begin a transaction
            session.begin()
            
            # Execute the provided function with the session
            result = func(session)
            
            # Commit the transaction if successful
            session.commit()
            
            return result
            
        except Exception as e:
            # Rollback the transaction if an exception occurs
            session.rollback()
            logger.error(f"Transaction error: {str(e)}", exc_info=True)
            raise
        finally:
            # Close the session
            session.close()
    
    def health_check(self) -> bool:
        """
        Performs a database health check.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            # Try to execute a simple query (SELECT 1)
            self.execute_query("SELECT 1 AS result")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}", exc_info=True)
            return False


# Create a singleton instance of Database for application-wide use
db = Database()