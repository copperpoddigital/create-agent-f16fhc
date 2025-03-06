"""
Controller module for the admin API of the Freight Price Movement Agent.

Implements business logic for system configuration management, admin activity logging,
and maintenance scheduling. Serves as an intermediary between API routes and data models.
"""

from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any

import sqlalchemy
from sqlalchemy import func, or_, and_

from ...core.db import db
from ...core.logging import logger
from ...core.security import encrypt_data, decrypt_data
from ...core.exceptions import ValidationException, NotFoundException, ConfigurationException
from ...core.config import settings
from .models import SystemConfig, AdminActivity, MaintenanceSchedule
from .schemas import SystemConfigResponse, AdminActivityResponse, MaintenanceScheduleResponse


def get_system_configs(key: Optional[str] = None, config_type: Optional[str] = None, 
                     skip: int = 0, limit: int = 100) -> List[SystemConfigResponse]:
    """
    Retrieves system configurations with optional filtering.
    
    Args:
        key: Optional key to filter by
        config_type: Optional config type to filter by
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of SystemConfigResponse objects
    """
    query = db.session.query(SystemConfig)
    
    if key:
        query = query.filter(SystemConfig.key.ilike(f'%{key}%'))
    
    if config_type:
        query = query.filter(SystemConfig.config_type == config_type)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    configs = query.all()
    
    # Convert to response models
    return [SystemConfigResponse.from_orm(config) for config in configs]


def get_system_config_by_key(key: str, decrypt: bool = False) -> SystemConfigResponse:
    """
    Retrieves a system configuration by its key.
    
    Args:
        key: Unique key of the configuration
        decrypt: Whether to decrypt the value if it's encrypted
        
    Returns:
        SystemConfigResponse object
        
    Raises:
        NotFoundException: If configuration with the key is not found
    """
    # Normalize key to lowercase with underscores
    key = key.lower().replace(' ', '_')
    
    # Query the database
    config = db.session.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    if not config:
        raise NotFoundException(f"System configuration with key '{key}' not found")
    
    # Decrypt value if needed
    if decrypt and config.is_encrypted:
        config.value = decrypt_data(config.value, settings.ENCRYPTION_KEY)
    
    # Convert to response model
    return SystemConfigResponse.from_orm(config)


def create_system_config(config_data: dict, user_id: str, ip_address: str) -> SystemConfigResponse:
    """
    Creates a new system configuration.
    
    Args:
        config_data: Configuration data including key, value, description, etc.
        user_id: ID of the user creating the config
        ip_address: IP address of the user
        
    Returns:
        SystemConfigResponse object
        
    Raises:
        ValidationException: If a configuration with the same key already exists
    """
    # Normalize key to lowercase with underscores
    key = config_data.get('key', '').lower().replace(' ', '_')
    config_data['key'] = key
    
    # Check if config with same key already exists
    existing_config = db.session.query(SystemConfig).filter(SystemConfig.key == key).first()
    if existing_config:
        raise ValidationException(f"Configuration with key '{key}' already exists")
    
    # Encrypt value if needed
    if config_data.get('is_encrypted', False) and 'value' in config_data:
        config_data['value'] = encrypt_data(config_data['value'], settings.ENCRYPTION_KEY)
    
    # Create new config
    config = SystemConfig(
        key=key,
        value=config_data.get('value'),
        description=config_data.get('description'),
        config_type=config_data.get('config_type'),
        is_encrypted=config_data.get('is_encrypted', False),
        created_by_id=user_id
    )
    
    db.session.add(config)
    db.session.commit()
    
    # Log admin activity
    log_activity = AdminActivity(
        user_id=user_id,
        action="CREATE_SYSTEM_CONFIG",
        details={"key": key},
        ip_address=ip_address,
        resource_type="system_config",
        resource_id=str(config.id)
    )
    db.session.add(log_activity)
    db.session.commit()
    
    logger.info(f"System configuration created: {key} by user {user_id}")
    
    # Convert to response model
    return SystemConfigResponse.from_orm(config)


def update_system_config(key: str, config_data: dict, user_id: str, ip_address: str) -> SystemConfigResponse:
    """
    Updates an existing system configuration.
    
    Args:
        key: Key of the configuration to update
        config_data: New configuration data
        user_id: ID of the user updating the config
        ip_address: IP address of the user
        
    Returns:
        SystemConfigResponse object
        
    Raises:
        NotFoundException: If configuration with the key is not found
    """
    # Normalize key to lowercase with underscores
    key = key.lower().replace(' ', '_')
    
    # Query the database
    config = db.session.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    if not config:
        raise NotFoundException(f"System configuration with key '{key}' not found")
    
    # Store old values for logging
    old_values = {
        "value": config.value if not config.is_encrypted else "*****",
        "description": config.description,
        "config_type": config.config_type.name if config.config_type else None,
        "is_encrypted": config.is_encrypted
    }
    
    # Update fields if provided
    if 'description' in config_data:
        config.description = config_data['description']
    
    if 'config_type' in config_data:
        config.config_type = config_data['config_type']
    
    if 'is_encrypted' in config_data:
        config.is_encrypted = config_data['is_encrypted']
    
    # Handle value update with encryption if needed
    if 'value' in config_data:
        if config_data.get('is_encrypted', config.is_encrypted):
            config.value = encrypt_data(config_data['value'], settings.ENCRYPTION_KEY)
        else:
            config.value = config_data['value']
    
    db.session.commit()
    
    # Log admin activity
    log_activity = AdminActivity(
        user_id=user_id,
        action="UPDATE_SYSTEM_CONFIG",
        details={
            "key": key,
            "old_values": old_values,
            "new_values": {
                "value": "*****" if config.is_encrypted else config.value,
                "description": config.description,
                "config_type": config.config_type.name if config.config_type else None,
                "is_encrypted": config.is_encrypted
            }
        },
        ip_address=ip_address,
        resource_type="system_config",
        resource_id=str(config.id)
    )
    db.session.add(log_activity)
    db.session.commit()
    
    logger.info(f"System configuration updated: {key} by user {user_id}")
    
    # Convert to response model
    return SystemConfigResponse.from_orm(config)


def delete_system_config_by_key(key: str, user_id: str, ip_address: str) -> Dict[str, str]:
    """
    Deletes a system configuration by its key.
    
    Args:
        key: Key of the configuration to delete
        user_id: ID of the user deleting the config
        ip_address: IP address of the user
        
    Returns:
        Success message
        
    Raises:
        NotFoundException: If configuration with the key is not found
    """
    # Normalize key to lowercase with underscores
    key = key.lower().replace(' ', '_')
    
    # Query the database
    config = db.session.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    if not config:
        raise NotFoundException(f"System configuration with key '{key}' not found")
    
    # Store config info for logging
    config_id = str(config.id)
    
    # Delete the config
    db.session.delete(config)
    db.session.commit()
    
    # Log admin activity
    log_activity = AdminActivity(
        user_id=user_id,
        action="DELETE_SYSTEM_CONFIG",
        details={"key": key},
        ip_address=ip_address,
        resource_type="system_config",
        resource_id=config_id
    )
    db.session.add(log_activity)
    db.session.commit()
    
    logger.info(f"System configuration deleted: {key} by user {user_id}")
    
    return {"message": f"System configuration '{key}' deleted successfully"}


def get_admin_activities_list(user_id: Optional[str] = None, action: Optional[str] = None,
                             resource_type: Optional[str] = None, resource_id: Optional[str] = None,
                             start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                             skip: int = 0, limit: int = 100) -> List[AdminActivityResponse]:
    """
    Retrieves admin activities with optional filtering.
    
    Args:
        user_id: Optional user ID to filter by
        action: Optional action to filter by
        resource_type: Optional resource type to filter by
        resource_id: Optional resource ID to filter by
        start_date: Optional start date for time range filtering
        end_date: Optional end date for time range filtering
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of AdminActivityResponse objects
    """
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
    
    # Apply date range filters if provided
    if start_date:
        query = query.filter(AdminActivity.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AdminActivity.timestamp <= end_date)
    
    # Apply pagination and order by timestamp descending
    query = query.order_by(AdminActivity.timestamp.desc()).offset(skip).limit(limit)
    
    # Execute query
    activities = query.all()
    
    # Convert to response models
    return [AdminActivityResponse.from_orm(activity) for activity in activities]


def create_admin_activity(activity_data: dict, ip_address: str) -> AdminActivityResponse:
    """
    Creates a new admin activity log entry.
    
    Args:
        activity_data: Activity data including user_id, action, details, etc.
        ip_address: IP address of the user
        
    Returns:
        AdminActivityResponse object
    """
    # Create new activity
    activity = AdminActivity(
        user_id=activity_data.get('user_id'),
        action=activity_data.get('action'),
        details=activity_data.get('details', {}),
        resource_type=activity_data.get('resource_type'),
        resource_id=activity_data.get('resource_id'),
        ip_address=ip_address
    )
    
    db.session.add(activity)
    db.session.commit()
    
    logger.info(f"Admin activity logged: {activity.action} by user {activity.user_id}")
    
    # Convert to response model
    return AdminActivityResponse.from_orm(activity)


def get_maintenance_schedules(is_active: Optional[bool] = None, 
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             skip: int = 0, limit: int = 100) -> List[MaintenanceScheduleResponse]:
    """
    Retrieves maintenance schedules with optional filtering.
    
    Args:
        is_active: Optional filter for active/inactive schedules
        start_date: Optional start date for time range filtering
        end_date: Optional end date for time range filtering
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of MaintenanceScheduleResponse objects
    """
    query = db.session.query(MaintenanceSchedule)
    
    # Apply active filter if provided
    if is_active is not None:
        query = query.filter(MaintenanceSchedule.is_active == is_active)
    
    # Apply date range filters if provided
    if start_date:
        query = query.filter(MaintenanceSchedule.end_time >= start_date)
    
    if end_date:
        query = query.filter(MaintenanceSchedule.start_time <= end_date)
    
    # Apply pagination and order by start_time
    query = query.order_by(MaintenanceSchedule.start_time).offset(skip).limit(limit)
    
    # Execute query
    schedules = query.all()
    
    # Convert to response models
    return [MaintenanceScheduleResponse.from_orm(schedule) for schedule in schedules]


def get_maintenance_schedule_by_id(schedule_id: str) -> MaintenanceScheduleResponse:
    """
    Retrieves a maintenance schedule by its ID.
    
    Args:
        schedule_id: ID of the maintenance schedule
        
    Returns:
        MaintenanceScheduleResponse object
        
    Raises:
        NotFoundException: If schedule with the ID is not found
    """
    try:
        # Convert string ID to UUID
        uuid_id = uuid.UUID(schedule_id)
    except ValueError:
        raise ValidationException(f"Invalid schedule ID format: {schedule_id}")
    
    # Query the database
    schedule = db.session.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == str(uuid_id)).first()
    
    if not schedule:
        raise NotFoundException(f"Maintenance schedule with ID '{schedule_id}' not found")
    
    # Convert to response model
    return MaintenanceScheduleResponse.from_orm(schedule)


def create_maintenance_schedule_controller(schedule_data: dict, user_id: str, ip_address: str) -> MaintenanceScheduleResponse:
    """
    Creates a new maintenance schedule.
    
    Args:
        schedule_data: Schedule data including title, description, start_time, end_time, etc.
        user_id: ID of the user creating the schedule
        ip_address: IP address of the user
        
    Returns:
        MaintenanceScheduleResponse object
        
    Raises:
        ValidationException: If end_time is not after start_time
    """
    # Validate that end_time is after start_time
    start_time = schedule_data.get('start_time')
    end_time = schedule_data.get('end_time')
    
    if start_time and end_time and end_time <= start_time:
        raise ValidationException("End time must be after start time")
    
    # Create new schedule
    schedule = MaintenanceSchedule(
        title=schedule_data.get('title'),
        description=schedule_data.get('description'),
        start_time=start_time,
        end_time=end_time,
        is_active=schedule_data.get('is_active', True),
        created_by_id=user_id
    )
    
    db.session.add(schedule)
    db.session.commit()
    
    # Log admin activity
    log_activity = AdminActivity(
        user_id=user_id,
        action="CREATE_MAINTENANCE_SCHEDULE",
        details={"title": schedule.title, "start_time": schedule.start_time.isoformat(), "end_time": schedule.end_time.isoformat()},
        ip_address=ip_address,
        resource_type="maintenance_schedule",
        resource_id=str(schedule.id)
    )
    db.session.add(log_activity)
    db.session.commit()
    
    logger.info(f"Maintenance schedule created: {schedule.title} by user {user_id}")
    
    # Convert to response model
    return MaintenanceScheduleResponse.from_orm(schedule)


def update_maintenance_schedule_controller(schedule_id: str, schedule_data: dict, user_id: str, ip_address: str) -> MaintenanceScheduleResponse:
    """
    Updates an existing maintenance schedule.
    
    Args:
        schedule_id: ID of the maintenance schedule to update
        schedule_data: New schedule data
        user_id: ID of the user updating the schedule
        ip_address: IP address of the user
        
    Returns:
        MaintenanceScheduleResponse object
        
    Raises:
        NotFoundException: If schedule with the ID is not found
        ValidationException: If end_time is not after start_time
    """
    try:
        # Convert string ID to UUID
        uuid_id = uuid.UUID(schedule_id)
    except ValueError:
        raise ValidationException(f"Invalid schedule ID format: {schedule_id}")
    
    # Query the database
    schedule = db.session.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == str(uuid_id)).first()
    
    if not schedule:
        raise NotFoundException(f"Maintenance schedule with ID '{schedule_id}' not found")
    
    # Store old values for logging
    old_values = {
        "title": schedule.title,
        "description": schedule.description,
        "start_time": schedule.start_time.isoformat() if schedule.start_time else None,
        "end_time": schedule.end_time.isoformat() if schedule.end_time else None,
        "is_active": schedule.is_active
    }
    
    # Validate that end_time is after start_time if both are provided
    start_time = schedule_data.get('start_time', schedule.start_time)
    end_time = schedule_data.get('end_time', schedule.end_time)
    
    if start_time and end_time and end_time <= start_time:
        raise ValidationException("End time must be after start time")
    
    # Update fields if provided
    if 'title' in schedule_data:
        schedule.title = schedule_data['title']
    
    if 'description' in schedule_data:
        schedule.description = schedule_data['description']
    
    if 'start_time' in schedule_data:
        schedule.start_time = schedule_data['start_time']
    
    if 'end_time' in schedule_data:
        schedule.end_time = schedule_data['end_time']
    
    if 'is_active' in schedule_data:
        schedule.is_active = schedule_data['is_active']
    
    db.session.commit()
    
    # Log admin activity
    log_activity = AdminActivity(
        user_id=user_id,
        action="UPDATE_MAINTENANCE_SCHEDULE",
        details={
            "id": str(schedule.id),
            "old_values": old_values,
            "new_values": {
                "title": schedule.title,
                "description": schedule.description,
                "start_time": schedule.start_time.isoformat() if schedule.start_time else None,
                "end_time": schedule.end_time.isoformat() if schedule.end_time else None,
                "is_active": schedule.is_active
            }
        },
        ip_address=ip_address,
        resource_type="maintenance_schedule",
        resource_id=str(schedule.id)
    )
    db.session.add(log_activity)
    db.session.commit()
    
    logger.info(f"Maintenance schedule updated: {schedule.title} by user {user_id}")
    
    # Convert to response model
    return MaintenanceScheduleResponse.from_orm(schedule)


def delete_maintenance_schedule_controller(schedule_id: str, user_id: str, ip_address: str) -> Dict[str, str]:
    """
    Deletes a maintenance schedule by its ID.
    
    Args:
        schedule_id: ID of the maintenance schedule to delete
        user_id: ID of the user deleting the schedule
        ip_address: IP address of the user
        
    Returns:
        Success message
        
    Raises:
        NotFoundException: If schedule with the ID is not found
    """
    try:
        # Convert string ID to UUID
        uuid_id = uuid.UUID(schedule_id)
    except ValueError:
        raise ValidationException(f"Invalid schedule ID format: {schedule_id}")
    
    # Query the database
    schedule = db.session.query(MaintenanceSchedule).filter(MaintenanceSchedule.id == str(uuid_id)).first()
    
    if not schedule:
        raise NotFoundException(f"Maintenance schedule with ID '{schedule_id}' not found")
    
    # Store schedule info for logging
    schedule_title = schedule.title
    
    # Delete the schedule
    db.session.delete(schedule)
    db.session.commit()
    
    # Log admin activity
    log_activity = AdminActivity(
        user_id=user_id,
        action="DELETE_MAINTENANCE_SCHEDULE",
        details={"id": schedule_id, "title": schedule_title},
        ip_address=ip_address,
        resource_type="maintenance_schedule",
        resource_id=schedule_id
    )
    db.session.add(log_activity)
    db.session.commit()
    
    logger.info(f"Maintenance schedule deleted: {schedule_title} by user {user_id}")
    
    return {"message": f"Maintenance schedule '{schedule_title}' deleted successfully"}


def get_active_maintenance_schedules_controller() -> List[MaintenanceScheduleResponse]:
    """
    Retrieves currently active maintenance schedules.
    
    Returns:
        List of MaintenanceScheduleResponse objects for active schedules
    """
    current_time = datetime.utcnow()
    
    # Query for active schedules where current time is between start and end time
    query = db.session.query(MaintenanceSchedule).filter(
        MaintenanceSchedule.is_active == True,
        MaintenanceSchedule.start_time <= current_time,
        MaintenanceSchedule.end_time >= current_time
    )
    
    # Execute query
    schedules = query.all()
    
    # Convert to response models
    return [MaintenanceScheduleResponse.from_orm(schedule) for schedule in schedules]


def check_system_maintenance_status() -> Dict[str, Any]:
    """
    Checks if the system is currently under maintenance.
    
    Returns:
        Dict with maintenance status information
    """
    active_schedules = get_active_maintenance_schedules_controller()
    
    is_under_maintenance = len(active_schedules) > 0
    
    result = {
        "is_under_maintenance": is_under_maintenance,
        "maintenance_details": [schedule.dict() for schedule in active_schedules] if is_under_maintenance else None
    }
    
    return result