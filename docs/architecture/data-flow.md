# Data Flow Architecture

## Introduction

This document describes the data flow architecture of the Freight Price Movement Agent system. It details how freight pricing data moves through the system from initial ingestion from various sources, through analysis processing, to final presentation to users. Understanding these data flows is essential for developers, system administrators, and integrators working with the system.

## High-Level Data Flow Overview

The Freight Price Movement Agent implements a multi-stage data flow architecture with clear boundaries between ingestion, processing, analysis, and presentation layers. Data flows through the system in a logical progression, with each component responsible for a specific transformation or operation on the data.

### Core Data Flow Diagram

```mermaid
graph TD
    subgraph "External Data Sources"
        A1[CSV Files] 
        A2[TMS Systems]
        A3[ERP Systems]
        A4[External APIs]
        A5[Databases]
    end
    
    subgraph "Data Ingestion Layer"
        B1[Data Ingestion Service]
        B2[Integration Service]
        B3[File Connector]
        B4[Database Connector]
        B5[TMS/ERP Connector]
        B6[API Connector]
    end
    
    subgraph "Data Storage Layer"
        C1[(PostgreSQL Database)]
        C2[(Redis Cache)]
        C3[S3 Storage]
    end
    
    subgraph "Analysis Layer"
        D1[Analysis Engine]
        D2[Calculation Module]
        D3[Time Period Processor]
        D4[Trend Analyzer]
    end
    
    subgraph "Presentation Layer"
        E1[Presentation Service]
        E2[JSON Formatter]
        E3[CSV Formatter]
        E4[Text Formatter]
        E5[Visualization Generator]
    end
    
    subgraph "API Layer"
        F1[API Gateway]
        F2[Authentication]
        F3[Rate Limiting]
    end
    
    subgraph "Client Applications"
        G1[Web Interface]
        G2[Reporting Tools]
        G3[External Systems]
    end
    
    %% Data Source to Ingestion
    A1 -->|Upload| B3
    A2 -->|Connect| B5
    A3 -->|Connect| B5
    A4 -->|Request| B6
    A5 -->|Query| B4
    
    %% Connectors to Services
    B3 -->|Raw Data| B1
    B4 -->|Raw Data| B1
    B5 -->|Raw Data| B2
    B6 -->|Raw Data| B2
    
    %% Integration to Ingestion
    B2 -->|Standardized Data| B1
    
    %% Ingestion to Storage
    B1 -->|Validated Data| C1
    B1 -->|Large Files| C3
    
    %% Storage to Analysis
    C1 -->|Freight Data| D1
    D1 -->|Analysis Results| C1
    D1 -->|Cached Results| C2
    
    %% Analysis Components
    D1 -->|Time Period Data| D3
    D3 -->|Processed Data| D2
    D2 -->|Calculated Changes| D4
    D4 -->|Complete Results| D1
    
    %% Analysis to Presentation
    D1 -->|Analysis Results| E1
    C2 -->|Cached Results| E1
    
    %% Presentation Components
    E1 -->|Format JSON| E2
    E1 -->|Format CSV| E3
    E1 -->|Format Text| E4
    E1 -->|Generate Visuals| E5
    
    %% Presentation to API
    E2 -->|Formatted Results| F1
    E3 -->|Formatted Results| F1
    E4 -->|Formatted Results| F1
    E5 -->|Visualizations| F1
    
    %% API to Clients
    F1 -->|API Response| G1
    F1 -->|API Response| G2
    F1 -->|API Response| G3
    
    %% Client to API
    G1 -->|API Request| F1
    G2 -->|API Request| F1
    G3 -->|API Request| F1
    
    %% API Security
    F1 -->|Authenticate| F2
    F1 -->|Rate Limit| F3
```

### Key Data Flow Stages

1. **Data Ingestion**: External data is collected, validated, and normalized
2. **Data Storage**: Normalized data is persisted in the database
3. **Analysis Processing**: Stored data is analyzed to calculate price movements
4. **Result Presentation**: Analysis results are formatted for delivery
5. **API Delivery**: Formatted results are delivered to clients via API

## Data Ingestion Flow

The data ingestion process is responsible for collecting freight pricing data from various sources, validating it, transforming it to a standard format, and storing it in the database for analysis.

### Ingestion Process Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant DIS as Data Ingestion Service
    participant IS as Integration Service
    participant Conn as Source Connector
    participant Val as Data Validator
    participant DB as Database
    
    User->>API: Request Data Import
    API->>DIS: Forward Import Request
    
    alt Direct File Upload
        User->>API: Upload CSV File
        API->>DIS: Process File
        DIS->>Conn: Create File Connector
        Conn->>DIS: Return Raw Data
    else External System Connection
        DIS->>IS: Request External Data
        IS->>Conn: Create Appropriate Connector
        Conn->>IS: Connect to External System
        Conn->>IS: Fetch Raw Data
        IS->>IS: Standardize Data Format
        IS->>DIS: Return Standardized Data
    end
    
    DIS->>Val: Validate Data
    
    alt Valid Data
        Val->>DIS: Validation Success
        DIS->>DIS: Transform to Standard Format
        DIS->>DB: Store Validated Data
        DB->>DIS: Confirm Storage
        DIS->>API: Return Success Response
        API->>User: Display Success Message
    else Invalid Data
        Val->>DIS: Validation Errors
        DIS->>API: Return Validation Errors
        API->>User: Display Error Details
    end
```

### Data Source Types

The system supports multiple data source types, each with its own connector implementation:

1. **CSV Files**: Direct upload or SFTP retrieval of CSV files
2. **TMS Systems**: Connection to Transportation Management Systems via API
3. **ERP Systems**: Connection to Enterprise Resource Planning systems
4. **External APIs**: Connection to third-party freight rate APIs
5. **Databases**: Direct connection to external databases

### Data Validation Rules

All ingested data undergoes validation to ensure quality and consistency:

1. **Schema Validation**: Ensures required fields are present
2. **Type Validation**: Verifies data types (e.g., numeric freight charges)
3. **Range Validation**: Checks values are within expected ranges
4. **Relationship Validation**: Verifies referential integrity
5. **Business Rule Validation**: Applies domain-specific validation rules

### Data Transformation

Raw data from various sources is transformed into a standardized format:

1. **Field Mapping**: Source fields are mapped to standard schema
2. **Data Type Conversion**: Values are converted to appropriate types
3. **Unit Standardization**: Units are standardized (e.g., currencies)
4. **Date Normalization**: Dates are converted to standard format
5. **Null Handling**: Missing values are handled according to rules

## Data Storage Architecture

The system employs a multi-tiered storage architecture to efficiently manage freight pricing data and analysis results.

### Database Schema

```mermaid
erDiagram
    FREIGHT_DATA {
        uuid id PK
        datetime record_date
        string origin_id FK
        string destination_id FK
        string carrier_id FK
        decimal freight_charge
        string currency_code
        string transport_mode
        string service_level
        jsonb additional_charges
        datetime created_at
        datetime updated_at
        string source_system
        string data_quality_flag
    }
    
    LOCATION {
        uuid id PK
        string name
        string code
        string country
        string region
        string type
        point coordinates
        boolean active
    }
    
    CARRIER {
        uuid id PK
        string name
        string code
        string type
        boolean active
    }
    
    ROUTE {
        uuid id PK
        string origin_id FK
        string destination_id FK
        string transport_mode
        decimal distance
        boolean active
    }
    
    TIME_PERIOD {
        uuid id PK
        string name
        datetime start_date
        datetime end_date
        string granularity
        boolean is_custom
        string created_by
        datetime created_at
    }
    
    ANALYSIS_RESULT {
        uuid id PK
        string time_period_id FK
        jsonb parameters
        jsonb results
        datetime calculated_at
        string created_by
        boolean is_cached
        datetime cache_expires_at
    }
    
    LOCATION ||--o{ FREIGHT_DATA : "origin"
    LOCATION ||--o{ FREIGHT_DATA : "destination"
    CARRIER ||--o{ FREIGHT_DATA : "carrier"
    ROUTE ||--o{ FREIGHT_DATA : "route"
    TIME_PERIOD ||--o{ ANALYSIS_RESULT : "defines"
```

### Storage Tiers

The system uses multiple storage tiers for different data types and access patterns:

1. **PostgreSQL Database**: Primary storage for structured freight data and analysis results
2. **TimescaleDB Extension**: Time-series optimization for freight data
3. **Redis Cache**: High-speed caching for frequent queries and analysis results
4. **S3 Object Storage**: Storage for large files, exports, and backups

### Data Partitioning

Freight data is partitioned by time to optimize query performance:

1. **Monthly Partitions**: Current month + 3 previous months in hot storage
2. **Quarterly Partitions**: Current year by quarter in warm storage
3. **Annual Partitions**: Previous years in cold storage

### Caching Strategy

The system implements a multi-level caching strategy:

1. **Analysis Result Cache**: Completed analysis results cached for 60 minutes
2. **Query Cache**: Frequent database queries cached for 15 minutes
3. **Reference Data Cache**: Locations, carriers, and routes cached in application memory
4. **API Response Cache**: Common API responses cached at the API gateway level

## Analysis Engine Data Flow

The Analysis Engine is responsible for processing freight data to calculate price movements across specified time periods.

### Analysis Process Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant AE as Analysis Engine
    participant Cache as Redis Cache
    participant DB as Database
    participant TP as Time Period Processor
    participant Calc as Calculation Module
    participant Trend as Trend Analyzer
    
    User->>API: Request Price Movement Analysis
    API->>AE: Forward Analysis Request
    
    AE->>Cache: Check for Cached Result
    
    alt Cache Hit
        Cache->>AE: Return Cached Result
        AE->>API: Return Analysis from Cache
        API->>User: Display Results
    else Cache Miss
        Cache->>AE: No Cached Result
        AE->>DB: Retrieve Time Period
        DB->>AE: Return Time Period
        
        AE->>DB: Retrieve Freight Data
        DB->>AE: Return Freight Data
        
        AE->>TP: Process Time Periods
        TP->>AE: Return Processed Periods
        
        AE->>Calc: Calculate Price Movements
        Calc->>AE: Return Calculations
        
        AE->>Trend: Analyze Trend Direction
        Trend->>AE: Return Trend Analysis
        
        AE->>AE: Compile Complete Results
        AE->>DB: Store Analysis Result
        AE->>Cache: Cache Analysis Result
        
        AE->>API: Return Analysis Results
        API->>User: Display Results
    end
```

### Calculation Algorithms

The Analysis Engine implements several key calculation algorithms:

1. **Absolute Change Calculation**:
   ```
   Absolute Change = End Value - Start Value
   ```

2. **Percentage Change Calculation**:
   ```
   Percentage Change = (Absolute Change / Start Value) * 100
   ```
   With special handling for zero start values.

3. **Trend Direction Determination**:
   ```
   If Percentage Change > +1%: Trend = "Increasing"
   If Percentage Change < -1%: Trend = "Decreasing"
   If -1% ≤ Percentage Change ≤ +1%: Trend = "Stable"
   ```

### Time Period Processing

Time periods are processed according to the specified granularity:

1. **Daily**: Each day is processed as a separate period
2. **Weekly**: Data is aggregated by week
3. **Monthly**: Data is aggregated by month
4. **Custom**: User-defined intervals are applied

### Analysis Result Structure

The analysis result contains the following key components:

1. **Metadata**: Analysis parameters, time period, filters
2. **Price Movement Metrics**: Start value, end value, absolute change, percentage change
3. **Trend Information**: Direction, indicators, patterns
4. **Time Series Data**: Data points for each period in the analysis
5. **Aggregated Statistics**: Min, max, average, standard deviation

## Presentation Layer Data Flow

The Presentation Layer transforms raw analysis results into user-friendly formats for delivery to clients.

### Presentation Process Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Gateway
    participant PS as Presentation Service
    participant AE as Analysis Engine
    participant DB as Database
    participant Cache as Redis Cache
    participant Fmt as Formatters
    participant Viz as Visualization Generator
    
    User->>API: Request Analysis Results
    API->>PS: Forward Request
    
    PS->>AE: Get Analysis Result
    AE->>DB: Retrieve Result
    DB->>AE: Return Result
    AE->>PS: Return Analysis Result
    
    alt Format = JSON
        PS->>Fmt: Format as JSON
        Fmt->>PS: Return JSON
    else Format = CSV
        PS->>Fmt: Format as CSV
        Fmt->>PS: Return CSV
    else Format = TEXT
        PS->>Fmt: Format as Text
        Fmt->>PS: Return Text
    end
    
    alt Include Visualization
        PS->>Viz: Generate Visualization
        Viz->>PS: Return Visualization
        PS->>PS: Combine Results and Visualization
    end
    
    PS->>API: Return Formatted Results
    API->>User: Deliver Results
```

### Output Formats

The system supports multiple output formats for analysis results:

1. **JSON Format**: Structured data for API consumers and web applications
2. **CSV Format**: Tabular data for spreadsheet applications
3. **Text Format**: Human-readable summaries for reports and notifications
4. **Visualization**: Charts and graphs for visual representation of trends

### JSON Output Structure

```json
{
  "metadata": {
    "analysis_id": "string",
    "time_period": {
      "start_date": "ISO8601 date",
      "end_date": "ISO8601 date",
      "granularity": "string"
    },
    "filters": {
      "routes": ["string"],
      "carriers": ["string"]
    },
    "generated_at": "ISO8601 datetime"
  },
  "results": {
    "absolute_change": {
      "value": number,
      "unit": "string"
    },
    "percentage_change": {
      "value": number,
      "formatted": "string"
    },
    "trend": {
      "direction": "string",
      "indicator": "string"
    },
    "aggregates": {
      "start_period": {
        "average": number,
        "minimum": number,
        "maximum": number
      },
      "end_period": {
        "average": number,
        "minimum": number,
        "maximum": number
      }
    }
  },
  "time_series": [
    {
      "timestamp": "ISO8601 datetime",
      "value": number
    }
  ]
}
```

### Visualization Types

The system generates several types of visualizations for analysis results:

1. **Line Charts**: Time series visualization of freight charges
2. **Bar Charts**: Comparative visualization of different periods
3. **Trend Indicators**: Visual representation of trend direction
4. **Comparison Charts**: Side-by-side comparison of different analyses

## External System Integration

The system integrates with various external systems for data exchange and interoperability.

### Integration Flow Diagram

```mermaid
graph TD
    subgraph "Freight Price Movement Agent"
        A[Integration Service]
        B[Data Ingestion Service]
        C[Analysis Engine]
        D[Presentation Service]
    end
    
    subgraph "External Systems"
        E[TMS Systems]
        F[ERP Systems]
        G[Rate APIs]
        H[Reporting Tools]
    end
    
    A <-->|Data Collection| E
    A <-->|Cost Data| F
    A <-->|Market Rates| G
    D -->|Analysis Results| H
    
    A -->|Standardized Data| B
    B -->|Stored Data| C
    C -->|Analysis Results| D
```

### TMS Integration

Integration with Transportation Management Systems:

1. **Data Retrieval**: Freight rates, shipment details, carrier information
2. **Authentication**: OAuth 2.0, API keys, or custom authentication
3. **Connection Methods**: REST API, SOAP API, or database connection
4. **Supported Systems**: SAP TM, Oracle TMS, JDA TMS, and others

### ERP Integration

Integration with Enterprise Resource Planning systems:

1. **Data Retrieval**: Cost data, vendor information, accounting codes
2. **Authentication**: System-specific authentication methods
3. **Connection Methods**: API, database, or file-based integration
4. **Supported Systems**: SAP ERP, Oracle ERP, Microsoft Dynamics, and others

### API Integration

Integration with external freight rate APIs:

1. **Data Retrieval**: Market rates, benchmark data, historical trends
2. **Authentication**: API keys, OAuth, or custom tokens
3. **Connection Methods**: REST API with JSON or XML formats
4. **Supported APIs**: Freightos Baltic Index, World Container Index, and others

## Error Handling and Recovery

The system implements comprehensive error handling and recovery mechanisms throughout the data flow.

### Error Handling Flow

```mermaid
flowchart TD
    A[Error Detected] --> B{Error Type?}
    
    B -->|Data Source| C[Log Connection Error]
    C --> D{Retry Possible?}
    D -->|Yes| E[Wait for Retry Interval]
    E --> F[Increment Retry Counter]
    F --> G{Max Retries Reached?}
    G -->|No| H[Attempt Reconnection]
    H --> I{Reconnection Successful?}
    I -->|Yes| J[Resume Operation]
    I -->|No| K[Return to Retry Decision]
    K --> D
    
    G -->|Yes| L[Escalate to Critical Error]
    
    D -->|No| L
    
    B -->|Validation| M[Log Validation Error]
    M --> N[Identify Invalid Fields]
    N --> O[Generate User-Friendly Message]
    O --> P[Return Validation Error Response]
    
    B -->|Calculation| Q[Log Calculation Error]
    Q --> R{Error Type?}
    R -->|Divide by Zero| S[Handle Division Edge Case]
    R -->|Overflow| T[Scale Values and Retry]
    R -->|Other| U[Capture Error Details]
    
    S --> V[Apply Fallback Calculation]
    T --> V
    U --> W[Return Partial Results if Available]
    V --> W
    
    B -->|System| X[Log System Error]
    X --> Y[Capture Stack Trace]
    Y --> Z[Notify System Administrator]
    Z --> AA[Return Service Unavailable]
    
    L --> AB[Notify Administrator]
    AB --> AC[Suggest Alternative Data Source]
    AC --> AD[Return Service Error]
    
    P --> AE[End with User Guidance]
    W --> AF[End with Partial Results]
    AA --> AG[End with System Error]
    AD --> AH[End with Critical Error]
    J --> AI[End with Recovery]
```

### Error Categories

The system handles several categories of errors:

1. **Data Source Errors**: Connection failures, authentication issues, timeout errors
2. **Validation Errors**: Schema violations, data type mismatches, business rule violations
3. **Calculation Errors**: Division by zero, numeric overflow, algorithm failures
4. **System Errors**: Resource exhaustion, component failures, unexpected exceptions

### Retry Mechanisms

The system implements retry mechanisms for transient errors:

1. **Exponential Backoff**: Increasing delay between retry attempts
2. **Circuit Breaker**: Preventing repeated failures by temporarily disabling problematic connections
3. **Fallback Options**: Alternative data sources or calculation methods when primary options fail

### Data Recovery

The system includes data recovery mechanisms:

1. **Transaction Rollback**: Database transactions ensure data consistency
2. **Partial Results**: Returning available results when complete processing fails
3. **Data Correction**: Automated correction of minor data issues
4. **Audit Logging**: Comprehensive logging for troubleshooting and recovery

## Caching and Performance Optimization

The system employs various caching and optimization techniques to ensure high performance and responsiveness.

### Caching Architecture

```mermaid
graph TD
    A[User Request] --> B{Cache Check}
    
    B -->|Cache Hit| C[Return Cached Result]
    B -->|Cache Miss| D[Process Request]
    
    D --> E[Store in Cache]
    E --> F[Return Fresh Result]
    C --> G[Response to User]
    F --> G
    
    subgraph "Cache Layers"
        H[API Response Cache]
        I[Analysis Result Cache]
        J[Query Cache]
        K[Reference Data Cache]
    end
    
    B -.->|Check| H
    B -.->|Check| I
    D -.->|Check| J
    D -.->|Check| K
    
    E -.->|Update| H
    E -.->|Update| I
    E -.->|Update| J
    E -.->|Update| K
```

### Cache Types and TTLs

The system implements multiple cache types with different time-to-live (TTL) values:

1. **Analysis Result Cache**: 60 minutes TTL, invalidated on data updates
2. **Query Cache**: 15 minutes TTL, automatic invalidation on data changes
3. **Reference Data Cache**: 24 hours TTL, explicit invalidation on updates
4. **API Response Cache**: 5 minutes TTL, varies by endpoint

### Database Optimization

Database performance is optimized through several techniques:

1. **Indexing Strategy**: B-tree indexes on frequently queried fields
2. **Partitioning**: Time-based partitioning for efficient queries
3. **Query Optimization**: Execution plan analysis and optimization
4. **Connection Pooling**: Efficient reuse of database connections

### Computational Optimization

Computational performance is optimized through:

1. **Vectorized Operations**: Using NumPy for efficient calculations
2. **Parallel Processing**: Multi-threaded calculations for large datasets
3. **Incremental Processing**: Processing only new or changed data
4. **Materialized Views**: Pre-calculated aggregates for common metrics

## Batch Processing Flows

The system supports batch processing for scheduled operations and large dataset handling.

### Batch Processing Sequence

```mermaid
sequenceDiagram
    participant Scheduler
    participant BatchProcessor
    participant DataSource
    participant DataStorage
    participant AnalysisEngine
    
    Scheduler->>BatchProcessor: Trigger batch job
    BatchProcessor->>DataSource: Request data chunk
    DataSource->>BatchProcessor: Return data chunk
    BatchProcessor->>BatchProcessor: Process data
    BatchProcessor->>DataStorage: Store processed data
    
    loop Until complete
        BatchProcessor->>DataSource: Request next chunk
        DataSource->>BatchProcessor: Return next chunk
        BatchProcessor->>BatchProcessor: Process data
        BatchProcessor->>DataStorage: Store processed data
    end
    
    BatchProcessor->>AnalysisEngine: Trigger analysis
    AnalysisEngine->>DataStorage: Retrieve data
    AnalysisEngine->>AnalysisEngine: Perform analysis
    AnalysisEngine->>DataStorage: Store results
    BatchProcessor->>Scheduler: Report completion
```

### Scheduled Operations

The system supports several scheduled batch operations:

1. **Data Import**: Scheduled import from external systems
2. **Historical Analysis**: Periodic analysis of historical data
3. **Data Archival**: Moving aged data to archive storage
4. **Report Generation**: Scheduled generation of standard reports

### Batch Processing Optimization

Batch processing is optimized through several techniques:

1. **Chunking**: Processing data in manageable chunks
2. **Parallel Processing**: Distributing work across multiple workers
3. **Resource Management**: Scheduling batch jobs during off-peak hours
4. **Progress Tracking**: Monitoring and reporting batch job progress

### Failure Handling

Batch processing includes robust failure handling:

1. **Checkpointing**: Saving progress at regular intervals
2. **Resumable Jobs**: Ability to resume from the last successful checkpoint
3. **Partial Success**: Processing valid records while logging invalid ones
4. **Notification**: Alerting administrators of batch job failures

## Monitoring and Observability

The system includes comprehensive monitoring and observability features to track data flow and system health.

### Monitoring Architecture

```mermaid
graph TD
    subgraph "Application Components"
        A1[Data Ingestion Service]
        A2[Analysis Engine]
        A3[Presentation Service]
        A4[Integration Service]
    end
    
    subgraph "Monitoring Infrastructure"
        B1[Metrics Collection]
        B2[Log Aggregation]
        B3[Distributed Tracing]
        B4[Alerting System]
    end
    
    subgraph "Visualization & Analysis"
        C1[Dashboards]
        C2[Log Search & Analysis]
        C3[Trace Visualization]
        C4[Alert Management]
    end
    
    A1 -->|Metrics| B1
    A2 -->|Metrics| B1
    A3 -->|Metrics| B1
    A4 -->|Metrics| B1
    
    A1 -->|Logs| B2
    A2 -->|Logs| B2
    A3 -->|Logs| B2
    A4 -->|Logs| B2
    
    A1 -->|Traces| B3
    A2 -->|Traces| B3
    A3 -->|Traces| B3
    A4 -->|Traces| B3
    
    B1 -->|Processed Metrics| C1
    B2 -->|Indexed Logs| C2
    B3 -->|Structured Traces| C3
    
    B1 -->|Threshold Alerts| B4
    B2 -->|Log Pattern Alerts| B4
    B3 -->|Trace Anomaly Alerts| B4
    
    B4 -->|Managed Alerts| C4
```

### Key Metrics

The system tracks several key metrics for data flow monitoring:

1. **Ingestion Metrics**: Records processed, validation errors, processing time
2. **Analysis Metrics**: Analyses performed, calculation time, cache hit ratio
3. **Storage Metrics**: Database size, query performance, cache utilization
4. **API Metrics**: Request rate, response time, error rate

### Log Aggregation

The system implements centralized log aggregation:

1. **Application Logs**: Component-specific operational logs
2. **Data Flow Logs**: Tracking data movement between components
3. **Error Logs**: Detailed error information with context
4. **Audit Logs**: Security and compliance-related events

### Distributed Tracing

The system implements distributed tracing to track requests across components:

1. **End-to-End Tracing**: Following requests from API to database and back
2. **Component Spans**: Measuring time spent in each component
3. **Dependency Tracking**: Monitoring external system interactions
4. **Error Correlation**: Linking errors across components

## Conclusion

This document has provided a comprehensive overview of the data flow architecture in the Freight Price Movement Agent system. Understanding these data flows is essential for effective development, maintenance, and troubleshooting of the system.

The multi-stage architecture with clear separation between ingestion, storage, analysis, and presentation layers ensures a modular, maintainable system that can scale to meet the needs of freight price analysis. The various optimization techniques, error handling mechanisms, and monitoring capabilities ensure reliable operation and high performance.