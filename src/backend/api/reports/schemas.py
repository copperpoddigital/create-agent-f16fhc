"""
Defines Pydantic schema models for the reports API of the Freight Price Movement Agent.

This module provides schemas for data validation, serialization, and API documentation
of reports, report templates, scheduled reports, report sharing, and report executions.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from pydantic import validator

from ...core.schemas import BaseModel
from ...schemas.common import IDModel, TimestampModel, AuditableModel, FreightDataFilterParams, OutputFormatParams
from ...schemas.analysis_result import AnalysisResultDetail
from ...models.enums import ReportFormat, ReportStatus, ScheduleFrequency


# Report schemas
class ReportBase(BaseModel):
    """Base schema for report data without ID or audit fields."""
    name: str
    description: Optional[str] = None
    analysis_result_id: uuid.UUID
    format: ReportFormat = ReportFormat.JSON
    include_visualization: bool = True
    parameters: Dict
    filters: Dict
    file_path: Optional[str] = None
    is_template: Optional[bool] = False
    last_run_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class ReportCreate(ReportBase):
    """Schema for creating a new report."""
    user_id: Optional[uuid.UUID] = None


class ReportUpdate(BaseModel):
    """Schema for updating an existing report."""
    name: Optional[str] = None
    description: Optional[str] = None
    analysis_result_id: Optional[uuid.UUID] = None
    format: Optional[ReportFormat] = None
    include_visualization: Optional[bool] = None
    parameters: Optional[Dict] = None
    filters: Optional[Dict] = None
    file_path: Optional[str] = None
    is_template: Optional[bool] = None
    last_run_at: Optional[datetime] = None


class Report(IDModel, TimestampModel, AuditableModel, ReportBase):
    """Complete schema for a report with ID and audit fields."""
    analysis_result: Optional[AnalysisResultDetail] = None


class ReportResponse(BaseModel):
    """Schema for API responses containing a report."""
    data: Report
    success: bool = True
    message: Optional[str] = None


class ReportListResponse(BaseModel):
    """Schema for API responses containing a list of reports."""
    data: List[Report]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


# Report Template schemas
class ReportTemplateBase(BaseModel):
    """Base schema for report template data without ID or audit fields."""
    name: str
    description: Optional[str] = None
    default_parameters: Dict
    default_filters: Dict
    default_format: ReportFormat = ReportFormat.JSON
    include_visualization: bool = True
    is_public: bool = False
    
    class Config:
        orm_mode = True


class ReportTemplateCreate(ReportTemplateBase):
    """Schema for creating a new report template."""
    user_id: Optional[uuid.UUID] = None


class ReportTemplateUpdate(BaseModel):
    """Schema for updating an existing report template."""
    name: Optional[str] = None
    description: Optional[str] = None
    default_parameters: Optional[Dict] = None
    default_filters: Optional[Dict] = None
    default_format: Optional[ReportFormat] = None
    include_visualization: Optional[bool] = None
    is_public: Optional[bool] = None


class ReportTemplate(IDModel, TimestampModel, AuditableModel, ReportTemplateBase):
    """Complete schema for a report template with ID and audit fields."""
    pass


class ReportTemplateResponse(BaseModel):
    """Schema for API responses containing a report template."""
    data: ReportTemplate
    success: bool = True
    message: Optional[str] = None


class ReportTemplateListResponse(BaseModel):
    """Schema for API responses containing a list of report templates."""
    data: List[ReportTemplate]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


# Scheduled Report schemas
class ScheduledReportBase(BaseModel):
    """Base schema for scheduled report data without ID or audit fields."""
    report_id: uuid.UUID
    frequency: ScheduleFrequency
    day_of_week: Optional[int] = None  # 0-6, where 0 is Monday
    day_of_month: Optional[int] = None  # 1-31
    hour: int  # 0-23
    minute: int  # 0-59
    active: bool = True
    notification_settings: Optional[Dict] = None
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    status: ReportStatus = ReportStatus.PENDING
    
    class Config:
        orm_mode = True


class ScheduledReportCreate(ScheduledReportBase):
    """Schema for creating a new scheduled report."""
    user_id: Optional[uuid.UUID] = None


class ScheduledReportUpdate(BaseModel):
    """Schema for updating an existing scheduled report."""
    report_id: Optional[uuid.UUID] = None
    frequency: Optional[ScheduleFrequency] = None
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    active: Optional[bool] = None
    notification_settings: Optional[Dict] = None
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    status: Optional[ReportStatus] = None


class ScheduledReport(IDModel, TimestampModel, AuditableModel, ScheduledReportBase):
    """Complete schema for a scheduled report with ID and audit fields."""
    report: Optional[Report] = None


class ScheduledReportResponse(BaseModel):
    """Schema for API responses containing a scheduled report."""
    data: ScheduledReport
    success: bool = True
    message: Optional[str] = None


class ScheduledReportListResponse(BaseModel):
    """Schema for API responses containing a list of scheduled reports."""
    data: List[ScheduledReport]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


# Report Share schemas
class ReportShareBase(BaseModel):
    """Base schema for report share data without ID or audit fields."""
    report_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with_id: uuid.UUID
    can_edit: bool = False
    can_run: bool = True
    can_share: bool = False
    expires_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class ReportShareCreate(ReportShareBase):
    """Schema for creating a new report share."""
    pass


class ReportShareUpdate(BaseModel):
    """Schema for updating an existing report share."""
    report_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with_id: uuid.UUID
    can_edit: Optional[bool] = None
    can_run: Optional[bool] = None
    can_share: Optional[bool] = None
    expires_at: Optional[datetime] = None


class ReportShare(IDModel, TimestampModel, ReportShareBase):
    """Complete schema for a report share with ID and audit fields."""
    report: Optional[Report] = None
    is_valid: bool = True  # Calculated field to check if share has not expired


class ReportShareResponse(BaseModel):
    """Schema for API responses containing a report share."""
    data: ReportShare
    success: bool = True
    message: Optional[str] = None


class ReportShareListResponse(BaseModel):
    """Schema for API responses containing a list of report shares."""
    data: List[ReportShare]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


# Report Execution schemas
class ReportExecutionBase(BaseModel):
    """Base schema for report execution data without ID or audit fields."""
    report_id: uuid.UUID
    scheduled_report_id: Optional[uuid.UUID] = None
    started_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None
    status: ReportStatus = ReportStatus.PROCESSING
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
    output_location: Optional[str] = None
    execution_parameters: Dict
    
    class Config:
        orm_mode = True


class ReportExecutionCreate(ReportExecutionBase):
    """Schema for creating a new report execution."""
    user_id: Optional[uuid.UUID] = None


class ReportExecution(IDModel, TimestampModel, AuditableModel, ReportExecutionBase):
    """Complete schema for a report execution with ID and audit fields."""
    report: Optional[Report] = None
    scheduled_report: Optional[ScheduledReport] = None


class ReportExecutionResponse(BaseModel):
    """Schema for API responses containing a report execution."""
    data: ReportExecution
    success: bool = True
    message: Optional[str] = None


class ReportExecutionListResponse(BaseModel):
    """Schema for API responses containing a list of report executions."""
    data: List[ReportExecution]
    total: int
    page: int
    page_size: int
    success: bool = True
    message: Optional[str] = None


# Filter Parameter schemas
class ReportFilterParams(BaseModel):
    """Schema for filtering reports in API requests."""
    analysis_result_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    is_template: Optional[bool] = None
    format: Optional[ReportFormat] = None
    
    def to_query_params(self) -> Dict:
        """Converts filter parameters to query parameters."""
        return {k: v for k, v in self.dict().items() if v is not None}


class ScheduledReportFilterParams(BaseModel):
    """Schema for filtering scheduled reports in API requests."""
    report_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    active: Optional[bool] = None
    frequency: Optional[ScheduleFrequency] = None
    
    def to_query_params(self) -> Dict:
        """Converts filter parameters to query parameters."""
        return {k: v for k, v in self.dict().items() if v is not None}


class ReportShareFilterParams(BaseModel):
    """Schema for filtering report shares in API requests."""
    report_id: Optional[uuid.UUID] = None
    owner_id: Optional[uuid.UUID] = None
    shared_with_id: Optional[uuid.UUID] = None
    can_edit: Optional[bool] = None
    can_run: Optional[bool] = None
    can_share: Optional[bool] = None
    is_valid: Optional[bool] = None
    
    def to_query_params(self) -> Dict:
        """Converts filter parameters to query parameters."""
        return {k: v for k, v in self.dict().items() if v is not None}


class ReportExecutionFilterParams(BaseModel):
    """Schema for filtering report executions in API requests."""
    report_id: Optional[uuid.UUID] = None
    scheduled_report_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    status: Optional[ReportStatus] = None
    
    def to_query_params(self) -> Dict:
        """Converts filter parameters to query parameters."""
        return {k: v for k, v in self.dict().items() if v is not None}