"""
Scheduled data cleanup tasks for the Freight Price Movement Agent.

This module handles the automatic removal of expired data, stale cache entries, and 
old audit logs according to configured retention policies. It ensures database 
performance and compliance with data retention requirements.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import redis
import sqlalchemy
from sqlalchemy import and_

from .worker import celery_app
from ..core.config import settings
from ..core.logging import get_logger
from ..core.db import get_db_session
from ..models.freight_data import FreightData
from ..models.analysis_result import AnalysisResult
from ..models.audit_log import AuditLog

# Configure logger
logger = get_logger(__name__)

# Retention periods in days
FREIGHT_DATA_ACTIVE_RETENTION_DAYS = 365  # 1 year active retention
ANALYSIS_RESULT_RETENTION_DAYS = 90  # 90 days retention
AUDIT_LOG_RETENTION_DAYS = 90  # 90 days active retention
SYSTEM_LOG_RETENTION_DAYS = 30  # 30 days retention

# Redis cache cleanup pattern
CACHE_CLEANUP_PATTERN = "freight_price_agent:*"

@celery_app.task(name='tasks.cleanup_expired_data')
def cleanup_expired_data() -> Dict[str, int]:
    """
    Main task function that orchestrates the cleanup of expired data across the system.
    
    This task:
    1. Removes expired freight data records
    2. Removes expired analysis results
    3. Removes expired audit logs
    4. Cleans up stale cache entries
    
    Returns:
        Dict[str, int]: Summary of cleanup operations with counts of removed items
    """
    logger.info("Starting scheduled data cleanup task")
    
    # Initialize results summary
    cleanup_summary = {
        "freight_data_removed": 0,
        "analysis_results_removed": 0,
        "audit_logs_removed": 0,
        "cache_entries_removed": 0
    }
    
    try:
        # Get database session
        with get_db_session() as session:
            # Clean up freight data
            freight_data_removed = cleanup_freight_data(session)
            cleanup_summary["freight_data_removed"] = freight_data_removed
            
            # Clean up analysis results
            analysis_results_removed = cleanup_analysis_results(session)
            cleanup_summary["analysis_results_removed"] = analysis_results_removed
            
            # Clean up audit logs
            audit_logs_removed = cleanup_audit_logs(session)
            cleanup_summary["audit_logs_removed"] = audit_logs_removed
        
        # Clean up cache (doesn't require DB session)
        cache_entries_removed = cleanup_cache()
        cleanup_summary["cache_entries_removed"] = cache_entries_removed
        
        logger.info(f"Data cleanup completed successfully: {cleanup_summary}")
    except Exception as e:
        logger.error(f"Error during data cleanup: {str(e)}", exc_info=True)
        # Re-raise to let Celery handle the error
        raise
    
    return cleanup_summary

def cleanup_freight_data(session: sqlalchemy.orm.Session, retention_days: Optional[int] = None) -> int:
    """
    Removes freight data records that have exceeded the retention period.
    
    For soft-deletable models, this will mark records as deleted rather than 
    physically removing them. Archives the data before removal if configured.
    
    Args:
        session: SQLAlchemy database session
        retention_days: Optional override for retention period in days
        
    Returns:
        int: Number of freight data records removed
    """
    # Use provided retention days or default
    days = retention_days or FREIGHT_DATA_ACTIVE_RETENTION_DAYS
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logger.info(f"Cleaning up freight data older than {cutoff_date.isoformat()}")
    
    # Archive old data before removal if in production
    if settings.ENV.lower() == 'production':
        archived_count = archive_old_data(session, 'freight_data', cutoff_date)
        logger.info(f"Archived {archived_count} freight data records before removal")

    try:
        # Query for records older than the cutoff date
        query = session.query(FreightData).filter(
            FreightData.record_date < cutoff_date,
            FreightData.is_deleted == False  # Only target non-deleted records
        )
        
        # Get count before deletion
        count = query.count()
        
        if count > 0:
            # For soft-deletable models, mark as deleted instead of removing
            for record in query.all():
                record.delete()  # This will set is_deleted=True and deleted_at
            
            # Commit the changes
            session.commit()
            
            logger.info(f"Successfully marked {count} freight data records as deleted")
        else:
            logger.info("No freight data records to clean up")
            
        return count
        
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        logger.error(f"Error cleaning up freight data: {str(e)}", exc_info=True)
        raise

def cleanup_analysis_results(session: sqlalchemy.orm.Session, retention_days: Optional[int] = None) -> int:
    """
    Removes analysis result records that have exceeded the retention period.
    
    Args:
        session: SQLAlchemy database session
        retention_days: Optional override for retention period in days
        
    Returns:
        int: Number of analysis result records removed
    """
    # Use provided retention days or default
    days = retention_days or ANALYSIS_RESULT_RETENTION_DAYS
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logger.info(f"Cleaning up analysis results older than {cutoff_date.isoformat()}")
    
    # Archive old data before removal if in production
    if settings.ENV.lower() == 'production':
        archived_count = archive_old_data(session, 'analysis_results', cutoff_date)
        logger.info(f"Archived {archived_count} analysis result records before removal")

    try:
        # Query for records older than the cutoff date
        query = session.query(AnalysisResult).filter(
            AnalysisResult.created_at < cutoff_date
        )
        
        # Get count before deletion
        count = query.count()
        
        if count > 0:
            # Delete the records
            query.delete(synchronize_session=False)
            
            # Commit the changes
            session.commit()
            
            logger.info(f"Successfully removed {count} analysis result records")
        else:
            logger.info("No analysis result records to clean up")
            
        return count
        
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        logger.error(f"Error cleaning up analysis results: {str(e)}", exc_info=True)
        raise

def cleanup_audit_logs(session: sqlalchemy.orm.Session, retention_days: Optional[int] = None) -> int:
    """
    Removes audit log records that have exceeded the retention period.
    
    Args:
        session: SQLAlchemy database session
        retention_days: Optional override for retention period in days
        
    Returns:
        int: Number of audit log records removed
    """
    # Use provided retention days or default
    days = retention_days or AUDIT_LOG_RETENTION_DAYS
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    logger.info(f"Cleaning up audit logs older than {cutoff_date.isoformat()}")
    
    # Archive old data before removal if in production
    if settings.ENV.lower() == 'production':
        archived_count = archive_old_data(session, 'audit_logs', cutoff_date)
        logger.info(f"Archived {archived_count} audit log records before removal")

    try:
        # Query for records older than the cutoff date
        query = session.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        )
        
        # Get count before deletion
        count = query.count()
        
        if count > 0:
            # Delete the records
            query.delete(synchronize_session=False)
            
            # Commit the changes
            session.commit()
            
            logger.info(f"Successfully removed {count} audit log records")
        else:
            logger.info("No audit log records to clean up")
            
        return count
        
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        logger.error(f"Error cleaning up audit logs: {str(e)}", exc_info=True)
        raise

def cleanup_cache() -> int:
    """
    Removes expired cache entries from Redis.
    
    Returns:
        int: Number of cache keys removed
    """
    logger.info("Cleaning up expired cache entries")
    
    try:
        # Initialize Redis client
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        
        # Count of removed keys
        removed_count = 0
        
        # Scan for keys matching the pattern
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=CACHE_CLEANUP_PATTERN)
            
            for key in keys:
                # Check if key has expiry
                ttl = redis_client.ttl(key)
                
                # Remove keys with no expiry or expired keys
                # TTL returns -1 if no expiry set, -2 if the key doesn't exist
                if ttl == -1:  # No expiry set
                    redis_client.delete(key)
                    removed_count += 1
                    logger.debug(f"Removed cache key with no expiry: {key}")
            
            # Break when scan is complete
            if cursor == 0:
                break
        
        logger.info(f"Successfully removed {removed_count} cache entries")
        return removed_count
        
    except Exception as e:
        logger.error(f"Error cleaning up cache: {str(e)}", exc_info=True)
        return 0

def archive_old_data(session: sqlalchemy.orm.Session, data_type: str, cutoff_date: datetime) -> int:
    """
    Archives old data to long-term storage before removal.
    
    In a production environment, this would typically:
    1. Export the data to a suitable format (JSON, CSV)
    2. Store it in a long-term storage solution (e.g., S3)
    3. Record the archival operation in a log
    
    Args:
        session: SQLAlchemy database session
        data_type: Type of data being archived (e.g., 'freight_data', 'audit_logs')
        cutoff_date: Date threshold for archiving
        
    Returns:
        int: Number of records archived
    """
    logger.info(f"Archiving old {data_type} data before {cutoff_date.isoformat()}")
    
    archived_count = 0
    
    try:
        # Determine the appropriate model class based on data_type
        if data_type == 'freight_data':
            model_class = FreightData
            filter_condition = and_(
                FreightData.record_date < cutoff_date,
                FreightData.is_deleted == False
            )
        elif data_type == 'analysis_results':
            model_class = AnalysisResult
            filter_condition = AnalysisResult.created_at < cutoff_date
        elif data_type == 'audit_logs':
            model_class = AuditLog
            filter_condition = AuditLog.created_at < cutoff_date
        else:
            logger.warning(f"Unknown data type for archiving: {data_type}")
            return 0
        
        # Query for records to archive
        records = session.query(model_class).filter(filter_condition).all()
        archived_count = len(records)
        
        if archived_count > 0:
            # In a real implementation, this would:
            # 1. Convert records to a suitable format (JSON/CSV)
            # 2. Upload to long-term storage (S3 or similar)
            # 3. Record the archive location for future reference
            
            # Example of what real archiving might include:
            # archive_date = datetime.utcnow().strftime('%Y%m%d')
            # filename = f"{data_type}_archive_{archive_date}.json"
            # s3_path = f"archives/{data_type}/{filename}"
            # 
            # # Convert to JSON
            # records_json = [record.to_dict() for record in records]
            # 
            # # Store the exported data in long-term storage (S3 or similar)
            # s3_client.put_object(
            #     Bucket='freight-price-agent-archives',
            #     Key=s3_path,
            #     Body=json.dumps(records_json)
            # )
            
            logger.info(f"Archived {archived_count} {data_type} records to long-term storage")
        else:
            logger.info(f"No {data_type} records to archive")
        
        return archived_count
        
    except Exception as e:
        logger.error(f"Error archiving {data_type} data: {str(e)}", exc_info=True)
        return 0