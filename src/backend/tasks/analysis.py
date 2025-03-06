"""
Celery task module for asynchronous freight price movement analysis operations.

This module implements background tasks for running freight price movement analyses,
handling retries, and managing result caching. It provides both synchronous and 
asynchronous functions for analysis operations that can be used throughout the application.
"""

import logging
from typing import Optional, Dict, Any, List

import celery
from celery.exceptions import Retry

from .worker import celery_app
from ..core.config import settings
from ..services.analysis_engine import (
    AnalysisEngine, 
    get_cached_analysis,
    cache_analysis_result
)
from ..core.exceptions import AnalysisException
from ..models.enums import AnalysisStatus, OutputFormat

# Set up logger
logger = logging.getLogger(__name__)

# Define task retry settings
RETRY_LIMIT = settings.TASK_RETRY_LIMIT
RETRY_DELAY = settings.TASK_RETRY_DELAY


def run_analysis(time_period_id: str, 
                filters: Optional[dict] = None, 
                user_id: Optional[str] = None,
                output_format: Optional[OutputFormat] = None,
                use_cache: Optional[bool] = True) -> dict:
    """
    Synchronously runs a freight price movement analysis.
    
    Args:
        time_period_id: ID of the time period to analyze
        filters: Optional filters to apply to the freight data
        user_id: Optional ID of the user requesting the analysis
        output_format: Optional format for the results
        use_cache: Whether to use cached results if available
        
    Returns:
        Analysis result with status and data
        
    Raises:
        AnalysisException: If the analysis fails
    """
    logger.info(f"Running price movement analysis for time period: {time_period_id}")
    
    try:
        # Create analysis engine instance
        engine = AnalysisEngine()
        
        # Execute analysis
        result, from_cache = engine.analyze_price_movement(
            time_period_id=time_period_id,
            filters=filters,
            user_id=user_id,
            output_format=output_format,
            use_cache=use_cache
        )
        
        # Convert to dictionary for return
        result_dict = result.to_dict(include_details=True)
        result_dict['from_cache'] = from_cache
        
        logger.info(f"Analysis completed for time period: {time_period_id}, cache_hit: {from_cache}")
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in run_analysis: {str(e)}", exc_info=True)
        if isinstance(e, AnalysisException):
            raise
        raise AnalysisException(f"Failed to run analysis: {str(e)}", original_exception=e)


def get_analysis(analysis_id: str, include_details: Optional[bool] = False) -> Optional[dict]:
    """
    Retrieves an existing analysis result by ID.
    
    Args:
        analysis_id: ID of the analysis result to retrieve
        include_details: Whether to include full results details
        
    Returns:
        Analysis result if found, None otherwise
    """
    logger.info(f"Retrieving analysis result: {analysis_id}")
    
    try:
        # Create analysis engine instance
        engine = AnalysisEngine()
        
        # Get analysis result
        result = engine.get_analysis_result(analysis_id=analysis_id)
        
        if not result:
            logger.info(f"Analysis result not found: {analysis_id}")
            return None
        
        # Convert to dictionary for return
        result_dict = result.to_dict(include_details=include_details)
        logger.info(f"Retrieved analysis result: {analysis_id}")
        
        return result_dict
        
    except Exception as e:
        logger.error(f"Error in get_analysis: {str(e)}", exc_info=True)
        if isinstance(e, AnalysisException):
            raise
        raise AnalysisException(f"Failed to retrieve analysis: {str(e)}", original_exception=e)


def compare_periods(base_period_id: str, 
                   comparison_period_id: str,
                   filters: Optional[dict] = None,
                   user_id: Optional[str] = None) -> dict:
    """
    Compares freight prices between two time periods.
    
    Args:
        base_period_id: ID of the base time period
        comparison_period_id: ID of the comparison time period
        filters: Optional filters to apply to the freight data
        user_id: Optional ID of the user requesting the comparison
        
    Returns:
        Comparison results between the two periods
        
    Raises:
        AnalysisException: If the comparison fails
    """
    logger.info(f"Comparing time periods: {base_period_id} and {comparison_period_id}")
    
    try:
        # Create analysis engine instance
        engine = AnalysisEngine()
        
        # Execute comparison
        comparison_results = engine.compare_time_periods(
            base_period_id=base_period_id,
            comparison_period_id=comparison_period_id,
            filters=filters,
            user_id=user_id
        )
        
        logger.info(f"Period comparison completed: {base_period_id} vs {comparison_period_id}")
        return comparison_results
        
    except Exception as e:
        logger.error(f"Error in compare_periods: {str(e)}", exc_info=True)
        if isinstance(e, AnalysisException):
            raise
        raise AnalysisException(f"Failed to compare time periods: {str(e)}", original_exception=e)


def run_analysis_batch(analysis_configs: list) -> list:
    """
    Runs multiple analyses in a single batch operation.
    
    Args:
        analysis_configs: List of dictionaries containing analysis parameters
        
    Returns:
        List of analysis results with status and data
        
    Raises:
        AnalysisException: If the batch operation fails
    """
    results = []
    success_count = 0
    failure_count = 0
    
    logger.info(f"Running batch analysis with {len(analysis_configs)} configurations")
    
    try:
        for config in analysis_configs:
            try:
                # Extract parameters from config
                time_period_id = config.get('time_period_id')
                filters = config.get('filters')
                user_id = config.get('user_id')
                output_format = config.get('output_format')
                use_cache = config.get('use_cache', True)
                
                if not time_period_id:
                    raise ValueError("Missing required parameter: time_period_id")
                
                # Run analysis
                result = run_analysis(
                    time_period_id=time_period_id,
                    filters=filters,
                    user_id=user_id,
                    output_format=output_format,
                    use_cache=use_cache
                )
                
                # Add to results
                results.append({
                    'config': config,
                    'result': result,
                    'status': 'success'
                })
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error in batch analysis item: {str(e)}", exc_info=True)
                
                # Add failed result to results
                results.append({
                    'config': config,
                    'error': str(e),
                    'status': 'failure'
                })
                
                failure_count += 1
        
        logger.info(f"Batch analysis completed: {success_count} successful, {failure_count} failed")
        return results
        
    except Exception as e:
        logger.error(f"Error in run_analysis_batch: {str(e)}", exc_info=True)
        if isinstance(e, AnalysisException):
            raise
        raise AnalysisException(f"Failed to run analysis batch: {str(e)}", original_exception=e)


@celery_app.task(bind=True, name='tasks.analysis.run_analysis_async', 
                max_retries=RETRY_LIMIT, default_retry_delay=RETRY_DELAY)
def run_analysis_async(self, time_period_id: str, 
                      filters: Optional[dict] = None, 
                      user_id: Optional[str] = None,
                      output_format: Optional[str] = None,
                      use_cache: Optional[bool] = True) -> dict:
    """
    Asynchronously runs a freight price movement analysis.
    
    Args:
        time_period_id: ID of the time period to analyze
        filters: Optional filters to apply to the freight data
        user_id: Optional ID of the user requesting the analysis
        output_format: Optional format for the results (string representation)
        use_cache: Whether to use cached results if available
        
    Returns:
        Analysis result with status and data
        
    Raises:
        Retry: If a retryable error occurs
    """
    logger.info(f"Starting async price movement analysis for time period: {time_period_id}")
    
    # Convert string representation of output_format to enum if provided
    output_format_enum = None
    if output_format:
        try:
            output_format_enum = OutputFormat[output_format]
        except (KeyError, ValueError):
            logger.warning(f"Invalid output format: {output_format}, using default")
    
    try:
        result = run_analysis(
            time_period_id=time_period_id,
            filters=filters,
            user_id=user_id,
            output_format=output_format_enum,
            use_cache=use_cache
        )
        logger.info(f"Async analysis completed for time period: {time_period_id}")
        return result
        
    except AnalysisException as e:
        logger.error(f"Analysis error in async task: {str(e)}")
        # Don't retry if it's a validation or data error
        if e.details and e.details.get('retryable', False):
            raise self.retry(exc=e, countdown=RETRY_DELAY)
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in async analysis task: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=RETRY_DELAY)


@celery_app.task(bind=True, name='tasks.analysis.get_analysis_async',
                max_retries=RETRY_LIMIT, default_retry_delay=RETRY_DELAY)
def get_analysis_async(self, analysis_id: str, include_details: Optional[bool] = False) -> Optional[dict]:
    """
    Asynchronously retrieves an existing analysis result by ID.
    
    Args:
        analysis_id: ID of the analysis result to retrieve
        include_details: Whether to include full results details
        
    Returns:
        Analysis result if found, None otherwise
    """
    logger.info(f"Starting async retrieval of analysis: {analysis_id}")
    
    try:
        result = get_analysis(analysis_id=analysis_id, include_details=include_details)
        logger.info(f"Async retrieval completed for analysis: {analysis_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_analysis_async: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=RETRY_DELAY)


@celery_app.task(bind=True, name='tasks.analysis.compare_periods_async',
                max_retries=RETRY_LIMIT, default_retry_delay=RETRY_DELAY)
def compare_periods_async(self, base_period_id: str, 
                         comparison_period_id: str,
                         filters: Optional[dict] = None,
                         user_id: Optional[str] = None) -> dict:
    """
    Asynchronously compares freight prices between two time periods.
    
    Args:
        base_period_id: ID of the base time period
        comparison_period_id: ID of the comparison time period
        filters: Optional filters to apply to the freight data
        user_id: Optional ID of the user requesting the comparison
        
    Returns:
        Comparison results between the two periods
    """
    logger.info(f"Starting async period comparison: {base_period_id} vs {comparison_period_id}")
    
    try:
        result = compare_periods(
            base_period_id=base_period_id,
            comparison_period_id=comparison_period_id,
            filters=filters,
            user_id=user_id
        )
        logger.info(f"Async period comparison completed: {base_period_id} vs {comparison_period_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in compare_periods_async: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=RETRY_DELAY)


@celery_app.task(bind=True, name='tasks.analysis.run_analysis_batch_async',
                max_retries=RETRY_LIMIT, default_retry_delay=RETRY_DELAY)
def run_analysis_batch_async(self, analysis_configs: list) -> list:
    """
    Asynchronously runs multiple analyses in a single batch operation.
    
    Args:
        analysis_configs: List of dictionaries containing analysis parameters
        
    Returns:
        List of analysis results with status and data
    """
    logger.info(f"Starting async batch analysis with {len(analysis_configs)} configurations")
    
    try:
        results = run_analysis_batch(analysis_configs=analysis_configs)
        logger.info(f"Async batch analysis completed: {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in run_analysis_batch_async: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=RETRY_DELAY)