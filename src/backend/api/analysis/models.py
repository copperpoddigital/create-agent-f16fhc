"""
API-specific models for the analysis module in the Freight Price Movement Agent.

This module defines database models that handle analysis requests, saved analyses,
and scheduled analyses. These models extend the core database models with API-specific
functionality for handling user interactions with the analysis system.
"""

from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Union, Any

import sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ...core.db import Base
from ...models.analysis_result import AnalysisResult
from ...models.time_period import TimePeriod
from ...models.mixins import UUIDMixin, TimestampMixin
from ...models.enums import TrendDirection, AnalysisStatus, GranularityType, OutputFormat


class AnalysisRequest(Base, UUIDMixin, TimestampMixin):
    """
    API model for handling freight price movement analysis requests.
    
    This model represents an analysis request initiated through the API,
    tracks its status, and maintains relationships with the time period and analysis result.
    """
    __tablename__ = "analysis_requests"
    
    # Relationships
    time_period_id = Column(String(36), ForeignKey('time_period.id'), nullable=False, index=True)
    time_period = relationship('TimePeriod')
    
    # Analysis configuration
    parameters = Column(JSON, nullable=False)
    output_format = Column(Enum(OutputFormat), nullable=False, default=OutputFormat.JSON)
    include_visualization = Column(Boolean, nullable=False, default=False)
    
    # Result tracking
    result_id = Column(String(36), ForeignKey('analysis_results.id'), nullable=True)
    result = relationship('AnalysisResult')
    
    # Status and error handling
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)
    error_message = Column(String, nullable=True)
    
    # User identification
    user_id = Column(String(36), nullable=False, index=True)
    
    def __init__(self, time_period_id: str, parameters: Dict, user_id: str,
                 output_format: Optional[OutputFormat] = None,
                 include_visualization: Optional[bool] = None):
        """
        Initializes a new AnalysisRequest instance.
        
        Args:
            time_period_id: ID of the time period for the analysis
            parameters: Dictionary of analysis parameters
            user_id: ID of the user creating the request
            output_format: Output format (JSON, CSV, TEXT)
            include_visualization: Whether to include visualization
        """
        super().__init__()
        self.time_period_id = time_period_id
        self.parameters = parameters
        self.user_id = user_id
        self.output_format = output_format or OutputFormat.JSON
        self.include_visualization = include_visualization if include_visualization is not None else False
        self.status = AnalysisStatus.PENDING
    
    def set_processing(self) -> None:
        """
        Updates the status to PROCESSING.
        """
        self.status = AnalysisStatus.PROCESSING
    
    def set_completed(self, result_id: str) -> None:
        """
        Updates the status to COMPLETED and links to the result.
        
        Args:
            result_id: ID of the completed AnalysisResult
        """
        self.result_id = result_id
        self.status = AnalysisStatus.COMPLETED
    
    def set_failed(self, error_message: str) -> None:
        """
        Updates the status to FAILED and sets an error message.
        
        Args:
            error_message: Error message explaining the failure
        """
        self.error_message = error_message
        self.status = AnalysisStatus.FAILED
    
    def to_dict(self) -> dict:
        """
        Converts the analysis request to a dictionary representation.
        
        Returns:
            Dictionary representation of the analysis request
        """
        return {
            "id": self.id,
            "time_period_id": self.time_period_id,
            "parameters": self.parameters,
            "output_format": self.output_format.name if self.output_format else None,
            "include_visualization": self.include_visualization,
            "result_id": self.result_id,
            "status": self.status.name if self.status else None,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def create_analysis_result(self) -> AnalysisResult:
        """
        Creates an AnalysisResult instance from this request.
        
        Returns:
            New AnalysisResult instance
        """
        return AnalysisResult(
            time_period_id=self.time_period_id,
            parameters=self.parameters,
            created_by=self.user_id,
            output_format=self.output_format
        )


class SavedAnalysis(Base, UUIDMixin, TimestampMixin):
    """
    API model for storing saved analysis configurations for reuse.
    
    This model allows users to save analysis configurations for future use,
    including all necessary parameters and settings.
    """
    __tablename__ = "saved_analyses"
    
    # Basic fields
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    time_period_id = Column(String(36), ForeignKey('time_period.id'), nullable=True)
    time_period = relationship('TimePeriod')
    
    # Analysis configuration
    parameters = Column(JSON, nullable=False)
    output_format = Column(Enum(OutputFormat), nullable=False, default=OutputFormat.JSON)
    include_visualization = Column(Boolean, nullable=False, default=False)
    
    # User identification and usage tracking
    user_id = Column(String(36), nullable=False, index=True)
    last_run_at = Column(DateTime, nullable=True)
    
    def __init__(self, name: str, parameters: Dict, user_id: str,
                 description: Optional[str] = None,
                 time_period_id: Optional[str] = None,
                 output_format: Optional[OutputFormat] = None,
                 include_visualization: Optional[bool] = None):
        """
        Initializes a new SavedAnalysis instance.
        
        Args:
            name: Descriptive name for the saved analysis
            parameters: Dictionary of analysis parameters
            user_id: ID of the user creating the saved analysis
            description: Optional description of the analysis
            time_period_id: Optional ID of a saved time period
            output_format: Output format preference
            include_visualization: Whether to include visualization
        """
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.user_id = user_id
        self.description = description
        self.time_period_id = time_period_id
        self.output_format = output_format or OutputFormat.JSON
        self.include_visualization = include_visualization if include_visualization is not None else False
    
    def update_last_run(self) -> None:
        """
        Updates the last_run_at timestamp to current time.
        """
        self.last_run_at = datetime.utcnow()
    
    def to_analysis_request(self) -> AnalysisRequest:
        """
        Creates an AnalysisRequest from this saved analysis.
        
        Returns:
            New AnalysisRequest instance
        """
        return AnalysisRequest(
            time_period_id=self.time_period_id,
            parameters=self.parameters,
            user_id=self.user_id,
            output_format=self.output_format,
            include_visualization=self.include_visualization
        )
    
    def to_dict(self) -> dict:
        """
        Converts the saved analysis to a dictionary representation.
        
        Returns:
            Dictionary representation of the saved analysis
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "time_period_id": self.time_period_id,
            "parameters": self.parameters,
            "output_format": self.output_format.name if self.output_format else None,
            "include_visualization": self.include_visualization,
            "user_id": self.user_id,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AnalysisSchedule(Base, UUIDMixin, TimestampMixin):
    """
    API model for scheduling recurring analysis jobs.
    
    This model allows users to schedule saved analyses to run at regular intervals,
    tracking execution history and upcoming runs.
    """
    __tablename__ = "analysis_schedules"
    
    # Basic fields
    name = Column(String(255), nullable=False)
    
    # Relationships
    saved_analysis_id = Column(String(36), ForeignKey('saved_analyses.id'), nullable=False)
    saved_analysis = relationship('SavedAnalysis')
    
    # Schedule configuration
    schedule_type = Column(String(50), nullable=False)  # daily, weekly, monthly, cron
    schedule_value = Column(String(100), nullable=False)  # Specific value for the schedule type
    
    # Status tracking
    is_active = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    
    # User identification
    user_id = Column(String(36), nullable=False, index=True)
    
    def __init__(self, name: str, saved_analysis_id: str, schedule_type: str,
                 schedule_value: str, user_id: str, is_active: Optional[bool] = None):
        """
        Initializes a new AnalysisSchedule instance.
        
        Args:
            name: Descriptive name for the schedule
            saved_analysis_id: ID of the saved analysis to schedule
            schedule_type: Type of schedule (daily, weekly, monthly, cron)
            schedule_value: Value specific to the schedule type
            user_id: ID of the user creating the schedule
            is_active: Whether the schedule is active
        """
        super().__init__()
        self.name = name
        self.saved_analysis_id = saved_analysis_id
        self.schedule_type = schedule_type
        self.schedule_value = schedule_value
        self.user_id = user_id
        self.is_active = is_active if is_active is not None else True
        
        # Calculate initial next run time
        self.next_run_at = self.calculate_next_run()
    
    def update_last_run(self) -> None:
        """
        Updates the last_run_at timestamp and calculates the next run time.
        """
        self.last_run_at = datetime.utcnow()
        self.next_run_at = self.calculate_next_run()
        
        # Update the saved analysis last run time as well
        if hasattr(self, 'saved_analysis') and self.saved_analysis:
            self.saved_analysis.update_last_run()
    
    def calculate_next_run(self) -> datetime:
        """
        Calculates the next scheduled run time based on schedule settings.
        
        Returns:
            Next scheduled run time
        """
        now = datetime.utcnow()
        
        if self.schedule_type == 'daily':
            # Add 1 day
            return now + timedelta(days=1)
        
        elif self.schedule_type == 'weekly':
            # Add 7 days
            return now + timedelta(days=7)
        
        elif self.schedule_type == 'monthly':
            # Add approximately 1 month (30 days)
            return now + timedelta(days=30)
        
        elif self.schedule_type == 'cron':
            # Basic implementation for cron-like schedules
            # In a real implementation, this would use a cron parser library
            try:
                # Simplified: Assume schedule_value contains hours as an integer
                hours_to_add = int(self.schedule_value)
                return now + timedelta(hours=hours_to_add)
            except ValueError:
                # Default to daily if parsing fails
                return now + timedelta(days=1)
        
        # Default fallback
        return now + timedelta(days=1)
    
    def activate(self) -> None:
        """
        Activates the schedule.
        """
        self.is_active = True
        if not self.next_run_at:
            self.next_run_at = self.calculate_next_run()
    
    def deactivate(self) -> None:
        """
        Deactivates the schedule.
        """
        self.is_active = False
    
    def to_dict(self) -> dict:
        """
        Converts the analysis schedule to a dictionary representation.
        
        Returns:
            Dictionary representation of the analysis schedule
        """
        return {
            "id": self.id,
            "name": self.name,
            "saved_analysis_id": self.saved_analysis_id,
            "schedule_type": self.schedule_type,
            "schedule_value": self.schedule_value,
            "is_active": self.is_active,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }