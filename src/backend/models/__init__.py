"""
Initialize the models package for the Freight Price Movement Agent application.

This file imports and exposes all SQLAlchemy model classes and enumerations
from individual model files, providing a centralized access point for
the application's data models.
"""

# Import models
from .audit_log import ActionType, AuditLog
from .analysis_result import AnalysisResult
from .carrier import Carrier
from .freight_data import FreightData, FreightDataRoute
from .location import Location
from .route import Route
from .time_period import TimePeriod
from .user import User

# Import enums
from .enums import (
    TransportMode, 
    CarrierType, 
    TrendDirection, 
    AnalysisStatus, 
    OutputFormat, 
    GranularityType, 
    UserRole, 
    DataSourceType, 
    DataSourceStatus
)

# Import mixins
from .mixins import (
    TimestampMixin,
    UUIDMixin,
    SoftDeleteMixin,
    UserTrackingMixin,
    TimescaleDBModelMixin,
    AuditableMixin
)

# Define what gets imported with "from backend.models import *"
__all__ = [
    # Models
    'ActionType',
    'AuditLog',
    'AnalysisResult',
    'Carrier',
    'FreightData',
    'FreightDataRoute',
    'Location',
    'Route',
    'TimePeriod',
    'User',
    
    # Enums
    'TransportMode',
    'CarrierType',
    'TrendDirection',
    'AnalysisStatus',
    'OutputFormat',
    'GranularityType',
    'UserRole',
    'DataSourceType',
    'DataSourceStatus',
    
    # Mixins
    'TimestampMixin',
    'UUIDMixin',
    'SoftDeleteMixin',
    'UserTrackingMixin',
    'TimescaleDBModelMixin',
    'AuditableMixin'
]