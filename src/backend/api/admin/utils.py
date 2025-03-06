"""
Utility functions for the admin module of the Freight Price Movement Agent.

This module provides core functionality for system configuration management,
audit logging, and maintenance scheduling. It implements secure configuration
handling, comprehensive activity logging for audit trails, and maintenance
window management to support system operations.
"""

import datetime
from typing import Dict, List, Optional, Any

import sqlalchemy
from sqlalchemy import exc as sqlalchemy_exc

from ...core.db import db
from ...core.logging import logger
from ...core.security import encrypt_data, decrypt_data
from ...core.config import settings
from ...core.exceptions import NotFoundError, ValidationError
from .models import SystemConfig, AdminActivity, MaintenanceSchedule

# Constants for admin action types
ADMIN_ACTIONS = {
    'CREATE': 'create',
    'UPDATE': 'update',
    'DELETE': 'delete',
    'VIEW': 'view',
    'EXPORT': 'export',
    'IMPORT': 'import',
    'LOGIN': 'login',
    'LOGOUT': 'logout',
    'MAINTENANCE': 'maintenance'
}

# Constants for resource types in admin activities
RESOURCE_TYPES = {
    'SYSTEM_CONFIG': 'system_config',
    'USER': 'user',
    'MAINTENANCE': 'maintenance',
    'DATA_SOURCE': 'data_source',
    'ANALYSIS': 'analysis',
    'REPORT': 'report'
}


def get_system_config(key: str, decrypt: bool = False) -> Optional[SystemConfig]:
    """
    Retrieves a system configuration by key.

    Args:
        key: The configuration key to retrieve
        decrypt: Whether to decrypt encrypted values

    Returns:
        The system configuration object or None if not found
    """
    # Normalize key to lowercase with underscores for consistency
    normalized_key = key.lower().replace(' ', '_')
    
    try:
        # Query the database for the configuration
        config = db.session.query(SystemConfig).filter(SystemConfig.key == normalized_key).first()
        
        if config and decrypt and config.is_encrypted:
            # Decrypt the value if requested and the value is encrypted
            config.value = decrypt_data(config.value, settings.ENCRYPTION_KEY)
        
        return config
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Error retrieving system config with key {key}: {str(e)}")
        return None


def set_system_config(
    key: str,
    value: Any,
    user_id: str,
    description: Optional[str] = None,
    config_type: Optional[str] = None,
    is_encrypted: bool = False
) -> SystemConfig:
    """
    Creates or updates a system configuration.

    Args:
        key: The configuration key
        value: The configuration value
        user_id: ID of the user making the change
        description: Optional description of the configuration
        config_type: Optional configuration type category
        is_encrypted: Whether the value should be encrypted

    Returns:
        The created or updated system configuration object
    """
    # Normalize key to lowercase with underscores for consistency
    normalized_key = key.lower().replace(' ', '_')
    
    # Convert value to string if not already
    if value is not None and not isinstance(value, str):
        value = str(value)
    
    # Encrypt the value if specified
    if is_encrypted and value is not None:
        value = encrypt_data(value, settings.ENCRYPTION_KEY)
    
    try:
        # Check if configuration already exists
        config = db.session.query(SystemConfig).filter(SystemConfig.key == normalized_key).first()
        
        if config:
            # Update existing configuration
            config.value = value
            config.is_encrypted = is_encrypted
            
            if description:
                config.description = description
            
            if config_type:
                config.config_type = config_type
            
            logger.info(f"Updated system config: {normalized_key} by user {user_id}")
        else:
            # Create new configuration
            config = SystemConfig(
                key=normalized_key,
                value=value,
                description=description,
                config_type=config_type,
                is_encrypted=is_encrypted,
                created_by_id=user_id
            )
            db.session.add(config)
            
            logger.info(f"Created new system config: {normalized_key} by user {user_id}")
        
        # Commit the changes
        db.session.commit()
        
        return config
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error setting system config with key {key}: {str(e)}")
        raise ValidationError(f"Failed to save system configuration: {str(e)}")


def delete_system_config(key: str, user_id: str) -> bool:
    """
    Deletes a system configuration by key.

    Args:
        key: The configuration key to delete
        user_id: ID of the user performing the deletion

    Returns:
        True if deleted successfully, False if not found
    """
    # Normalize key to lowercase with underscores for consistency
    normalized_key = key.lower().replace(' ', '_')
    
    try:
        # Find the configuration
        config = db.session.query(SystemConfig).filter(SystemConfig.key == normalized_key).first()
        
        if not config:
            logger.warning(f"Attempted to delete non-existent system config: {normalized_key}")
            return False
        
        # Delete the configuration
        db.session.delete(config)
        db.session.commit()
        
        logger.info(f"Deleted system config: {normalized_key} by user {user_id}")
        return True
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting system config with key {key}: {str(e)}")
        return False


def log_admin_activity(
    user_id: str,
    action: str,
    details: Dict,
    resource_type: str,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AdminActivity:
    """
    Logs an administrative activity for audit purposes.

    Args:
        user_id: ID of the user performing the action
        action: Type of action performed (use ADMIN_ACTIONS constants)
        details: Dictionary with details about the action
        resource_type: Type of resource affected (use RESOURCE_TYPES constants)
        resource_id: Optional ID of the specific resource
        ip_address: Optional IP address of the user

    Returns:
        The created admin activity log entry
    """
    # Validate action type
    if action not in ADMIN_ACTIONS.values():
        logger.warning(f"Invalid admin action type: {action}. Using 'unknown'.")
        action = 'unknown'
    
    # Validate resource type
    if resource_type not in RESOURCE_TYPES.values():
        logger.warning(f"Invalid resource type: {resource_type}. Using 'unknown'.")
        resource_type = 'unknown'
    
    try:
        # Create the activity log
        activity = AdminActivity(
            user_id=user_id,
            action=action,
            details=details,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address
        )
        
        # Add and commit to the database
        db.session.add(activity)
        db.session.commit()
        
        logger.info(
            f"Admin activity logged: {action} on {resource_type}"
            f"{f' (ID: {resource_id})' if resource_id else ''} by user {user_id}"
        )
        
        return activity
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error logging admin activity: {str(e)}")
        # Still create an activity object even if saving failed
        activity = AdminActivity(
            user_id=user_id, 
            action=action,
            details=details,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address
        )
        return activity


def get_admin_activities(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AdminActivity]:
    """
    Retrieves admin activities with filtering options.

    Args:
        user_id: Optional filter by user ID
        action: Optional filter by action type
        resource_type: Optional filter by resource type
        resource_id: Optional filter by resource ID
        start_date: Optional filter for activities after this date
        end_date: Optional filter for activities before this date
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of admin activity records matching the filters
    """
    try:
        # Start building the query
        query = db.session.query(AdminActivity)
        
        # Apply filters if provided
        if user_id:
            query = query.filter(AdminActivity.user_id == user_id)
        
        if action:
            query = query.filter(AdminActivity.action == action)
        
        if resource_type:
            query = query.filter(AdminActivity.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(AdminActivity.resource_id == resource_id)
        
        # Apply date range filters
        if start_date:
            query = query.filter(AdminActivity.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AdminActivity.timestamp <= end_date)
        
        # Order by timestamp descending (newest first)
        query = query.order_by(AdminActivity.timestamp.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query and return results
        return query.all()
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Error retrieving admin activities: {str(e)}")
        return []


def create_maintenance_schedule(
    title: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    created_by_id: str,
    description: Optional[str] = None,
    is_active: bool = True
) -> MaintenanceSchedule:
    """
    Creates a new maintenance schedule.

    Args:
        title: Title of the maintenance window
        start_time: Start time of the maintenance window
        end_time: End time of the maintenance window
        created_by_id: ID of the user creating the schedule
        description: Optional description of the maintenance
        is_active: Whether the maintenance schedule is active

    Returns:
        The created maintenance schedule
    """
    # Validate end_time is after start_time
    if end_time <= start_time:
        raise ValidationError("End time must be after start time")
    
    try:
        # Create new maintenance schedule
        schedule = MaintenanceSchedule(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            is_active=is_active,
            created_by_id=created_by_id
        )
        
        # Add and commit to the database
        db.session.add(schedule)
        db.session.commit()
        
        # Log the activity
        log_admin_activity(
            user_id=created_by_id,
            action=ADMIN_ACTIONS['MAINTENANCE'],
            resource_type=RESOURCE_TYPES['MAINTENANCE'],
            resource_id=schedule.id,
            details={
                'title': title,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'is_active': is_active
            }
        )
        
        logger.info(f"Created maintenance schedule: {title} by user {created_by_id}")
        
        return schedule
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating maintenance schedule: {str(e)}")
        raise ValidationError(f"Failed to create maintenance schedule: {str(e)}")


def update_maintenance_schedule(
    schedule_id: str,
    update_data: Dict,
    user_id: str
) -> Optional[MaintenanceSchedule]:
    """
    Updates an existing maintenance schedule.

    Args:
        schedule_id: ID of the schedule to update
        update_data: Dictionary of fields to update
        user_id: ID of the user making the update

    Returns:
        The updated maintenance schedule or None if not found
    """
    try:
        # Find the schedule
        schedule = db.session.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == schedule_id).first()
        
        if not schedule:
            logger.warning(f"Attempted to update non-existent maintenance schedule: {schedule_id}")
            return None
        
        # Validate time ranges if both are provided
        if 'start_time' in update_data and 'end_time' in update_data:
            start_time = update_data['start_time']
            end_time = update_data['end_time']
            
            if end_time <= start_time:
                raise ValidationError("End time must be after start time")
        elif 'start_time' in update_data and update_data['start_time'] >= schedule.end_time:
            raise ValidationError("Start time must be before end time")
        elif 'end_time' in update_data and update_data['end_time'] <= schedule.start_time:
            raise ValidationError("End time must be after start time")
        
        # Track changes for activity log
        changes = {}
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(schedule, key):
                old_value = getattr(schedule, key)
                setattr(schedule, key, value)
                
                # Record the change for logging
                if old_value != value:
                    changes[key] = {
                        'old': old_value.isoformat() if isinstance(old_value, datetime.datetime) else old_value,
                        'new': value.isoformat() if isinstance(value, datetime.datetime) else value
                    }
        
        # Commit changes
        db.session.commit()
        
        # Log the activity
        log_admin_activity(
            user_id=user_id,
            action=ADMIN_ACTIONS['UPDATE'],
            resource_type=RESOURCE_TYPES['MAINTENANCE'],
            resource_id=schedule.id,
            details={
                'title': schedule.title,
                'changes': changes
            }
        )
        
        logger.info(f"Updated maintenance schedule: {schedule.title} by user {user_id}")
        
        return schedule
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating maintenance schedule {schedule_id}: {str(e)}")
        raise ValidationError(f"Failed to update maintenance schedule: {str(e)}")


def delete_maintenance_schedule(schedule_id: str, user_id: str) -> bool:
    """
    Deletes a maintenance schedule.

    Args:
        schedule_id: ID of the schedule to delete
        user_id: ID of the user performing the deletion

    Returns:
        True if deleted successfully, False if not found
    """
    try:
        # Find the schedule
        schedule = db.session.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == schedule_id).first()
        
        if not schedule:
            logger.warning(f"Attempted to delete non-existent maintenance schedule: {schedule_id}")
            return False
        
        # Store details for logging
        schedule_details = {
            'title': schedule.title,
            'start_time': schedule.start_time.isoformat(),
            'end_time': schedule.end_time.isoformat()
        }
        
        # Delete the schedule
        db.session.delete(schedule)
        db.session.commit()
        
        # Log the activity
        log_admin_activity(
            user_id=user_id,
            action=ADMIN_ACTIONS['DELETE'],
            resource_type=RESOURCE_TYPES['MAINTENANCE'],
            resource_id=schedule_id,
            details=schedule_details
        )
        
        logger.info(f"Deleted maintenance schedule: {schedule_details['title']} by user {user_id}")
        
        return True
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting maintenance schedule {schedule_id}: {str(e)}")
        return False


def get_active_maintenance_schedules() -> List[MaintenanceSchedule]:
    """
    Retrieves currently active maintenance schedules.

    Returns:
        List of active maintenance schedules
    """
    try:
        # Get current time
        now = datetime.datetime.utcnow()
        
        # Query for active schedules that are currently in progress
        schedules = db.session.query(MaintenanceSchedule).filter(
            MaintenanceSchedule.is_active == True,
            MaintenanceSchedule.start_time <= now,
            MaintenanceSchedule.end_time > now
        ).order_by(MaintenanceSchedule.start_time).all()
        
        return schedules
        
    except sqlalchemy_exc.SQLAlchemyError as e:
        logger.error(f"Error retrieving active maintenance schedules: {str(e)}")
        return []


def is_system_in_maintenance() -> bool:
    """
    Checks if the system is currently in maintenance mode.

    Returns:
        True if any active maintenance schedule is currently in effect
    """
    active_schedules = get_active_maintenance_schedules()
    return len(active_schedules) > 0