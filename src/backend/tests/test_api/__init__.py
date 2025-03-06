"""
Initialization file for the test_api package in the Freight Price Movement Agent test suite.

This package contains tests for the API endpoints of the application, ensuring that all
API contracts are met and functioning as expected. The tests in this package cover authentication,
data sources, analysis, and reporting endpoints.
"""

import os
from pathlib import Path

# Version identifier for the test_api package
__version__ = "0.1.0"

# Path to the root of the test_api package for relative imports
TEST_API_PACKAGE_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))

# API version and base URL constants for all API tests
API_VERSION = "v1"
BASE_URL = f"/api/{API_VERSION}"