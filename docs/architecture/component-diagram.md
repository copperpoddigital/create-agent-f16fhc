# Component Diagram

## Introduction

This document provides a comprehensive view of the Freight Price Movement Agent's component architecture, illustrating how different modules interact to deliver the system's functionality.

## High-Level Architecture

The following diagram provides a high-level view of the Freight Price Movement Agent system architecture, showing the main components and their relationships:

```mermaid
graph TD
    subgraph "Data Sources"
        A1[CSV Files] 
        A2[TMS/ERP Systems]
        A3[External APIs]
        A4[Databases]
    end
    
    subgraph "Application Layer"
        B1[Data Ingestion Module]
        B2[Data Quality Management]
        B3[Analysis Engine]
        B4[Result Presentation]
        B5[Error Handling & Logging]
    end
    
    subgraph "Storage Layer"
        C1[(PostgreSQL)]
        C2[(Redis Cache)]
        C3[S3 Storage]
    end
    
    subgraph "Deployment Infrastructure"
        D1[Docker Containers]
        D2[AWS ECS/Kubernetes]
        D3[Load Balancer]
    end
    
    subgraph "Monitoring & Operations"
        E1[Prometheus]
        E2[Grafana]
        E3[Sentry]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    
    B1 --> B2
    B2 --> C1
    B2 --> B3
    B3 --> C2
    B3 --> B4
    B4 --> C3
    
    B1 --> B5
    B2 --> B5
    B3 --> B5
    B4 --> B5
    
    C1 --> B3
    C2 --> B3
    C3 --> B4
    
    B1 --> D1
    B2 --> D1
    B3 --> D1
    B4 --> D1
    B5 --> D1
    
    D1 --> D2
    D2 --> D3
    
    D1 --> E1
    D2 --> E1
    E1 --> E2
    D1 --> E3
```

## Component Details

### Data Ingestion Module

Responsible for collecting, validating, and normalizing freight pricing data from multiple sources.

Subcomponents:
- Source Connector Factory
- Data Validator
- Data Transformer
- Ingestion Orchestrator

```mermaid
graph TD
    A[Data Ingestion Module] --> B[Source Connector Factory]
    A --> C[Data Validator]
    A --> D[Data Transformer]
    A --> E[Ingestion Orchestrator]
    
    B --> B1[CSV Connector]
    B --> B2[Database Connector]
    B --> B3[API Connector]
    B --> B4[TMS/ERP Connector]
    
    C --> C1[Schema Validator]
    C --> C2[Business Rule Validator]
    C --> C3[Anomaly Detector]
    
    D --> D1[Format Standardizer]
    D --> D2[Field Mapper]
    D --> D3[Unit Converter]
    
    E --> E1[Job Scheduler]
    E --> E2[Error Handler]
    E --> E3[Audit Logger]
```

### Analysis Engine

Core computational component responsible for calculating freight price movements and identifying trends based on user-defined parameters.

Subcomponents:
- Query Builder
- Calculation Manager
- Trend Analyzer
- Result Compiler

```mermaid
graph TD
    A[Analysis Engine] --> B[Query Builder]
    A --> C[Calculation Manager]
    A --> D[Trend Analyzer]
    A --> E[Result Compiler]
    
    B --> B1[Time Period Resolver]
    B --> B2[Filter Generator]
    B --> B3[Query Optimizer]
    
    C --> C1[Absolute Change Calculator]
    C --> C2[Percentage Change Calculator]
    C --> C3[Aggregation Processor]
    
    D --> D1[Direction Identifier]
    D --> D2[Pattern Recognizer]
    D --> D3[Anomaly Highlighter]
    
    E --> E1[Metric Formatter]
    E --> E2[Summary Generator]
    E --> E3[Result Cacher]
```

### Presentation Service

Transforms analytical results into user-friendly formats and delivers them through various channels according to user preferences.

Subcomponents:
- Format Converter
- Visualization Generator
- Export Manager
- Delivery Controller

```mermaid
graph TD
    A[Presentation Service] --> B[Format Converter]
    A --> C[Visualization Generator]
    A --> D[Export Manager]
    A --> E[Delivery Controller]
    
    B --> B1[JSON Formatter]
    B --> B2[CSV Formatter]
    B --> B3[Text Formatter]
    
    C --> C1[Chart Generator]
    C --> C2[Table Generator]
    C --> C3[Dashboard Composer]
    
    D --> D1[File Exporter]
    D --> D2[Email Formatter]
    D --> D3[API Response Builder]
    
    E --> E1[Web Delivery]
    E --> E2[Email Delivery]
    E --> E3[API Response Delivery]
```

### Integration Layer

Facilitates communication between the Freight Price Movement Agent and external systems, providing standardized interfaces for data exchange and interoperability.

Subcomponents:
- Adapter Factory
- Authentication Manager
- Data Mapper
- Integration Orchestrator

```mermaid
graph TD
    A[Integration Layer] --> B[Adapter Factory]
    A --> C[Authentication Manager]
    A --> D[Data Mapper]
    A --> E[Integration Orchestrator]
    
    B --> B1[TMS Adapter]
    B --> B2[ERP Adapter]
    B --> B3[API Adapter]
    B --> B4[File System Adapter]
    
    C --> C1[Credential Manager]
    C --> C2[Token Service]
    C --> C3[Certificate Manager]
    
    D --> D1[Schema Mapper]
    D --> D2[Transformation Engine]
    D --> D3[Validation Service]
    
    E --> E1[Job Scheduler]
    E --> E2[Error Handler]
    E --> E3[Audit Logger]
```

### Data Storage Layer

Manages the persistence, retrieval, and organization of all data within the Freight Price Movement Agent, ensuring data integrity, performance, and security.

Subcomponents:
- Primary Data Store
- Caching Layer
- File Storage

```mermaid
graph TD
    A[Data Storage Layer] --> B[Primary Data Store]
    A --> C[Caching Layer]
    A --> D[File Storage]
    
    B --> B1[PostgreSQL with TimescaleDB]
    B --> B2[Time-Series Extension]
    B --> B3[JSON Support]
    
    C --> C1[In-Memory Cache]
    C --> C2[Query Cache]
    C --> C3[Application Cache]
    
    D --> D1[Object Storage]
    D --> D2[Temporary Storage]
    D --> D3[Archive Storage]
```

### Error Handling & Logging

Provides comprehensive monitoring, error management, and audit capabilities across the Freight Price Movement Agent.

Subcomponents:
- Error Classification
- Error Handling Strategy
- Logging Framework
- Audit Logging

```mermaid
graph TD
    A[Error Handling & Logging] --> B[Error Classification]
    A --> C[Error Handling Strategy]
    A --> D[Logging Framework]
    A --> E[Audit Logging]
    
    B --> B1[Validation Errors]
    B --> B2[Processing Errors]
    B --> B3[System Errors]
    B --> B4[Integration Errors]
    B --> B5[Security Errors]
    
    C --> C1[Retry Mechanisms]
    C --> C2[Fallback Strategies]
    C --> C3[Circuit Breakers]
    
    D --> D1[Structured Logging]
    D --> D2[Log Levels]
    D --> D3[Context Enrichment]
    
    E --> E1[Data Access Logging]
    E --> E2[Data Modification Logging]
    E --> E3[Authentication Logging]
```

## Interaction Diagrams

### Data Flow Diagram

Illustrates how data flows through the system from ingestion to presentation.

```mermaid
flowchart TD
    A[Data Sources] --> B[Data Ingestion Service]
    
    B --> C{Source Type?}
    C -->|CSV| D[CSV Parser]
    C -->|API| E[API Client]
    C -->|Database| F[DB Connector]
    
    D --> G[Data Validation]
    E --> G
    F --> G
    
    G --> H{Valid?}
    H -->|No| I[Error Handling]
    I --> J[Error Log]
    
    H -->|Yes| K[Data Transformation]
    K --> L[Staging Area]
    
    L --> M[Data Quality Check]
    M --> N{Quality OK?}
    
    N -->|No| O[Flag for Review]
    O --> P[Review Queue]
    
    N -->|Yes| Q[Load to Database]
    Q --> R[FREIGHT_DATA Table]
    Q --> S[Update Metadata]
    
    R --> T[Update Materialized Views]
    S --> U[Trigger Analysis Jobs]
```

### Analysis Sequence Diagram

Shows the sequence of operations during a price movement analysis.

```mermaid
sequenceDiagram
    participant User
    participant API
    participant AnalysisEngine
    participant DataStorage
    participant Cache
    participant Presentation
    
    User->>API: Request Analysis
    API->>AnalysisEngine: Forward Request
    
    AnalysisEngine->>Cache: Check for Cached Results
    
    alt Cache Hit
        Cache-->>AnalysisEngine: Return Cached Results
    else Cache Miss
        Cache-->>AnalysisEngine: No Cached Data
        AnalysisEngine->>DataStorage: Retrieve Required Data
        DataStorage-->>AnalysisEngine: Return Dataset
        AnalysisEngine->>AnalysisEngine: Perform Calculations
        AnalysisEngine->>Cache: Store Results in Cache
    end
    
    AnalysisEngine->>Presentation: Format Results
    Presentation->>API: Return Formatted Results
    API->>User: Deliver Results
```

### Integration Pattern Diagram

Illustrates how the system integrates with external systems.

```mermaid
sequenceDiagram
    participant FPA as Freight Price Movement Agent
    participant IL as Integration Layer
    participant Auth as Authentication Service
    participant TMS as Transportation Management System
    
    FPA->>IL: Request TMS Integration
    IL->>Auth: Request Authentication
    Auth->>TMS: Authenticate
    TMS-->>Auth: Authentication Response
    Auth-->>IL: Authentication Token
    
    IL->>TMS: Request Freight Data
    TMS-->>IL: Return Raw Data
    
    IL->>IL: Transform Data
    IL->>IL: Validate Data
    
    IL-->>FPA: Deliver Transformed Data
    
    FPA->>FPA: Process Data
    FPA->>IL: Send Analysis Results
    
    IL->>TMS: Update TMS (if required)
    TMS-->>IL: Confirmation
    IL-->>FPA: Integration Complete
```

## Deployment Architecture

The following diagram illustrates how the system components are deployed to the infrastructure.

```mermaid
graph TD
    subgraph "AWS Cloud"
        subgraph "VPC"
            subgraph "Public Subnets"
                C[Application Load Balancer]
                D[NAT Gateway]
                E[API Gateway]
            end
            
            subgraph "Private Subnets - Application Tier"
                F[ECS Services]
                G[Lambda Functions]
            end
            
            subgraph "Private Subnets - Data Tier"
                H[RDS Database]
                I[ElastiCache]
            end
            
            J[S3 Buckets]
            K[VPC Endpoints]
        end
    end
    
    A[End Users] --> C
    B[External Systems] --> E
    C --> F
    E --> G
    F --> H
    F --> I
    F --> K
    G --> K
    K --> J
    F --> D
    G --> D
    D --> L[Internet Gateway]
```

## Conclusion

This component diagram provides a comprehensive view of the Freight Price Movement Agent's architecture. The modular design ensures separation of concerns, maintainability, and scalability, while the integration patterns enable seamless communication with external systems. The deployment architecture leverages cloud infrastructure to provide high availability and performance.