#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defines FastAPI routes for the analysis module of the Freight Price Movement Agent.
This file implements RESTful API endpoints for time period management, analysis requests,
saved analyses, and analysis schedules.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, Response

from ...core.db import get_db
from ...core.exceptions import AnalysisException
from ...core.logging import logger  # Logging for API operations
from ...models.enums import OutputFormat  # Enum for output format options
from ...schemas.time_period import TimePeriodCreate  # Schema for time period creation
from ..auth.controllers import get_current_user  # Authentication dependency to get current user
from . import controllers
from .schemas import (
    AnalysisListResponse,  # Schema for analysis list response
    AnalysisRequestCreate,  # Schema for analysis request creation
    AnalysisRequestResponse,  # Schema for analysis request response
    AnalysisScheduleCreate,  # Schema for analysis schedule creation
    AnalysisScheduleListResponse,  # Schema for analysis schedule list response
    AnalysisScheduleResponse,  # Schema for analysis schedule response
    PriceMovementResult,  # Schema for price movement analysis results
    SavedAnalysisCreate,  # Schema for saved analysis creation
    SavedAnalysisListResponse,  # Schema for saved analysis list response
    SavedAnalysisResponse,  # Schema for saved analysis response
    )

# Create an APIRouter instance with a prefix and tags
router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/time-periods", response_model=PriceMovementResult, status_code=status.HTTP_201_CREATED)
async def create_time_period_handler(time_period_data: TimePeriodCreate, db: Depends(get_db), current_user: Depends(get_current_user)):
    """Creates a new time period for analysis."""
    try:
        return controllers.create_time_period(db, time_period_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error creating time period: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/time-periods/{time_period_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def get_time_period_handler(time_period_id: str = Path(..., title="The ID of the time period to get"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Retrieves a time period by ID."""
    try:
        time_period = controllers.get_time_period(db, time_period_id)
        if not time_period:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Time period not found")
        return time_period
    except Exception as e:
        logger.error(f"Error getting time period: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/time-periods", response_model=List[PriceMovementResult], status_code=status.HTTP_200_OK)
async def list_time_periods_handler(skip: int = Query(0, description="Number of records to skip"), limit: int = Query(10, description="Maximum number of records to return"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Lists time periods with pagination and filtering."""
    try:
        time_periods, total = controllers.list_time_periods(db, skip, limit, {})
        return time_periods
    except Exception as e:
        logger.error(f"Error listing time periods: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/time-periods/{time_period_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def update_time_period_handler(time_period_id: str = Path(..., title="The ID of the time period to update"), time_period_data: TimePeriodCreate = Body(..., description="Data to update the time period with"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Updates an existing time period."""
    try:
        return controllers.update_time_period(db, time_period_id, time_period_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error updating time period: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/time-periods/{time_period_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_time_period_handler(time_period_id: str = Path(..., title="The ID of the time period to delete"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Deletes a time period."""
    try:
        if controllers.delete_time_period(db, time_period_id, current_user.id):
            return {"message": "Time period deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete time period")
    except Exception as e:
        logger.error(f"Error deleting time period: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests", response_model=PriceMovementResult, status_code=status.HTTP_201_CREATED)
async def create_analysis_request_handler(analysis_request_data: AnalysisRequestCreate, db: Depends(get_db), current_user: Depends(get_current_user)):
    """Creates a new analysis request."""
    try:
        return controllers.create_analysis_request(db, analysis_request_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error creating analysis request: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests/{analysis_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def get_analysis_request_handler(analysis_id: str = Path(..., title="The ID of the analysis request to get"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Retrieves an analysis request by ID."""
    try:
        analysis_request = controllers.get_analysis_request(db, analysis_id, current_user.id)
        if not analysis_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis request not found")
        return analysis_request
    except Exception as e:
        logger.error(f"Error getting analysis request: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests", response_model=List[PriceMovementResult], status_code=status.HTTP_200_OK)
async def list_analysis_requests_handler(skip: int = Query(0, description="Number of records to skip"), limit: int = Query(10, description="Maximum number of records to return"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Lists analysis requests with pagination and filtering."""
    try:
        analysis_requests, total = controllers.list_analysis_requests(db, skip, limit, {})
        return analysis_requests
    except Exception as e:
        logger.error(f"Error listing analysis requests: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/requests/{analysis_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_analysis_request_handler(analysis_id: str = Path(..., title="The ID of the analysis request to delete"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Deletes an analysis request."""
    try:
        if controllers.delete_analysis_request(db, analysis_id, current_user.id):
            return {"message": "Analysis request deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete analysis request")
    except Exception as e:
        logger.error(f"Error deleting analysis request: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests/{analysis_id}/execute", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def execute_analysis_handler(analysis_id: str = Path(..., title="The ID of the analysis request to execute"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Executes a price movement analysis for the specified analysis request."""
    try:
        return controllers.execute_analysis(db, analysis_id, current_user.id)
    except Exception as e:
        logger.error(f"Error executing analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests/{analysis_id}/results", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def get_analysis_result_handler(analysis_id: str = Path(..., title="The ID of the analysis to retrieve results for"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Retrieves the results of a completed analysis."""
    try:
        return controllers.get_analysis_result(db, analysis_id)
    except Exception as e:
        logger.error(f"Error getting analysis result: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests/{analysis_id}/cancel", response_model=dict, status_code=status.HTTP_200_OK)
async def cancel_analysis_handler(analysis_id: str = Path(..., title="The ID of the analysis to cancel"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Cancels an in-progress analysis."""
    try:
        analysis_request = controllers.cancel_analysis(db, analysis_id, current_user.id)
        return {"message": f"Analysis request {analysis_request.id} cancelled successfully"}
    except Exception as e:
        logger.error(f"Error cancelling analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/requests/{analysis_id}/rerun", response_model=dict, status_code=status.HTTP_200_OK)
async def rerun_analysis_handler(analysis_id: str = Path(..., title="The ID of the analysis to re-run"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Re-executes a previously completed or failed analysis."""
    try:
        analysis_request = controllers.rerun_analysis(db, analysis_id, current_user.id)
        return {"message": f"Analysis request {analysis_request.id} re-queued successfully"}
    except Exception as e:
        logger.error(f"Error re-running analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/requests/{analysis_id}/status", response_model=dict, status_code=status.HTTP_200_OK)
async def check_analysis_status_handler(analysis_id: str = Path(..., title="The ID of the analysis to check"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Checks the current status of an analysis request."""
    try:
        return controllers.check_analysis_status(db, analysis_id, current_user.id)
    except Exception as e:
        logger.error(f"Error checking analysis status: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/saved", response_model=PriceMovementResult, status_code=status.HTTP_201_CREATED)
async def create_saved_analysis_handler(saved_analysis_data: SavedAnalysisCreate, db: Depends(get_db), current_user: Depends(get_current_user)):
    """Creates a new saved analysis configuration."""
    try:
        return controllers.create_saved_analysis(db, saved_analysis_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error creating saved analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/saved/{saved_analysis_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def get_saved_analysis_handler(saved_analysis_id: str = Path(..., title="The ID of the saved analysis to get"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Retrieves a saved analysis by ID."""
    try:
        saved_analysis = controllers.get_saved_analysis(db, saved_analysis_id, current_user.id)
        if not saved_analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved analysis not found")
        return saved_analysis
    except Exception as e:
        logger.error(f"Error getting saved analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/saved", response_model=List[PriceMovementResult], status_code=status.HTTP_200_OK)
async def list_saved_analyses_handler(skip: int = Query(0, description="Number of records to skip"), limit: int = Query(10, description="Maximum number of records to return"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Lists saved analyses with pagination and filtering."""
    try:
        saved_analyses, total = controllers.list_saved_analyses(db, skip, limit, {})
        return saved_analyses
    except Exception as e:
        logger.error(f"Error listing saved analyses: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/saved/{saved_analysis_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def update_saved_analysis_handler(saved_analysis_id: str = Path(..., title="The ID of the saved analysis to update"), saved_analysis_data: SavedAnalysisCreate = Body(..., description="Data to update the saved analysis with"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Updates an existing saved analysis."""
    try:
        return controllers.update_saved_analysis(db, saved_analysis_id, saved_analysis_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error updating saved analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/saved/{saved_analysis_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_saved_analysis_handler(saved_analysis_id: str = Path(..., title="The ID of the saved analysis to delete"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Deletes a saved analysis."""
    try:
        if controllers.delete_saved_analysis(db, saved_analysis_id, current_user.id):
            return {"message": "Saved analysis deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete saved analysis")
    except Exception as e:
        logger.error(f"Error deleting saved analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/saved/{saved_analysis_id}/run", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def run_saved_analysis_handler(saved_analysis_id: str = Path(..., title="The ID of the saved analysis to run"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Executes a price movement analysis using a saved analysis configuration."""
    try:
        analysis_request, analysis_result = controllers.run_saved_analysis(db, saved_analysis_id, current_user.id)
        return analysis_result
    except Exception as e:
        logger.error(f"Error running saved analysis: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/schedules", response_model=PriceMovementResult, status_code=status.HTTP_201_CREATED)
async def create_analysis_schedule_handler(schedule_data: AnalysisScheduleCreate, db: Depends(get_db), current_user: Depends(get_current_user)):
    """Creates a new analysis schedule."""
    try:
        return controllers.create_analysis_schedule(db, schedule_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error creating analysis schedule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/schedules/{schedule_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def get_analysis_schedule_handler(schedule_id: str = Path(..., title="The ID of the analysis schedule to get"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Retrieves an analysis schedule by ID."""
    try:
        analysis_schedule = controllers.get_analysis_schedule(db, schedule_id, current_user.id)
        if not analysis_schedule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis schedule not found")
        return analysis_schedule
    except Exception as e:
        logger.error(f"Error getting analysis schedule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/schedules", response_model=List[PriceMovementResult], status_code=status.HTTP_200_OK)
async def list_analysis_schedules_handler(skip: int = Query(0, description="Number of records to skip"), limit: int = Query(10, description="Maximum number of records to return"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Lists analysis schedules with pagination and filtering."""
    try:
        analysis_schedules, total = controllers.list_analysis_schedules(db, skip, limit, {})
        return analysis_schedules
    except Exception as e:
        logger.error(f"Error listing analysis schedules: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/schedules/{schedule_id}", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def update_analysis_schedule_handler(schedule_id: str = Path(..., title="The ID of the analysis schedule to update"), schedule_data: AnalysisScheduleCreate = Body(..., description="Data to update the analysis schedule with"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Updates an existing analysis schedule."""
    try:
        return controllers.update_analysis_schedule(db, schedule_id, schedule_data.dict(), current_user.id)
    except Exception as e:
        logger.error(f"Error updating analysis schedule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/schedules/{schedule_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_analysis_schedule_handler(schedule_id: str = Path(..., title="The ID of the analysis schedule to delete"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Deletes an analysis schedule."""
    try:
        if controllers.delete_analysis_schedule(db, schedule_id, current_user.id):
            return {"message": "Analysis schedule deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete analysis schedule")
    except Exception as e:
        logger.error(f"Error deleting analysis schedule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/schedules/{schedule_id}/activate", response_model=PriceMovementResult, status_code=status.HTTP_200_OK)
async def activate_analysis_schedule_handler(schedule_id: str = Path(..., title="The ID of the analysis schedule to activate"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Activates an analysis schedule."""
    try:
        return controllers.activate_analysis_schedule(db, schedule_id, current_user.id)
    except Exception as e:
        logger.error(f"Error activating analysis schedule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/schedules/{schedule_id}/deactivate", response_model=dict, status_code=status.HTTP_200_OK)
async def deactivate_analysis_schedule_handler(schedule_id: str = Path(..., title="The ID of the analysis schedule to deactivate"), db: Depends(get_db), current_user: Depends(get_current_user)):
    """Deactivates an analysis schedule."""
    try:
        analysis_schedule = controllers.deactivate_analysis_schedule(db, schedule_id, current_user.id)
        return {"message": f"Analysis schedule {analysis_schedule.name} deactivated successfully"}
    except Exception as e:
        logger.error(f"Error deactivating analysis schedule: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def register_time_period_routes():
    """Registers all time period related routes with the router"""
    # Register POST /time-periods endpoint for time period creation
    # Register GET /time-periods/{time_period_id} endpoint to retrieve a time period
    # Register GET /time-periods endpoint to list time periods
    # Register PUT /time-periods/{time_period_id} endpoint to update a time period
    # Register DELETE /time-periods/{time_period_id} endpoint to delete a time period
    pass


def register_analysis_request_routes():
    """Registers all analysis request related routes with the router"""
    # Register POST /requests endpoint for analysis request creation
    # Register GET /requests/{analysis_id} endpoint to retrieve an analysis request
    # Register GET /requests endpoint to list analysis requests
    # Register DELETE /requests/{analysis_id} endpoint to delete an analysis request
    # Register POST /requests/{analysis_id}/execute endpoint to execute an analysis
    # Register GET /requests/{analysis_id}/results endpoint to retrieve analysis results
    # Register POST /requests/{analysis_id}/cancel endpoint to cancel an analysis
    # Register POST /requests/{analysis_id}/rerun endpoint to rerun an analysis
    # Register GET /requests/{analysis_id}/status endpoint to check analysis status
    pass


def register_saved_analysis_routes():
    """Registers all saved analysis related routes with the router"""
    # Register POST /saved endpoint for saved analysis creation
    # Register GET /saved/{saved_analysis_id} endpoint to retrieve a saved analysis
    # Register GET /saved endpoint to list saved analyses
    # Register PUT /saved/{saved_analysis_id} endpoint to update a saved analysis
    # Register DELETE /saved/{saved_analysis_id} endpoint to delete a saved analysis
    # Register POST /saved/{saved_analysis_id}/run endpoint to run a saved analysis
    pass


def register_schedule_routes():
    """Registers all analysis schedule related routes with the router"""
    # Register POST /schedules endpoint for analysis schedule creation
    # Register GET /schedules/{schedule_id} endpoint to retrieve an analysis schedule
    # Register GET /schedules endpoint to list analysis schedules
    # Register PUT /schedules/{schedule_id} endpoint to update an analysis schedule
    # Register DELETE /schedules/{schedule_id} endpoint to delete an analysis schedule
    # Register POST /schedules/{schedule_id}/activate endpoint to activate an analysis schedule
    # Register POST /schedules/{schedule_id}/deactivate endpoint to deactivate an analysis schedule
    pass