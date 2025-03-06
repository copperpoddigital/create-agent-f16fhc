# Freight Price Movement Agent API Reference

## Introduction

This document provides a comprehensive reference for the Freight Price Movement Agent API. The API follows RESTful principles and uses JSON for request and response bodies. All API endpoints are versioned and require authentication unless explicitly stated otherwise.

## Base URL

All API endpoints are relative to the base URL: `/api/v1`

## Authentication

The API uses OAuth 2.0 with JWT tokens for authentication. Most endpoints require a valid access token to be included in the Authorization header using the Bearer scheme.

### Authentication Endpoints

#### POST /auth/login

Authenticate a user and obtain access and refresh tokens.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "string",
  "expires_in": 900
}
```

**Status Codes:**
- 200 OK - Authentication successful
- 401 Unauthorized - Invalid credentials

#### POST /auth/refresh

Obtain a new access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "string (required)"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "string",
  "expires_in": 900
}
```

**Status Codes:**
- 200 OK - Token refresh successful
- 401 Unauthorized - Invalid refresh token

#### POST /auth/revoke

Revoke a specific token.

**Authentication:** Required

**Request Body:**
```json
{
  "token": "string (required)",
  "token_type_hint": "string (access_token or refresh_token)"
}
```

**Response:**
```json
{
  "message": "Token successfully revoked"
}
```

**Status Codes:**
- 200 OK - Token revocation successful
- 400 Bad Request - Invalid token

#### POST /auth/logout

Log out the current user and revoke their tokens.

**Authentication:** Required

**Request Body:** None

**Response:**
```json
{
  "message": "Logout successful"
}
```

**Status Codes:**
- 200 OK - Logout successful

#### GET /auth/me

Get information about the currently authenticated user.

**Authentication:** Required

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john.smith",
  "email": "john.smith@example.com",
  "roles": ["analyst", "manager"],
  "last_login": "2023-06-15T09:30:00Z"
}
```

**Status Codes:**
- 200 OK - User information retrieved successfully

#### POST /auth/password/change

Change the current user's password.

**Authentication:** Required

**Request Body:**
```json
{
  "current_password": "string (required)",
  "new_password": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

**Status Codes:**
- 200 OK - Password changed successfully
- 400 Bad Request - Invalid password
- 401 Unauthorized - Current password is incorrect

#### POST /auth/password/reset/request

Request a password reset for a user.

**Request Body:**
```json
{
  "email": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password reset instructions sent if email exists"
}
```

**Status Codes:**
- 200 OK - Password reset request processed

#### POST /auth/password/reset/confirm

Confirm a password reset using a token.

**Request Body:**
```json
{
  "token": "string (required)",
  "new_password": "string (required)"
}
```

**Response:**
```json
{
  "message": "Password reset successful"
}
```

**Status Codes:**
- 200 OK - Password reset successful
- 400 Bad Request - Invalid token or password

#### GET /auth/session

Get information about the current session.

**Authentication:** Required

**Response:**
```json
{
  "session_id": "string",
  "created_at": "2023-06-15T09:30:00Z",
  "expires_at": "2023-06-15T09:45:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
}
```

**Status Codes:**
- 200 OK - Session information retrieved successfully

#### POST /auth/session/terminate

Terminate the current session.

**Authentication:** Required

**Response:**
```json
{
  "message": "Session terminated successfully"
}
```

**Status Codes:**
- 200 OK - Session terminated successfully

#### POST /auth/session/terminate-others

Terminate all other sessions for the current user.

**Authentication:** Required

**Response:**
```json
{
  "message": "Other sessions terminated successfully",
  "terminated_count": 3
}
```

**Status Codes:**
- 200 OK - Other sessions terminated successfully

## Analysis API

The Analysis API provides endpoints for managing time periods, creating and executing analyses, and working with saved analyses.

### Time Period Endpoints

#### GET /analysis/time-periods

List time periods with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Q1 2023",
      "start_date": "2023-01-01",
      "end_date": "2023-03-31",
      "granularity": "weekly",
      "is_custom": false,
      "created_by": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-04-01T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Time periods retrieved successfully

#### POST /analysis/time-periods

Create a new time period.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "string (required)",
  "start_date": "2023-01-01 (required)",
  "end_date": "2023-03-31 (required)",
  "granularity": "weekly (daily, weekly, monthly, custom)",
  "is_custom": false,
  "custom_interval": "string (only if is_custom is true)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "weekly",
  "is_custom": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-04-01T10:00:00Z"
}
```

**Status Codes:**
- 201 Created - Time period created successfully
- 400 Bad Request - Invalid time period data

#### GET /analysis/time-periods/{time_period_id}

Get a specific time period by ID.

**Authentication:** Required

**Path Parameters:**
- `time_period_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "weekly",
  "is_custom": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-04-01T10:00:00Z"
}
```

**Status Codes:**
- 200 OK - Time period retrieved successfully
- 404 Not Found - Time period not found

#### PUT /analysis/time-periods/{time_period_id}

Update a specific time period.

**Authentication:** Required

**Path Parameters:**
- `time_period_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "string",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "weekly (daily, weekly, monthly, custom)",
  "is_custom": false,
  "custom_interval": "string (only if is_custom is true)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 2023 Updated",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "weekly",
  "is_custom": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-04-01T10:00:00Z",
  "updated_at": "2023-04-05T11:30:00Z"
}
```

**Status Codes:**
- 200 OK - Time period updated successfully
- 400 Bad Request - Invalid time period data
- 404 Not Found - Time period not found

#### DELETE /analysis/time-periods/{time_period_id}

Delete a specific time period.

**Authentication:** Required

**Path Parameters:**
- `time_period_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Time period deleted successfully"
}
```

**Status Codes:**
- 200 OK - Time period deleted successfully
- 404 Not Found - Time period not found

### Analysis Request Endpoints

#### GET /analysis/requests

List analysis requests with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `status`: string (pending, running, completed, failed)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
      "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
      "filters": {
        "origins": ["Shanghai"],
        "destinations": ["Rotterdam"],
        "carriers": ["MAERSK"]
      },
      "options": {
        "calculate_absolute_change": true,
        "calculate_percentage_change": true,
        "identify_trend_direction": true
      },
      "output_format": "json",
      "status": "completed",
      "created_by": "550e8400-e29b-41d4-a716-446655440003",
      "created_at": "2023-06-15T14:30:00Z",
      "completed_at": "2023-06-15T14:32:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Analysis requests retrieved successfully

#### POST /analysis/requests

Create a new analysis request.

**Authentication:** Required

**Request Body:**
```json
{
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false,
    "baseline_period_id": "550e8400-e29b-41d4-a716-446655440003"
  },
  "output_format": "json (json, csv, text)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json",
  "status": "pending",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Analysis request created successfully
- 400 Bad Request - Invalid analysis request data

#### GET /analysis/requests/{analysis_id}

Get a specific analysis request by ID.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json",
  "status": "completed",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z",
  "completed_at": "2023-06-15T14:32:00Z"
}
```

**Status Codes:**
- 200 OK - Analysis request retrieved successfully
- 404 Not Found - Analysis request not found

#### DELETE /analysis/requests/{analysis_id}

Delete a specific analysis request.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Analysis request deleted successfully"
}
```

**Status Codes:**
- 200 OK - Analysis request deleted successfully
- 404 Not Found - Analysis request not found

#### POST /analysis/requests/{analysis_id}/execute

Execute a price movement analysis for the specified analysis request.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "metadata": {
    "time_period": {
      "start_date": "2023-01-01",
      "end_date": "2023-03-31",
      "granularity": "weekly"
    },
    "filters": {
      "origins": ["Shanghai"],
      "destinations": ["Rotterdam"],
      "carriers": ["MAERSK"],
      "modes": ["ocean"]
    },
    "generated_at": "2023-06-15T14:32:00Z"
  },
  "results": {
    "absolute_change": {
      "value": 245.00,
      "unit": "USD"
    },
    "percentage_change": {
      "value": 5.2,
      "formatted": "+5.2%"
    },
    "trend": {
      "direction": "increasing",
      "indicator": "↑"
    },
    "aggregates": {
      "start_period": {
        "average": 4120.00,
        "minimum": 4050.00,
        "maximum": 4200.00
      },
      "end_period": {
        "average": 4365.00,
        "minimum": 4300.00,
        "maximum": 4450.00
      }
    }
  },
  "time_series": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "value": 4120.00
    },
    {
      "timestamp": "2023-01-08T00:00:00Z",
      "value": 4150.00
    }
  ]
}
```

**Status Codes:**
- 200 OK - Analysis executed successfully
- 404 Not Found - Analysis request not found
- 400 Bad Request - Invalid analysis parameters

#### GET /analysis/requests/{analysis_id}/results

Retrieve the results of a completed analysis.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Query Parameters:**
- `format`: string (json, csv, text)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "metadata": {
    "time_period": {
      "start_date": "2023-01-01",
      "end_date": "2023-03-31",
      "granularity": "weekly"
    },
    "filters": {
      "origins": ["Shanghai"],
      "destinations": ["Rotterdam"],
      "carriers": ["MAERSK"],
      "modes": ["ocean"]
    },
    "generated_at": "2023-06-15T14:32:00Z"
  },
  "results": {
    "absolute_change": {
      "value": 245.00,
      "unit": "USD"
    },
    "percentage_change": {
      "value": 5.2,
      "formatted": "+5.2%"
    },
    "trend": {
      "direction": "increasing",
      "indicator": "↑"
    },
    "aggregates": {
      "start_period": {
        "average": 4120.00,
        "minimum": 4050.00,
        "maximum": 4200.00
      },
      "end_period": {
        "average": 4365.00,
        "minimum": 4300.00,
        "maximum": 4450.00
      }
    }
  },
  "time_series": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "value": 4120.00
    },
    {
      "timestamp": "2023-01-08T00:00:00Z",
      "value": 4150.00
    }
  ]
}
```

**Status Codes:**
- 200 OK - Analysis results retrieved successfully
- 404 Not Found - Analysis request not found
- 400 Bad Request - Analysis not completed yet

#### POST /analysis/requests/{analysis_id}/cancel

Cancel an in-progress analysis.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Analysis cancelled successfully"
}
```

**Status Codes:**
- 200 OK - Analysis cancelled successfully
- 404 Not Found - Analysis request not found
- 400 Bad Request - Analysis not in progress

#### POST /analysis/requests/{analysis_id}/rerun

Re-execute a previously completed or failed analysis.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Analysis rerun initiated successfully"
}
```

**Status Codes:**
- 200 OK - Analysis rerun initiated successfully
- 404 Not Found - Analysis request not found

#### GET /analysis/requests/{analysis_id}/status

Check the current status of an analysis request.

**Authentication:** Required

**Path Parameters:**
- `analysis_id`: string (UUID, required)

**Response:**
```json
{
  "status": "running",
  "progress": 65,
  "message": "Processing week 6 of 12",
  "started_at": "2023-06-15T14:30:00Z",
  "completed_at": null
}
```

**Status Codes:**
- 200 OK - Analysis status retrieved successfully
- 404 Not Found - Analysis request not found

### Saved Analysis Endpoints

#### GET /analysis/saved

List saved analyses with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `name`: string

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Quarterly Ocean Rates",
      "description": "Analysis of ocean freight rates by quarter",
      "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
      "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
      "filters": {
        "modes": ["ocean"]
      },
      "created_by": "550e8400-e29b-41d4-a716-446655440003",
      "created_at": "2023-06-15T14:30:00Z",
      "last_run_at": "2023-06-15T14:32:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Saved analyses retrieved successfully

#### POST /analysis/saved

Create a new saved analysis configuration.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Quarterly Ocean Rates (required)",
  "description": "Analysis of ocean freight rates by quarter",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false,
    "baseline_period_id": "550e8400-e29b-41d4-a716-446655440003"
  },
  "output_format": "json (json, csv, text)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Quarterly Ocean Rates",
  "description": "Analysis of ocean freight rates by quarter",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Saved analysis created successfully
- 400 Bad Request - Invalid saved analysis data

#### GET /analysis/saved/{saved_analysis_id}

Get a specific saved analysis by ID.

**Authentication:** Required

**Path Parameters:**
- `saved_analysis_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Quarterly Ocean Rates",
  "description": "Analysis of ocean freight rates by quarter",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z",
  "last_run_at": "2023-06-15T14:32:00Z"
}
```

**Status Codes:**
- 200 OK - Saved analysis retrieved successfully
- 404 Not Found - Saved analysis not found

#### PUT /analysis/saved/{saved_analysis_id}

Update a specific saved analysis.

**Authentication:** Required

**Path Parameters:**
- `saved_analysis_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Quarterly Ocean Rates Updated",
  "description": "Updated analysis of ocean freight rates by quarter",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam", "Hamburg"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Quarterly Ocean Rates Updated",
  "description": "Updated analysis of ocean freight rates by quarter",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": ["550e8400-e29b-41d4-a716-446655440002"],
  "filters": {
    "origins": ["Shanghai"],
    "destinations": ["Rotterdam", "Hamburg"],
    "carriers": ["MAERSK"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T10:15:00Z",
  "last_run_at": "2023-06-15T14:32:00Z"
}
```

**Status Codes:**
- 200 OK - Saved analysis updated successfully
- 400 Bad Request - Invalid saved analysis data
- 404 Not Found - Saved analysis not found

#### DELETE /analysis/saved/{saved_analysis_id}

Delete a specific saved analysis.

**Authentication:** Required

**Path Parameters:**
- `saved_analysis_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Saved analysis deleted successfully"
}
```

**Status Codes:**
- 200 OK - Saved analysis deleted successfully
- 404 Not Found - Saved analysis not found

#### POST /analysis/saved/{saved_analysis_id}/run

Execute a price movement analysis using a saved analysis configuration.

**Authentication:** Required

**Path Parameters:**
- `saved_analysis_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "metadata": {
    "time_period": {
      "start_date": "2023-01-01",
      "end_date": "2023-03-31",
      "granularity": "weekly"
    },
    "filters": {
      "origins": ["Shanghai"],
      "destinations": ["Rotterdam", "Hamburg"],
      "carriers": ["MAERSK"],
      "modes": ["ocean"]
    },
    "generated_at": "2023-06-16T10:20:00Z"
  },
  "results": {
    "absolute_change": {
      "value": 245.00,
      "unit": "USD"
    },
    "percentage_change": {
      "value": 5.2,
      "formatted": "+5.2%"
    },
    "trend": {
      "direction": "increasing",
      "indicator": "↑"
    },
    "aggregates": {
      "start_period": {
        "average": 4120.00,
        "minimum": 4050.00,
        "maximum": 4200.00
      },
      "end_period": {
        "average": 4365.00,
        "minimum": 4300.00,
        "maximum": 4450.00
      }
    }
  },
  "time_series": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "value": 4120.00
    },
    {
      "timestamp": "2023-01-08T00:00:00Z",
      "value": 4150.00
    }
  ]
}
```

**Status Codes:**
- 200 OK - Analysis executed successfully
- 404 Not Found - Saved analysis not found
- 400 Bad Request - Invalid analysis parameters

### Analysis Schedule Endpoints

#### GET /analysis/schedules

List analysis schedules with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `is_active`: boolean

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Weekly Ocean Analysis",
      "description": "Run ocean analysis every Monday",
      "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
      "schedule": "0 9 * * 1",
      "is_active": true,
      "notification_email": "john.smith@example.com",
      "created_by": "550e8400-e29b-41d4-a716-446655440002",
      "created_at": "2023-06-15T14:30:00Z",
      "next_run_at": "2023-06-19T09:00:00Z",
      "last_run_at": "2023-06-12T09:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Analysis schedules retrieved successfully

#### POST /analysis/schedules

Create a new analysis schedule.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Weekly Ocean Analysis (required)",
  "description": "Run ocean analysis every Monday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "schedule": "0 9 * * 1 (cron expression, required)",
  "is_active": true,
  "notification_email": "john.smith@example.com"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Ocean Analysis",
  "description": "Run ocean analysis every Monday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 1",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "next_run_at": "2023-06-19T09:00:00Z"
}
```

**Status Codes:**
- 201 Created - Analysis schedule created successfully
- 400 Bad Request - Invalid analysis schedule data

#### GET /analysis/schedules/{schedule_id}

Get a specific analysis schedule by ID.

**Authentication:** Required

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Ocean Analysis",
  "description": "Run ocean analysis every Monday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 1",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "next_run_at": "2023-06-19T09:00:00Z",
  "last_run_at": "2023-06-12T09:00:00Z"
}
```

**Status Codes:**
- 200 OK - Analysis schedule retrieved successfully
- 404 Not Found - Analysis schedule not found

#### PUT /analysis/schedules/{schedule_id}

Update a specific analysis schedule.

**Authentication:** Required

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Weekly Ocean Analysis Updated",
  "description": "Run ocean analysis every Tuesday instead",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 2",
  "is_active": true,
  "notification_email": "john.smith@example.com"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Ocean Analysis Updated",
  "description": "Run ocean analysis every Tuesday instead",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 2",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T10:45:00Z",
  "next_run_at": "2023-06-20T09:00:00Z",
  "last_run_at": "2023-06-12T09:00:00Z"
}
```

**Status Codes:**
- 200 OK - Analysis schedule updated successfully
- 400 Bad Request - Invalid analysis schedule data
- 404 Not Found - Analysis schedule not found

#### DELETE /analysis/schedules/{schedule_id}

Delete a specific analysis schedule.

**Authentication:** Required

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Analysis schedule deleted successfully"
}
```

**Status Codes:**
- 200 OK - Analysis schedule deleted successfully
- 404 Not Found - Analysis schedule not found

#### POST /analysis/schedules/{schedule_id}/activate

Activate an analysis schedule.

**Authentication:** Required

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Ocean Analysis",
  "description": "Run ocean analysis every Tuesday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 2",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T11:00:00Z",
  "next_run_at": "2023-06-20T09:00:00Z",
  "last_run_at": "2023-06-12T09:00:00Z"
}
```

**Status Codes:**
- 200 OK - Analysis schedule activated successfully
- 404 Not Found - Analysis schedule not found

#### POST /analysis/schedules/{schedule_id}/deactivate

Deactivate an analysis schedule.

**Authentication:** Required

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Ocean Analysis",
  "description": "Run ocean analysis every Tuesday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 2",
  "is_active": false,
  "notification_email": "john.smith@example.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T11:15:00Z",
  "next_run_at": null,
  "last_run_at": "2023-06-12T09:00:00Z"
}
```

**Status Codes:**
- 200 OK - Analysis schedule deactivated successfully
- 404 Not Found - Analysis schedule not found

## Data Sources API

The Data Sources API provides endpoints for managing data sources for freight pricing data.

### Data Source Endpoints

#### GET /data-sources

List data sources with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `type`: string (csv, database, api, tms, erp)
- `status`: string (active, inactive)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "TMS Export",
      "description": "Daily export from transportation management system",
      "type": "csv",
      "status": "active",
      "created_by": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-06-15T14:30:00Z",
      "last_updated_at": "2023-06-15T14:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Data sources retrieved successfully

#### GET /data-sources/{data_source_id}

Get a specific data source by ID.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export",
  "description": "Daily export from transportation management system",
  "type": "csv",
  "config": {
    "file_path": "/exports/tms/daily.csv",
    "delimiter": ",",
    "has_header": true,
    "date_format": "YYYY-MM-DD",
    "field_mapping": {
      "freight_charge": "price",
      "currency": "currency_code",
      "origin": "origin",
      "destination": "destination",
      "date": "quote_date"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 200 OK - Data source retrieved successfully
- 404 Not Found - Data source not found

#### POST /data-sources

Create a new generic data source.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "TMS Export (required)",
  "description": "Daily export from transportation management system",
  "type": "csv (required, one of: csv, database, api, tms, erp)",
  "status": "active (active, inactive)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export",
  "description": "Daily export from transportation management system",
  "type": "csv",
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Data source created successfully
- 400 Bad Request - Invalid data source data

#### PUT /data-sources/{data_source_id}

Update a specific data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "TMS Export Updated",
  "description": "Updated daily export from transportation management system",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export Updated",
  "description": "Updated daily export from transportation management system",
  "type": "csv",
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T11:30:00Z"
}
```

**Status Codes:**
- 200 OK - Data source updated successfully
- 400 Bad Request - Invalid data source data
- 404 Not Found - Data source not found

#### DELETE /data-sources/{data_source_id}

Delete a specific data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Data source deleted successfully"
}
```

**Status Codes:**
- 200 OK - Data source deleted successfully
- 404 Not Found - Data source not found

#### POST /data-sources/test-connection

Test the connection to a data source.

**Authentication:** Required

**Request Body:**
```json
{
  "data_source_id": "550e8400-e29b-41d4-a716-446655440000",
  "connection_params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "details": {
    "connection_time": "125ms",
    "record_count": 1000
  }
}
```

**Status Codes:**
- 200 OK - Connection test completed

#### POST /data-sources/{data_source_id}/activate

Activate a data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export",
  "description": "Daily export from transportation management system",
  "type": "csv",
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T11:45:00Z"
}
```

**Status Codes:**
- 200 OK - Data source activated successfully
- 404 Not Found - Data source not found

#### POST /data-sources/{data_source_id}/deactivate

Deactivate a data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export",
  "description": "Daily export from transportation management system",
  "type": "csv",
  "status": "inactive",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T12:00:00Z"
}
```

**Status Codes:**
- 200 OK - Data source deactivated successfully
- 404 Not Found - Data source not found

#### GET /data-sources/{data_source_id}/logs

Get logs for a specific data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "data_source_id": "550e8400-e29b-41d4-a716-446655440001",
      "timestamp": "2023-06-15T14:35:00Z",
      "level": "info",
      "message": "Data source processed 1,000 records successfully",
      "details": {
        "record_count": 1000,
        "process_time": "5s"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Data source logs retrieved successfully
- 404 Not Found - Data source not found

### CSV Data Source Endpoints

#### POST /data-sources/csv

Create a new CSV data source.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "TMS Export (required)",
  "description": "Daily export from transportation management system",
  "file_path": "/exports/tms/daily.csv (required)",
  "delimiter": ",",
  "has_header": true,
  "date_format": "YYYY-MM-DD",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency_code",
    "origin": "origin",
    "destination": "destination",
    "date": "quote_date"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export",
  "description": "Daily export from transportation management system",
  "type": "csv",
  "config": {
    "file_path": "/exports/tms/daily.csv",
    "delimiter": ",",
    "has_header": true,
    "date_format": "YYYY-MM-DD",
    "field_mapping": {
      "freight_charge": "price",
      "currency": "currency_code",
      "origin": "origin",
      "destination": "destination",
      "date": "quote_date"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - CSV data source created successfully
- 400 Bad Request - Invalid CSV data source data

#### PUT /data-sources/csv/{data_source_id}

Update a specific CSV data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "TMS Export Updated",
  "description": "Updated daily export from transportation management system",
  "file_path": "/exports/tms/updated_daily.csv",
  "delimiter": ",",
  "has_header": true,
  "date_format": "YYYY-MM-DD",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency_code",
    "origin": "origin_code",
    "destination": "destination_code",
    "date": "quote_date"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "TMS Export Updated",
  "description": "Updated daily export from transportation management system",
  "type": "csv",
  "config": {
    "file_path": "/exports/tms/updated_daily.csv",
    "delimiter": ",",
    "has_header": true,
    "date_format": "YYYY-MM-DD",
    "field_mapping": {
      "freight_charge": "price",
      "currency": "currency_code",
      "origin": "origin_code",
      "destination": "destination_code",
      "date": "quote_date"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T12:15:00Z"
}
```

**Status Codes:**
- 200 OK - CSV data source updated successfully
- 400 Bad Request - Invalid CSV data source data
- 404 Not Found - CSV data source not found

### Database Data Source Endpoints

#### POST /data-sources/database

Create a new database data source.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "ERP Database (required)",
  "description": "Connection to ERP database",
  "connection_string": "postgresql://username:password@host:port/database (required)",
  "query": "SELECT * FROM freight_rates WHERE date >= :start_date (required)",
  "field_mapping": {
    "freight_charge": "rate",
    "currency": "currency",
    "origin": "origin_location",
    "destination": "destination_location",
    "date": "rate_date"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ERP Database",
  "description": "Connection to ERP database",
  "type": "database",
  "config": {
    "connection_string": "postgresql://username:***@host:port/database",
    "query": "SELECT * FROM freight_rates WHERE date >= :start_date",
    "field_mapping": {
      "freight_charge": "rate",
      "currency": "currency",
      "origin": "origin_location",
      "destination": "destination_location",
      "date": "rate_date"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Database data source created successfully
- 400 Bad Request - Invalid database data source data

#### PUT /data-sources/database/{data_source_id}

Update a specific database data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "ERP Database Updated",
  "description": "Updated connection to ERP database",
  "connection_string": "postgresql://username:password@host:port/database",
  "query": "SELECT * FROM freight_rates WHERE date >= :start_date AND carrier = :carrier",
  "field_mapping": {
    "freight_charge": "rate",
    "currency": "currency",
    "origin": "origin_location",
    "destination": "destination_location",
    "date": "rate_date"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ERP Database Updated",
  "description": "Updated connection to ERP database",
  "type": "database",
  "config": {
    "connection_string": "postgresql://username:***@host:port/database",
    "query": "SELECT * FROM freight_rates WHERE date >= :start_date AND carrier = :carrier",
    "field_mapping": {
      "freight_charge": "rate",
      "currency": "currency",
      "origin": "origin_location",
      "destination": "destination_location",
      "date": "rate_date"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T12:30:00Z"
}
```

**Status Codes:**
- 200 OK - Database data source updated successfully
- 400 Bad Request - Invalid database data source data
- 404 Not Found - Database data source not found

### API Data Source Endpoints

#### POST /data-sources/api

Create a new API data source.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Rate API (required)",
  "description": "Connection to external rate API",
  "url": "https://api.example.com/rates (required)",
  "method": "GET (required)",
  "headers": {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
  },
  "body": {
    "query": "query GetRates($startDate: String!) { rates(startDate: $startDate) { ... } }"
  },
  "auth_type": "bearer",
  "auth_credentials": {
    "token": "your-bearer-token"
  },
  "response_path": "data.rates",
  "field_mapping": {
    "freight_charge": "amount",
    "currency": "currencyCode",
    "origin": "originPort",
    "destination": "destinationPort",
    "date": "effectiveDate"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Rate API",
  "description": "Connection to external rate API",
  "type": "api",
  "config": {
    "url": "https://api.example.com/rates",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer ***",
      "Content-Type": "application/json"
    },
    "body": {
      "query": "query GetRates($startDate: String!) { rates(startDate: $startDate) { ... } }"
    },
    "auth_type": "bearer",
    "auth_credentials": {
      "token": "***"
    },
    "response_path": "data.rates",
    "field_mapping": {
      "freight_charge": "amount",
      "currency": "currencyCode",
      "origin": "originPort",
      "destination": "destinationPort",
      "date": "effectiveDate"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - API data source created successfully
- 400 Bad Request - Invalid API data source data

#### PUT /data-sources/api/{data_source_id}

Update a specific API data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Rate API Updated",
  "description": "Updated connection to external rate API",
  "url": "https://api.example.com/v2/rates",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer updated-token",
    "Content-Type": "application/json"
  },
  "body": {
    "query": "query GetRates($startDate: String!, $carrier: String) { rates(startDate: $startDate, carrier: $carrier) { ... } }"
  },
  "auth_type": "bearer",
  "auth_credentials": {
    "token": "updated-bearer-token"
  },
  "response_path": "data.rates",
  "field_mapping": {
    "freight_charge": "amount",
    "currency": "currencyCode",
    "origin": "originPort",
    "destination": "destinationPort",
    "date": "effectiveDate",
    "carrier": "carrierCode"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Rate API Updated",
  "description": "Updated connection to external rate API",
  "type": "api",
  "config": {
    "url": "https://api.example.com/v2/rates",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer ***",
      "Content-Type": "application/json"
    },
    "body": {
      "query": "query GetRates($startDate: String!, $carrier: String) { rates(startDate: $startDate, carrier: $carrier) { ... } }"
    },
    "auth_type": "bearer",
    "auth_credentials": {
      "token": "***"
    },
    "response_path": "data.rates",
    "field_mapping": {
      "freight_charge": "amount",
      "currency": "currencyCode",
      "origin": "originPort",
      "destination": "destinationPort",
      "date": "effectiveDate",
      "carrier": "carrierCode"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T12:45:00Z"
}
```

**Status Codes:**
- 200 OK - API data source updated successfully
- 400 Bad Request - Invalid API data source data
- 404 Not Found - API data source not found

### TMS Data Source Endpoints

#### POST /data-sources/tms

Create a new TMS data source.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "SAP TMS (required)",
  "description": "Connection to SAP Transportation Management System",
  "tms_type": "sap (required)",
  "connection_params": {
    "url": "https://sap-tms.example.com",
    "username": "api_user",
    "password": "password",
    "client": "100"
  },
  "field_mapping": {
    "freight_charge": "NETVAL",
    "currency": "CURRCY",
    "origin": "ORIGIN",
    "destination": "DESTIN",
    "date": "CREDAT"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "SAP TMS",
  "description": "Connection to SAP Transportation Management System",
  "type": "tms",
  "config": {
    "tms_type": "sap",
    "connection_params": {
      "url": "https://sap-tms.example.com",
      "username": "api_user",
      "password": "***",
      "client": "100"
    },
    "field_mapping": {
      "freight_charge": "NETVAL",
      "currency": "CURRCY",
      "origin": "ORIGIN",
      "destination": "DESTIN",
      "date": "CREDAT"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - TMS data source created successfully
- 400 Bad Request - Invalid TMS data source data

#### PUT /data-sources/tms/{data_source_id}

Update a specific TMS data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "SAP TMS Updated",
  "description": "Updated connection to SAP Transportation Management System",
  "tms_type": "sap",
  "connection_params": {
    "url": "https://sap-tms-new.example.com",
    "username": "api_user_updated",
    "password": "updated_password",
    "client": "200"
  },
  "field_mapping": {
    "freight_charge": "NETVAL",
    "currency": "CURRCY",
    "origin": "ORIGIN",
    "destination": "DESTIN",
    "date": "CREDAT",
    "carrier": "CARRIER"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "SAP TMS Updated",
  "description": "Updated connection to SAP Transportation Management System",
  "type": "tms",
  "config": {
    "tms_type": "sap",
    "connection_params": {
      "url": "https://sap-tms-new.example.com",
      "username": "api_user_updated",
      "password": "***",
      "client": "200"
    },
    "field_mapping": {
      "freight_charge": "NETVAL",
      "currency": "CURRCY",
      "origin": "ORIGIN",
      "destination": "DESTIN",
      "date": "CREDAT",
      "carrier": "CARRIER"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T13:00:00Z"
}
```

**Status Codes:**
- 200 OK - TMS data source updated successfully
- 400 Bad Request - Invalid TMS data source data
- 404 Not Found - TMS data source not found

### ERP Data Source Endpoints

#### POST /data-sources/erp

Create a new ERP data source.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "SAP ERP (required)",
  "description": "Connection to SAP ERP System",
  "erp_type": "sap (required)",
  "connection_params": {
    "url": "https://sap-erp.example.com",
    "username": "api_user",
    "password": "password",
    "client": "100",
    "system_id": "ERP"
  },
  "field_mapping": {
    "freight_charge": "DMBTR",
    "currency": "WAERS",
    "origin": "REGIO",
    "destination": "REGIO_DEST",
    "date": "BUDAT"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "SAP ERP",
  "description": "Connection to SAP ERP System",
  "type": "erp",
  "config": {
    "erp_type": "sap",
    "connection_params": {
      "url": "https://sap-erp.example.com",
      "username": "api_user",
      "password": "***",
      "client": "100",
      "system_id": "ERP"
    },
    "field_mapping": {
      "freight_charge": "DMBTR",
      "currency": "WAERS",
      "origin": "REGIO",
      "destination": "REGIO_DEST",
      "date": "BUDAT"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - ERP data source created successfully
- 400 Bad Request - Invalid ERP data source data

#### PUT /data-sources/erp/{data_source_id}

Update a specific ERP data source.

**Authentication:** Required

**Path Parameters:**
- `data_source_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "SAP ERP Updated",
  "description": "Updated connection to SAP ERP System",
  "erp_type": "sap",
  "connection_params": {
    "url": "https://sap-erp-new.example.com",
    "username": "api_user_updated",
    "password": "updated_password",
    "client": "200",
    "system_id": "ERP"
  },
  "field_mapping": {
    "freight_charge": "DMBTR",
    "currency": "WAERS",
    "origin": "REGIO",
    "destination": "REGIO_DEST",
    "date": "BUDAT",
    "carrier": "LIFNR"
  },
  "status": "active"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "SAP ERP Updated",
  "description": "Updated connection to SAP ERP System",
  "type": "erp",
  "config": {
    "erp_type": "sap",
    "connection_params": {
      "url": "https://sap-erp-new.example.com",
      "username": "api_user_updated",
      "password": "***",
      "client": "200",
      "system_id": "ERP"
    },
    "field_mapping": {
      "freight_charge": "DMBTR",
      "currency": "WAERS",
      "origin": "REGIO",
      "destination": "REGIO_DEST",
      "date": "BUDAT",
      "carrier": "LIFNR"
    }
  },
  "status": "active",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "last_updated_at": "2023-06-16T13:15:00Z"
}
```

**Status Codes:**
- 200 OK - ERP data source updated successfully
- 400 Bad Request - Invalid ERP data source data
- 404 Not Found - ERP data source not found

## Reports API

The Reports API provides endpoints for managing reports, report templates, scheduled reports, and report sharing.

### Report Endpoints

#### GET /reports

List reports with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `name`: string

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Q1 Ocean Rates",
      "description": "Ocean freight rates for Q1 2023",
      "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
      "format": "pdf",
      "created_by": "550e8400-e29b-41d4-a716-446655440002",
      "created_at": "2023-06-15T14:30:00Z",
      "last_run_at": "2023-06-15T14:35:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Reports retrieved successfully

#### POST /reports

Create a new report.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Q1 Ocean Rates (required)",
  "description": "Ocean freight rates for Q1 2023",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 5
  },
  "filters": {
    "modes": ["ocean"],
    "minimum_change": 1.0
  },
  "format": "pdf"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 Ocean Rates",
  "description": "Ocean freight rates for Q1 2023",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 5
  },
  "filters": {
    "modes": ["ocean"],
    "minimum_change": 1.0
  },
  "format": "pdf",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Report created successfully
- 400 Bad Request - Invalid report data

#### GET /reports/{report_id}

Get a specific report by ID.

**Authentication:** Required

**Path Parameters:**
- `report_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 Ocean Rates",
  "description": "Ocean freight rates for Q1 2023",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 5
  },
  "filters": {
    "modes": ["ocean"],
    "minimum_change": 1.0
  },
  "format": "pdf",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "last_run_at": "2023-06-15T14:35:00Z"
}
```

**Status Codes:**
- 200 OK - Report retrieved successfully
- 404 Not Found - Report not found

#### PUT /reports/{report_id}

Update a specific report.

**Authentication:** Required

**Path Parameters:**
- `report_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Q1 Ocean Rates Updated",
  "description": "Updated ocean freight rates for Q1 2023",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 3
  },
  "filters": {
    "modes": ["ocean"],
    "carriers": ["MAERSK", "MSC"],
    "minimum_change": 1.0
  },
  "format": "excel"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 Ocean Rates Updated",
  "description": "Updated ocean freight rates for Q1 2023",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 3
  },
  "filters": {
    "modes": ["ocean"],
    "carriers": ["MAERSK", "MSC"],
    "minimum_change": 1.0
  },
  "format": "excel",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T13:30:00Z",
  "last_run_at": "2023-06-15T14:35:00Z"
}
```

**Status Codes:**
- 200 OK - Report updated successfully
- 400 Bad Request - Invalid report data
- 404 Not Found - Report not found

#### DELETE /reports/{report_id}

Delete a specific report.

**Authentication:** Required

**Path Parameters:**
- `report_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Report deleted successfully"
}
```

**Status Codes:**
- 200 OK - Report deleted successfully
- 404 Not Found - Report not found

#### POST /reports/{report_id}/run

Execute a report and generate results.

**Authentication:** Required

**Path Parameters:**
- `report_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "execution_time": "5s",
  "result_url": "/api/v1/reports/executions/550e8400-e29b-41d4-a716-446655440000/download",
  "executed_by": "550e8400-e29b-41d4-a716-446655440002",
  "executed_at": "2023-06-16T13:45:00Z"
}
```

**Status Codes:**
- 200 OK - Report executed successfully
- 404 Not Found - Report not found
- 400 Bad Request - Invalid report parameters

#### POST /reports/{report_id}/duplicate

Create a duplicate of an existing report.

**Authentication:** Required

**Path Parameters:**
- `report_id`: string (UUID, required)

**Query Parameters:**
- `new_name`: string (required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "Q1 Ocean Rates - Copy",
  "description": "Updated ocean freight rates for Q1 2023",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440001",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 3
  },
  "filters": {
    "modes": ["ocean"],
    "carriers": ["MAERSK", "MSC"],
    "minimum_change": 1.0
  },
  "format": "excel",
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-16T14:00:00Z"
}
```

**Status Codes:**
- 200 OK - Report duplicated successfully
- 404 Not Found - Report not found

### Report Template Endpoints

#### GET /reports/templates

List report templates with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `include_public`: boolean (default: true)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Standard Rate Analysis",
      "description": "Standard template for rate analysis",
      "parameters": {
        "include_charts": true,
        "highlight_threshold": 5
      },
      "filters": {},
      "format": "pdf",
      "is_public": true,
      "created_by": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-06-15T14:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Report templates retrieved successfully

#### POST /reports/templates

Create a new report template.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Standard Rate Analysis (required)",
  "description": "Standard template for rate analysis",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 5
  },
  "filters": {
    "minimum_change": 1.0
  },
  "format": "pdf",
  "is_public": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Standard Rate Analysis",
  "description": "Standard template for rate analysis",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 5
  },
  "filters": {
    "minimum_change": 1.0
  },
  "format": "pdf",
  "is_public": true,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Report template created successfully
- 400 Bad Request - Invalid report template data

#### GET /reports/templates/{template_id}

Get a specific report template by ID.

**Authentication:** Required

**Path Parameters:**
- `template_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Standard Rate Analysis",
  "description": "Standard template for rate analysis",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 5
  },
  "filters": {
    "minimum_change": 1.0
  },
  "format": "pdf",
  "is_public": true,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 200 OK - Report template retrieved successfully
- 404 Not Found - Report template not found

#### PUT /reports/templates/{template_id}

Update a specific report template.

**Authentication:** Required

**Path Parameters:**
- `template_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Standard Rate Analysis Updated",
  "description": "Updated standard template for rate analysis",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 3,
    "include_summary": true
  },
  "filters": {
    "minimum_change": 1.0,
    "show_only_increases": false
  },
  "format": "excel",
  "is_public": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Standard Rate Analysis Updated",
  "description": "Updated standard template for rate analysis",
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 3,
    "include_summary": true
  },
  "filters": {
    "minimum_change": 1.0,
    "show_only_increases": false
  },
  "format": "excel",
  "is_public": true,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T14:15:00Z"
}
```

**Status Codes:**
- 200 OK - Report template updated successfully
- 400 Bad Request - Invalid report template data
- 404 Not Found - Report template not found

#### DELETE /reports/templates/{template_id}

Delete a specific report template.

**Authentication:** Required

**Path Parameters:**
- `template_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Report template deleted successfully"
}
```

**Status Codes:**
- 200 OK - Report template deleted successfully
- 404 Not Found - Report template not found

#### POST /reports/templates/{template_id}/create-report

Create a new report from a template.

**Authentication:** Required

**Path Parameters:**
- `template_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Q2 Rate Analysis (required)",
  "parameters_override": {
    "highlight_threshold": 2
  },
  "filters_override": {
    "modes": ["ocean"],
    "minimum_change": 2.0
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q2 Rate Analysis",
  "description": "Updated standard template for rate analysis",
  "analysis_id": null,
  "parameters": {
    "include_charts": true,
    "highlight_threshold": 2,
    "include_summary": true
  },
  "filters": {
    "modes": ["ocean"],
    "minimum_change": 2.0,
    "show_only_increases": false
  },
  "format": "excel",
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-16T14:30:00Z"
}
```

**Status Codes:**
- 200 OK - Report created from template successfully
- 404 Not Found - Report template not found
- 400 Bad Request - Invalid parameters

### Scheduled Report Endpoints

#### GET /reports/scheduled

List scheduled reports with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `is_active`: boolean

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Weekly Rate Report",
      "description": "Weekly report on rate changes",
      "report_id": "550e8400-e29b-41d4-a716-446655440001",
      "schedule": "0 9 * * 1",
      "is_active": true,
      "notification_email": "john.smith@example.com",
      "delivery_options": {
        "email": true,
        "storage": true
      },
      "created_by": "550e8400-e29b-41d4-a716-446655440002",
      "created_at": "2023-06-15T14:30:00Z",
      "next_run_at": "2023-06-19T09:00:00Z",
      "last_run_at": "2023-06-12T09:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Scheduled reports retrieved successfully

#### POST /reports/scheduled

Create a new scheduled report.

**Authentication:** Required

**Request Body:**
```json
{
  "name": "Weekly Rate Report (required)",
  "description": "Weekly report on rate changes",
  "report_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "schedule": "0 9 * * 1 (cron expression, required)",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "delivery_options": {
    "email": true,
    "storage": true
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Rate Report",
  "description": "Weekly report on rate changes",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 1",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "delivery_options": {
    "email": true,
    "storage": true
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "next_run_at": "2023-06-19T09:00:00Z"
}
```

**Status Codes:**
- 201 Created - Scheduled report created successfully
- 400 Bad Request - Invalid scheduled report data

#### GET /reports/scheduled/{scheduled_report_id}

Get a specific scheduled report by ID.

**Authentication:** Required

**Path Parameters:**
- `scheduled_report_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Rate Report",
  "description": "Weekly report on rate changes",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 9 * * 1",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "delivery_options": {
    "email": true,
    "storage": true
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "next_run_at": "2023-06-19T09:00:00Z",
  "last_run_at": "2023-06-12T09:00:00Z"
}
```

**Status Codes:**
- 200 OK - Scheduled report retrieved successfully
- 404 Not Found - Scheduled report not found

#### PUT /reports/scheduled/{scheduled_report_id}

Update a specific scheduled report.

**Authentication:** Required

**Path Parameters:**
- `scheduled_report_id`: string (UUID, required)

**Request Body:**
```json
{
  "name": "Weekly Rate Report Updated",
  "description": "Updated weekly report on rate changes",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 10 * * 1",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "delivery_options": {
    "email": true,
    "storage": true,
    "slack": true
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Weekly Rate Report Updated",
  "description": "Updated weekly report on rate changes",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "schedule": "0 10 * * 1",
  "is_active": true,
  "notification_email": "john.smith@example.com",
  "delivery_options": {
    "email": true,
    "storage": true,
    "slack": true
  },
  "created_by": "550e8400-e29b-41d4-a716-446655440002",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T14:45:00Z",
  "next_run_at": "2023-06-19T10:00:00Z",
  "last_run_at": "2023-06-12T09:00:00Z"
}
```

**Status Codes:**
- 200 OK - Scheduled report updated successfully
- 400 Bad Request - Invalid scheduled report data
- 404 Not Found - Scheduled report not found

#### DELETE /reports/scheduled/{scheduled_report_id}

Delete a specific scheduled report.

**Authentication:** Required

**Path Parameters:**
- `scheduled_report_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Scheduled report deleted successfully"
}
```

**Status Codes:**
- 200 OK - Scheduled report deleted successfully
- 404 Not Found - Scheduled report not found

### Report Share Endpoints

#### GET /reports/shares

List report shares with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `report_id`: string (UUID)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "report_id": "550e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440002",
      "permission": "view",
      "created_by": "550e8400-e29b-41d4-a716-446655440003",
      "created_at": "2023-06-15T14:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Report shares retrieved successfully

#### POST /reports/shares

Create a new report share.

**Authentication:** Required

**Request Body:**
```json
{
  "report_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "user_id": "550e8400-e29b-41d4-a716-446655440002 (required)",
  "permission": "view (required, one of: view, edit, admin)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "permission": "view",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - Report share created successfully
- 400 Bad Request - Invalid report share data

#### GET /reports/shares/{share_id}

Get a specific report share by ID.

**Authentication:** Required

**Path Parameters:**
- `share_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "permission": "view",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 200 OK - Report share retrieved successfully
- 404 Not Found - Report share not found

#### PUT /reports/shares/{share_id}

Update a specific report share.

**Authentication:** Required

**Path Parameters:**
- `share_id`: string (UUID, required)

**Request Body:**
```json
{
  "permission": "edit (one of: view, edit, admin)"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440002",
  "permission": "edit",
  "created_by": "550e8400-e29b-41d4-a716-446655440003",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T15:00:00Z"
}
```

**Status Codes:**
- 200 OK - Report share updated successfully
- 400 Bad Request - Invalid report share data
- 404 Not Found - Report share not found

#### DELETE /reports/shares/{share_id}

Delete a specific report share.

**Authentication:** Required

**Path Parameters:**
- `share_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Report share deleted successfully"
}
```

**Status Codes:**
- 200 OK - Report share deleted successfully
- 404 Not Found - Report share not found

### Report Execution Endpoints

#### GET /reports/executions

List report executions with pagination and filtering.

**Authentication:** Required

**Query Parameters:**
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)
- `report_id`: string (UUID)
- `status`: string (pending, running, completed, failed)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "report_id": "550e8400-e29b-41d4-a716-446655440001",
      "status": "completed",
      "execution_time": "5s",
      "result_url": "/api/v1/reports/executions/550e8400-e29b-41d4-a716-446655440000/download",
      "executed_by": "550e8400-e29b-41d4-a716-446655440002",
      "executed_at": "2023-06-15T14:35:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Report executions retrieved successfully

#### GET /reports/executions/{execution_id}

Get a specific report execution by ID.

**Authentication:** Required

**Path Parameters:**
- `execution_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "report_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "completed",
  "execution_time": "5s",
  "result_url": "/api/v1/reports/executions/550e8400-e29b-41d4-a716-446655440000/download",
  "executed_by": "550e8400-e29b-41d4-a716-446655440002",
  "executed_at": "2023-06-15T14:35:00Z",
  "completed_at": "2023-06-15T14:35:05Z"
}
```

**Status Codes:**
- 200 OK - Report execution retrieved successfully
- 404 Not Found - Report execution not found

#### GET /reports/executions/{execution_id}/download

Download the result of a report execution.

**Authentication:** Required

**Path Parameters:**
- `execution_id`: string (UUID, required)

**Response:** File download

**Status Codes:**
- 200 OK - Report execution result downloaded successfully
- 404 Not Found - Report execution not found or result not available

## Admin API

The Admin API provides endpoints for system configuration, admin activity logging, and maintenance scheduling. These endpoints require administrator privileges.

### System Configuration Endpoints

#### GET /admin/configs

List system configurations with optional filtering.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `key`: string
- `config_type`: string
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
{
  "items": [
    {
      "key": "app.data_retention_days",
      "value": 90,
      "config_type": "system",
      "description": "Number of days to retain data",
      "is_encrypted": false,
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2023-06-15T14:30:00Z",
      "updated_at": "2023-06-15T14:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - System configurations retrieved successfully

#### GET /admin/configs/{key}

Get a specific system configuration by key.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `key`: string (required)

**Query Parameters:**
- `decrypt`: boolean (default: false)

**Response:**
```json
{
  "key": "app.data_retention_days",
  "value": 90,
  "config_type": "system",
  "description": "Number of days to retain data",
  "is_encrypted": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 200 OK - System configuration retrieved successfully
- 404 Not Found - System configuration not found

#### POST /admin/configs

Create a new system configuration.

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "key": "app.data_retention_days (required)",
  "value": 90,
  "config_type": "system (required)",
  "description": "Number of days to retain data",
  "is_encrypted": false
}
```

**Response:**
```json
{
  "key": "app.data_retention_days",
  "value": 90,
  "config_type": "system",
  "description": "Number of days to retain data",
  "is_encrypted": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T14:30:00Z"
}
```

**Status Codes:**
- 201 Created - System configuration created successfully
- 400 Bad Request - Invalid system configuration data

#### PUT /admin/configs/{key}

Update a specific system configuration.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `key`: string (required)

**Request Body:**
```json
{
  "value": 180,
  "config_type": "system",
  "description": "Updated number of days to retain data",
  "is_encrypted": false
}
```

**Response:**
```json
{
  "key": "app.data_retention_days",
  "value": 180,
  "config_type": "system",
  "description": "Updated number of days to retain data",
  "is_encrypted": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T15:15:00Z"
}
```

**Status Codes:**
- 200 OK - System configuration updated successfully
- 400 Bad Request - Invalid system configuration data
- 404 Not Found - System configuration not found

#### DELETE /admin/configs/{key}

Delete a specific system configuration.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `key`: string (required)

**Response:**
```json
{
  "message": "System configuration deleted successfully"
}
```

**Status Codes:**
- 200 OK - System configuration deleted successfully
- 404 Not Found - System configuration not found

### Admin Activity Endpoints

#### GET /admin/activities

List admin activities with optional filtering.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `user_id`: string (UUID)
- `action`: string
- `resource_type`: string
- `resource_id`: string
- `start_date`: string (ISO8601 date)
- `end_date`: string (ISO8601 date)
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "action": "update_config",
      "resource_type": "system_config",
      "resource_id": "app.data_retention_days",
      "details": {
        "old_value": 90,
        "new_value": 180
      },
      "ip_address": "192.168.1.1",
      "timestamp": "2023-06-16T15:15:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Admin activities retrieved successfully

#### POST /admin/activities

Create a new admin activity log entry.

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440001 (required)",
  "action": "update_config (required)",
  "resource_type": "system_config (required)",
  "resource_id": "app.data_retention_days",
  "details": {
    "old_value": 90,
    "new_value": 180
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "action": "update_config",
  "resource_type": "system_config",
  "resource_id": "app.data_retention_days",
  "details": {
    "old_value": 90,
    "new_value": 180
  },
  "ip_address": "192.168.1.1",
  "timestamp": "2023-06-16T15:30:00Z"
}
```

**Status Codes:**
- 201 Created - Admin activity created successfully
- 400 Bad Request - Invalid admin activity data

### Maintenance Schedule Endpoints

#### GET /admin/maintenance/schedules

List maintenance schedules with optional filtering.

**Authentication:** Required (Admin only)

**Query Parameters:**
- `is_active`: boolean
- `start_date`: string (ISO8601 date)
- `end_date`: string (ISO8601 date)
- `skip`: integer (default: 0)
- `limit`: integer (default: 100)

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Database Maintenance",
      "description": "Scheduled database maintenance and optimization",
      "start_time": "2023-06-20T02:00:00Z",
      "end_time": "2023-06-20T04:00:00Z",
      "affected_services": ["api", "database"],
      "is_active": true,
      "created_by": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-06-16T15:45:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Status Codes:**
- 200 OK - Maintenance schedules retrieved successfully

#### GET /admin/maintenance/schedules/{schedule_id}

Get a specific maintenance schedule by ID.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Database Maintenance",
  "description": "Scheduled database maintenance and optimization",
  "start_time": "2023-06-20T02:00:00Z",
  "end_time": "2023-06-20T04:00:00Z",
  "affected_services": ["api", "database"],
  "is_active": true,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-16T15:45:00Z"
}
```

**Status Codes:**
- 200 OK - Maintenance schedule retrieved successfully
- 404 Not Found - Maintenance schedule not found

#### POST /admin/maintenance/schedules

Create a new maintenance schedule.

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "title": "Database Maintenance (required)",
  "description": "Scheduled database maintenance and optimization",
  "start_time": "2023-06-20T02:00:00Z (required)",
  "end_time": "2023-06-20T04:00:00Z (required)",
  "affected_services": ["api", "database"],
  "is_active": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Database Maintenance",
  "description": "Scheduled database maintenance and optimization",
  "start_time": "2023-06-20T02:00:00Z",
  "end_time": "2023-06-20T04:00:00Z",
  "affected_services": ["api", "database"],
  "is_active": true,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-16T15:45:00Z"
}
```

**Status Codes:**
- 201 Created - Maintenance schedule created successfully
- 400 Bad Request - Invalid maintenance schedule data

#### PUT /admin/maintenance/schedules/{schedule_id}

Update a specific maintenance schedule.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Request Body:**
```json
{
  "title": "Database Maintenance and Backup",
  "description": "Updated scheduled database maintenance and optimization",
  "start_time": "2023-06-20T01:00:00Z",
  "end_time": "2023-06-20T05:00:00Z",
  "affected_services": ["api", "database", "reporting"],
  "is_active": true
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Database Maintenance and Backup",
  "description": "Updated scheduled database maintenance and optimization",
  "start_time": "2023-06-20T01:00:00Z",
  "end_time": "2023-06-20T05:00:00Z",
  "affected_services": ["api", "database", "reporting"],
  "is_active": true,
  "created_by": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2023-06-16T15:45:00Z",
  "updated_at": "2023-06-16T16:00:00Z"
}
```

**Status Codes:**
- 200 OK - Maintenance schedule updated successfully
- 400 Bad Request - Invalid maintenance schedule data
- 404 Not Found - Maintenance schedule not found

#### DELETE /admin/maintenance/schedules/{schedule_id}

Delete a specific maintenance schedule.

**Authentication:** Required (Admin only)

**Path Parameters:**
- `schedule_id`: string (UUID, required)

**Response:**
```json
{
  "message": "Maintenance schedule deleted successfully"
}
```

**Status Codes:**
- 200 OK - Maintenance schedule deleted successfully
- 404 Not Found - Maintenance schedule not found

#### GET /admin/maintenance/active

Get currently active maintenance schedules.

**Authentication:** Required

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Database Maintenance",
      "description": "Scheduled database maintenance and optimization",
      "start_time": "2023-06-16T15:30:00Z",
      "end_time": "2023-06-16T17:30:00Z",
      "affected_services": ["api", "database"],
      "is_active": true,
      "created_by": "550e8400-e29b-41d4-a716-446655440001",
      "created_at": "2023-06-16T15:45:00Z"
    }
  ]
}
```

**Status Codes:**
- 200 OK - Active maintenance schedules retrieved successfully

#### GET /admin/maintenance/status

Check if the system is currently under maintenance.

**Authentication:** Not required

**Response:**
```json
{
  "under_maintenance": true,
  "current_schedule": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Database Maintenance",
    "description": "Scheduled database maintenance and optimization",
    "start_time": "2023-06-16T15:30:00Z",
    "end_time": "2023-06-16T17:30:00Z",
    "affected_services": ["api", "database"],
    "is_active": true
  },
  "message": "The system is currently undergoing scheduled maintenance. Some features may be unavailable."
}
```

**Status Codes:**
- 200 OK - Maintenance status retrieved successfully

## Common Response Formats

The API uses consistent response formats for different types of operations.

### Success Responses

Successful responses include the requested data and appropriate HTTP status codes.

**Single resource response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T14:30:00Z",
  "updated_at": "2023-06-16T15:45:00Z",
  "field1": "value1",
  "field2": "value2"
}
```

**List response with pagination:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "field1": "value1",
      "field2": "value2"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**Simple success response:**
```json
{
  "message": "Operation completed successfully"
}
```

### Error Responses

Error responses include details about the error and appropriate HTTP status codes.

**Validation error (400 Bad Request):**
```json
{
  "error": "Validation Error",
  "detail": {
    "field1": "Error message for field1",
    "field2": "Error message for field2"
  }
}
```

**Authentication error (401 Unauthorized):**
```json
{
  "error": "Authentication Error",
  "detail": "Invalid or expired token"
}
```

**Authorization error (403 Forbidden):**
```json
{
  "error": "Permission Denied",
  "detail": "You do not have permission to access this resource"
}
```

**Resource not found (404 Not Found):**
```json
{
  "error": "Not Found",
  "detail": "The requested resource was not found"
}
```

**Server error (500 Internal Server Error):**
```json
{
  "error": "Internal Server Error",
  "detail": "An unexpected error occurred"
}
```

## API Versioning

The API uses versioning to ensure backward compatibility as it evolves.

### Version Format

The API version is specified in the URL path as `/api/v{major_version}`.

### Current Version

The current API version is v1.

### Deprecation Policy

When a new API version is released, the previous version will be supported for at least 6 months. Deprecation notices will be provided in the API responses using the `Deprecation` and `Sunset` headers.

## Rate Limiting

The API implements rate limiting to prevent abuse and ensure fair usage.

### Rate Limit Headers

The API includes the following headers in responses to indicate rate limit status:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current time window
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window
- `X-RateLimit-Reset`: The time at which the current rate limit window resets, in Unix time

### Rate Limit Exceeded

When the rate limit is exceeded, the API returns a 429 Too Many Requests response with a Retry-After header indicating when to retry the request.

## Webhooks

The API supports webhooks for event notifications.

### Webhook Events

The following events can trigger webhooks:

- `analysis.completed`: Triggered when an analysis is completed
- `analysis.failed`: Triggered when an analysis fails
- `report.completed`: Triggered when a report is completed
- `report.failed`: Triggered when a report fails
- `data_source.updated`: Triggered when a data source is updated
- `maintenance.scheduled`: Triggered when a maintenance is scheduled

### Webhook Payload

Webhook payloads include event details and relevant data.

```json
{
  "event": "analysis.completed",
  "timestamp": "2023-06-15T14:30:00Z",
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result_url": "/api/v1/analysis/requests/550e8400-e29b-41d4-a716-446655440000/results"
  }
}
```

### Webhook Security

Webhooks are secured using HMAC signatures. The signature is included in the X-Signature header of the webhook request.