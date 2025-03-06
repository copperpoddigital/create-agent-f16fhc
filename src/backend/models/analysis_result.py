"""
SQLAlchemy ORM model for analysis results in the Freight Price Movement Agent.

This model stores the outcomes of freight price movement analyses, including
absolute and percentage changes, trend directions, and related metadata.
"""

import json
from datetime import datetime
from typing import Optional, Union, List, Dict, Any

import sqlalchemy
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, JSON, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from ..core.db import Base
from .mixins import UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin
from .enums import TrendDirection, AnalysisStatus, OutputFormat


class AnalysisResult(Base, UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin):
    """
    SQLAlchemy model representing the result of a freight price movement analysis.
    
    This model stores all details related to a price movement analysis, including
    the analysis parameters, calculated values, trend direction, and output format preferences.
    It also supports caching of results for performance optimization.
    """
    __tablename__ = "analysis_results"
    
    # Foreign keys and relationships
    time_period_id = Column(String(36), ForeignKey('time_periods.id'), nullable=False, index=True)
    
    # Analysis metadata
    name = Column(String(255), nullable=True)
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)
    parameters = Column(JSON, nullable=True)
    
    # Calculation results
    start_value = Column(Numeric(precision=15, scale=2), nullable=True)
    end_value = Column(Numeric(precision=15, scale=2), nullable=True)
    absolute_change = Column(Numeric(precision=15, scale=2), nullable=True)
    percentage_change = Column(Numeric(precision=10, scale=2), nullable=True)
    trend_direction = Column(Enum(TrendDirection), nullable=True)
    
    # Output settings
    currency_code = Column(String(3), nullable=False, default='USD')
    output_format = Column(Enum(OutputFormat), nullable=False, default=OutputFormat.JSON)
    
    # Results and error handling
    results = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    calculated_at = Column(DateTime, nullable=True)
    is_cached = Column(Boolean, nullable=False, default=False)
    cache_expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    time_period = relationship('TimePeriod', back_populates='analysis_results')
    user = relationship('User', foreign_keys=[created_by])
    
    def __init__(self, time_period_id: str, name: Optional[str] = None, 
                 parameters: Optional[dict] = None, created_by: Optional[str] = None,
                 output_format: Optional[OutputFormat] = None, currency_code: Optional[str] = None):
        """
        Initialize a new AnalysisResult instance.
        
        Args:
            time_period_id: ID of the time period for this analysis
            name: Optional name for the analysis
            parameters: Optional dictionary of analysis parameters
            created_by: Optional ID of the user creating the analysis
            output_format: Optional output format, defaults to JSON
            currency_code: Optional currency code, defaults to USD
        """
        # Initialize base class
        super().__init__()
        
        # Set required fields
        self.time_period_id = time_period_id
        self.name = name or f"Analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.parameters = parameters or {}
        
        # Set optional fields with defaults
        if created_by:
            self.created_by = created_by
        
        self.output_format = output_format or OutputFormat.JSON
        self.currency_code = currency_code or 'USD'
        self.status = AnalysisStatus.PENDING
    
    def update_status(self, status: AnalysisStatus, error_message: Optional[str] = None) -> None:
        """
        Updates the analysis status.
        
        Args:
            status: New status value
            error_message: Optional error message if status is FAILED
        """
        self.status = status
        
        if status == AnalysisStatus.FAILED and error_message:
            self.error_message = error_message
        
        if status == AnalysisStatus.COMPLETED:
            self.calculated_at = datetime.utcnow()
    
    def set_results(self, results: Union[dict, List], start_value: Optional[float] = None,
                   end_value: Optional[float] = None, absolute_change: Optional[float] = None,
                   percentage_change: Optional[float] = None, 
                   trend_direction: Optional[TrendDirection] = None) -> None:
        """
        Sets the analysis results.
        
        Args:
            results: The full analysis results as a dictionary or list
            start_value: Starting freight charge value
            end_value: Ending freight charge value
            absolute_change: Calculated absolute price change
            percentage_change: Calculated percentage price change
            trend_direction: Trend direction based on the price movement
        """
        # Store the full results
        self.results = results
        
        # Store individual metrics if provided
        if start_value is not None:
            self.start_value = start_value
        
        if end_value is not None:
            self.end_value = end_value
        
        if absolute_change is not None:
            self.absolute_change = absolute_change
        
        if percentage_change is not None:
            self.percentage_change = percentage_change
        
        # Set trend direction or calculate from percentage change
        if trend_direction:
            self.trend_direction = trend_direction
        elif percentage_change is not None:
            if percentage_change > 1.0:
                self.trend_direction = TrendDirection.INCREASING
            elif percentage_change < -1.0:
                self.trend_direction = TrendDirection.DECREASING
            else:
                self.trend_direction = TrendDirection.STABLE
        
        # Update status and calculation timestamp
        self.status = AnalysisStatus.COMPLETED
        self.calculated_at = datetime.utcnow()
    
    def set_cache_expiry(self, expiry_time: Optional[datetime] = None, 
                         minutes: Optional[int] = None) -> None:
        """
        Sets the cache expiry time for the analysis result.
        
        Args:
            expiry_time: Specific expiry datetime
            minutes: Number of minutes from now until expiry
        """
        self.is_cached = True
        
        if expiry_time:
            self.cache_expires_at = expiry_time
        elif minutes:
            self.cache_expires_at = datetime.utcnow().replace(microsecond=0) + datetime.timedelta(minutes=minutes)
        else:
            # Default cache expiry of 60 minutes
            self.cache_expires_at = datetime.utcnow().replace(microsecond=0) + datetime.timedelta(minutes=60)
    
    def is_cache_valid(self) -> bool:
        """
        Checks if the cached result is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        if not self.is_cached or not self.cache_expires_at:
            return False
        
        return datetime.utcnow() < self.cache_expires_at
    
    def to_dict(self, include_details: Optional[bool] = False) -> dict:
        """
        Converts the analysis result to a dictionary representation.
        
        Args:
            include_details: Whether to include the full results detail
            
        Returns:
            Dictionary representation of the analysis result
        """
        result = {
            "id": self.id,
            "name": self.name,
            "time_period_id": self.time_period_id,
            "status": self.status.name if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "created_by": self.created_by,
            "currency_code": self.currency_code,
            "output_format": self.output_format.name if self.output_format else None
        }
        
        # Add calculation results if available
        if self.status == AnalysisStatus.COMPLETED:
            result.update({
                "start_value": float(self.start_value) if self.start_value is not None else None,
                "end_value": float(self.end_value) if self.end_value is not None else None,
                "absolute_change": float(self.absolute_change) if self.absolute_change is not None else None,
                "percentage_change": float(self.percentage_change) if self.percentage_change is not None else None,
                "trend_direction": self.trend_direction.name if self.trend_direction else None
            })
        
        # Include error message if failed
        if self.status == AnalysisStatus.FAILED and self.error_message:
            result["error_message"] = self.error_message
        
        # Include full results if requested and available
        if include_details and self.results:
            result["results"] = self.results
        
        # Include cache information
        result["is_cached"] = self.is_cached
        if self.is_cached and self.cache_expires_at:
            result["cache_expires_at"] = self.cache_expires_at.isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AnalysisResult':
        """
        Creates an AnalysisResult instance from a dictionary.
        
        Args:
            data: Dictionary containing analysis result data
            
        Returns:
            New AnalysisResult instance
        """
        # Extract required fields
        time_period_id = data.get('time_period_id')
        if not time_period_id:
            raise ValueError("time_period_id is required")
        
        # Create a new instance with required fields
        instance = cls(
            time_period_id=time_period_id,
            name=data.get('name'),
            parameters=data.get('parameters'),
            created_by=data.get('created_by'),
            output_format=OutputFormat[data['output_format']] if 'output_format' in data else None,
            currency_code=data.get('currency_code')
        )
        
        # Set additional fields if present
        if 'status' in data:
            instance.status = AnalysisStatus[data['status']] if isinstance(data['status'], str) else data['status']
        
        if 'results' in data:
            instance.results = data['results']
        
        if 'start_value' in data:
            instance.start_value = data['start_value']
        
        if 'end_value' in data:
            instance.end_value = data['end_value']
        
        if 'absolute_change' in data:
            instance.absolute_change = data['absolute_change']
        
        if 'percentage_change' in data:
            instance.percentage_change = data['percentage_change']
        
        if 'trend_direction' in data:
            instance.trend_direction = TrendDirection[data['trend_direction']] if isinstance(data['trend_direction'], str) else data['trend_direction']
        
        if 'calculated_at' in data and data['calculated_at']:
            instance.calculated_at = datetime.fromisoformat(data['calculated_at']) if isinstance(data['calculated_at'], str) else data['calculated_at']
        
        if 'error_message' in data:
            instance.error_message = data['error_message']
        
        # Set cache properties
        if 'is_cached' in data:
            instance.is_cached = data['is_cached']
        
        if 'cache_expires_at' in data and data['cache_expires_at']:
            instance.cache_expires_at = datetime.fromisoformat(data['cache_expires_at']) if isinstance(data['cache_expires_at'], str) else data['cache_expires_at']
        
        return instance