"""
Analysis Engine module for the Freight Price Movement Agent.

This module provides the core analysis engine service that calculates price movements
across user-defined time periods. It processes freight data, performs calculations for
absolute and percentage changes, determines trend directions, and manages caching of
analysis results.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any, Union

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from ..core.db import session_scope
from ..core.exceptions import AnalysisException
from ..core.cache import cache_manager, cached
from ..models.freight_data import FreightData
from ..models.time_period import TimePeriod
from ..models.analysis_result import AnalysisResult
from ..models.enums import TrendDirection, AnalysisStatus, OutputFormat
from ..utils.calculation import calculate_absolute_change, calculate_percentage_change, determine_trend_direction

# Initialize logger
logger = logging.getLogger(__name__)

# Default cache TTL for analysis results (in minutes)
CACHE_TTL_MINUTES = 60  # Default cache TTL for analysis results


def get_cached_analysis(analysis_id: str) -> Optional[dict]:
    """
    Retrieves a cached analysis result if available.
    
    Args:
        analysis_id: Unique identifier for the analysis
    
    Returns:
        Cached analysis result or None if not found
    """
    logger.debug(f"Attempting to retrieve cached analysis: {analysis_id}")
    cached_result = cache_manager.get_result_cache(analysis_id)
    
    if cached_result:
        logger.info(f"Cache hit for analysis: {analysis_id}")
        return cached_result
    
    logger.debug(f"Cache miss for analysis: {analysis_id}")
    return None


def cache_analysis_result(analysis_id: str, result: dict, ttl_minutes: Optional[int] = None) -> bool:
    """
    Caches an analysis result for future retrieval.
    
    Args:
        analysis_id: Unique identifier for the analysis
        result: Analysis result data to cache
        ttl_minutes: Time-to-live in minutes (defaults to CACHE_TTL_MINUTES)
    
    Returns:
        True if caching was successful, False otherwise
    """
    cache_ttl = ttl_minutes or CACHE_TTL_MINUTES
    logger.debug(f"Caching analysis result: {analysis_id} with TTL {cache_ttl} minutes")
    
    success = cache_manager.set_result_cache(analysis_id, result)
    
    if success:
        logger.info(f"Successfully cached analysis result: {analysis_id}")
    else:
        logger.warning(f"Failed to cache analysis result: {analysis_id}")
    
    return success


def aggregate_freight_data(freight_data: List[FreightData], 
                         start_date: datetime, 
                         end_date: datetime) -> Dict[str, Any]:
    """
    Aggregates freight data for a specific time period.
    
    Args:
        freight_data: List of freight data records
        start_date: Start date of the period
        end_date: End date of the period
    
    Returns:
        Aggregated freight data statistics
    """
    # Filter data for the specified period
    period_data = [data for data in freight_data 
                 if start_date <= data.record_date <= end_date]
    
    if not period_data:
        logger.warning(f"No freight data found for period {start_date} to {end_date}")
        return {
            "count": 0,
            "average": None,
            "minimum": None,
            "maximum": None,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
    
    # Convert to pandas DataFrame for easier aggregation
    df = pd.DataFrame([{
        "record_date": data.record_date,
        "freight_charge": float(data.freight_charge),
        "currency_code": data.currency_code,
    } for data in period_data])
    
    # Calculate aggregates
    stats = {
        "count": len(period_data),
        "average": float(df["freight_charge"].mean()),
        "minimum": float(df["freight_charge"].min()),
        "maximum": float(df["freight_charge"].max()),
        "std_dev": float(df["freight_charge"].std()) if len(period_data) > 1 else 0,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat()
    }
    
    logger.debug(f"Aggregated {stats['count']} freight records for period {start_date} to {end_date}")
    return stats


def calculate_time_series(freight_data: List[FreightData], 
                        periods: List[Tuple[datetime, datetime]]) -> List[Dict[str, Any]]:
    """
    Calculates a time series of freight charges over a period.
    
    Args:
        freight_data: List of freight data records
        periods: List of period start and end date tuples
    
    Returns:
        Time series data with freight charges for each period
    """
    time_series = []
    
    for period_start, period_end in periods:
        # Aggregate data for this period
        period_stats = aggregate_freight_data(freight_data, period_start, period_end)
        
        # Create period entry
        period_entry = {
            "start_date": period_start.isoformat(),
            "end_date": period_end.isoformat(),
            "average_freight_charge": period_stats["average"],
            "min_freight_charge": period_stats["minimum"],
            "max_freight_charge": period_stats["maximum"],
            "count": period_stats["count"]
        }
        
        time_series.append(period_entry)
    
    logger.debug(f"Generated time series with {len(time_series)} periods")
    return time_series


class AnalysisEngine:
    """
    Core service for performing freight price movement analysis.
    
    This class provides methods for analyzing price movements over specified time periods,
    calculating absolute and percentage changes, determining trend directions, and managing
    analysis results.
    """
    
    def __init__(self):
        """
        Initializes the AnalysisEngine.
        """
        self.logger = logger
        self.logger.info("AnalysisEngine initialized")
    
    def analyze_price_movement(self, time_period_id: str, 
                              filters: Optional[dict] = None,
                              user_id: Optional[str] = None,
                              output_format: Optional[OutputFormat] = None,
                              use_cache: Optional[bool] = True) -> Tuple[AnalysisResult, bool]:
        """
        Analyzes freight price movements for a specified time period.
        
        Args:
            time_period_id: ID of the time period to analyze
            filters: Optional filters to apply to the freight data
            user_id: Optional ID of the user requesting the analysis
            output_format: Optional format for the results
            use_cache: Whether to use cached results if available
        
        Returns:
            Tuple of (AnalysisResult, was_cached)
            
        Raises:
            AnalysisException: If analysis fails
        """
        filters = filters or {}
        self.logger.info(f"Starting price movement analysis for time period: {time_period_id}")
        
        try:
            # Create a new AnalysisResult object
            with session_scope() as session:
                analysis_result = AnalysisResult(
                    time_period_id=time_period_id,
                    parameters=filters,
                    created_by=user_id,
                    output_format=output_format or OutputFormat.JSON
                )
                session.add(analysis_result)
                session.flush()  # Generate ID without committing
                analysis_id = analysis_result.id
                
                # Check cache if enabled
                from_cache = False
                if use_cache:
                    cached_result = get_cached_analysis(analysis_id)
                    if cached_result:
                        self.logger.info(f"Using cached analysis result: {analysis_id}")
                        analysis_result.set_results(
                            results=cached_result.get("results", {}),
                            start_value=cached_result.get("start_value"),
                            end_value=cached_result.get("end_value"),
                            absolute_change=cached_result.get("absolute_change"),
                            percentage_change=cached_result.get("percentage_change"),
                            trend_direction=TrendDirection[cached_result.get("trend_direction")]
                            if "trend_direction" in cached_result else None
                        )
                        analysis_result.set_cache_expiry()
                        analysis_result.update_status(AnalysisStatus.COMPLETED)
                        from_cache = True
                        return analysis_result, from_cache
                
                # Update status to PROCESSING
                analysis_result.update_status(AnalysisStatus.PROCESSING)
                
                # Get time period
                time_period = session.query(TimePeriod).get(time_period_id)
                if not time_period:
                    raise AnalysisException(f"Time period not found: {time_period_id}")
                
                # Validate time period
                if not time_period.validate_dates():
                    raise AnalysisException(f"Invalid time period: Start date must be before end date")
                
                # Extract filter parameters from filters dict
                origin_ids = filters.get("origin_ids")
                destination_ids = filters.get("destination_ids")
                carrier_ids = filters.get("carrier_ids")
                transport_modes = filters.get("transport_modes")
                
                # Get freight data for the time period and filters
                freight_data = FreightData.get_for_analysis(
                    session,
                    start_date=time_period.start_date,
                    end_date=time_period.end_date,
                    origin_ids=origin_ids,
                    destination_ids=destination_ids,
                    carrier_ids=carrier_ids,
                    transport_modes=transport_modes
                )
                
                # Calculate price movements
                results = self.calculate_price_movement(freight_data, time_period, filters)
                
                # Update AnalysisResult with calculated results
                analysis_result.set_results(
                    results=results,
                    start_value=results.get("start_value"),
                    end_value=results.get("end_value"),
                    absolute_change=results.get("absolute_change"),
                    percentage_change=results.get("percentage_change"),
                    trend_direction=TrendDirection[results.get("trend_direction")]
                    if "trend_direction" in results else None
                )
                
                # Cache the result if not from cache
                if not from_cache:
                    cache_analysis_result(analysis_id, results)
                    
                return analysis_result, from_cache
                
        except Exception as e:
            self.logger.error(f"Error in price movement analysis: {str(e)}", exc_info=True)
            if 'analysis_result' in locals() and 'session' in locals():
                analysis_result.update_status(AnalysisStatus.FAILED, str(e))
                
            if isinstance(e, AnalysisException):
                raise
            raise AnalysisException(f"Failed to analyze price movement: {str(e)}", original_exception=e)
    
    def calculate_price_movement(self, freight_data: List[FreightData], 
                               time_period: TimePeriod,
                               parameters: Optional[dict] = None) -> Dict[str, Any]:
        """
        Calculates price movements from freight data.
        
        Args:
            freight_data: List of freight data records
            time_period: Time period definition
            parameters: Optional additional parameters
        
        Returns:
            Dictionary containing calculated price movement results
            
        Raises:
            AnalysisException: If calculation fails
        """
        self.logger.info(f"Calculating price movements for time period: {time_period.id}")
        
        try:
            # Validate freight data
            if not freight_data:
                raise AnalysisException("No freight data available for analysis")
            
            # Get time periods based on granularity
            periods = time_period.get_periods()
            
            # Calculate time series data
            time_series = calculate_time_series(freight_data, periods)
            
            if not time_series:
                raise AnalysisException("Failed to generate time series data")
            
            # Filter out periods with no data
            valid_time_series = [period for period in time_series if period["average_freight_charge"] is not None]
            
            if not valid_time_series:
                raise AnalysisException("No valid data points in time series")
            
            # Determine start and end values for the entire period
            start_period = valid_time_series[0]
            end_period = valid_time_series[-1]
            
            start_value = Decimal(str(start_period["average_freight_charge"]))
            end_value = Decimal(str(end_period["average_freight_charge"]))
            
            # Calculate absolute change
            absolute_change = calculate_absolute_change(start_value, end_value)
            
            # Calculate percentage change
            percentage_change = calculate_percentage_change(start_value, end_value)
            
            # Determine trend direction
            trend_direction = determine_trend_direction(percentage_change)
            
            # Calculate aggregate statistics for the entire period
            overall_stats = aggregate_freight_data(
                freight_data, 
                time_period.start_date,
                time_period.end_date
            )
            
            # Compile results
            results = {
                "time_period": {
                    "id": time_period.id,
                    "name": time_period.name,
                    "start_date": time_period.start_date.isoformat(),
                    "end_date": time_period.end_date.isoformat(),
                    "granularity": time_period.granularity.name,
                },
                "start_value": float(start_value),
                "end_value": float(end_value),
                "absolute_change": float(absolute_change),
                "percentage_change": float(percentage_change),
                "trend_direction": trend_direction.name,
                "statistics": overall_stats,
                "time_series": time_series,
                "parameters": parameters or {},
                "data_points": len(freight_data),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Successfully calculated price movements: {trend_direction.name} ({percentage_change}%)")
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating price movements: {str(e)}", exc_info=True)
            if isinstance(e, AnalysisException):
                raise
            raise AnalysisException(f"Failed to calculate price movements: {str(e)}", original_exception=e)
    
    def get_analysis_result(self, analysis_id: str, 
                          include_details: Optional[bool] = False) -> Optional[AnalysisResult]:
        """
        Retrieves an existing analysis result by ID.
        
        Args:
            analysis_id: ID of the analysis result to retrieve
            include_details: Whether to include full results details
        
        Returns:
            AnalysisResult if found, None otherwise
        """
        self.logger.debug(f"Retrieving analysis result: {analysis_id}")
        
        try:
            with session_scope() as session:
                analysis_result = session.query(AnalysisResult).get(analysis_id)
                
                if not analysis_result:
                    self.logger.info(f"Analysis result not found: {analysis_id}")
                    return None
                
                self.logger.debug(f"Retrieved analysis result: {analysis_id}, status: {analysis_result.status.name if analysis_result.status else 'None'}")
                return analysis_result
                
        except Exception as e:
            self.logger.error(f"Error retrieving analysis result: {str(e)}", exc_info=True)
            raise AnalysisException(f"Failed to retrieve analysis result: {str(e)}", original_exception=e)
    
    def list_analysis_results(self, user_id: Optional[str] = None, 
                            limit: Optional[int] = None,
                            offset: Optional[int] = None) -> List[AnalysisResult]:
        """
        Lists analysis results with optional filtering.
        
        Args:
            user_id: Optional user ID to filter results by
            limit: Optional maximum number of results to return
            offset: Optional offset for pagination
        
        Returns:
            List of AnalysisResult objects
        """
        self.logger.debug(f"Listing analysis results for user: {user_id or 'any'}")
        
        try:
            with session_scope() as session:
                query = session.query(AnalysisResult)
                
                # Filter by user ID if provided
                if user_id:
                    query = query.filter(AnalysisResult.created_by == user_id)
                
                # Apply pagination if provided
                if limit is not None:
                    query = query.limit(limit)
                
                if offset is not None:
                    query = query.offset(offset)
                
                # Order by created_at descending (newest first)
                query = query.order_by(AnalysisResult.created_at.desc())
                
                results = query.all()
                self.logger.debug(f"Found {len(results)} analysis results")
                return results
                
        except Exception as e:
            self.logger.error(f"Error listing analysis results: {str(e)}", exc_info=True)
            raise AnalysisException(f"Failed to list analysis results: {str(e)}", original_exception=e)
    
    def delete_analysis_result(self, analysis_id: str, 
                             user_id: Optional[str] = None) -> bool:
        """
        Deletes an analysis result by ID.
        
        Args:
            analysis_id: ID of the analysis result to delete
            user_id: Optional user ID for permission check
        
        Returns:
            True if deletion was successful, False otherwise
        """
        self.logger.info(f"Deleting analysis result: {analysis_id}")
        
        try:
            with session_scope() as session:
                analysis_result = session.query(AnalysisResult).get(analysis_id)
                
                if not analysis_result:
                    self.logger.warning(f"Analysis result not found: {analysis_id}")
                    return False
                
                # Check if user has permission to delete
                if user_id and analysis_result.created_by != user_id:
                    self.logger.warning(f"User {user_id} does not have permission to delete analysis {analysis_id}")
                    return False
                
                # Delete the analysis result
                session.delete(analysis_result)
                
                # Invalidate cache
                self.invalidate_cache(analysis_id)
                
                self.logger.info(f"Successfully deleted analysis result: {analysis_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting analysis result: {str(e)}", exc_info=True)
            raise AnalysisException(f"Failed to delete analysis result: {str(e)}", original_exception=e)
    
    def rerun_analysis(self, analysis_id: str, 
                      use_cache: Optional[bool] = False) -> Optional[AnalysisResult]:
        """
        Re-runs an existing analysis with the same parameters.
        
        Args:
            analysis_id: ID of the analysis to re-run
            use_cache: Whether to use cached results if available
        
        Returns:
            Updated analysis result if successful, None otherwise
        """
        self.logger.info(f"Re-running analysis: {analysis_id}")
        
        try:
            # Retrieve existing analysis result
            existing_result = self.get_analysis_result(analysis_id)
            
            if not existing_result:
                self.logger.warning(f"Analysis result not found: {analysis_id}")
                return None
            
            # Extract parameters from existing result
            time_period_id = existing_result.time_period_id
            filters = existing_result.parameters or {}
            user_id = existing_result.created_by
            output_format = existing_result.output_format
            
            # Invalidate cache for this analysis
            if not use_cache:
                self.invalidate_cache(analysis_id)
            
            # Run a new analysis with the same parameters
            updated_result, _ = self.analyze_price_movement(
                time_period_id=time_period_id,
                filters=filters,
                user_id=user_id,
                output_format=output_format,
                use_cache=use_cache
            )
            
            self.logger.info(f"Successfully re-ran analysis: {analysis_id}")
            return updated_result
            
        except Exception as e:
            self.logger.error(f"Error re-running analysis: {str(e)}", exc_info=True)
            raise AnalysisException(f"Failed to re-run analysis: {str(e)}", original_exception=e)
    
    def compare_time_periods(self, base_period_id: str, 
                           comparison_period_id: str,
                           filters: Optional[dict] = None,
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compares freight prices between two time periods.
        
        Args:
            base_period_id: ID of the base time period
            comparison_period_id: ID of the comparison time period
            filters: Optional filters to apply to the freight data
            user_id: Optional ID of the user requesting the comparison
        
        Returns:
            Dictionary containing comparison results
        """
        self.logger.info(f"Comparing time periods: {base_period_id} and {comparison_period_id}")
        
        try:
            # Analyze both time periods
            base_result, _ = self.analyze_price_movement(base_period_id, filters, user_id)
            comparison_result, _ = self.analyze_price_movement(comparison_period_id, filters, user_id)
            
            # Extract key metrics from both analyses
            base_data = base_result.to_dict(include_details=True)
            comparison_data = comparison_result.to_dict(include_details=True)
            
            # Calculate differences between periods
            base_value = Decimal(str(base_data.get("end_value", 0)))
            comparison_value = Decimal(str(comparison_data.get("end_value", 0)))
            
            absolute_difference = calculate_absolute_change(base_value, comparison_value)
            percentage_difference = calculate_percentage_change(base_value, comparison_value)
            difference_trend = determine_trend_direction(percentage_difference)
            
            # Compile comparison results
            comparison_results = {
                "base_period": {
                    "id": base_period_id,
                    "name": base_data.get("time_period", {}).get("name", "Base Period"),
                    "start_date": base_data.get("time_period", {}).get("start_date"),
                    "end_date": base_data.get("time_period", {}).get("end_date"),
                    "value": float(base_value),
                },
                "comparison_period": {
                    "id": comparison_period_id,
                    "name": comparison_data.get("time_period", {}).get("name", "Comparison Period"),
                    "start_date": comparison_data.get("time_period", {}).get("start_date"),
                    "end_date": comparison_data.get("time_period", {}).get("end_date"),
                    "value": float(comparison_value),
                },
                "difference": {
                    "absolute": float(absolute_difference),
                    "percentage": float(percentage_difference),
                    "trend_direction": difference_trend.name,
                },
                "base_analysis_id": base_result.id,
                "comparison_analysis_id": comparison_result.id,
                "parameters": filters or {},
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Successfully compared time periods: {difference_trend.name} ({percentage_difference}%)")
            return comparison_results
            
        except Exception as e:
            self.logger.error(f"Error comparing time periods: {str(e)}", exc_info=True)
            raise AnalysisException(f"Failed to compare time periods: {str(e)}", original_exception=e)
    
    def invalidate_cache(self, analysis_id: Optional[str] = None) -> int:
        """
        Invalidates cached analysis results.
        
        Args:
            analysis_id: Optional specific analysis ID to invalidate
        
        Returns:
            Number of invalidated cache entries
        """
        if analysis_id:
            self.logger.info(f"Invalidating cache for analysis: {analysis_id}")
            cache_manager.delete("result", analysis_id)
            return 1
        else:
            self.logger.info("Invalidating all analysis result caches")
            return cache_manager.invalidate_result_cache()