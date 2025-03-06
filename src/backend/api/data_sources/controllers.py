#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controller module for managing data sources in the Freight Price Movement Agent.
This module implements business logic for creating, retrieving, updating, and
deleting different types of data sources (CSV, Database, API, TMS, ERP), as
well as testing connections and managing data source status.
"""

# Standard library imports
import logging  # Logging functionality
import typing  # Type annotations
import uuid  # UUID handling
import datetime  # Date and time handling

# Third-party library imports
from sqlalchemy.exc import SQLAlchemyError  # SQLAlchemy exceptions for database error handling

# Internal application imports
from ...core.logging import get_logger  # Logging functionality
from .models import (  # Data source model classes
    DataSource,
    CSVDataSource,
    DatabaseDataSource,
    APIDataSource,
    TMSDataSource,
    ERPDataSource,
    DataSourceLog,
)
from ...models.enums import (  # Enumeration types for data source types and statuses
    DataSourceType,
    DataSourceStatus,
)
from .utils import (  # Utility functions for data source operations
    validate_data_source_config,
    test_data_source_connection,
    create_data_source_log,
    get_data_source_by_type,
)
from ...core.exceptions import (  # Custom exceptions for error handling
    HTTPException,
    NotFoundError,
    ValidationException,
    DatabaseError,
)

# Initialize logger for this module
logger = get_logger(__name__)


def get_data_sources(skip: int, limit: int, db: typing.Any) -> dict:
    """
    Retrieves a paginated list of data sources.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): Database session.

    Returns:
        dict: Paginated list of data sources with total count.
    """
    try:
        # Query the database for data sources with pagination
        data_sources = db.query(DataSource).offset(skip).limit(limit).all()

        # Count total number of data sources
        total = db.query(DataSource).count()

        # Return dictionary with items, total, page, and size
        return {"items": data_sources, "total": total, "page": skip // limit + 1, "size": limit}
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving data sources: {str(e)}")
        raise DatabaseError("Could not retrieve data sources from the database") from e


def get_data_source(data_source_id: uuid.UUID, db: typing.Any) -> DataSource:
    """
    Retrieves a specific data source by ID.

    Args:
        data_source_id (uuid.UUID): ID of the data source to retrieve.
        db (Session): Database session.

    Returns:
        DataSource: Data source with the specified ID.
    """
    try:
        # Query the database for data source with the specified ID
        data_source = db.query(DataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Return the data source
        return data_source
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving data source: {str(e)}")
        raise DatabaseError("Could not retrieve data source from the database") from e


def create_data_source(data_source_data: dict, db: typing.Any) -> DataSource:
    """
    Creates a new generic data source.

    Args:
        data_source_data (dict): Data for the new data source.
        db (Session): Database session.

    Returns:
        DataSource: Created data source.
    """
    try:
        # Create a new DataSource instance with the provided data
        data_source = DataSource(**data_source_data)

        # Validate the data source configuration
        validate_data_source_config(data_source)

        # Add the data source to the database session
        db.add(data_source)

        # Commit the transaction
        db.commit()

        # Refresh the data source to get the generated ID
        db.refresh(data_source)

        # Create a log entry for the creation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="CREATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the created data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error creating data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating data source: {str(e)}")
        db.rollback()
        raise


def create_csv_data_source(data_source_data: dict, db: typing.Any) -> CSVDataSource:
    """
    Creates a new CSV data source.

    Args:
        data_source_data (dict): Data for the new CSV data source.
        db (Session): Database session.

    Returns:
        CSVDataSource: Created CSV data source.
    """
    try:
        # Create a new CSVDataSource instance with the provided data
        data_source = CSVDataSource(**data_source_data)

        # Validate the CSV data source configuration
        validate_data_source_config(data_source)

        # Add the data source to the database session
        db.add(data_source)

        # Commit the transaction
        db.commit()

        # Refresh the data source to get the generated ID
        db.refresh(data_source)

        # Create a log entry for the creation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="CREATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the created CSV data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error creating CSV data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating CSV data source: {str(e)}")
        db.rollback()
        raise


def create_database_data_source(data_source_data: dict, db: typing.Any) -> DatabaseDataSource:
    """
    Creates a new database data source.

    Args:
        data_source_data (dict): Data for the new database data source.
        db (Session): Database session.

    Returns:
        DatabaseDataSource: Created database data source.
    """
    try:
        # Create a new DatabaseDataSource instance with the provided data
        data_source = DatabaseDataSource(**data_source_data)

        # Validate the database data source configuration
        validate_data_source_config(data_source)

        # Add the data source to the database session
        db.add(data_source)

        # Commit the transaction
        db.commit()

        # Refresh the data source to get the generated ID
        db.refresh(data_source)

        # Create a log entry for the creation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="CREATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the created database data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error creating database data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating database data source: {str(e)}")
        db.rollback()
        raise


def create_api_data_source(data_source_data: dict, db: typing.Any) -> APIDataSource:
    """
    Creates a new API data source.

    Args:
        data_source_data (dict): Data for the new API data source.
        db (Session): Database session.

    Returns:
        APIDataSource: Created API data source.
    """
    try:
        # Create a new APIDataSource instance with the provided data
        data_source = APIDataSource(**data_source_data)

        # Validate the API data source configuration
        validate_data_source_config(data_source)

        # Add the data source to the database session
        db.add(data_source)

        # Commit the transaction
        db.commit()

        # Refresh the data source to get the generated ID
        db.refresh(data_source)

        # Create a log entry for the creation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="CREATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the created API data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error creating API data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating API data source: {str(e)}")
        db.rollback()
        raise


def create_tms_data_source(data_source_data: dict, db: typing.Any) -> TMSDataSource:
    """
    Creates a new TMS data source.

    Args:
        data_source_data (dict): Data for the new TMS data source.
        db (Session): Database session.

    Returns:
        TMSDataSource: Created TMS data source.
    """
    try:
        # Create a new TMSDataSource instance with the provided data
        data_source = TMSDataSource(**data_source_data)

        # Validate the TMS data source configuration
        validate_data_source_config(data_source)

        # Add the data source to the database session
        db.add(data_source)

        # Commit the transaction
        db.commit()

        # Refresh the data source to get the generated ID
        db.refresh(data_source)

        # Create a log entry for the creation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="CREATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the created TMS data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error creating TMS data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating TMS data source: {str(e)}")
        db.rollback()
        raise


def create_erp_data_source(data_source_data: dict, db: typing.Any) -> ERPDataSource:
    """
    Creates a new ERP data source.

    Args:
        data_source_data (dict): Data for the new ERP data source.
        db (Session): Database session.

    Returns:
        ERPDataSource: Created ERP data source.
    """
    try:
        # Create a new ERPDataSource instance with the provided data
        data_source = ERPDataSource(**data_source_data)

        # Validate the ERP data source configuration
        validate_data_source_config(data_source)

        # Add the data source to the database session
        db.add(data_source)

        # Commit the transaction
        db.commit()

        # Refresh the data source to get the generated ID
        db.refresh(data_source)

        # Create a log entry for the creation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="CREATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the created ERP data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error creating ERP data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating ERP data source: {str(e)}")
        db.rollback()
        raise


def update_data_source(data_source_id: uuid.UUID, data_source_data: dict, db: typing.Any) -> DataSource:
    """
    Updates an existing data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to update.
        data_source_data (dict): Data to update the data source with.
        db (Session): Database session.

    Returns:
        DataSource: Updated data source.
    """
    try:
        # Retrieve the data source with the specified ID
        data_source = db.query(DataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Update the data source with the provided data
        for key, value in data_source_data.items():
            setattr(data_source, key, value)

        # Validate the updated configuration
        validate_data_source_config(data_source)

        # Commit the transaction
        db.commit()

        # Create a log entry for the update operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="UPDATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the updated data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error updating data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating data source: {str(e)}")
        db.rollback()
        raise


def update_csv_data_source(data_source_id: uuid.UUID, data_source_data: dict, db: typing.Any) -> CSVDataSource:
    """
    Updates an existing CSV data source.

    Args:
        data_source_id (uuid.UUID): ID of the CSV data source to update.
        data_source_data (dict): Data to update the CSV data source with.
        db (Session): Database session.

    Returns:
        CSVDataSource: Updated CSV data source.
    """
    try:
        # Retrieve the CSV data source with the specified ID
        data_source = db.query(CSVDataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"CSV data source with ID '{data_source_id}' not found")

        # Update the CSV data source with the provided data
        for key, value in data_source_data.items():
            setattr(data_source, key, value)

        # Validate the updated configuration
        validate_data_source_config(data_source)

        # Commit the transaction
        db.commit()

        # Create a log entry for the update operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="UPDATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the updated CSV data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error updating CSV data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating CSV data source: {str(e)}")
        db.rollback()
        raise


def update_database_data_source(data_source_id: uuid.UUID, data_source_data: dict, db: typing.Any) -> DatabaseDataSource:
    """
    Updates an existing database data source.

    Args:
        data_source_id (uuid.UUID): ID of the database data source to update.
        data_source_data (dict): Data to update the database data source with.
        db (Session): Database session.

    Returns:
        DatabaseDataSource: Updated database data source.
    """
    try:
        # Retrieve the database data source with the specified ID
        data_source = db.query(DatabaseDataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Database data source with ID '{data_source_id}' not found")

        # Update the database data source with the provided data
        for key, value in data_source_data.items():
            setattr(data_source, key, value)

        # Validate the updated configuration
        validate_data_source_config(data_source)

        # Commit the transaction
        db.commit()

        # Create a log entry for the update operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="UPDATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the updated database data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error updating database data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating database data source: {str(e)}")
        db.rollback()
        raise


def update_api_data_source(data_source_id: uuid.UUID, data_source_data: dict, db: typing.Any) -> APIDataSource:
    """
    Updates an existing API data source.

    Args:
        data_source_id (uuid.UUID): ID of the API data source to update.
        data_source_data (dict): Data to update the API data source with.
        db (Session): Database session.

    Returns:
        APIDataSource: Updated API data source.
    """
    try:
        # Retrieve the API data source with the specified ID
        data_source = db.query(APIDataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"API data source with ID '{data_source_id}' not found")

        # Update the API data source with the provided data
        for key, value in data_source_data.items():
            setattr(data_source, key, value)

        # Validate the updated configuration
        validate_data_source_config(data_source)

        # Commit the transaction
        db.commit()

        # Create a log entry for the update operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="UPDATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the updated API data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error updating API data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating API data source: {str(e)}")
        db.rollback()
        raise


def update_tms_data_source(data_source_id: uuid.UUID, data_source_data: dict, db: typing.Any) -> TMSDataSource:
    """
    Updates an existing TMS data source.

    Args:
        data_source_id (uuid.UUID): ID of the TMS data source to update.
        data_source_data (dict): Data to update the TMS data source with.
        db (Session): Database session.

    Returns:
        TMSDataSource: Updated TMS data source.
    """
    try:
        # Retrieve the TMS data source with the specified ID
        data_source = db.query(TMSDataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"TMS data source with ID '{data_source_id}' not found")

        # Update the TMS data source with the provided data
        for key, value in data_source_data.items():
            setattr(data_source, key, value)

        # Validate the updated configuration
        validate_data_source_config(data_source)

        # Commit the transaction
        db.commit()

        # Create a log entry for the update operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="UPDATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the updated TMS data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error updating TMS data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating TMS data source: {str(e)}")
        db.rollback()
        raise


def update_erp_data_source(data_source_id: uuid.UUID, data_source_data: dict, db: typing.Any) -> ERPDataSource:
    """
    Updates an existing ERP data source.

    Args:
        data_source_id (uuid.UUID): ID of the ERP data source to update.
        data_source_data (dict): Data to update the ERP data source with.
        db (Session): Database session.

    Returns:
        ERPDataSource: Updated ERP data source.
    """
    try:
        # Retrieve the ERP data source with the specified ID
        data_source = db.query(ERPDataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"ERP data source with ID '{data_source_id}' not found")

        # Update the ERP data source with the provided data
        for key, value in data_source_data.items():
            setattr(data_source, key, value)

        # Validate the updated configuration
        validate_data_source_config(data_source)

        # Commit the transaction
        db.commit()

        # Create a log entry for the update operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="UPDATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the updated ERP data source
        return data_source
    except (ValidationException, SQLAlchemyError) as e:
        logger.error(f"Error updating ERP data source: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating ERP data source: {str(e)}")
        db.rollback()
        raise


def delete_data_source(data_source_id: uuid.UUID, db: typing.Any) -> dict:
    """
    Deletes a data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to delete.
        db (Session): Database session.

    Returns:
        dict: Success message.
    """
    try:
        # Retrieve the data source with the specified ID
        data_source = db.query(DataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Mark the data source as deleted (soft delete)
        data_source.delete()

        # Commit the transaction
        db.commit()

        # Create a log entry for the deletion operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="DELETE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return success message
        return {"message": "Data source deleted successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting data source: {str(e)}")
        db.rollback()
        raise DatabaseError("Could not delete data source from the database") from e


def test_connection(request_data: dict, db: typing.Any) -> dict:
    """
    Tests the connection to a data source.

    Args:
        request_data (dict): Request data containing the data_source_id.
        db (Session): Database session.

    Returns:
        dict: Connection test results.
    """
    try:
        # Extract data_source_id from request_data
        data_source_id = request_data.get("data_source_id")
        if not data_source_id:
            raise ValidationException("Data source ID is required")

        # Retrieve the data source with the specified ID
        data_source = db.query(DataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Get the specific data source instance based on its type
        specific_data_source = get_data_source_by_type(data_source, db_session=db)

        # Test the connection using the appropriate connector
        connection_test_result = test_data_source_connection(specific_data_source)

        # Return the connection test results
        return connection_test_result
    except (ValidationException, NotFoundError, SQLAlchemyError) as e:
        logger.error(f"Error testing connection: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error testing connection: {str(e)}")
        raise


def activate_data_source(data_source_id: uuid.UUID, db: typing.Any) -> DataSource:
    """
    Activates a data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to activate.
        db (Session): Database session.

    Returns:
        DataSource: Activated data source.
    """
    try:
        # Retrieve the data source with the specified ID
        data_source = db.query(DataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Update the data source status to ACTIVE
        data_source.status = DataSourceStatus.ACTIVE

        # Commit the transaction
        db.commit()

        # Create a log entry for the activation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="ACTIVATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the activated data source
        return data_source
    except SQLAlchemyError as e:
        logger.error(f"Database error while activating data source: {str(e)}")
        db.rollback()
        raise DatabaseError("Could not activate data source in the database") from e


def deactivate_data_source(data_source_id: uuid.UUID, db: typing.Any) -> DataSource:
    """
    Deactivates a data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to deactivate.
        db (Session): Database session.

    Returns:
        DataSource: Deactivated data source.
    """
    try:
        # Retrieve the data source with the specified ID
        data_source = db.query(DataSource).get(data_source_id)

        # If data source not found, raise NotFoundError
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Update the data source status to INACTIVE
        data_source.status = DataSourceStatus.INACTIVE

        # Commit the transaction
        db.commit()

        # Create a log entry for the deactivation operation
        create_data_source_log(
            data_source_id=data_source.id,
            operation="DEACTIVATE",
            status="SUCCESS",
            performed_by="system",  # TODO: Get user ID from context
            db_session=db,
        )

        # Return the deactivated data source
        return data_source
    except SQLAlchemyError as e:
        logger.error(f"Database error while deactivating data source: {str(e)}")
        db.rollback()
        raise DatabaseError("Could not deactivate data source in the database") from e


def get_data_source_logs(data_source_id: uuid.UUID, skip: int, limit: int, db: typing.Any) -> dict:
    """
    Retrieves logs for a specific data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): Database session.

    Returns:
        dict: Paginated list of data source logs.
    """
    try:
        # Verify that the data source exists
        data_source = db.query(DataSource).get(data_source_id)
        if not data_source:
            raise NotFoundError(f"Data source with ID '{data_source_id}' not found")

        # Query the database for logs related to the specified data source with pagination
        logs = db.query(DataSourceLog).filter(DataSourceLog.data_source_id == data_source_id).offset(skip).limit(limit).all()

        # Count total number of logs for the data source
        total = db.query(DataSourceLog).filter(DataSourceLog.data_source_id == data_source_id).count()

        # Return dictionary with items, total, page, and size
        return {"items": logs, "total": total, "page": skip // limit + 1, "size": limit}
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving data source logs: {str(e)}")
        raise DatabaseError("Could not retrieve data source logs from the database") from e