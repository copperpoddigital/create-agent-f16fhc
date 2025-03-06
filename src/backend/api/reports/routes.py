from typing import Optional, Dict, List, Union, Tuple

import uuid
import sqlalchemy
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, Response, File, UploadFile

from ...core.db import get_db
from ...core.exceptions import (
    ReportNotFoundException, ReportTemplateNotFoundException,
    ScheduledReportNotFoundException, ReportShareNotFoundException,
    ReportExecutionNotFoundException, PermissionDeniedException
)
from ...models.user import User
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
from .controllers import (
    get_report, get_reports, create_report, update_report, delete_report, run_report, duplicate_report,
    get_report_template, get_report_templates, create_report_template, update_report_template, delete_report_template, create_report_from_template,
    get_scheduled_report, get_scheduled_reports, create_scheduled_report, update_scheduled_report, delete_scheduled_report,
    get_report_share, get_report_shares, create_report_share, update_report_share, delete_report_share,
    get_report_execution, get_report_executions
)
from ..auth.controllers import get_current_user
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Define the reports router
router = APIRouter(prefix='/reports', tags=['reports'])

@router.get('/{report_id}', response_model=ReportResponse)
def get_report_endpoint(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a report by ID"""
    try:
        report = get_report(report_id, db, current_user)
        return ReportResponse(data=report)
    except ReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/', response_model=ReportListResponse)
def get_reports_endpoint(
    skip: int = Query(0, description="Skip n items"),
    limit: int = Query(10, description="Limit results to n items"),
    filters: ReportFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a paginated list of reports"""
    reports, total = get_reports(skip, limit, filters, db, current_user)
    return ReportListResponse(data=reports, total=total, page=skip // limit + 1, page_size=limit)

@router.post('/', response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report_endpoint(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to create a new report"""
    try:
        report = create_report(report_data, db, current_user)
        return ReportResponse(data=report)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put('/{report_id}', response_model=ReportResponse)
def update_report_endpoint(
    report_id: uuid.UUID,
    report_data: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to update an existing report"""
    try:
        report = update_report(report_id, report_data, db, current_user)
        return ReportResponse(data=report)
    except ReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/{report_id}', status_code=status.HTTP_200_OK)
def delete_report_endpoint(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to delete a report"""
    try:
        return delete_report(report_id, db, current_user)
    except ReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post('/{report_id}/run', response_model=ReportExecutionResponse)
def run_report_endpoint(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to execute a report and generate results"""
    try:
        report_execution = run_report(report_id, db, current_user)
        return ReportExecutionResponse(data=report_execution)
    except ReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post('/{report_id}/duplicate', response_model=ReportResponse)
def duplicate_report_endpoint(
    report_id: uuid.UUID,
    new_name: str = Body(..., description="New name for the duplicated report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to create a duplicate of an existing report"""
    try:
        report = duplicate_report(report_id, new_name, db, current_user)
        return ReportResponse(data=report)
    except ReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get('/templates/{template_id}', response_model=ReportTemplateResponse)
def get_report_template_endpoint(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a report template by ID"""
    try:
        report_template = get_report_template(template_id, db, current_user)
        return ReportTemplateResponse(data=report_template)
    except ReportTemplateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/templates', response_model=ReportTemplateListResponse)
def get_report_templates_endpoint(
    skip: int = Query(0, description="Skip n items"),
    limit: int = Query(10, description="Limit results to n items"),
    include_public: bool = Query(False, description="Include public templates"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a paginated list of report templates"""
    report_templates, total = get_report_templates(skip, limit, include_public, db, current_user)
    return ReportTemplateListResponse(data=report_templates, total=total, page=skip // limit + 1, page_size=limit)

@router.post('/templates', response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_report_template_endpoint(
    template_data: ReportTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to create a new report template"""
    try:
        report_template = create_report_template(template_data, db, current_user)
        return ReportTemplateResponse(data=report_template)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put('/templates/{template_id}', response_model=ReportTemplateResponse)
def update_report_template_endpoint(
    template_id: uuid.UUID,
    template_data: ReportTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to update an existing report template"""
    try:
        report_template = update_report_template(template_id, template_data, db, current_user)
        return ReportTemplateResponse(data=report_template)
    except ReportTemplateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/templates/{template_id}', status_code=status.HTTP_200_OK)
def delete_report_template_endpoint(
    template_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to delete a report template"""
    try:
        return delete_report_template(template_id, db, current_user)
    except ReportTemplateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post('/templates/{template_id}/create-report', response_model=ReportResponse)
def create_report_from_template_endpoint(
    template_id: uuid.UUID,
    name: str = Body(..., description="Name for the new report"),
    parameters_override: Optional[Dict] = Body(None, description="Override parameters from the template"),
    filters_override: Optional[Dict] = Body(None, description="Override filters from the template"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to create a new report from a template"""
    try:
        report = create_report_from_template(template_id, name, parameters_override, filters_override, db, current_user)
        return ReportResponse(data=report)
    except ReportTemplateNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get('/scheduled/{scheduled_report_id}', response_model=ScheduledReportResponse)
def get_scheduled_report_endpoint(
    scheduled_report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a scheduled report by ID"""
    try:
        scheduled_report = get_scheduled_report(scheduled_report_id, db, current_user)
        return ScheduledReportResponse(data=scheduled_report)
    except ScheduledReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/scheduled', response_model=ScheduledReportListResponse)
def get_scheduled_reports_endpoint(
    skip: int = Query(0, description="Skip n items"),
    limit: int = Query(10, description="Limit results to n items"),
    filters: ScheduledReportFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a paginated list of scheduled reports"""
    scheduled_reports, total = get_scheduled_reports(skip, limit, filters, db, current_user)
    return ScheduledReportListResponse(data=scheduled_reports, total=total, page=skip // limit + 1, page_size=limit)

@router.post('/scheduled', response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_report_endpoint(
    scheduled_report_data: ScheduledReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to create a new scheduled report"""
    try:
        scheduled_report = create_scheduled_report(scheduled_report_data, db, current_user)
        return ScheduledReportResponse(data=scheduled_report)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put('/scheduled/{scheduled_report_id}', response_model=ScheduledReportResponse)
def update_scheduled_report_endpoint(
    scheduled_report_id: uuid.UUID,
    scheduled_report_data: ScheduledReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to update an existing scheduled report"""
    try:
        scheduled_report = update_scheduled_report(scheduled_report_id, scheduled_report_data, db, current_user)
        return ScheduledReportResponse(data=scheduled_report)
    except ScheduledReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/scheduled/{scheduled_report_id}', status_code=status.HTTP_200_OK)
def delete_scheduled_report_endpoint(
    scheduled_report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to delete a scheduled report"""
    try:
        return delete_scheduled_report(scheduled_report_id, db, current_user)
    except ScheduledReportNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/shares/{share_id}', response_model=ReportShareResponse)
def get_report_share_endpoint(
    share_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a report share by ID"""
    try:
        report_share = get_report_share(share_id, db, current_user)
        return ReportShareResponse(data=report_share)
    except ReportShareNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/shares', response_model=ReportShareListResponse)
def get_report_shares_endpoint(
    skip: int = Query(0, description="Skip n items"),
    limit: int = Query(10, description="Limit results to n items"),
    filters: ReportShareFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a paginated list of report shares"""
    report_shares, total = get_report_shares(skip, limit, filters, db, current_user)
    return ReportShareListResponse(data=report_shares, total=total, page=skip // limit + 1, page_size=limit)

@router.post('/shares', response_model=ReportShareResponse, status_code=status.HTTP_201_CREATED)
def create_report_share_endpoint(
    share_data: ReportShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to create a new report share"""
    try:
        report_share = create_report_share(share_data, db, current_user)
        return ReportShareResponse(data=report_share)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put('/shares/{share_id}', response_model=ReportShareResponse)
def update_report_share_endpoint(
    share_id: uuid.UUID,
    share_data: ReportShareUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to update an existing report share"""
    try:
        report_share = update_report_share(share_id, share_data, db, current_user)
        return ReportShareResponse(data=report_share)
    except ReportShareNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete('/shares/{share_id}', status_code=status.HTTP_200_OK)
def delete_report_share_endpoint(
    share_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to delete a report share"""
    try:
        return delete_report_share(share_id, db, current_user)
    except ReportShareNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/executions/{execution_id}', response_model=ReportExecutionResponse)
def get_report_execution_endpoint(
    execution_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a report execution by ID"""
    try:
        report_execution = get_report_execution(execution_id, db, current_user)
        return ReportExecutionResponse(data=report_execution)
    except ReportExecutionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get('/executions', response_model=ReportExecutionListResponse)
def get_report_executions_endpoint(
    skip: int = Query(0, description="Skip n items"),
    limit: int = Query(10, description="Limit results to n items"),
    filters: ReportExecutionFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to retrieve a paginated list of report executions"""
    report_executions, total = get_report_executions(skip, limit, filters, db, current_user)
    return ReportExecutionListResponse(data=report_executions, total=total, page=skip // limit + 1, page_size=limit)

@router.get('/executions/{execution_id}/download')
def download_report_execution_endpoint(
    execution_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to download the result of a report execution"""
    try:
        report_execution = get_report_execution(execution_id, db, current_user)

        if report_execution.status != ReportStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report execution has not completed successfully."
            )

        if not report_execution.output_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Output file not found for this report execution."
            )

        # Retrieve the output file from storage (e.g., S3)
        file_path = report_execution.output_location
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Output file not found on the server."
            )

        # Determine the content type based on the report format
        content_type = "application/json"  # Default to JSON
        if report_execution.report.format == ReportFormat.CSV:
            content_type = "text/csv"
        elif report_execution.report.format == ReportFormat.TEXT:
            content_type = "text/plain"

        # Return the file as a downloadable response
        return Response(
            content=file_content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment;filename={report_execution.report.name}.{report_execution.report.format.lower()}"},
        )

    except ReportExecutionNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"Error downloading report execution result: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report execution result: {e}"
        )