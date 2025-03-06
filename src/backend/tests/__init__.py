"""
Test package for the Freight Price Movement Agent.

This package contains all test modules and fixtures for testing the functionality
of the Freight Price Movement Agent, including unit, integration, and API tests.
The package supports the implementation of the comprehensive testing strategy
outlined in the technical specifications.
"""

import pathlib
import pytest  # pytest 7.0.0

# Define the root path of the tests package to enable relative imports
# and resource loading in test modules
TEST_PACKAGE_ROOT = pathlib.Path(__file__).parent.absolute()

# Version identifier for the tests package
__version__ = "1.0.0"