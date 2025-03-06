# Freight Price Movement Agent API Examples

## Introduction

This document provides practical examples of using the Freight Price Movement Agent API. It complements the [API Reference](api-reference.md) by showing real-world usage scenarios with sample requests and responses. All examples assume you have already obtained an authentication token as described in the Authentication section.

## Authentication Examples

### Login and Obtain Access Token

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "john.smith@company.com",
  "password": "your-secure-password"
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

*Store both tokens securely. The access token is used for API requests, while the refresh token can be used to obtain a new access token when the current one expires.*

### Refresh Access Token

**Request:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

*Use this endpoint when your access token expires but your refresh token is still valid.*

### Get Current User Information

**Request:**
```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john.smith",
  "email": "john.smith@company.com",
  "roles": ["analyst"],
  "last_login": "2023-06-15T14:30:00Z"
}
```

*This endpoint is useful for verifying authentication and retrieving user information.*

## Time Period Management Examples

### Create a Time Period

**Request:**
```http
POST /api/v1/analysis/time-periods
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Q1 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "weekly",
  "is_custom": false
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Q1 2023",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "weekly",
  "is_custom": false,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T14:35:00Z"
}
```

*Time periods are used to define the date ranges for price movement analysis. The granularity parameter determines how data is aggregated (daily, weekly, monthly).*

### Create a Custom Time Period

**Request:**
```http
POST /api/v1/analysis/time-periods
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Custom Bi-Weekly",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "custom",
  "is_custom": true,
  "custom_interval": "14D"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "Custom Bi-Weekly",
  "start_date": "2023-01-01",
  "end_date": "2023-03-31",
  "granularity": "custom",
  "is_custom": true,
  "custom_interval": "14D",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T14:40:00Z"
}
```

*Custom time periods allow you to define specific intervals for aggregation. The custom_interval uses pandas frequency strings (e.g., '14D' for 14 days).*

### List Time Periods

**Request:**
```http
GET /api/v1/analysis/time-periods?skip=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Q1 2023",
      "start_date": "2023-01-01",
      "end_date": "2023-03-31",
      "granularity": "weekly",
      "is_custom": false,
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2023-06-15T14:35:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "Custom Bi-Weekly",
      "start_date": "2023-01-01",
      "end_date": "2023-03-31",
      "granularity": "custom",
      "is_custom": true,
      "custom_interval": "14D",
      "created_by": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2023-06-15T14:40:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 10
}
```

*This endpoint returns a paginated list of time periods. Use the skip and limit parameters to control pagination.*

## Data Source Management Examples

### Create a CSV Data Source

**Request:**
```http
POST /api/v1/data-sources/csv
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Ocean Freight Rates",
  "description": "Weekly ocean freight rates from TMS export",
  "file_path": "/data/freight_rates.csv",
  "delimiter": ",",
  "has_header": true,
  "date_format": "YYYY-MM-DD",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency_code",
    "origin": "origin",
    "destination": "destination",
    "date": "quote_date",
    "carrier": "carrier_name",
    "mode": "transport_mode"
  },
  "status": "active"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "name": "Ocean Freight Rates",
  "description": "Weekly ocean freight rates from TMS export",
  "type": "csv",
  "file_path": "/data/freight_rates.csv",
  "delimiter": ",",
  "has_header": true,
  "date_format": "YYYY-MM-DD",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency_code",
    "origin": "origin",
    "destination": "destination",
    "date": "quote_date",
    "carrier": "carrier_name",
    "mode": "transport_mode"
  },
  "status": "active",
  "created_at": "2023-06-15T14:45:00Z",
  "updated_at": "2023-06-15T14:45:00Z"
}
```

*CSV data sources require field mapping to match your CSV columns to the system's expected fields. The field_mapping object maps system field names to your CSV column names.*

### Create a Database Data Source

**Request:**
```http
POST /api/v1/data-sources/database
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "ERP Freight Data",
  "description": "Freight data from enterprise ERP system",
  "connection_string": "postgresql://user:password@localhost:5432/erp_db",
  "query": "SELECT rate as price, currency, origin_code as origin, dest_code as destination, rate_date as quote_date, carrier, 'ocean' as mode FROM freight_rates WHERE rate_date >= '2023-01-01'",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency",
    "origin": "origin",
    "destination": "destination",
    "date": "quote_date",
    "carrier": "carrier",
    "mode": "mode"
  },
  "status": "active"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "name": "ERP Freight Data",
  "description": "Freight data from enterprise ERP system",
  "type": "database",
  "connection_string": "postgresql://user:***@localhost:5432/erp_db",
  "query": "SELECT rate as price, currency, origin_code as origin, dest_code as destination, rate_date as quote_date, carrier, 'ocean' as mode FROM freight_rates WHERE rate_date >= '2023-01-01'",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency",
    "origin": "origin",
    "destination": "destination",
    "date": "quote_date",
    "carrier": "carrier",
    "mode": "mode"
  },
  "status": "active",
  "created_at": "2023-06-15T14:50:00Z",
  "updated_at": "2023-06-15T14:50:00Z"
}
```

*Database data sources connect directly to your database systems. Note that sensitive information like passwords in the connection string will be masked in responses.*

### Test a Data Source Connection

**Request:**
```http
POST /api/v1/data-sources/test-connection
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "data_source_id": "550e8400-e29b-41d4-a716-446655440004",
  "connection_params": {
    "timeout": 30
  }
}
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Connection successful",
  "details": {
    "connection_time_ms": 125,
    "record_count": 1250,
    "sample_record": {
      "price": 1200.5,
      "currency": "USD",
      "origin": "CNSHA",
      "destination": "USNYC",
      "quote_date": "2023-01-15",
      "carrier": "MAERSK",
      "mode": "ocean"
    }
  }
}
```

*Always test your data source connections before using them in analysis. This helps verify that the connection parameters and field mappings are correct.*

## Price Movement Analysis Examples

### Create an Analysis Request

**Request:**
```http
POST /api/v1/analysis/requests
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": [
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440004"
  ],
  "filters": {
    "origins": ["CNSHA", "CNNGB"],
    "destinations": ["USNYC", "USLAX"],
    "carriers": ["MAERSK", "MSC"],
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
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440005",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": [
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440004"
  ],
  "filters": {
    "origins": ["CNSHA", "CNNGB"],
    "destinations": ["USNYC", "USLAX"],
    "carriers": ["MAERSK", "MSC"],
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
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T15:00:00Z"
}
```

*Creating an analysis request defines the parameters for your price movement analysis. The actual analysis is executed separately.*

### Execute an Analysis

**Request:**
```http
POST /api/v1/analysis/requests/550e8400-e29b-41d4-a716-446655440005/execute
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440005",
  "time_period": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Q1 2023",
    "start_date": "2023-01-01",
    "end_date": "2023-03-31",
    "granularity": "weekly"
  },
  "results": {
    "absolute_change": 245.0,
    "percentage_change": 5.2,
    "trend_direction": "increasing",
    "start_value": 4120.0,
    "end_value": 4365.0,
    "currency": "USD",
    "statistics": {
      "average": 4242.5,
      "minimum": 4120.0,
      "maximum": 4450.0,
      "median": 4235.0,
      "standard_deviation": 98.75
    }
  },
  "time_series": [
    {
      "period_start": "2023-01-01",
      "period_end": "2023-01-07",
      "value": 4120.0,
      "absolute_change": null,
      "percentage_change": null
    },
    {
      "period_start": "2023-01-08",
      "period_end": "2023-01-14",
      "value": 4150.0,
      "absolute_change": 30.0,
      "percentage_change": 0.7
    },
    {
      "period_start": "2023-01-15",
      "period_end": "2023-01-21",
      "value": 4320.0,
      "absolute_change": 170.0,
      "percentage_change": 4.1
    },
    "... additional time periods ...",
    {
      "period_start": "2023-03-25",
      "period_end": "2023-03-31",
      "value": 4365.0,
      "absolute_change": -85.0,
      "percentage_change": -1.9
    }
  ],
  "executed_at": "2023-06-15T15:05:00Z",
  "execution_time_ms": 1250
}
```

*The analysis results include the overall price movement metrics (absolute and percentage changes), as well as a time series breakdown showing the progression of prices over the selected time period.*

### Save an Analysis Configuration

**Request:**
```http
POST /api/v1/analysis/saved
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "China to US Ocean Rates",
  "description": "Weekly analysis of ocean rates from China to US major ports",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": [
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440004"
  ],
  "filters": {
    "origins": ["CNSHA", "CNNGB"],
    "destinations": ["USNYC", "USLAX"],
    "carriers": ["MAERSK", "MSC"],
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
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "name": "China to US Ocean Rates",
  "description": "Weekly analysis of ocean rates from China to US major ports",
  "time_period_id": "550e8400-e29b-41d4-a716-446655440001",
  "data_source_ids": [
    "550e8400-e29b-41d4-a716-446655440003",
    "550e8400-e29b-41d4-a716-446655440004"
  ],
  "filters": {
    "origins": ["CNSHA", "CNNGB"],
    "destinations": ["USNYC", "USLAX"],
    "carriers": ["MAERSK", "MSC"],
    "modes": ["ocean"]
  },
  "options": {
    "calculate_absolute_change": true,
    "calculate_percentage_change": true,
    "identify_trend_direction": true,
    "compare_to_baseline": false
  },
  "output_format": "json",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T15:10:00Z",
  "last_run_at": null
}
```

*Saved analyses allow you to store analysis configurations for repeated use. You can run them on demand or schedule them for automatic execution.*

### Run a Saved Analysis

**Request:**
```http
POST /api/v1/analysis/saved/550e8400-e29b-41d4-a716-446655440006/run
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440006",
  "time_period": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Q1 2023",
    "start_date": "2023-01-01",
    "end_date": "2023-03-31",
    "granularity": "weekly"
  },
  "results": {
    "absolute_change": 245.0,
    "percentage_change": 5.2,
    "trend_direction": "increasing",
    "start_value": 4120.0,
    "end_value": 4365.0,
    "currency": "USD",
    "statistics": {
      "average": 4242.5,
      "minimum": 4120.0,
      "maximum": 4450.0,
      "median": 4235.0,
      "standard_deviation": 98.75
    }
  },
  "time_series": ["... time series data (same format as execute analysis example) ..."],
  "executed_at": "2023-06-15T15:15:00Z",
  "execution_time_ms": 1180
}
```

*Running a saved analysis executes the analysis with the stored configuration. The response format is the same as executing an analysis request directly.*

## Report Management Examples

### Create a Report

**Request:**
```http
POST /api/v1/reports
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Q1 2023 Ocean Freight Analysis",
  "description": "Quarterly analysis of ocean freight rates from China to US",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440006",
  "parameters": {
    "include_visualization": true,
    "include_time_series": true,
    "include_statistics": true
  },
  "filters": {
    "min_value": 4000,
    "max_value": 5000
  },
  "format": "pdf"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440007",
  "name": "Q1 2023 Ocean Freight Analysis",
  "description": "Quarterly analysis of ocean freight rates from China to US",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440006",
  "parameters": {
    "include_visualization": true,
    "include_time_series": true,
    "include_statistics": true
  },
  "filters": {
    "min_value": 4000,
    "max_value": 5000
  },
  "format": "pdf",
  "status": "pending",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T15:20:00Z",
  "last_run_at": null
}
```

*Reports allow you to format analysis results for presentation and sharing. You can specify various parameters to customize the report content and format.*

### Run a Report

**Request:**
```http
POST /api/v1/reports/550e8400-e29b-41d4-a716-446655440007/run
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "report_id": "550e8400-e29b-41d4-a716-446655440007",
  "execution_id": "550e8400-e29b-41d4-a716-446655440008",
  "status": "completed",
  "result_url": "/api/v1/reports/executions/550e8400-e29b-41d4-a716-446655440008/download",
  "executed_at": "2023-06-15T15:25:00Z",
  "execution_time_ms": 2500
}
```

*Running a report generates the report file based on the specified format and parameters. The result_url provides a link to download the generated report.*

### Download a Report

**Request:**
```http
GET /api/v1/reports/executions/550e8400-e29b-41d4-a716-446655440008/download
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="Q1_2023_Ocean_Freight_Analysis.pdf"

Binary PDF content
```

*This endpoint returns the actual report file. The Content-Type header will vary based on the report format (PDF, Excel, CSV, etc.).*

## Scheduled Analysis Examples

### Create an Analysis Schedule

**Request:**
```http
POST /api/v1/analysis/schedules
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Weekly Ocean Rate Analysis",
  "description": "Automatically run China-US ocean rate analysis every Monday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440006",
  "schedule": "0 8 * * 1",
  "is_active": true,
  "notification_email": "john.smith@company.com"
}
```

**Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440009",
  "name": "Weekly Ocean Rate Analysis",
  "description": "Automatically run China-US ocean rate analysis every Monday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440006",
  "schedule": "0 8 * * 1",
  "is_active": true,
  "notification_email": "john.smith@company.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T15:30:00Z",
  "next_run_at": "2023-06-19T08:00:00Z"
}
```

*Analysis schedules allow you to automatically run saved analyses on a recurring basis. The schedule parameter uses cron syntax (in this example, 8:00 AM every Monday).*

### Deactivate an Analysis Schedule

**Request:**
```http
POST /api/v1/analysis/schedules/550e8400-e29b-41d4-a716-446655440009/deactivate
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440009",
  "name": "Weekly Ocean Rate Analysis",
  "description": "Automatically run China-US ocean rate analysis every Monday",
  "saved_analysis_id": "550e8400-e29b-41d4-a716-446655440006",
  "schedule": "0 8 * * 1",
  "is_active": false,
  "notification_email": "john.smith@company.com",
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-06-15T15:30:00Z",
  "next_run_at": null
}
```

*You can temporarily deactivate a schedule without deleting it. This is useful when you want to pause scheduled analyses during certain periods.*

## Error Handling Examples

### Validation Error

**Request:**
```http
POST /api/v1/analysis/time-periods
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Invalid Period",
  "start_date": "2023-04-15",
  "end_date": "2023-01-01",
  "granularity": "weekly"
}
```

**Response:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Validation Error",
  "detail": {
    "end_date": "End date must be after start date"
  }
}
```

*Validation errors occur when the request data doesn't meet the required format or business rules. The response includes specific details about what's wrong.*

### Resource Not Found Error

**Request:**
```http
GET /api/v1/analysis/time-periods/550e8400-e29b-41d4-a716-446655440099
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "Not Found",
  "detail": "Time period with ID 550e8400-e29b-41d4-a716-446655440099 not found"
}
```

*Not Found errors occur when you try to access a resource that doesn't exist. Always check that you're using valid IDs in your requests.*

### Authentication Error

**Request:**
```http
GET /api/v1/analysis/time-periods
Authorization: Bearer invalid-token
```

**Response:**
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "Authentication Error",
  "detail": "Invalid or expired token"
}
```

*Authentication errors occur when your token is invalid, expired, or missing. Make sure to refresh your token before it expires.*

## Webhook Integration Examples

### Webhook Payload: Analysis Completed

When an analysis is completed, a webhook can be triggered with the following payload:

```json
{
  "event": "analysis.completed",
  "timestamp": "2023-06-15T15:05:00Z",
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440005",
    "status": "completed",
    "result_url": "/api/v1/analysis/requests/550e8400-e29b-41d4-a716-446655440005/results",
    "summary": {
      "absolute_change": 245.0,
      "percentage_change": 5.2,
      "trend_direction": "increasing"
    }
  }
}
```

*Webhooks allow your systems to be notified of events in real-time. To set up webhooks, configure them in the system settings.*

### Webhook Payload: Data Source Updated

When a data source is updated, a webhook can be triggered with the following payload:

```json
{
  "event": "data_source.updated",
  "timestamp": "2023-06-15T16:00:00Z",
  "data": {
    "data_source_id": "550e8400-e29b-41d4-a716-446655440003",
    "name": "Ocean Freight Rates",
    "type": "csv",
    "status": "active",
    "updated_at": "2023-06-15T16:00:00Z"
  }
}
```

*This webhook can be used to trigger dependent processes when data sources are updated.*

## Batch Processing Examples

### Bulk Data Import

**Request:**
```http
POST /api/v1/data-sources/csv/bulk-import
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

{
  "name": "Bulk Ocean Rates Import",
  "description": "Multiple CSV files with ocean freight rates",
  "files": ["file1.csv", "file2.csv", "file3.csv"],
  "delimiter": ",",
  "has_header": true,
  "date_format": "YYYY-MM-DD",
  "field_mapping": {
    "freight_charge": "price",
    "currency": "currency_code",
    "origin": "origin",
    "destination": "destination",
    "date": "quote_date",
    "carrier": "carrier_name",
    "mode": "transport_mode"
  }
}
```

**Response:**
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "job_id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "processing",
  "files_count": 3,
  "processed_count": 0,
  "status_url": "/api/v1/jobs/550e8400-e29b-41d4-a716-446655440010/status"
}
```

*Bulk operations are processed asynchronously. The response includes a job ID that can be used to check the status of the operation.*

### Check Batch Job Status

**Request:**
```http
GET /api/v1/jobs/550e8400-e29b-41d4-a716-446655440010/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "job_id": "550e8400-e29b-41d4-a716-446655440010",
  "status": "completed",
  "files_count": 3,
  "processed_count": 3,
  "records_processed": 15000,
  "records_failed": 25,
  "data_source_ids": [
    "550e8400-e29b-41d4-a716-446655440011",
    "550e8400-e29b-41d4-a716-446655440012",
    "550e8400-e29b-41d4-a716-446655440013"
  ],
  "completed_at": "2023-06-15T16:15:00Z",
  "execution_time_ms": 45000
}
```

*Use the job status endpoint to track the progress of batch operations. The response includes detailed information about the operation's results.*