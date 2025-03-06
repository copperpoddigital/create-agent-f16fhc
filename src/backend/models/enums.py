"""
Enumerations for the Freight Price Movement Agent.

This module defines various enumeration types used throughout the application,
providing standardized options for transport modes, carrier types, trend directions,
analysis statuses, output formats, granularity types, user roles, and data source types/statuses.
"""

from enum import Enum, auto
from typing import Optional


class TransportMode(Enum):
    """Enumeration of transportation modes for freight."""
    OCEAN = auto()
    AIR = auto()
    ROAD = auto()
    RAIL = auto()
    MULTIMODAL = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the transport mode."""
        return self.name


class CarrierType(Enum):
    """Enumeration of carrier types in the freight industry."""
    OCEAN_CARRIER = auto()
    AIRLINE = auto()
    TRUCKING_COMPANY = auto()
    RAILWAY = auto()
    FREIGHT_FORWARDER = auto()
    INTEGRATOR = auto()
    OTHER = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the carrier type."""
        return self.name


class TrendDirection(Enum):
    """Enumeration of trend directions for price movement analysis."""
    INCREASING = auto()
    DECREASING = auto()
    STABLE = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the trend direction."""
        return self.name
    
    @classmethod
    def from_percentage(cls, percentage_change: float) -> 'TrendDirection':
        """Determines trend direction based on percentage change.
        
        Args:
            percentage_change: The percentage change value
            
        Returns:
            TrendDirection: The appropriate trend direction based on the percentage
        """
        if percentage_change > 1.0:
            return cls.INCREASING
        elif percentage_change < -1.0:
            return cls.DECREASING
        else:
            return cls.STABLE


class AnalysisStatus(Enum):
    """Enumeration of analysis job statuses."""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the analysis status."""
        return self.name


class OutputFormat(Enum):
    """Enumeration of output formats for analysis results."""
    JSON = auto()
    CSV = auto()
    TEXT = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the output format."""
        return self.name


class GranularityType(Enum):
    """Enumeration of time granularity options for analysis."""
    DAILY = auto()
    WEEKLY = auto()
    MONTHLY = auto()
    QUARTERLY = auto()
    CUSTOM = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the granularity type."""
        return self.name
    
    def get_days(self) -> Optional[int]:
        """Returns the number of days for a standard granularity type.
        
        Returns:
            int: Number of days for the granularity, or None for CUSTOM type
        """
        if self == GranularityType.DAILY:
            return 1
        elif self == GranularityType.WEEKLY:
            return 7
        elif self == GranularityType.MONTHLY:
            return 30
        elif self == GranularityType.QUARTERLY:
            return 90
        elif self == GranularityType.CUSTOM:
            return None


class UserRole(Enum):
    """Enumeration of user roles for access control."""
    ADMIN = auto()
    MANAGER = auto()
    ANALYST = auto()
    VIEWER = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the user role."""
        return self.name


class DataSourceType(Enum):
    """Enumeration of data source types for data ingestion."""
    CSV = auto()
    DATABASE = auto()
    API = auto()
    TMS = auto()
    ERP = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the data source type."""
        return self.name


class DataSourceStatus(Enum):
    """Enumeration of data source statuses."""
    ACTIVE = auto()
    INACTIVE = auto()
    ERROR = auto()
    WARNING = auto()
    
    def __str__(self) -> str:
        """Returns the string representation of the data source status."""
        return self.name