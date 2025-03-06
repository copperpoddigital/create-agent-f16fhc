#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controller module for the analysis API of the Freight Price Movement Agent.
Implements business logic for managing time periods, analysis requests,
and executing price movement calculations.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import sqlalchemy
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ...core.db import get_db, transaction
from ...core.exceptions import AnalysisException, NotFoundException, AuthorizationException
from ...core.logging import logger
from ...models.time_period import TimePeriod
from ...models.analysis_result import AnalysisResult
from .models import AnalysisRequest, SavedAnalysis, AnalysisSchedule
from ...models.enums import AnalysisStatus, OutputFormat
from ...services.analysis_engine import AnalysisEngine
from ...services.presentation import PresentationService


# Function to retrieve a time period by ID
def get_time_period(db: Session, time_period_id: str) -> Optional[TimePeriod]:
    """
    Retrieves a time period by ID.

    Args:
        db (Session): Database session.
        time_period_id (str): ID of the time period to retrieve.

    Returns:
        Optional[TimePeriod]: Time period if found, None otherwise.
    """
    logger.info(f"Retrieving time period with ID: {time_period_id}")
    try:
        time_period = db.query(TimePeriod).get(time_period_id)
        if time_period:
            logger.debug(f"Time period found: {time_period.name}")
        else:
            logger.warning(f"Time period not found: {time_period_id}")
        return time_period
    except Exception as e:
        logger.error(f"Error retrieving time period: {e}", exc_info=True)
        raise


# Function to create a new time period
def create_time_period(db: Session, time_period_data: dict, user_id: str) -> TimePeriod:
    """
    Creates a new time period.

    Args:
        db (Session): Database session.
        time_period_data (dict): Data for the new time period.
        user_id (str): ID of the user creating the time period.

    Returns:
        TimePeriod: Newly created time period.
    """
    logger.info(f"Creating new time period for user: {user_id}")
    try:
        time_period = TimePeriod(**time_period_data, created_by=user_id)
        db.add(time_period)
        db.commit()
        db.refresh(time_period)
        logger.info(f"Time period created successfully: {time_period.name}")
        return time_period
    except Exception as e:
        logger.error(f"Error creating time period: {e}", exc_info=True)
        db.rollback()
        raise


# Function to list time periods with pagination and filtering
def list_time_periods(db: Session, skip: int, limit: int, filters: Dict) -> Tuple[List[TimePeriod], int]:
    """
    Lists time periods with pagination and filtering.

    Args:
        db (Session): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        filters (Dict): Filters to apply to the query.

    Returns:
        Tuple[List[TimePeriod], int]: List of time periods and total count.
    """
    logger.info(f"Listing time periods with skip: {skip}, limit: {limit}, filters: {filters}")
    try:
        query = db.query(TimePeriod)
        total = query.count()
        time_periods = query.offset(skip).limit(limit).all()
        logger.debug(f"Found {len(time_periods)} time periods")
        return time_periods, total
    except Exception as e:
        logger.error(f"Error listing time periods: {e}", exc_info=True)
        raise


# Function to update an existing time period
def update_time_period(db: Session, time_period_id: str, time_period_data: dict, user_id: str) -> TimePeriod:
    """
    Updates an existing time period.

    Args:
        db (Session): Database session.
        time_period_id (str): ID of the time period to update.
        time_period_data (dict): Data to update the time period with.
        user_id (str): ID of the user updating the time period.

    Returns:
        TimePeriod: Updated time period.
    """
    logger.info(f"Updating time period with ID: {time_period_id} for user: {user_id}")
    try:
        time_period = db.query(TimePeriod).get(time_period_id)
        if not time_period:
            raise NotFoundException(f"Time period not found: {time_period_id}")
        # Update time period attributes
        for key, value in time_period_data.items():
            setattr(time_period, key, value)
        db.commit()
        db.refresh(time_period)
        logger.info(f"Time period updated successfully: {time_period.name}")
        return time_period
    except Exception as e:
        logger.error(f"Error updating time period: {e}", exc_info=True)
        db.rollback()
        raise


# Function to delete a time period
def delete_time_period(db: Session, time_period_id: str, user_id: str) -> bool:
    """
    Deletes a time period.

    Args:
        db (Session): Database session.
        time_period_id (str): ID of the time period to delete.
        user_id (str): ID of the user deleting the time period.

    Returns:
        bool: True if deleted successfully.
    """
    logger.info(f"Deleting time period with ID: {time_period_id} for user: {user_id}")
    try:
        time_period = db.query(TimePeriod).get(time_period_id)
        if not time_period:
            raise NotFoundException(f"Time period not found: {time_period_id}")
        db.delete(time_period)
        db.commit()
        logger.info(f"Time period deleted successfully: {time_period_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting time period: {e}", exc_info=True)
        db.rollback()
        raise


# Function to create a new analysis request
def create_analysis_request(db: Session, analysis_request_data: dict, user_id: str) -> AnalysisRequest:
    """
    Creates a new analysis request.

    Args:
        db (Session): Database session.
        analysis_request_data (dict): Data for the new analysis request.
        user_id (str): ID of the user creating the analysis request.

    Returns:
        AnalysisRequest: Newly created analysis request.
    """
    logger.info(f"Creating new analysis request for user: {user_id}")
    try:
        analysis_request = AnalysisRequest(**analysis_request_data, user_id=user_id)
        db.add(analysis_request)
        db.commit()
        db.refresh(analysis_request)
        logger.info(f"Analysis request created successfully: {analysis_request.id}")
        return analysis_request
    except Exception as e:
        logger.error(f"Error creating analysis request: {e}", exc_info=True)
        db.rollback()
        raise


# Function to retrieve an analysis request by ID
def get_analysis_request(db: Session, analysis_id: str, user_id: str) -> Optional[AnalysisRequest]:
    """
    Retrieves an analysis request by ID.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis request to retrieve.
        user_id (str): ID of the user requesting the analysis.

    Returns:
        Optional[AnalysisRequest]: Analysis request if found, None otherwise.
    """
    logger.info(f"Retrieving analysis request with ID: {analysis_id} for user: {user_id}")
    try:
        analysis_request = db.query(AnalysisRequest).get(analysis_id)
        if analysis_request:
            logger.debug(f"Analysis request found: {analysis_request.id}")
        else:
            logger.warning(f"Analysis request not found: {analysis_id}")
        return analysis_request
    except Exception as e:
        logger.error(f"Error retrieving analysis request: {e}", exc_info=True)
        raise


# Function to list analysis requests with pagination and filtering
def list_analysis_requests(db: Session, skip: int, limit: int, filters: Dict) -> Tuple[List[AnalysisRequest], int]:
    """
    Lists analysis requests with pagination and filtering.

    Args:
        db (Session): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        filters (Dict): Filters to apply to the query.

    Returns:
        Tuple[List[AnalysisRequest], int]: List of analysis requests and total count.
    """
    logger.info(f"Listing analysis requests with skip: {skip}, limit: {limit}, filters: {filters}")
    try:
        query = db.query(AnalysisRequest)
        total = query.count()
        analysis_requests = query.offset(skip).limit(limit).all()
        logger.debug(f"Found {len(analysis_requests)} analysis requests")
        return analysis_requests, total
    except Exception as e:
        logger.error(f"Error listing analysis requests: {e}", exc_info=True)
        raise


# Function to delete an analysis request
def delete_analysis_request(db: Session, analysis_id: str, user_id: str) -> bool:
    """
    Deletes an analysis request.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis request to delete.
        user_id (str): ID of the user deleting the analysis request.

    Returns:
        bool: True if deleted successfully.
    """
    logger.info(f"Deleting analysis request with ID: {analysis_id} for user: {user_id}")
    try:
        analysis_request = db.query(AnalysisRequest).get(analysis_id)
        if not analysis_request:
            raise NotFoundException(f"Analysis request not found: {analysis_id}")
        db.delete(analysis_request)
        db.commit()
        logger.info(f"Analysis request deleted successfully: {analysis_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting analysis request: {e}", exc_info=True)
        db.rollback()
        raise


# Function to execute a price movement analysis
def execute_analysis(db: Session, analysis_id: str, user_id: str) -> Dict:
    """
    Executes a price movement analysis for the specified analysis request.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis request to execute.
        user_id (str): ID of the user executing the analysis.

    Returns:
        Dict: Analysis results.
    """
    logger.info(f"Executing analysis with ID: {analysis_id} for user: {user_id}")
    try:
        analysis_engine = AnalysisEngine()
        analysis_result, from_cache = analysis_engine.analyze_price_movement(analysis_id, user_id=user_id)
        return analysis_result.to_dict()
    except Exception as e:
        logger.error(f"Error executing analysis: {e}", exc_info=True)
        raise


# Function to retrieve the results of a completed analysis
def get_analysis_result(db: Session, analysis_id: str, user_id: str, format: Optional[str] = None) -> Union[Dict, bytes, str]:
    """
    Retrieves the results of a completed analysis.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis to retrieve results for.
        user_id (str): ID of the user requesting the results.
        format (Optional[str], optional): The format to return the results in. Defaults to None.

    Returns:
        Union[Dict, bytes, str]: Analysis results in the requested format.
    """
    logger.info(f"Retrieving analysis result with ID: {analysis_id} for user: {user_id}")
    try:
        presentation_service = PresentationService()
        formatted_result = presentation_service.format_result(analysis_id)
        return formatted_result
    except Exception as e:
        logger.error(f"Error retrieving analysis result: {e}", exc_info=True)
        raise


# Function to cancel an in-progress analysis
def cancel_analysis(db: Session, analysis_id: str, user_id: str) -> AnalysisRequest:
    """
    Cancels an in-progress analysis.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis to cancel.
        user_id (str): ID of the user requesting the cancellation.

    Returns:
        AnalysisRequest: Updated analysis request.
    """
    logger.info(f"Cancelling analysis with ID: {analysis_id} for user: {user_id}")
    try:
        analysis_request = db.query(AnalysisRequest).get(analysis_id)
        if not analysis_request:
            raise NotFoundException(f"Analysis request not found: {analysis_id}")
        analysis_request.status = AnalysisStatus.CANCELLED
        db.commit()
        db.refresh(analysis_request)
        logger.info(f"Analysis request cancelled successfully: {analysis_id}")
        return analysis_request
    except Exception as e:
        logger.error(f"Error cancelling analysis: {e}", exc_info=True)
        db.rollback()
        raise


# Function to re-execute a previously completed or failed analysis
def rerun_analysis(db: Session, analysis_id: str, user_id: str) -> AnalysisRequest:
    """
    Re-executes a previously completed or failed analysis.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis to re-run.
        user_id (str): ID of the user requesting the re-run.

    Returns:
        AnalysisRequest: Updated analysis request.
    """
    logger.info(f"Re-running analysis with ID: {analysis_id} for user: {user_id}")
    try:
        analysis_request = db.query(AnalysisRequest).get(analysis_id)
        if not analysis_request:
            raise NotFoundException(f"Analysis request not found: {analysis_id}")
        analysis_request.status = AnalysisStatus.PENDING
        db.commit()
        db.refresh(analysis_request)
        logger.info(f"Analysis request re-queued successfully: {analysis_id}")
        return analysis_request
    except Exception as e:
        logger.error(f"Error re-running analysis: {e}", exc_info=True)
        db.rollback()
        raise


# Function to check the current status of an analysis request
def check_analysis_status(db: Session, analysis_id: str, user_id: str) -> Dict:
    """
    Checks the current status of an analysis request.

    Args:
        db (Session): Database session.
        analysis_id (str): ID of the analysis to check.
        user_id (str): ID of the user requesting the status.

    Returns:
        Dict: Status information including current status and progress.
    """
    logger.info(f"Checking status of analysis with ID: {analysis_id} for user: {user_id}")
    try:
        analysis_request = db.query(AnalysisRequest).get(analysis_id)
        if not analysis_request:
            raise NotFoundException(f"Analysis request not found: {analysis_id}")
        status = {"status": analysis_request.status.value}
        logger.debug(f"Analysis status: {status}")
        return status
    except Exception as e:
        logger.error(f"Error checking analysis status: {e}", exc_info=True)
        raise


# Function to create a new saved analysis configuration
def create_saved_analysis(db: Session, saved_analysis_data: dict, user_id: str) -> SavedAnalysis:
    """
    Creates a new saved analysis configuration.

    Args:
        db (Session): Database session.
        saved_analysis_data (dict): Data for the new saved analysis.
        user_id (str): ID of the user creating the saved analysis.

    Returns:
        SavedAnalysis: Newly created saved analysis.
    """
    logger.info(f"Creating new saved analysis for user: {user_id}")
    try:
        saved_analysis = SavedAnalysis(**saved_analysis_data, user_id=user_id)
        db.add(saved_analysis)
        db.commit()
        db.refresh(saved_analysis)
        logger.info(f"Saved analysis created successfully: {saved_analysis.name}")
        return saved_analysis
    except Exception as e:
        logger.error(f"Error creating saved analysis: {e}", exc_info=True)
        db.rollback()
        raise


# Function to retrieve a saved analysis by ID
def get_saved_analysis(db: Session, saved_analysis_id: str, user_id: str) -> Optional[SavedAnalysis]:
    """
    Retrieves a saved analysis by ID.

    Args:
        db (Session): Database session.
        saved_analysis_id (str): ID of the saved analysis to retrieve.
        user_id (str): ID of the user requesting the saved analysis.

    Returns:
        Optional[SavedAnalysis]: Saved analysis if found, None otherwise.
    """
    logger.info(f"Retrieving saved analysis with ID: {saved_analysis_id} for user: {user_id}")
    try:
        saved_analysis = db.query(SavedAnalysis).get(saved_analysis_id)
        if saved_analysis:
            logger.debug(f"Saved analysis found: {saved_analysis.name}")
        else:
            logger.warning(f"Saved analysis not found: {saved_analysis_id}")
        return saved_analysis
    except Exception as e:
        logger.error(f"Error retrieving saved analysis: {e}", exc_info=True)
        raise


# Function to list saved analyses with pagination and filtering
def list_saved_analyses(db: Session, skip: int, limit: int, filters: Dict) -> Tuple[List[SavedAnalysis], int]:
    """
    Lists saved analyses with pagination and filtering.

    Args:
        db (Session): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        filters (Dict): Filters to apply to the query.

    Returns:
        Tuple[List[SavedAnalysis], int]: List of saved analyses and total count.
    """
    logger.info(f"Listing saved analyses with skip: {skip}, limit: {limit}, filters: {filters}")
    try:
        query = db.query(SavedAnalysis)
        total = query.count()
        saved_analyses = query.offset(skip).limit(limit).all()
        logger.debug(f"Found {len(saved_analyses)} saved analyses")
        return saved_analyses, total
    except Exception as e:
        logger.error(f"Error listing saved analyses: {e}", exc_info=True)
        raise


# Function to update an existing saved analysis
def update_saved_analysis(db: Session, saved_analysis_id: str, saved_analysis_data: dict, user_id: str) -> SavedAnalysis:
    """
    Updates an existing saved analysis.

    Args:
        db (Session): Database session.
        saved_analysis_id (str): ID of the saved analysis to update.
        saved_analysis_data (dict): Data to update the saved analysis with.
        user_id (str): ID of the user updating the saved analysis.

    Returns:
        SavedAnalysis: Updated saved analysis.
    """
    logger.info(f"Updating saved analysis with ID: {saved_analysis_id} for user: {user_id}")
    try:
        saved_analysis = db.query(SavedAnalysis).get(saved_analysis_id)
        if not saved_analysis:
            raise NotFoundException(f"Saved analysis not found: {saved_analysis_id}")
        # Update saved analysis attributes
        for key, value in saved_analysis_data.items():
            setattr(saved_analysis, key, value)
        db.commit()
        db.refresh(saved_analysis)
        logger.info(f"Saved analysis updated successfully: {saved_analysis.name}")
        return saved_analysis
    except Exception as e:
        logger.error(f"Error updating saved analysis: {e}", exc_info=True)
        db.rollback()
        raise


# Function to delete a saved analysis
def delete_saved_analysis(db: Session, saved_analysis_id: str, user_id: str) -> bool:
    """
    Deletes a saved analysis.

    Args:
        db (Session): Database session.
        saved_analysis_id (str): ID of the saved analysis to delete.
        user_id (str): ID of the user deleting the saved analysis.

    Returns:
        bool: True if deleted successfully.
    """
    logger.info(f"Deleting saved analysis with ID: {saved_analysis_id} for user: {user_id}")
    try:
        saved_analysis = db.query(SavedAnalysis).get(saved_analysis_id)
        if not saved_analysis:
            raise NotFoundException(f"Saved analysis not found: {saved_analysis_id}")
        db.delete(saved_analysis)
        db.commit()
        logger.info(f"Saved analysis deleted successfully: {saved_analysis_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting saved analysis: {e}", exc_info=True)
        db.rollback()
        raise


# Function to execute a price movement analysis using a saved analysis configuration
def run_saved_analysis(db: Session, saved_analysis_id: str, user_id: str) -> Tuple[AnalysisRequest, Dict]:
    """
    Executes a price movement analysis using a saved analysis configuration.

    Args:
        db (Session): Database session.
        saved_analysis_id (str): ID of the saved analysis to run.
        user_id (str): ID of the user executing the analysis.

    Returns:
        Tuple[AnalysisRequest, Dict]: Created analysis request and analysis results.
    """
    logger.info(f"Running saved analysis with ID: {saved_analysis_id} for user: {user_id}")
    try:
        saved_analysis = db.query(SavedAnalysis).get(saved_analysis_id)
        if not saved_analysis:
            raise NotFoundException(f"Saved analysis not found: {saved_analysis_id}")
        analysis_request = saved_analysis.to_analysis_request()
        db.add(analysis_request)
        db.commit()
        db.refresh(analysis_request)
        saved_analysis.update_last_run()
        db.commit()
        analysis_engine = AnalysisEngine()
        analysis_result = analysis_engine.analyze_price_movement(analysis_request.id, user_id=user_id)
        logger.info(f"Saved analysis executed successfully: {saved_analysis.name}")
        return analysis_request, analysis_result
    except Exception as e:
        logger.error(f"Error running saved analysis: {e}", exc_info=True)
        db.rollback()
        raise


# Function to create a new analysis schedule
def create_analysis_schedule(db: Session, schedule_data: dict, user_id: str) -> AnalysisSchedule:
    """
    Creates a new analysis schedule.

    Args:
        db (Session): Database session.
        schedule_data (dict): Data for the new analysis schedule.
        user_id (str): ID of the user creating the analysis schedule.

    Returns:
        AnalysisSchedule: Newly created analysis schedule.
    """
    logger.info(f"Creating new analysis schedule for user: {user_id}")
    try:
        analysis_schedule = AnalysisSchedule(**schedule_data, user_id=user_id)
        db.add(analysis_schedule)
        db.commit()
        db.refresh(analysis_schedule)
        logger.info(f"Analysis schedule created successfully: {analysis_schedule.name}")
        return analysis_schedule
    except Exception as e:
        logger.error(f"Error creating analysis schedule: {e}", exc_info=True)
        db.rollback()
        raise


# Function to retrieve an analysis schedule by ID
def get_analysis_schedule(db: Session, schedule_id: str, user_id: str) -> Optional[AnalysisSchedule]:
    """
    Retrieves an analysis schedule by ID.

    Args:
        db (Session): Database session.
        schedule_id (str): ID of the analysis schedule to retrieve.
        user_id (str): ID of the user requesting the analysis schedule.

    Returns:
        Optional[AnalysisSchedule]: Analysis schedule if found, None otherwise.
    """
    logger.info(f"Retrieving analysis schedule with ID: {schedule_id} for user: {user_id}")
    try:
        analysis_schedule = db.query(AnalysisSchedule).get(schedule_id)
        if analysis_schedule:
            logger.debug(f"Analysis schedule found: {analysis_schedule.name}")
        else:
            logger.warning(f"Analysis schedule not found: {schedule_id}")
        return analysis_schedule
    except Exception as e:
        logger.error(f"Error retrieving analysis schedule: {e}", exc_info=True)
        raise


# Function to list analysis schedules with pagination and filtering
def list_analysis_schedules(db: Session, skip: int, limit: int, filters: Dict) -> Tuple[List[AnalysisSchedule], int]:
    """
    Lists analysis schedules with pagination and filtering.

    Args:
        db (Session): Database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        filters (Dict): Filters to apply to the query.

    Returns:
        Tuple[List[AnalysisSchedule], int]: List of analysis schedules and total count.
    """
    logger.info(f"Listing analysis schedules with skip: {skip}, limit: {limit}, filters: {filters}")
    try:
        query = db.query(AnalysisSchedule)
        total = query.count()
        analysis_schedules = query.offset(skip).limit(limit).all()
        logger.debug(f"Found {len(analysis_schedules)} analysis schedules")
        return analysis_schedules, total
    except Exception as e:
        logger.error(f"Error listing analysis schedules: {e}", exc_info=True)
        raise


# Function to update an existing analysis schedule
def update_analysis_schedule(db: Session, schedule_id: str, schedule_data: dict, user_id: str) -> AnalysisSchedule:
    """
    Updates an existing analysis schedule.

    Args:
        db (Session): Database session.
        schedule_id (str): ID of the analysis schedule to update.
        schedule_data (dict): Data to update the analysis schedule with.
        user_id (str): ID of the user updating the analysis schedule.

    Returns:
        AnalysisSchedule: Updated analysis schedule.
    """
    logger.info(f"Updating analysis schedule with ID: {schedule_id} for user: {user_id}")
    try:
        analysis_schedule = db.query(AnalysisSchedule).get(schedule_id)
        if not analysis_schedule:
            raise NotFoundException(f"Analysis schedule not found: {schedule_id}")
        # Update analysis schedule attributes
        for key, value in schedule_data.items():
            setattr(analysis_schedule, key, value)
        db.commit()
        db.refresh(analysis_schedule)
        logger.info(f"Analysis schedule updated successfully: {analysis_schedule.name}")
        return analysis_schedule
    except Exception as e:
        logger.error(f"Error updating analysis schedule: {e}", exc_info=True)
        db.rollback()
        raise


# Function to delete an analysis schedule
def delete_analysis_schedule(db: Session, schedule_id: str, user_id: str) -> bool:
    """
    Deletes an analysis schedule.

    Args:
        db (Session): Database session.
        schedule_id (str): ID of the analysis schedule to delete.
        user_id (str): ID of the user deleting the analysis schedule.

    Returns:
        bool: True if deleted successfully.
    """
    logger.info(f"Deleting analysis schedule with ID: {schedule_id} for user: {user_id}")
    try:
        analysis_schedule = db.query(AnalysisSchedule).get(schedule_id)
        if not analysis_schedule:
            raise NotFoundException(f"Analysis schedule not found: {schedule_id}")
        db.delete(analysis_schedule)
        db.commit()
        logger.info(f"Analysis schedule deleted successfully: {schedule_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting analysis schedule: {e}", exc_info=True)
        db.rollback()
        raise


# Function to activate an analysis schedule
def activate_analysis_schedule(db: Session, schedule_id: str, user_id: str) -> AnalysisSchedule:
    """
    Activates an analysis schedule.

    Args:
        db (Session): Database session.
        schedule_id (str): ID of the analysis schedule to activate.
        user_id (str): ID of the user activating the analysis schedule.

    Returns:
        AnalysisSchedule: Updated analysis schedule.
    """
    logger.info(f"Activating analysis schedule with ID: {schedule_id} for user: {user_id}")
    try:
        analysis_schedule = db.query(AnalysisSchedule).get(schedule_id)
        if not analysis_schedule:
            raise NotFoundException(f"Analysis schedule not found: {schedule_id}")
        analysis_schedule.is_active = True
        db.commit()
        db.refresh(analysis_schedule)
        logger.info(f"Analysis schedule activated successfully: {analysis_schedule.name}")
        return analysis_schedule
    except Exception as e:
        logger.error(f"Error activating analysis schedule: {e}", exc_info=True)
        db.rollback()
        raise


# Function to deactivate an analysis schedule
def deactivate_analysis_schedule(db: Session, schedule_id: str, user_id: str) -> AnalysisSchedule:
    """
    Deactivates an analysis schedule.

    Args:
        db (Session): Database session.
        schedule_id (str): ID of the analysis schedule to deactivate.
        user_id (str): ID of the user deactivating the analysis schedule.

    Returns:
        AnalysisSchedule: Updated analysis schedule.
    """
    logger.info(f"Deactivating analysis schedule with ID: {schedule_id} for user: {user_id}")
    try:
        analysis_schedule = db.query(AnalysisSchedule).get(schedule_id)
        if not analysis_schedule:
            raise NotFoundException(f"Analysis schedule not found: {schedule_id}")
        analysis_schedule.is_active = False
        db.commit()
        db.refresh(analysis_schedule)
        logger.info(f"Analysis schedule deactivated successfully: {analysis_schedule.name}")
        return analysis_schedule
    except Exception as e:
        logger.error(f"Error deactivating analysis schedule: {e}", exc_info=True)
        db.rollback()
        raise


# Function to process all due analysis schedules
def process_due_schedules(db: Session) -> List[Dict]:
    """
    Processes all due analysis schedules.

    Args:
        db (Session): Database session.

    Returns:
        List[Dict]: List of execution results.
    """
    logger.info("Processing due analysis schedules")
    results = []
    try:
        # Query for active analysis schedules where next_run_at is in the past
        now = datetime.utcnow()
        due_schedules = db.query(AnalysisSchedule).filter(
            AnalysisSchedule.is_active == True,
            AnalysisSchedule.next_run_at <= now
        ).all()

        for schedule in due_schedules:
            try:
                # Execute the associated saved analysis
                saved_analysis = schedule.saved_analysis
                if not saved_analysis:
                    logger.error(f"Saved analysis not found for schedule: {schedule.id}")
                    results.append({"schedule_id": schedule.id, "status": "FAILED", "error": "Saved analysis not found"})
                    continue

                analysis_request, analysis_result = run_saved_analysis(db, schedule.saved_analysis_id, schedule.user_id)

                # Update the last_run_at and next_run_at for the schedule
                schedule.update_last_run()
                db.commit()

                results.append({"schedule_id": schedule.id, "status": "COMPLETED", "analysis_id": analysis_request.id})

            except Exception as e:
                logger.error(f"Error processing schedule {schedule.id}: {e}", exc_info=True)
                results.append({"schedule_id": schedule.id, "status": "FAILED", "error": str(e)})

        logger.info(f"Processed {len(due_schedules)} analysis schedules")
        return results

    except Exception as e:
        logger.error(f"Error processing due schedules: {e}", exc_info=True)
        db.rollback()
        raise