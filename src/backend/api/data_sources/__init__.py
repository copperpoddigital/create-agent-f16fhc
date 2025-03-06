#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialization file for the data_sources module in the Freight Price Movement Agent.
This file exports the router and necessary components for managing different types of data sources (CSV, Database, API, TMS, ERP) used for freight data collection.
"""

# Import the data sources router for exposure to the main API
from .routes import router  # Import APIRouter object

# Import data source model classes for exposure to other modules
from .models import (
    DataSource,
    CSVDataSource,
    DatabaseDataSource,
    APIDataSource,
    TMSDataSource,
    ERPDataSource,
    DataSourceLog,
)  # Import class definitions

# Import schema classes for exposure to other modules
from .schemas import (
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
)  # Import class definitions

# Export the data sources router for inclusion in the main API router
__all__ = [
    "router",
    "DataSource",
    "CSVDataSource",
    "DatabaseDataSource",
    "APIDataSource",
    "TMSDataSource",
    "ERPDataSource",
    "DataSourceLog",
    "DataSourceCreate",
    "DataSourceUpdate",
    "DataSourceResponse",
    "CSVDataSourceCreate",
    "CSVDataSourceUpdate",
    "CSVDataSourceResponse",
    "DatabaseDataSourceCreate",
    "DatabaseDataSourceUpdate",
    "DatabaseDataSourceResponse",
    "APIDataSourceCreate",
    "APIDataSourceUpdate",
    "APIDataSourceResponse",
    "TMSDataSourceCreate",
    "TMSDataSourceUpdate",
    "TMSDataSourceResponse",
    "ERPDataSourceCreate",
    "ERPDataSourceUpdate",
    "ERPDataSourceResponse",
    "DataSourceListResponse",
    "DataSourceLogResponse",
    "TestConnectionRequest",
    "TestConnectionResponse",
]