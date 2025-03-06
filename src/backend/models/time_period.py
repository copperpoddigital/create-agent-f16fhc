"""
Defines the SQLAlchemy ORM model for time periods used in freight price movement analysis.

This model represents user-defined time periods with start and end dates, granularity settings, 
and metadata for tracking and analysis purposes.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any

import sqlalchemy
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.db import Base
from .mixins import UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin
from .enums import GranularityType


class TimePeriod(Base, UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin):
    """SQLAlchemy model representing a time period for freight price movement analysis."""

    __tablename__ = "time_period"
    
    # Basic fields
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, index=True)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, index=True)
    granularity = sqlalchemy.Column(sqlalchemy.Enum(GranularityType), nullable=False, default=GranularityType.DAILY)
    custom_interval_days = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    is_custom = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    
    # Relationships
    analysis_results = sqlalchemy.orm.relationship('AnalysisResult', back_populates='time_period', cascade='all, delete-orphan')
    user = sqlalchemy.orm.relationship('User', foreign_keys=[created_by])
    
    def __init__(self, name: str, start_date: datetime, end_date: datetime, 
                granularity: Optional[GranularityType] = None, 
                custom_interval_days: Optional[int] = None,
                created_by: Optional[str] = None):
        """Initialize a new TimePeriod instance.
        
        Args:
            name: Descriptive name for the time period
            start_date: Starting date/time for the period
            end_date: Ending date/time for the period
            granularity: Time granularity (daily, weekly, monthly, etc.)
            custom_interval_days: Number of days for custom interval (used when granularity is CUSTOM)
            created_by: ID of the user creating this time period
        """
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.granularity = granularity or GranularityType.DAILY
        self.is_custom = self.granularity == GranularityType.CUSTOM
        
        if self.is_custom and custom_interval_days:
            self.custom_interval_days = custom_interval_days
            
        if created_by:
            self.created_by = created_by
    
    def validate_dates(self) -> bool:
        """Validates that the start date is before the end date.
        
        Returns:
            True if dates are valid, False otherwise
        """
        return self.start_date < self.end_date
    
    def get_duration_days(self) -> int:
        """Calculates the duration of the time period in days.
        
        Returns:
            Number of days between start and end dates
        """
        delta = self.end_date - self.start_date
        return delta.days
    
    def get_interval_days(self) -> int:
        """Gets the number of days for the granularity interval.
        
        Returns:
            Number of days in the granularity interval
        """
        if self.is_custom:
            return self.custom_interval_days
        return self.granularity.get_days()
    
    def get_periods(self) -> List[Tuple[datetime, datetime]]:
        """Generates a list of time periods based on the granularity.
        
        Returns:
            List of period start and end date tuples
        """
        interval_days = self.get_interval_days()
        periods = []
        
        current_start = self.start_date
        while current_start < self.end_date:
            # Calculate the end of this period
            current_end = current_start + timedelta(days=interval_days)
            
            # If we've gone past the overall end date, use the overall end date
            if current_end > self.end_date:
                current_end = self.end_date
                
            periods.append((current_start, current_end))
            current_start = current_end
            
        return periods
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the time period to a dictionary representation.
        
        Returns:
            Dictionary representation of the time period
        """
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "granularity": self.granularity.name,
            "is_custom": self.is_custom,
            "custom_interval_days": self.custom_interval_days if self.is_custom else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimePeriod':
        """Creates a TimePeriod instance from a dictionary.
        
        Args:
            data: Dictionary containing time period data
            
        Returns:
            New TimePeriod instance
        """
        # Convert date strings to datetime objects
        start_date = datetime.fromisoformat(data.get("start_date"))
        end_date = datetime.fromisoformat(data.get("end_date"))
        
        # Convert granularity string to GranularityType enum
        granularity_str = data.get("granularity", "DAILY")
        granularity = GranularityType[granularity_str]
        
        # Create new instance
        return cls(
            name=data.get("name"),
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            custom_interval_days=data.get("custom_interval_days"),
            created_by=data.get("created_by")
        )