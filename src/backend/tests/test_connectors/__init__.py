"""
Test package for connector components of the Freight Price Movement Agent.

This package contains unit tests for various data source connectors including:
- File connectors (CSV, Excel)
- Database connectors
- API connectors 
- TMS connectors (SAP, Oracle, JDA)
- ERP connectors

These tests verify the functionality of the data ingestion components
responsible for collecting and processing freight pricing data from multiple sources.
"""

import os
import sys

# Path to the root of the test_connectors package for relative imports
TEST_CONNECTORS_PACKAGE = os.path.dirname(os.path.abspath(__file__))

# List of modules to be imported when using 'from tests.test_connectors import *'
__all__ = [
    # File connectors
    'test_csv_connector',
    'test_excel_connector',
    
    # Database connectors
    'test_database_connector',
    
    # API connectors
    'test_api_connector',
    
    # TMS connectors
    'test_sap_connector',
    'test_oracle_connector',
    'test_jda_connector',
    
    # ERP connectors
    'test_erp_connector'
]