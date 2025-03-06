"""
Admin module for the Freight Price Movement Agent.

This module provides administrative functionality including system configuration
management, admin activity logging, and maintenance scheduling. It integrates with
the core error handling, logging, and security components to ensure robust and
secure administrative operations.

The admin module exposes a Flask Blueprint (admin_bp) that defines API routes
for administrative functions, which can be registered with the main Flask application.
"""

from typing import Dict, Any

# Import admin Blueprint from routes module
from .routes import admin_bp

# Set module version for tracking and compatibility
__version__ = "0.1.0"

# Export admin Blueprint for registration with the main Flask application
__all__ = ["admin_bp"]