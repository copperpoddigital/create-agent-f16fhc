#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines the RESTful API routes for managing data sources in the Freight Price Movement Agent.
This file implements endpoints for creating, retrieving, updating, and deleting different
types of data sources (CSV, Database, API, TMS, ERP), as well as testing connections
and managing data source status.
"""

# Import necessary modules and classes
import uuid  # v4
from typing import List  # Standard library
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response  # 0.95.x
from sqlalchemy.orm import Session  # ^1.4.40

from .controllers import (  # Internal imports
    get_data_sources,
    get_data_source,
    create_data_source,
    create_csv_data_source,
    create_database_data_source,
    create_api_data_source,
    create_tms_data_source,
    create_erp_data_source,
    update_data_source,
    update_csv_data_source,
    update_database_data_source,
    update_api_data_source,
    update_tms_data_source,
    update_erp_data_source,
    delete_data_source,
    test_connection,
    activate_data_source,
    deactivate_data_source,
    get_data_source_logs,
)
from .schemas import (  # Internal imports
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    CSVDataSourceCreate,
    CSVDataSourceUpdate,
    CSVDataSourceResponse,
    DatabaseDataSourceCreate,
    DatabaseDataSourceUpdate,
    DatabaseDataSourceResponse,
    APIDataSourceCreate,
    APIDataSourceUpdate,
    APIDataSourceResponse,
    TMSDataSourceCreate,
    TMSDataSourceUpdate,
    TMSDataSourceResponse,
    ERPDataSourceCreate,
    ERPDataSourceUpdate,
    ERPDataSourceResponse,
    DataSourceListResponse,
    DataSourceLogResponse,
    TestConnectionRequest,
    TestConnectionResponse,
)
from ...core.db import get_db  # Internal imports
from ..auth.controllers import get_current_user  # Internal imports
from ...models.user import User  # Internal imports
from ...core.exceptions import HTTPException, NotFoundError, ValidationError, DatabaseError  # Internal imports
from ...core.logging import logger  # Internal imports

# Define the router for data sources
router = APIRouter(prefix='/data-sources', tags=['Data Sources'])


@router.get('/', response_model=DataSourceListResponse)
def get_data_sources_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """
    Endpoint for retrieving a paginated list of data sources.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DataSourceListResponse: Paginated list of data sources.
    """
    logger.info(f"User {current_user.id} requested data sources list with skip={skip}, limit={limit}")
    try:
        data_sources = get_data_sources(skip=skip, limit=limit, db=db)
        return data_sources
    except Exception as e:
        logger.error(f"Error retrieving data sources: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/{data_source_id}', response_model=DataSourceResponse)
def get_data_source_route(data_source_id: uuid.UUID, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """
    Endpoint for retrieving a specific data source by ID.

    Args:
        data_source_id (uuid.UUID): ID of the data source to retrieve.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DataSourceResponse: Data source with the specified ID.
    """
    logger.info(f"User {current_user.id} requested data source with ID: {data_source_id}")
    try:
        data_source = get_data_source(data_source_id=data_source_id, db=db)
        return data_source
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/', response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_data_source_route(data_source: DataSourceCreate, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """
    Endpoint for creating a new generic data source.

    Args:
        data_source (DataSourceCreate): Data for the new data source.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DataSourceResponse: Created data source.
    """
    logger.info(f"User {current_user.id} requested creation of a new data source")
    try:
        created_data_source = create_data_source(data_source_data=data_source.dict(), db=db)
        return created_data_source
    except ValidationError as e:
        logger.error(f"Validation error creating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/csv', response_model=CSVDataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_csv_data_source_route(data_source: CSVDataSourceCreate, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    """
    Endpoint for creating a new CSV data source.

    Args:
        data_source (CSVDataSourceCreate): Data for the new CSV data source.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        CSVDataSourceResponse: Created CSV data source.
    """
    logger.info(f"User {current_user.id} requested creation of a new CSV data source")
    try:
        created_data_source = create_csv_data_source(data_source_data=data_source.dict(), db=db)
        return created_data_source
    except ValidationError as e:
        logger.error(f"Validation error creating CSV data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating CSV data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/database', response_model=DatabaseDataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_database_data_source_route(data_source: DatabaseDataSourceCreate, db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_user)):
    """
    Endpoint for creating a new database data source.

    Args:
        data_source (DatabaseDataSourceCreate): Data for the new database data source.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DatabaseDataSourceResponse: Created database data source.
    """
    logger.info(f"User {current_user.id} requested creation of a new database data source")
    try:
        created_data_source = create_database_data_source(data_source_data=data_source.dict(), db=db)
        return created_data_source
    except ValidationError as e:
        logger.error(f"Validation error creating database data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating database data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/api', response_model=APIDataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_api_data_source_route(data_source: APIDataSourceCreate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Endpoint for creating a new API data source.

    Args:
        data_source (APIDataSourceCreate): Data for the new API data source.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        APIDataSourceResponse: Created API data source.
    """
    logger.info(f"User {current_user.id} requested creation of a new API data source")
    try:
        created_data_source = create_api_data_source(data_source_data=data_source.dict(), db=db)
        return created_data_source
    except ValidationError as e:
        logger.error(f"Validation error creating API data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating API data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/tms', response_model=TMSDataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_tms_data_source_route(data_source: TMSDataSourceCreate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Endpoint for creating a new TMS data source.

    Args:
        data_source (TMSDataSourceCreate): Data for the new TMS data source.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        TMSDataSourceResponse: Created TMS data source.
    """
    logger.info(f"User {current_user.id} requested creation of a new TMS data source")
    try:
        created_data_source = create_tms_data_source(data_source_data=data_source.dict(), db=db)
        return created_data_source
    except ValidationError as e:
        logger.error(f"Validation error creating TMS data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating TMS data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/erp', response_model=ERPDataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_erp_data_source_route(data_source: ERPDataSourceCreate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Endpoint for creating a new ERP data source.

    Args:
        data_source (ERPDataSourceCreate): Data for the new ERP data source.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        ERPDataSourceResponse: Created ERP data source.
    """
    logger.info(f"User {current_user.id} requested creation of a new ERP data source")
    try:
        created_data_source = create_erp_data_source(data_source_data=data_source.dict(), db=db)
        return created_data_source
    except ValidationError as e:
        logger.error(f"Validation error creating ERP data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating ERP data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/{data_source_id}', response_model=DataSourceResponse)
def update_data_source_route(data_source_id: uuid.UUID, data_source: DataSourceUpdate, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating an existing data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to update.
        data_source (DataSourceUpdate): Data to update the data source with.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DataSourceResponse: Updated data source.
    """
    logger.info(f"User {current_user.id} requested update of data source with ID: {data_source_id}")
    try:
        updated_data_source = update_data_source(data_source_id=data_source_id, data_source_data=data_source.dict(), db=db)
        return updated_data_source
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error updating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/csv/{data_source_id}', response_model=CSVDataSourceResponse)
def update_csv_data_source_route(data_source_id: uuid.UUID, data_source: CSVDataSourceUpdate, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating an existing CSV data source.

    Args:
        data_source_id (uuid.UUID): ID of the CSV data source to update.
        data_source (CSVDataSourceUpdate): Data to update the CSV data source with.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        CSVDataSourceResponse: Updated CSV data source.
    """
    logger.info(f"User {current_user.id} requested update of CSV data source with ID: {data_source_id}")
    try:
        updated_data_source = update_csv_data_source(data_source_id=data_source_id, data_source_data=data_source.dict(), db=db)
        return updated_data_source
    except NotFoundError as e:
        logger.error(f"CSV data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error updating CSV data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating CSV data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/database/{data_source_id}', response_model=DatabaseDataSourceResponse)
def update_database_data_source_route(data_source_id: uuid.UUID, data_source: DatabaseDataSourceUpdate, db: Session = Depends(get_db),
                                     current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating an existing database data source.

    Args:
        data_source_id (uuid.UUID): ID of the database data source to update.
        data_source (DatabaseDataSourceUpdate): Data to update the database data source with.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DatabaseDataSourceResponse: Updated database data source.
    """
    logger.info(f"User {current_user.id} requested update of database data source with ID: {data_source_id}")
    try:
        updated_data_source = update_database_data_source(data_source_id=data_source_id, data_source_data=data_source.dict(), db=db)
        return updated_data_source
    except NotFoundError as e:
        logger.error(f"Database data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error updating database data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating database data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/api/{data_source_id}', response_model=APIDataSourceResponse)
def update_api_data_source_route(data_source_id: uuid.UUID, data_source: APIDataSourceUpdate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating an existing API data source.

    Args:
        data_source_id (uuid.UUID): ID of the API data source to update.
        data_source (APIDataSourceUpdate): Data to update the API data source with.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        APIDataSourceResponse: Updated API data source.
    """
    logger.info(f"User {current_user.id} requested update of API data source with ID: {data_source_id}")
    try:
        updated_data_source = update_api_data_source(data_source_id=data_source_id, data_source_data=data_source.dict(), db=db)
        return updated_data_source
    except NotFoundError as e:
        logger.error(f"API data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error updating API data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating API data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/tms/{data_source_id}', response_model=TMSDataSourceResponse)
def update_tms_data_source_route(data_source_id: uuid.UUID, data_source: TMSDataSourceUpdate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating an existing TMS data source.

    Args:
        data_source_id (uuid.UUID): ID of the TMS data source to update.
        data_source (TMSDataSourceUpdate): Data to update the TMS data source with.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        TMSDataSourceResponse: Updated TMS data source.
    """
    logger.info(f"User {current_user.id} requested update of TMS data source with ID: {data_source_id}")
    try:
        updated_data_source = update_tms_data_source(data_source_id=data_source_id, data_source_data=data_source.dict(), db=db)
        return updated_data_source
    except NotFoundError as e:
        logger.error(f"TMS data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error updating TMS data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating TMS data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/erp/{data_source_id}', response_model=ERPDataSourceResponse)
def update_erp_data_source_route(data_source_id: uuid.UUID, data_source: ERPDataSourceUpdate, db: Session = Depends(get_db),
                               current_user: User = Depends(get_current_user)):
    """
    Endpoint for updating an existing ERP data source.

    Args:
        data_source_id (uuid.UUID): ID of the ERP data source to update.
        data_source (ERPDataSourceUpdate): Data to update the ERP data source with.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        ERPDataSourceResponse: Updated ERP data source.
    """
    logger.info(f"User {current_user.id} requested update of ERP data source with ID: {data_source_id}")
    try:
        updated_data_source = update_erp_data_source(data_source_id=data_source_id, data_source_data=data_source.dict(), db=db)
        return updated_data_source
    except NotFoundError as e:
        logger.error(f"ERP data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error updating ERP data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating ERP data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/{data_source_id}')
def delete_data_source_route(data_source_id: uuid.UUID, db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    """
    Endpoint for deleting a data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to delete.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        dict: Success message.
    """
    logger.info(f"User {current_user.id} requested deletion of data source with ID: {data_source_id}")
    try:
        result = delete_data_source(data_source_id=data_source_id, db=db)
        return result
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/test-connection', response_model=TestConnectionResponse)
def test_connection_route(request_data: TestConnectionRequest, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    """
    Endpoint for testing the connection to a data source.

    Args:
        request_data (TestConnectionRequest): Request data containing the data_source_id.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        TestConnectionResponse: Connection test results.
    """
    logger.info(f"User {current_user.id} requested connection test for data source with ID: {request_data.data_source_id}")
    try:
        result = test_connection(request_data=request_data.dict(), db=db)
        return result
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.error(f"Validation error testing connection: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/{data_source_id}/activate', response_model=DataSourceResponse)
def activate_data_source_route(data_source_id: uuid.UUID, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    """
    Endpoint for activating a data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to activate.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DataSourceResponse: Activated data source.
    """
    logger.info(f"User {current_user.id} requested activation of data source with ID: {data_source_id}")
    try:
        activated_data_source = activate_data_source(data_source_id=data_source_id, db=db)
        return activated_data_source
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error activating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Error activating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/{data_source_id}/deactivate', response_model=DataSourceResponse)
def deactivate_data_source_route(data_source_id: uuid.UUID, db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    """
    Endpoint for deactivating a data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source to deactivate.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        DataSourceResponse: Deactivated data source.
    """
    logger.info(f"User {current_user.id} requested deactivation of data source with ID: {data_source_id}")
    try:
        deactivated_data_source = deactivate_data_source(data_source_id=data_source_id, db=db)
        return deactivated_data_source
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error deactivating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Error deactivating data source: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/{data_source_id}/logs', response_model=DataSourceListResponse)
def get_data_source_logs_route(data_source_id: uuid.UUID, skip: int = 0, limit: int = 100,
                              db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint for retrieving logs for a specific data source.

    Args:
        data_source_id (uuid.UUID): ID of the data source.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): Database session.
        current_user (User): Currently authenticated user.

    Returns:
        dict: Paginated list of data source logs.
    """
    logger.info(f"User {current_user.id} requested logs for data source with ID: {data_source_id}, skip={skip}, limit={limit}")
    try:
        data_source_logs = get_data_source_logs(data_source_id=data_source_id, skip=skip, limit=limit, db=db)
        return data_source_logs
    except NotFoundError as e:
        logger.error(f"Data source not found: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error retrieving data source logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving data source logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))