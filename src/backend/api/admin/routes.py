"""
Admin routes module for the Freight Price Movement Agent.

This module defines API routes for the admin module, providing endpoints for
system configuration management, admin activity logging, and maintenance scheduling.
"""

from datetime import datetime
from typing import Optional

from flask import Blueprint, request, jsonify, g

from ../../core.logging import logger
from ../../core.exceptions import ValidationException, NotFoundException, ConfigurationException
from ../../core.security import require_auth, admin_required
from .controllers import (
    get_system_configs, get_system_config_by_key, create_system_config, update_system_config,
    delete_system_config_by_key, get_admin_activities_list, create_admin_activity,
    get_maintenance_schedules, get_maintenance_schedule_by_id, create_maintenance_schedule_controller,
    update_maintenance_schedule_controller, delete_maintenance_schedule_controller,
    get_active_maintenance_schedules_controller, check_system_maintenance_status
)
from .schemas import (
    SystemConfigCreate, SystemConfigUpdate, AdminActivityCreate,
    MaintenanceScheduleCreate, MaintenanceScheduleUpdate
)

# Create Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

# System Configuration Routes

@admin_bp.route('/configs', methods=['GET'])
@require_auth
@admin_required
def get_system_configs_route():
    """
    Route handler for retrieving system configurations with optional filtering.
    
    Query Parameters:
        key (str, optional): Filter by key (partial match)
        config_type (str, optional): Filter by configuration type
        skip (int, optional): Number of records to skip for pagination
        limit (int, optional): Maximum number of records to return
    
    Returns:
        JSON response with system configurations
    """
    # Extract query parameters
    key = request.args.get('key')
    config_type = request.args.get('config_type')
    skip = request.args.get('skip', default=0, type=int)
    limit = request.args.get('limit', default=100, type=int)
    
    # Call controller function
    configs = get_system_configs(key, config_type, skip, limit)
    
    # Return JSON response
    return jsonify({
        "success": True,
        "data": [config.dict() for config in configs]
    })


@admin_bp.route('/configs/<string:key>', methods=['GET'])
@require_auth
@admin_required
def get_system_config_by_key_route(key):
    """
    Route handler for retrieving a system configuration by key.
    
    Path Parameters:
        key (str): The key of the configuration to retrieve
    
    Query Parameters:
        decrypt (bool, optional): Whether to decrypt the value if it's encrypted
    
    Returns:
        JSON response with system configuration
    """
    # Extract decrypt parameter
    decrypt = request.args.get('decrypt', default=False, type=bool)
    
    try:
        # Call controller function
        config = get_system_config_by_key(key, decrypt)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": config.dict()
        })
    except NotFoundException as e:
        logger.warning(f"Configuration not found: {key}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


@admin_bp.route('/configs', methods=['POST'])
@require_auth
@admin_required
def create_system_config_route():
    """
    Route handler for creating a new system configuration.
    
    Request Body:
        SystemConfigCreate schema
    
    Returns:
        JSON response with created system configuration
    """
    try:
        # Parse request data
        data = request.json
        
        # Validate with schema
        config_data = SystemConfigCreate(**data)
        
        # Extract user_id and ip_address from request
        user_id = g.user_id
        ip_address = request.remote_addr
        
        # Call controller function
        config = create_system_config(config_data.dict(), user_id, ip_address)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": config.dict()
        }), 201
    except ValidationException as e:
        logger.warning(f"Validation error in create_system_config: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@admin_bp.route('/configs/<string:key>', methods=['PUT'])
@require_auth
@admin_required
def update_system_config_route(key):
    """
    Route handler for updating an existing system configuration.
    
    Path Parameters:
        key (str): The key of the configuration to update
    
    Request Body:
        SystemConfigUpdate schema
    
    Returns:
        JSON response with updated system configuration
    """
    try:
        # Parse request data
        data = request.json
        
        # Validate with schema
        config_data = SystemConfigUpdate(**data)
        
        # Extract user_id and ip_address from request
        user_id = g.user_id
        ip_address = request.remote_addr
        
        # Call controller function
        config = update_system_config(key, config_data.dict(exclude_unset=True), user_id, ip_address)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": config.dict()
        })
    except NotFoundException as e:
        logger.warning(f"Configuration not found for update: {key}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
    except ValidationException as e:
        logger.warning(f"Validation error in update_system_config: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@admin_bp.route('/configs/<string:key>', methods=['DELETE'])
@require_auth
@admin_required
def delete_system_config_route(key):
    """
    Route handler for deleting a system configuration by key.
    
    Path Parameters:
        key (str): The key of the configuration to delete
    
    Returns:
        JSON response with success message
    """
    try:
        # Extract user_id and ip_address from request
        user_id = g.user_id
        ip_address = request.remote_addr
        
        # Call controller function
        result = delete_system_config_by_key(key, user_id, ip_address)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "message": result["message"]
        })
    except NotFoundException as e:
        logger.warning(f"Configuration not found for deletion: {key}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


# Admin Activity Routes

@admin_bp.route('/activities', methods=['GET'])
@require_auth
@admin_required
def get_admin_activities_route():
    """
    Route handler for retrieving admin activities with optional filtering.
    
    Query Parameters:
        user_id (str, optional): Filter by user ID
        action (str, optional): Filter by action type
        resource_type (str, optional): Filter by resource type
        resource_id (str, optional): Filter by resource ID
        start_date (str, optional): Filter by start date (ISO 8601 format)
        end_date (str, optional): Filter by end date (ISO 8601 format)
        skip (int, optional): Number of records to skip for pagination
        limit (int, optional): Maximum number of records to return
    
    Returns:
        JSON response with admin activities
    """
    # Extract query parameters
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    resource_id = request.args.get('resource_id')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    skip = request.args.get('skip', default=0, type=int)
    limit = request.args.get('limit', default=100, type=int)
    
    # Parse date parameters if provided
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid start_date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            }), 400
    
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid end_date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            }), 400
    
    # Call controller function
    activities = get_admin_activities_list(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    # Return JSON response
    return jsonify({
        "success": True,
        "data": [activity.dict() for activity in activities]
    })


@admin_bp.route('/activities', methods=['POST'])
@require_auth
@admin_required
def create_admin_activity_route():
    """
    Route handler for creating a new admin activity log entry.
    
    Request Body:
        AdminActivityCreate schema
    
    Returns:
        JSON response with created admin activity
    """
    try:
        # Parse request data
        data = request.json
        
        # Validate with schema
        activity_data = AdminActivityCreate(**data)
        
        # Extract ip_address from request
        ip_address = request.remote_addr
        
        # Call controller function
        activity = create_admin_activity(activity_data.dict(), ip_address)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": activity.dict()
        }), 201
    except ValidationException as e:
        logger.warning(f"Validation error in create_admin_activity: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# Maintenance Schedule Routes

@admin_bp.route('/maintenance/schedules', methods=['GET'])
@require_auth
@admin_required
def get_maintenance_schedules_route():
    """
    Route handler for retrieving maintenance schedules with optional filtering.
    
    Query Parameters:
        is_active (bool, optional): Filter by active status
        start_date (str, optional): Filter by start date (ISO 8601 format)
        end_date (str, optional): Filter by end date (ISO 8601 format)
        skip (int, optional): Number of records to skip for pagination
        limit (int, optional): Maximum number of records to return
    
    Returns:
        JSON response with maintenance schedules
    """
    # Extract query parameters
    is_active_str = request.args.get('is_active')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    skip = request.args.get('skip', default=0, type=int)
    limit = request.args.get('limit', default=100, type=int)
    
    # Parse boolean parameter if provided
    is_active = None
    if is_active_str is not None:
        is_active = is_active_str.lower() == 'true'
    
    # Parse date parameters if provided
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid start_date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            }), 400
    
    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid end_date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            }), 400
    
    # Call controller function
    schedules = get_maintenance_schedules(
        is_active=is_active,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    # Return JSON response
    return jsonify({
        "success": True,
        "data": [schedule.dict() for schedule in schedules]
    })


@admin_bp.route('/maintenance/schedules/<string:schedule_id>', methods=['GET'])
@require_auth
@admin_required
def get_maintenance_schedule_by_id_route(schedule_id):
    """
    Route handler for retrieving a maintenance schedule by ID.
    
    Path Parameters:
        schedule_id (str): The ID of the maintenance schedule to retrieve
    
    Returns:
        JSON response with maintenance schedule
    """
    try:
        # Call controller function
        schedule = get_maintenance_schedule_by_id(schedule_id)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": schedule.dict()
        })
    except NotFoundException as e:
        logger.warning(f"Maintenance schedule not found: {schedule_id}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


@admin_bp.route('/maintenance/schedules', methods=['POST'])
@require_auth
@admin_required
def create_maintenance_schedule_route():
    """
    Route handler for creating a new maintenance schedule.
    
    Request Body:
        MaintenanceScheduleCreate schema
    
    Returns:
        JSON response with created maintenance schedule
    """
    try:
        # Parse request data
        data = request.json
        
        # Validate with schema
        schedule_data = MaintenanceScheduleCreate(**data)
        
        # Parse date parameters
        start_time = schedule_data.start_time
        end_time = schedule_data.end_time
        
        # Validate that end_time is after start_time
        if end_time <= start_time:
            raise ValidationException("End time must be after start time")
        
        # Extract user_id and ip_address from request
        user_id = g.user_id
        ip_address = request.remote_addr
        
        # Call controller function
        schedule = create_maintenance_schedule_controller(schedule_data.dict(), user_id, ip_address)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": schedule.dict()
        }), 201
    except ValidationException as e:
        logger.warning(f"Validation error in create_maintenance_schedule: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@admin_bp.route('/maintenance/schedules/<string:schedule_id>', methods=['PUT'])
@require_auth
@admin_required
def update_maintenance_schedule_route(schedule_id):
    """
    Route handler for updating an existing maintenance schedule.
    
    Path Parameters:
        schedule_id (str): The ID of the maintenance schedule to update
    
    Request Body:
        MaintenanceScheduleUpdate schema
    
    Returns:
        JSON response with updated maintenance schedule
    """
    try:
        # Parse request data
        data = request.json
        
        # Validate with schema
        schedule_data = MaintenanceScheduleUpdate(**data)
        
        # Parse date parameters if provided
        start_time = getattr(schedule_data, 'start_time', None)
        end_time = getattr(schedule_data, 'end_time', None)
        
        # Validate that end_time is after start_time if both are provided
        if start_time is not None and end_time is not None and end_time <= start_time:
            raise ValidationException("End time must be after start time")
        
        # Extract user_id and ip_address from request
        user_id = g.user_id
        ip_address = request.remote_addr
        
        # Call controller function
        schedule = update_maintenance_schedule_controller(
            schedule_id,
            schedule_data.dict(exclude_unset=True),
            user_id,
            ip_address
        )
        
        # Return JSON response
        return jsonify({
            "success": True,
            "data": schedule.dict()
        })
    except NotFoundException as e:
        logger.warning(f"Maintenance schedule not found for update: {schedule_id}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
    except ValidationException as e:
        logger.warning(f"Validation error in update_maintenance_schedule: {str(e)}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@admin_bp.route('/maintenance/schedules/<string:schedule_id>', methods=['DELETE'])
@require_auth
@admin_required
def delete_maintenance_schedule_route(schedule_id):
    """
    Route handler for deleting a maintenance schedule by ID.
    
    Path Parameters:
        schedule_id (str): The ID of the maintenance schedule to delete
    
    Returns:
        JSON response with success message
    """
    try:
        # Extract user_id and ip_address from request
        user_id = g.user_id
        ip_address = request.remote_addr
        
        # Call controller function
        result = delete_maintenance_schedule_controller(schedule_id, user_id, ip_address)
        
        # Return JSON response
        return jsonify({
            "success": True,
            "message": result["message"]
        })
    except NotFoundException as e:
        logger.warning(f"Maintenance schedule not found for deletion: {schedule_id}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


@admin_bp.route('/maintenance/active', methods=['GET'])
@require_auth
def get_active_maintenance_schedules_route():
    """
    Route handler for retrieving currently active maintenance schedules.
    
    Returns:
        JSON response with active maintenance schedules
    """
    # Call controller function
    schedules = get_active_maintenance_schedules_controller()
    
    # Return JSON response
    return jsonify({
        "success": True,
        "data": [schedule.dict() for schedule in schedules]
    })


@admin_bp.route('/maintenance/status', methods=['GET'])
def check_maintenance_status_route():
    """
    Route handler for checking if the system is currently under maintenance.
    
    Returns:
        JSON response with maintenance status
    """
    # Call controller function
    status = check_system_maintenance_status()
    
    # Return JSON response
    return jsonify({
        "success": True,
        "data": status
    })


# Error handlers for common exceptions

@admin_bp.errorhandler(ValidationException)
def handle_validation_exception(error):
    """
    Error handler for ValidationException.
    
    Args:
        error: The ValidationException instance
    
    Returns:
        tuple: Error response and status code
    """
    logger.warning(f"Validation error: {str(error)}")
    return jsonify({
        "success": False,
        "message": str(error),
        "error_type": "validation_error"
    }), 400


@admin_bp.errorhandler(NotFoundException)
def handle_not_found_exception(error):
    """
    Error handler for NotFoundException.
    
    Args:
        error: The NotFoundException instance
    
    Returns:
        tuple: Error response and status code
    """
    logger.warning(f"Not found error: {str(error)}")
    return jsonify({
        "success": False,
        "message": str(error),
        "error_type": "not_found_error"
    }), 404


@admin_bp.errorhandler(ConfigurationException)
def handle_configuration_exception(error):
    """
    Error handler for ConfigurationException.
    
    Args:
        error: The ConfigurationException instance
    
    Returns:
        tuple: Error response and status code
    """
    logger.error(f"Configuration error: {str(error)}")
    return jsonify({
        "success": False,
        "message": str(error),
        "error_type": "configuration_error"
    }), 500