"""
Defines SQLAlchemy ORM models for the reports module of the Freight Price Movement Agent.

These models represent reports, report templates, scheduled reports, report sharing,
and report executions, enabling users to save, schedule, and share freight price
movement analysis results.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import sqlalchemy
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Integer, JSON, Text
from sqlalchemy.orm import relationship

from ...core.db import Base
from ...models.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin, UserTrackingMixin, AuditableMixin
from ...models.enums import ReportFormat, ReportStatus, ScheduleFrequency, OutputFormat
from ...models.analysis_result import AnalysisResult
from ...models.user import User


class Report(Base, UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin):
    """
    SQLAlchemy model representing a saved report in the Freight Price Movement Agent system.
    
    A report is based on an analysis result and includes format settings, parameters,
    and filters. Reports can be saved, scheduled, and shared with other users.
    """
    __tablename__ = "reports"
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Relationship to analysis result
    analysis_result_id = Column(String(36), ForeignKey('analysis_results.id'), nullable=False, index=True)
    analysis_result = relationship('AnalysisResult')
    
    # Output format and options
    format = Column(Enum(ReportFormat), nullable=False, default=ReportFormat.JSON)
    include_visualization = Column(Boolean, nullable=False, default=True)
    
    # Report configuration
    parameters = Column(JSON, nullable=False)  # Analysis parameters
    filters = Column(JSON, nullable=False)     # Data filters
    file_path = Column(String(255), nullable=True)  # Path to saved output file
    
    # Template flag
    is_template = Column(Boolean, nullable=False, default=False)
    
    # Execution tracking
    last_run_at = Column(DateTime, nullable=True)
    
    # Relationships
    schedules = relationship('ScheduledReport', back_populates='report', cascade='all, delete-orphan')
    shares = relationship('ReportShare', back_populates='report', cascade='all, delete-orphan')
    executions = relationship('ReportExecution', back_populates='report', cascade='all, delete-orphan')
    
    def __init__(self, name: str, analysis_result_id: str, format: ReportFormat, 
                 parameters: dict, filters: dict, description: Optional[str] = None,
                 include_visualization: Optional[bool] = None, file_path: Optional[str] = None,
                 is_template: Optional[bool] = None, created_by: Optional[str] = None):
        """
        Initializes a new Report instance.
        
        Args:
            name: Name of the report
            analysis_result_id: ID of the associated analysis result
            format: Output format for the report
            parameters: Dictionary of analysis parameters
            filters: Dictionary of data filters
            description: Optional description of the report
            include_visualization: Whether to include visualizations (defaults to True)
            file_path: Optional path to the saved output file
            is_template: Whether this report is a template (defaults to False)
            created_by: ID of the user creating the report
        """
        super().__init__()
        self.name = name
        self.analysis_result_id = analysis_result_id
        self.format = format
        self.parameters = parameters
        self.filters = filters
        if description:
            self.description = description
        self.include_visualization = True if include_visualization is None else include_visualization
        if file_path:
            self.file_path = file_path
        self.is_template = False if is_template is None else is_template
        if created_by:
            self.created_by = created_by
    
    def update_last_run(self) -> None:
        """
        Updates the last run timestamp to the current time.
        """
        self.last_run_at = datetime.utcnow()
    
    def to_dict(self, include_result: bool = False) -> dict:
        """
        Converts the report to a dictionary representation.
        
        Args:
            include_result: Whether to include the associated analysis result data
            
        Returns:
            Dictionary representation of the report
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'analysis_result_id': self.analysis_result_id,
            'format': self.format.name if self.format else None,
            'include_visualization': self.include_visualization,
            'parameters': self.parameters,
            'filters': self.filters,
            'file_path': self.file_path,
            'is_template': self.is_template,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
        
        if include_result and self.analysis_result:
            result['analysis_result'] = self.analysis_result.to_dict()
        
        return result
    
    def check_user_permission(self, user_id: str, permission_type: str) -> bool:
        """
        Checks if a user has specific permissions for this report.
        
        Args:
            user_id: The ID of the user to check
            permission_type: Type of permission to check ('view', 'edit', 'run', 'share')
            
        Returns:
            True if user has permission, False otherwise
        """
        # Owner has all permissions
        if self.created_by == user_id:
            return True
        
        # Check if this report is shared with the user
        for share in self.shares:
            if share.shared_with_id == user_id and share.is_valid():
                # Check specific permission
                if permission_type == 'view':
                    return True  # Any valid share grants view permission
                elif permission_type == 'edit':
                    return share.can_edit
                elif permission_type == 'run':
                    return share.can_run
                elif permission_type == 'share':
                    return share.can_share
        
        # No matching permission found
        return False


class ReportTemplate(Base, UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin):
    """
    SQLAlchemy model representing a report template that can be used to create new reports.
    
    Report templates define default parameters, filters, and output settings that can be
    used as a starting point for creating new reports.
    """
    __tablename__ = "report_templates"
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Default settings
    default_parameters = Column(JSON, nullable=False)
    default_filters = Column(JSON, nullable=False)
    default_format = Column(Enum(ReportFormat), nullable=False, default=ReportFormat.JSON)
    include_visualization = Column(Boolean, nullable=False, default=True)
    
    # Visibility
    is_public = Column(Boolean, nullable=False, default=False)
    
    def __init__(self, name: str, default_parameters: dict, default_filters: dict,
                 description: Optional[str] = None, default_format: Optional[ReportFormat] = None,
                 include_visualization: Optional[bool] = None, is_public: Optional[bool] = None,
                 created_by: Optional[str] = None):
        """
        Initializes a new ReportTemplate instance.
        
        Args:
            name: Name of the template
            default_parameters: Dictionary of default analysis parameters
            default_filters: Dictionary of default data filters
            description: Optional description of the template
            default_format: Default output format (defaults to JSON)
            include_visualization: Whether to include visualizations (defaults to True)
            is_public: Whether this template is publicly available (defaults to False)
            created_by: ID of the user creating the template
        """
        super().__init__()
        self.name = name
        self.default_parameters = default_parameters
        self.default_filters = default_filters
        if description:
            self.description = description
        self.default_format = default_format or ReportFormat.JSON
        self.include_visualization = True if include_visualization is None else include_visualization
        self.is_public = False if is_public is None else is_public
        if created_by:
            self.created_by = created_by
    
    def create_report(self, name: str, analysis_result_id: str, 
                     description: Optional[str] = None,
                     override_parameters: Optional[dict] = None, 
                     override_filters: Optional[dict] = None,
                     format: Optional[ReportFormat] = None,
                     include_visualization: Optional[bool] = None,
                     created_by: Optional[str] = None) -> 'Report':
        """
        Creates a new report based on this template.
        
        Args:
            name: Name for the new report
            analysis_result_id: ID of the analysis result for the report
            description: Optional description for the report
            override_parameters: Optional parameters to override template defaults
            override_filters: Optional filters to override template defaults
            format: Optional format to override template default
            include_visualization: Optional visualization setting to override template default
            created_by: ID of the user creating the report
            
        Returns:
            Newly created report instance
        """
        # Merge parameters and filters, with overrides taking precedence
        parameters = dict(self.default_parameters)
        if override_parameters:
            parameters.update(override_parameters)
            
        filters = dict(self.default_filters)
        if override_filters:
            filters.update(override_filters)
        
        # Use provided format or fall back to template default
        format = format or self.default_format
        
        # Use provided visualization setting or fall back to template default
        visualization = include_visualization if include_visualization is not None else self.include_visualization
        
        # Create a new report with the merged parameters
        report = Report(
            name=name,
            analysis_result_id=analysis_result_id,
            format=format,
            parameters=parameters,
            filters=filters,
            description=description,
            include_visualization=visualization,
            created_by=created_by or self.created_by
        )
        
        return report
    
    def to_dict(self) -> dict:
        """
        Converts the template to a dictionary representation.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'default_parameters': self.default_parameters,
            'default_filters': self.default_filters,
            'default_format': self.default_format.name if self.default_format else None,
            'include_visualization': self.include_visualization,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class ScheduledReport(Base, UUIDMixin, TimestampMixin, UserTrackingMixin, AuditableMixin):
    """
    SQLAlchemy model representing a scheduled execution of a report.
    
    Scheduled reports run automatically at defined intervals, generating
    report outputs and optionally sending notifications.
    """
    __tablename__ = "scheduled_reports"
    
    # Relationship to report
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False, index=True)
    report = relationship('Report', back_populates='schedules')
    
    # Schedule configuration
    frequency = Column(Enum(ScheduleFrequency), nullable=False)
    day_of_week = Column(Integer, nullable=True)  # 0-6, where 0 is Monday (for WEEKLY)
    day_of_month = Column(Integer, nullable=True)  # 1-31 (for MONTHLY)
    hour = Column(Integer, nullable=False)  # 0-23
    minute = Column(Integer, nullable=False)  # 0-59
    
    # Status
    active = Column(Boolean, nullable=False, default=True)
    next_run_at = Column(DateTime, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    
    # Notification settings
    notification_settings = Column(JSON, nullable=True)
    
    # Relationship to executions
    executions = relationship('ReportExecution', back_populates='scheduled_report')
    
    def __init__(self, report_id: str, frequency: ScheduleFrequency, hour: int, minute: int,
                 day_of_week: Optional[int] = None, day_of_month: Optional[int] = None,
                 active: Optional[bool] = None, notification_settings: Optional[dict] = None,
                 created_by: Optional[str] = None):
        """
        Initializes a new ScheduledReport instance.
        
        Args:
            report_id: ID of the report to schedule
            frequency: How often to run the report
            hour: Hour of the day to run (0-23)
            minute: Minute of the hour to run (0-59)
            day_of_week: Day of week for weekly schedules (0-6, where 0 is Monday)
            day_of_month: Day of month for monthly schedules (1-31)
            active: Whether the schedule is active (defaults to True)
            notification_settings: Optional settings for notifications
            created_by: ID of the user creating the schedule
        """
        super().__init__()
        self.report_id = report_id
        self.frequency = frequency
        self.hour = hour
        self.minute = minute
        
        # Set day_of_week for WEEKLY frequency
        if frequency == ScheduleFrequency.WEEKLY:
            if day_of_week is None:
                raise ValueError("day_of_week must be specified for WEEKLY frequency")
            if not 0 <= day_of_week <= 6:
                raise ValueError("day_of_week must be between 0 and 6")
            self.day_of_week = day_of_week
        
        # Set day_of_month for MONTHLY frequency
        if frequency == ScheduleFrequency.MONTHLY:
            if day_of_month is None:
                raise ValueError("day_of_month must be specified for MONTHLY frequency")
            if not 1 <= day_of_month <= 31:
                raise ValueError("day_of_month must be between 1 and 31")
            self.day_of_month = day_of_month
        
        self.active = True if active is None else active
        self.notification_settings = notification_settings
        
        # Calculate initial next_run_at
        self.next_run_at = self.calculate_next_run()
        self.status = ReportStatus.PENDING
        
        if created_by:
            self.created_by = created_by
    
    def calculate_next_run(self) -> datetime:
        """
        Calculates the next scheduled run time based on frequency and other parameters.
        
        Returns:
            Next scheduled run time
        """
        now = datetime.utcnow().replace(second=0, microsecond=0)
        
        if self.frequency == ScheduleFrequency.DAILY:
            next_run = datetime(now.year, now.month, now.day, self.hour, self.minute)
            if next_run <= now:
                next_run = next_run.replace(day=now.day + 1)
                
        elif self.frequency == ScheduleFrequency.WEEKLY:
            # Calculate days until the next occurrence of day_of_week
            days_ahead = self.day_of_week - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_date = now + timedelta(days=days_ahead)
            next_run = datetime(next_date.year, next_date.month, next_date.day, self.hour, self.minute)
            
        elif self.frequency == ScheduleFrequency.MONTHLY:
            # Try to find the specified day in the current month
            try:
                next_run = datetime(now.year, now.month, self.day_of_month, self.hour, self.minute)
                if next_run <= now:
                    # Move to next month
                    if now.month == 12:
                        next_run = next_run.replace(year=now.year + 1, month=1)
                    else:
                        next_run = next_run.replace(month=now.month + 1)
            except ValueError:
                # Handle invalid dates (e.g., February 30)
                # Move to the first of the following month
                if now.month == 12:
                    next_run = datetime(now.year + 1, 1, 1, self.hour, self.minute)
                else:
                    next_run = datetime(now.year, now.month + 1, 1, self.hour, self.minute)
                    
        elif self.frequency == ScheduleFrequency.QUARTERLY:
            # Determine the current quarter
            current_quarter = (now.month - 1) // 3 + 1
            next_quarter_month = 3 * current_quarter + 1  # First month of next quarter
            
            # Handle year boundary
            if next_quarter_month > 12:
                next_quarter_month = 1
                next_quarter_year = now.year + 1
            else:
                next_quarter_year = now.year
                
            next_run = datetime(next_quarter_year, next_quarter_month, 1, self.hour, self.minute)
            
        else:
            # Fallback for unknown frequency
            next_run = now + timedelta(days=1)
            
        return next_run
    
    def update_next_run(self) -> None:
        """
        Updates the next_run_at field based on current schedule.
        """
        self.next_run_at = self.calculate_next_run()
    
    def update_last_run(self, status: ReportStatus) -> None:
        """
        Updates the last_run_at timestamp and status.
        
        Args:
            status: New status for the scheduled report
        """
        self.last_run_at = datetime.utcnow()
        self.status = status
        
        # Update next_run_at for the next execution
        self.update_next_run()
    
    def to_dict(self) -> dict:
        """
        Converts the scheduled report to a dictionary representation.
        
        Returns:
            Dictionary representation of the scheduled report
        """
        return {
            'id': self.id,
            'report_id': self.report_id,
            'frequency': self.frequency.name if self.frequency else None,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'hour': self.hour,
            'minute': self.minute,
            'active': self.active,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'status': self.status.name if self.status else None,
            'notification_settings': self.notification_settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class ReportShare(Base, UUIDMixin, TimestampMixin, AuditableMixin):
    """
    SQLAlchemy model representing a report shared with another user.
    
    This model enables report sharing with granular permission control,
    allowing the owner to specify what actions the recipient can perform.
    """
    __tablename__ = "report_shares"
    
    # Relationship to report
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False, index=True)
    report = relationship('Report', back_populates='shares')
    
    # User relationships
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    owner = relationship('User', foreign_keys=[owner_id])
    
    shared_with_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    shared_with = relationship('User', foreign_keys=[shared_with_id])
    
    # Permission settings
    can_edit = Column(Boolean, nullable=False, default=False)
    can_run = Column(Boolean, nullable=False, default=True)
    can_share = Column(Boolean, nullable=False, default=False)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    def __init__(self, report_id: str, owner_id: str, shared_with_id: str,
                 can_edit: Optional[bool] = None, can_run: Optional[bool] = None,
                 can_share: Optional[bool] = None, expires_at: Optional[datetime] = None):
        """
        Initializes a new ReportShare instance.
        
        Args:
            report_id: ID of the report being shared
            owner_id: ID of the user who owns the report
            shared_with_id: ID of the user receiving access to the report
            can_edit: Whether the recipient can edit the report (defaults to False)
            can_run: Whether the recipient can run the report (defaults to True)
            can_share: Whether the recipient can reshare the report (defaults to False)
            expires_at: Optional expiration date for this share
        """
        super().__init__()
        self.report_id = report_id
        self.owner_id = owner_id
        self.shared_with_id = shared_with_id
        self.can_edit = False if can_edit is None else can_edit
        self.can_run = True if can_run is None else can_run
        self.can_share = False if can_share is None else can_share
        self.expires_at = expires_at
    
    def is_valid(self) -> bool:
        """
        Checks if the share is currently valid (not expired).
        
        Returns:
            True if share is valid, False if expired
        """
        if self.expires_at is None:
            return True  # No expiration set
        
        return datetime.utcnow() < self.expires_at
    
    def to_dict(self) -> dict:
        """
        Converts the report share to a dictionary representation.
        
        Returns:
            Dictionary representation of the report share
        """
        return {
            'id': self.id,
            'report_id': self.report_id,
            'owner_id': self.owner_id,
            'shared_with_id': self.shared_with_id,
            'can_edit': self.can_edit,
            'can_run': self.can_run,
            'can_share': self.can_share,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_valid': self.is_valid()
        }


class ReportExecution(Base, UUIDMixin, TimestampMixin, AuditableMixin):
    """
    SQLAlchemy model representing a single execution of a report.
    
    This model tracks the execution of reports, including execution time,
    status, and results location. It provides insight into report processing
    history and helps with performance tracking.
    """
    __tablename__ = "report_executions"
    
    # Relationship to report
    report_id = Column(String(36), ForeignKey('reports.id'), nullable=False, index=True)
    report = relationship('Report', back_populates='executions')
    
    # Relationship to scheduled report (if applicable)
    scheduled_report_id = Column(String(36), ForeignKey('scheduled_reports.id'), nullable=True, index=True)
    scheduled_report = relationship('ScheduledReport', back_populates='executions')
    
    # Execution details
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PROCESSING)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Output
    output_location = Column(String(255), nullable=True)
    
    # Execution parameters
    execution_parameters = Column(JSON, nullable=False)
    
    def __init__(self, report_id: str, execution_parameters: dict,
                 scheduled_report_id: Optional[str] = None, created_by: Optional[str] = None):
        """
        Initializes a new ReportExecution instance.
        
        Args:
            report_id: ID of the report being executed
            execution_parameters: Parameters used for this execution
            scheduled_report_id: Optional ID of the scheduled report that triggered this execution
            created_by: ID of the user who initiated the execution
        """
        super().__init__()
        self.report_id = report_id
        self.execution_parameters = execution_parameters
        self.scheduled_report_id = scheduled_report_id
        self.started_at = datetime.utcnow()
        self.status = ReportStatus.PROCESSING
        
        if created_by:
            self.created_by = created_by
    
    def complete(self, output_location: Optional[str] = None) -> None:
        """
        Marks the execution as completed successfully.
        
        Args:
            output_location: Optional location where the output is stored
        """
        now = datetime.utcnow()
        self.completed_at = now
        self.status = ReportStatus.COMPLETED
        
        # Calculate duration in seconds
        self.duration_seconds = int((now - self.started_at).total_seconds())
        
        if output_location:
            self.output_location = output_location
        
        # Update the report's last_run_at
        self.report.update_last_run()
        
        # Update the scheduled report if this was a scheduled execution
        if self.scheduled_report:
            self.scheduled_report.update_last_run(ReportStatus.COMPLETED)
    
    def fail(self, error_message: str) -> None:
        """
        Marks the execution as failed with an error message.
        
        Args:
            error_message: Description of the error that occurred
        """
        now = datetime.utcnow()
        self.completed_at = now
        self.status = ReportStatus.FAILED
        self.error_message = error_message
        
        # Calculate duration in seconds
        self.duration_seconds = int((now - self.started_at).total_seconds())
        
        # Update the scheduled report if this was a scheduled execution
        if self.scheduled_report:
            self.scheduled_report.update_last_run(ReportStatus.FAILED)
    
    def to_dict(self) -> dict:
        """
        Converts the report execution to a dictionary representation.
        
        Returns:
            Dictionary representation of the report execution
        """
        return {
            'id': self.id,
            'report_id': self.report_id,
            'scheduled_report_id': self.scheduled_report_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status.name if self.status else None,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds,
            'output_location': self.output_location,
            'execution_parameters': self.execution_parameters,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }