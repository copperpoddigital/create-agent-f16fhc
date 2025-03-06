"""
Controller module for the reports API of the Freight Price Movement Agent.
Implements business logic for creating, retrieving, updating, and deleting reports,
report templates, scheduled reports, and report shares. Handles report execution
and formatting of results.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple

import uuid
import sqlalchemy
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ...core.db import get_db, transaction
from ...core.exceptions import (
    ReportNotFoundException, ReportTemplateNotFoundException,
    ScheduledReportNotFoundException, ReportShareNotFoundException,
    ReportExecutionNotFoundException, PermissionDeniedException
)
from ...models.user import User
from ...models.analysis_result import AnalysisResult
from ...models.enums import ReportFormat, ReportStatus, ScheduleFrequency
from .schemas import (
    ReportCreate, ReportUpdate, Report as ReportSchema, ReportResponse, ReportListResponse,
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplate as ReportTemplateSchema,
    ReportTemplateResponse, ReportTemplateListResponse,
    ScheduledReportCreate, ScheduledReportUpdate, ScheduledReport as ScheduledReportSchema,
    ScheduledReportResponse, ScheduledReportListResponse,
    ReportShareCreate, ReportShareUpdate, ReportShare as ReportShareSchema,
    ReportShareResponse, ReportShareListResponse,
    ReportExecutionCreate, ReportExecution as ReportExecutionSchema,
    ReportExecutionResponse, ReportExecutionListResponse,
    ReportFilterParams, ScheduledReportFilterParams,
    ReportShareFilterParams, ReportExecutionFilterParams
)
from ...services.analysis_engine import AnalysisEngine
from ...services.presentation import PresentationService
from ...services.scheduler import SchedulerService, JobType, ScheduleType

# Initialize logger
logger = logging.getLogger(__name__)


def get_report(report_id: uuid.UUID, db: Session, current_user: User) -> ReportSchema:
    """Retrieves a report by ID"""
    logger.info(f"Retrieving report with ID: {report_id}")
    report = db.query(ReportSchema).get(report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{report_id}' not found")
    if not check_report_access(report, current_user, require_edit=False, require_run=False, require_share=False, db=db):
        raise PermissionDeniedException(f"User '{current_user.id}' does not have permission to view report '{report_id}'")
    return report


def get_reports(skip: int, limit: int, filters: ReportFilterParams, db: Session, current_user: User) -> ReportListResponse:
    """Retrieves a paginated list of reports"""
    logger.info(f"Retrieving reports with skip: {skip}, limit: {limit}, filters: {filters}")
    query = db.query(ReportSchema)
    query = query.filter(ReportSchema.created_by == current_user.id)
    total = query.count()
    reports = query.offset(skip).limit(limit).all()
    return ReportListResponse(data=reports, total=total, page=skip // limit + 1, page_size=limit)


@transaction
def create_report(report_data: ReportCreate, db: Session, current_user: User) -> ReportSchema:
    """Creates a new report"""
    logger.info(f"Creating a new report with data: {report_data}")
    analysis_result = db.query(AnalysisResult).get(report_data.analysis_result_id)
    if not analysis_result:
        raise ReportNotFoundException(f"Analysis Result with ID '{report_data.analysis_result_id}' not found")
    report = ReportSchema(**report_data.dict(), created_by=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@transaction
def update_report(report_id: uuid.UUID, report_data: ReportUpdate, db: Session, current_user: User) -> ReportSchema:
    """Updates an existing report"""
    logger.info(f"Updating report with ID: {report_id}, data: {report_data}")
    report = db.query(ReportSchema).get(report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{report_id}' not found")
    if not check_report_access(report, current_user, require_edit=True, require_run=False, require_share=False, db=db):
        raise PermissionDeniedException(f"User '{current_user.id}' does not have permission to update report '{report_id}'")
    for key, value in report_data.dict(exclude_unset=True).items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    return report


@transaction
def delete_report(report_id: uuid.UUID, db: Session, current_user: User) -> dict:
    """Deletes a report"""
    logger.info(f"Deleting report with ID: {report_id}")
    report = db.query(ReportSchema).get(report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{report_id}' not found")
    if not check_report_access(report, current_user, require_edit=True, require_run=False, require_share=False, db=db):
        raise PermissionDeniedException(f"User '{current_user.id}' does not have permission to delete report '{report_id}'")
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully"}


@transaction
def run_report(report_id: uuid.UUID, db: Session, current_user: User) -> ReportExecutionSchema:
    """Executes a report and generates results"""
    logger.info(f"Running report with ID: {report_id}")
    report = db.query(ReportSchema).get(report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{report_id}' not found")
    if not check_report_access(report, current_user, require_edit=False, require_run=True, require_share=False, db=db):
        raise PermissionDeniedException(f"User '{current_user.id}' does not have permission to run report '{report_id}'")
    report_execution = ReportExecutionSchema(report_id=report_id, execution_parameters={})
    db.add(report_execution)
    db.commit()
    db.refresh(report_execution)
    analysis_engine = AnalysisEngine()
    presentation_service = PresentationService(analysis_engine=analysis_engine)
    try:
        analysis_result = analysis_engine.analyze_price_movement(time_period_id=report.analysis_result_id, filters=report.filters, user_id=current_user.id, output_format=report.format)
        formatted_result = presentation_service.format_result(analysis_id=analysis_result[0].id, output_format=report.format, include_visualization=report.include_visualization)
        report_execution.completed_at = datetime.utcnow()
        report_execution.status = ReportStatus.COMPLETED
    except Exception as e:
        report_execution.status = ReportStatus.FAILED
        report_execution.error_message = str(e)
    db.commit()
    db.refresh(report_execution)
    return report_execution


@transaction
def duplicate_report(report_id: uuid.UUID, new_name: str, db: Session, current_user: User) -> ReportSchema:
    """Creates a duplicate of an existing report"""
    logger.info(f"Duplicating report with ID: {report_id}, new name: {new_name}")
    report = db.query(ReportSchema).get(report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{report_id}' not found")
    if not check_report_access(report, current_user, require_edit=False, require_run=False, require_share=False, db=db):
        raise PermissionDeniedException(f"User '{current_user.id}' does not have permission to view report '{report_id}'")
    new_report = ReportSchema(name=new_name, description=report.description, analysis_result_id=report.analysis_result_id, format=report.format, include_visualization=report.include_visualization, parameters=report.parameters, filters=report.filters, created_by=current_user.id)
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report


def get_report_template(template_id: uuid.UUID, db: Session, current_user: User) -> ReportTemplateSchema:
    """Retrieves a report template by ID"""
    logger.info(f"Retrieving report template with ID: {template_id}")
    template = db.query(ReportTemplateSchema).get(template_id)
    if not template:
        raise ReportTemplateNotFoundException(f"Report template with ID '{template_id}' not found")
    # TODO: Add permission check for report templates
    return template


def get_report_templates(skip: int, limit: int, include_public: bool, db: Session, current_user: User) -> ReportTemplateListResponse:
    """Retrieves a paginated list of report templates"""
    logger.info(f"Retrieving report templates with skip: {skip}, limit: {limit}, include_public: {include_public}")
    query = db.query(ReportTemplateSchema)
    query = query.filter(ReportTemplateSchema.created_by == current_user.id)
    if include_public:
        query = query.filter(ReportTemplateSchema.is_public == True)
    total = query.count()
    templates = query.offset(skip).limit(limit).all()
    return ReportTemplateListResponse(data=templates, total=total, page=skip // limit + 1, page_size=limit)


@transaction
def create_report_template(template_data: ReportTemplateCreate, db: Session, current_user: User) -> ReportTemplateSchema:
    """Creates a new report template"""
    logger.info(f"Creating a new report template with data: {template_data}")
    template = ReportTemplateSchema(**template_data.dict(), created_by=current_user.id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@transaction
def update_report_template(template_id: uuid.UUID, template_data: ReportTemplateUpdate, db: Session, current_user: User) -> ReportTemplateSchema:
    """Updates an existing report template"""
    logger.info(f"Updating report template with ID: {template_id}, data: {template_data}")
    template = db.query(ReportTemplateSchema).get(template_id)
    if not template:
        raise ReportTemplateNotFoundException(f"Report template with ID '{template_id}' not found")
    # TODO: Add permission check for report templates
    for key, value in template_data.dict(exclude_unset=True).items():
        setattr(template, key, value)
    db.commit()
    db.refresh(template)
    return template


@transaction
def delete_report_template(template_id: uuid.UUID, db: Session, current_user: User) -> dict:
    """Deletes a report template"""
    logger.info(f"Deleting report template with ID: {template_id}")
    template = db.query(ReportTemplateSchema).get(template_id)
    if not template:
        raise ReportTemplateNotFoundException(f"Report template with ID '{template_id}' not found")
    # TODO: Add permission check for report templates
    db.delete(template)
    db.commit()
    return {"message": "Report template deleted successfully"}


@transaction
def create_report_from_template(template_id: uuid.UUID, name: str, parameters_override: Optional[dict], filters_override: Optional[dict], db: Session, current_user: User) -> ReportSchema:
    """Creates a new report from a template"""
    logger.info(f"Creating a new report from template with ID: {template_id}, name: {name}")
    template = db.query(ReportTemplateSchema).get(template_id)
    if not template:
        raise ReportTemplateNotFoundException(f"Report template with ID '{template_id}' not found")
    # TODO: Add permission check for report templates
    report_data = template.dict()
    report_data.pop('id', None)
    report_data.pop('created_at', None)
    report_data.pop('updated_at', None)
    report_data.pop('created_by', None)
    report_data['name'] = name
    if parameters_override:
        report_data['default_parameters'].update(parameters_override)
    if filters_override:
        report_data['default_filters'].update(filters_override)
    report = ReportSchema(**report_data, created_by=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_scheduled_report(scheduled_report_id: uuid.UUID, db: Session, current_user: User) -> ScheduledReportSchema:
    """Retrieves a scheduled report by ID"""
    logger.info(f"Retrieving scheduled report with ID: {scheduled_report_id}")
    scheduled_report = db.query(ScheduledReportSchema).get(scheduled_report_id)
    if not scheduled_report:
        raise ScheduledReportNotFoundException(f"Scheduled report with ID '{scheduled_report_id}' not found")
    # TODO: Add permission check for scheduled reports
    return scheduled_report


def get_scheduled_reports(skip: int, limit: int, filters: ScheduledReportFilterParams, db: Session, current_user: User) -> ScheduledReportListResponse:
    """Retrieves a paginated list of scheduled reports"""
    logger.info(f"Retrieving scheduled reports with skip: {skip}, limit: {limit}, filters: {filters}")
    query = db.query(ScheduledReportSchema)
    query = query.filter(ScheduledReportSchema.created_by == current_user.id)
    total = query.count()
    scheduled_reports = query.offset(skip).limit(limit).all()
    return ScheduledReportListResponse(data=scheduled_reports, total=total, page=skip // limit + 1, page_size=limit)


@transaction
def create_scheduled_report(scheduled_report_data: ScheduledReportCreate, db: Session, current_user: User) -> ScheduledReportSchema:
    """Creates a new scheduled report"""
    logger.info(f"Creating a new scheduled report with data: {scheduled_report_data}")
    report = db.query(ReportSchema).get(scheduled_report_data.report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{scheduled_report_data.report_id}' not found")
    # TODO: Add permission check for scheduled reports
    scheduled_report = ScheduledReportSchema(**scheduled_report_data.dict(), created_by=current_user.id)
    db.add(scheduled_report)
    db.commit()
    db.refresh(scheduled_report)
    # TODO: Add scheduler job
    return scheduled_report


@transaction
def update_scheduled_report(scheduled_report_id: uuid.UUID, scheduled_report_data: ScheduledReportUpdate, db: Session, current_user: User) -> ScheduledReportSchema:
    """Updates an existing scheduled report"""
    logger.info(f"Updating scheduled report with ID: {scheduled_report_id}, data: {scheduled_report_data}")
    scheduled_report = db.query(ScheduledReportSchema).get(scheduled_report_id)
    if not scheduled_report:
        raise ScheduledReportNotFoundException(f"Scheduled report with ID '{scheduled_report_id}' not found")
    # TODO: Add permission check for scheduled reports
    for key, value in scheduled_report_data.dict(exclude_unset=True).items():
        setattr(scheduled_report, key, value)
    db.commit()
    db.refresh(scheduled_report)
    # TODO: Update scheduler job
    return scheduled_report


@transaction
def delete_scheduled_report(scheduled_report_id: uuid.UUID, db: Session, current_user: User) -> dict:
    """Deletes a scheduled report"""
    logger.info(f"Deleting scheduled report with ID: {scheduled_report_id}")
    scheduled_report = db.query(ScheduledReportSchema).get(scheduled_report_id)
    if not scheduled_report:
        raise ScheduledReportNotFoundException(f"Scheduled report with ID '{scheduled_report_id}' not found")
    # TODO: Add permission check for scheduled reports
    db.delete(scheduled_report)
    db.commit()
    # TODO: Remove scheduler job
    return {"message": "Scheduled report deleted successfully"}


def get_report_share(share_id: uuid.UUID, db: Session, current_user: User) -> ReportShareSchema:
    """Retrieves a report share by ID"""
    logger.info(f"Retrieving report share with ID: {share_id}")
    share = db.query(ReportShareSchema).get(share_id)
    if not share:
        raise ReportShareNotFoundException(f"Report share with ID '{share_id}' not found")
    # TODO: Add permission check for report shares
    return share


def get_report_shares(skip: int, limit: int, filters: ReportShareFilterParams, db: Session, current_user: User) -> ReportShareListResponse:
    """Retrieves a paginated list of report shares"""
    logger.info(f"Retrieving report shares with skip: {skip}, limit: {limit}, filters: {filters}")
    query = db.query(ReportShareSchema)
    query = query.filter(ReportShareSchema.owner_id == current_user.id)
    total = query.count()
    shares = query.offset(skip).limit(limit).all()
    return ReportShareListResponse(data=shares, total=total, page=skip // limit + 1, page_size=limit)


@transaction
def create_report_share(share_data: ReportShareCreate, db: Session, current_user: User) -> ReportShareSchema:
    """Creates a new report share"""
    logger.info(f"Creating a new report share with data: {share_data}")
    report = db.query(ReportSchema).get(share_data.report_id)
    if not report:
        raise ReportNotFoundException(f"Report with ID '{share_data.report_id}' not found")
    # TODO: Add permission check for report shares
    share = ReportShareSchema(**share_data.dict(), owner_id=current_user.id)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


@transaction
def update_report_share(share_id: uuid.UUID, share_data: ReportShareUpdate, db: Session, current_user: User) -> ReportShareSchema:
    """Updates an existing report share"""
    logger.info(f"Updating report share with ID: {share_id}, data: {share_data}")
    share = db.query(ReportShareSchema).get(share_id)
    if not share:
        raise ReportShareNotFoundException(f"Report share with ID '{share_id}' not found")
    # TODO: Add permission check for report shares
    for key, value in share_data.dict(exclude_unset=True).items():
        setattr(share, key, value)
    db.commit()
    db.refresh(share)
    return share


@transaction
def delete_report_share(share_id: uuid.UUID, db: Session, current_user: User) -> dict:
    """Deletes a report share"""
    logger.info(f"Deleting report share with ID: {share_id}")
    share = db.query(ReportShareSchema).get(share_id)
    if not share:
        raise ReportShareNotFoundException(f"Report share with ID '{share_id}' not found")
    # TODO: Add permission check for report shares
    db.delete(share)
    db.commit()
    return {"message": "Report share deleted successfully"}


def get_report_execution(execution_id: uuid.UUID, db: Session, current_user: User) -> ReportExecutionSchema:
    """Retrieves a report execution by ID"""
    logger.info(f"Retrieving report execution with ID: {execution_id}")
    execution = db.query(ReportExecutionSchema).get(execution_id)
    if not execution:
        raise ReportExecutionNotFoundException(f"Report execution with ID '{execution_id}' not found")
    # TODO: Add permission check for report executions
    return execution


def get_report_executions(skip: int, limit: int, filters: ReportExecutionFilterParams, db: Session, current_user: User) -> ReportExecutionListResponse:
    """Retrieves a paginated list of report executions"""
    logger.info(f"Retrieving report executions with skip: {skip}, limit: {limit}, filters: {filters}")
    query = db.query(ReportExecutionSchema)
    query = query.filter(ReportExecutionSchema.created_by == current_user.id)
    total = query.count()
    executions = query.offset(skip).limit(limit).all()
    return ReportExecutionListResponse(data=executions, total=total, page=skip // limit + 1, page_size=limit)


def check_report_access(report: ReportSchema, user: User, require_edit: bool, require_run: bool, require_share: bool, db: Session) -> bool:
    """Checks if a user has access to a report"""
    logger.debug(f"Checking access for user '{user.id}' to report '{report.id}'")
    if report.created_by == user.id:
        logger.debug(f"User '{user.id}' is the creator of report '{report.id}', granting access")
        return True
    # TODO: Implement report sharing access checks
    return False


def calculate_next_run_time(frequency: ScheduleFrequency, hour: int, minute: int, day_of_week: Optional[int], day_of_month: Optional[int]) -> datetime:
    """Calculates the next run time for a scheduled report"""
    logger.debug(f"Calculating next run time for frequency: {frequency}, hour: {hour}, minute: {minute}, day_of_week: {day_of_week}, day_of_month: {day_of_month}")
    # TODO: Implement next run time calculation
    return datetime.utcnow()


def create_scheduler_job(scheduled_report: ScheduledReportSchema, scheduler_service: SchedulerService) -> str:
    """Creates a scheduler job for a scheduled report"""
    logger.info(f"Creating scheduler job for scheduled report: {scheduled_report.id}")
    # TODO: Implement scheduler job creation
    return "job_id"