# Freight Price Movement Agent - Backend

Backend service for the Freight Price Movement Agent, an automated system designed to track, analyze, and report changes in freight charges over specified time periods.

## Features

- Data ingestion from multiple sources (CSV, databases, APIs, TMS/ERP systems)
- Time period-based freight price movement analysis
- Calculation of absolute and percentage changes in freight prices
- Trend direction identification (increasing, decreasing, stable)
- Result caching for improved performance
- RESTful API for integration with frontend and external systems
- Authentication and authorization with role-based access control
- Comprehensive error handling and logging

## Architecture

The backend follows a modular service-oriented architecture with the following components:

### Core Components

- **API Layer**: FastAPI-based REST API endpoints
- **Data Ingestion Service**: Collects and validates freight data from multiple sources
- **Analysis Engine**: Calculates price movements and identifies trends
- **Presentation Service**: Formats and delivers results
- **Integration Service**: Connects with external enterprise systems
- **Error Handling & Logging**: Comprehensive monitoring and error management

### Data Flow

1. Data is ingested from various sources through the Data Ingestion Service
2. Validated data is stored in the PostgreSQL database
3. Users request analysis through the API
4. Analysis Engine processes the data and calculates price movements
5. Results are cached for future requests
6. Formatted results are returned to the user

## Technology Stack

- **Python 3.9+**: Core programming language
- **FastAPI**: Web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **PostgreSQL**: Primary database with TimescaleDB extension
- **Redis**: Caching layer
- **Pandas/NumPy**: Data processing and analysis
- **Matplotlib**: Data visualization
- **Celery**: Distributed task queue for background processing
- **Pytest**: Testing framework
- **Docker**: Containerization

## Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- PostgreSQL 13+ with TimescaleDB extension
- Redis 6+
- Docker and Docker Compose (optional, for containerized setup)

## Setup and Installation

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/organization/freight-price-movement-agent.git
cd freight-price-movement-agent/src/backend

# Install dependencies using Poetry
poetry install

# Activate the virtual environment
poetry shell

# Create .env file from example
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app:app --reload
```

### Docker Setup

```bash
# Build and start the containers
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# The API will be available at http://localhost:8000
```

## Environment Variables

The application uses the following environment variables, which can be set in the `.env` file:

### Core Settings

```
ENV=development|staging|production
APP_NAME=Freight Price Movement Agent
APP_VERSION=0.1.0
DEBUG=True|False
API_PREFIX=/api/v1
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Database Settings

```
DATABASE_URL=postgresql://user:password@localhost:5432/freight_db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

### Redis Settings

```
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
RESULT_CACHE_TTL=3600
REFERENCE_CACHE_TTL=86400
QUERY_CACHE_TTL=900
```

### Authentication Settings

```
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Logging Settings

```
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=your-sentry-dsn
```

## Project Structure

```
src/backend/
├── api/                  # API endpoints and routes
│   ├── admin/            # Admin API endpoints
│   ├── analysis/         # Analysis API endpoints
│   ├── auth/             # Authentication API endpoints
│   ├── data_sources/     # Data source API endpoints
│   ├── reports/          # Reports API endpoints
│   └── routes.py         # API route registration
├── connectors/           # Data source connectors
│   ├── database_connector.py
│   ├── erp_connector.py
│   ├── file_connector.py
│   ├── generic_api_connector.py
│   └── tms_connector.py
├── core/                 # Core application components
│   ├── cache.py          # Caching functionality
│   ├── config.py         # Configuration management
│   ├── db.py             # Database connection management
│   ├── exceptions.py     # Custom exception classes
│   ├── logging.py        # Logging configuration
│   ├── security.py       # Authentication and security
│   └── schemas.py        # Common Pydantic schemas
├── migrations/           # Alembic database migrations
├── models/               # SQLAlchemy ORM models
│   ├── analysis_result.py
│   ├── audit_log.py
│   ├── carrier.py
│   ├── enums.py          # Enumeration types
│   ├── freight_data.py
│   ├── location.py
│   ├── mixins.py         # Model mixins
│   ├── route.py
│   ├── time_period.py
│   └── user.py
├── schemas/              # Pydantic schemas for API
│   ├── analysis_result.py
│   ├── audit_log.py
│   ├── carrier.py
│   ├── common.py
│   ├── freight_data.py
│   ├── location.py
│   ├── requests.py
│   ├── responses.py
│   ├── route.py
│   ├── time_period.py
│   └── user.py
├── services/             # Business logic services
│   ├── analysis_engine.py
│   ├── data_ingestion.py
│   ├── error_handling.py
│   ├── integration.py
│   ├── notifications.py
│   ├── presentation.py
│   └── scheduler.py
├── tasks/                # Background tasks
│   ├── analysis.py
│   ├── cleanup.py
│   ├── data_export.py
│   ├── data_import.py
│   ├── reporting.py
│   └── worker.py
├── tests/                # Test suite
│   ├── test_api/
│   ├── test_connectors/
│   ├── test_models/
│   ├── test_services/
│   └── test_utils/
├── utils/                # Utility functions
│   ├── api_client.py
│   ├── calculation.py
│   ├── csv_parser.py
│   ├── currency.py
│   ├── date_utils.py
│   ├── db_connector.py
│   ├── formatters.py
│   ├── validators.py
│   └── visualization.py
├── .env.example          # Example environment variables
├── .flaskenv             # Flask environment variables
├── alembic.ini           # Alembic configuration
├── app.py                # Application entry point
├── config.py             # Application configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker configuration
├── poetry.lock           # Poetry lock file
├── pyproject.toml        # Poetry project configuration
└── wsgi.py               # WSGI entry point
```

## API Documentation

Once the application is running, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

The API follows RESTful principles and includes the following main endpoints:

### Authentication

- `POST /api/v1/auth/login`: Authenticate user and get access token
- `POST /api/v1/auth/refresh`: Refresh access token
- `POST /api/v1/auth/logout`: Logout and invalidate token

### Data Sources

- `GET /api/v1/data-sources`: List all data sources
- `POST /api/v1/data-sources`: Register a new data source
- `GET /api/v1/data-sources/{id}`: Get data source details
- `PUT /api/v1/data-sources/{id}`: Update data source
- `DELETE /api/v1/data-sources/{id}`: Delete data source
- `POST /api/v1/data-sources/{id}/ingest`: Trigger data ingestion
- `GET /api/v1/data-sources/{id}/preview`: Preview data from source

### Analysis

- `POST /api/v1/analysis/price-movement`: Analyze price movements
- `GET /api/v1/analysis/results`: List analysis results
- `GET /api/v1/analysis/results/{id}`: Get analysis result details
- `DELETE /api/v1/analysis/results/{id}`: Delete analysis result
- `POST /api/v1/analysis/results/{id}/rerun`: Rerun analysis
- `POST /api/v1/analysis/compare`: Compare two time periods

### Time Periods

- `GET /api/v1/time-periods`: List time periods
- `POST /api/v1/time-periods`: Create a new time period
- `GET /api/v1/time-periods/{id}`: Get time period details
- `PUT /api/v1/time-periods/{id}`: Update time period
- `DELETE /api/v1/time-periods/{id}`: Delete time period

### Reports

- `GET /api/v1/reports`: List reports
- `POST /api/v1/reports`: Create a new report
- `GET /api/v1/reports/{id}`: Get report details
- `PUT /api/v1/reports/{id}`: Update report
- `DELETE /api/v1/reports/{id}`: Delete report
- `POST /api/v1/reports/{id}/run`: Run report
- `GET /api/v1/reports/{id}/export`: Export report

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/backend

# Run specific test file
pytest tests/test_services/test_analysis_engine.py
```

### Code Quality

```bash
# Format code with Black and isort
poetry run format

# Run linting
poetry run lint

# Run type checking
poetry run typecheck

# Run security checks
poetry run security
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

The application can be deployed using Docker and Docker Compose:

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production containers
docker-compose -f docker-compose.prod.yml up -d

# Apply database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Scaling

The application is designed to scale horizontally. You can scale the backend services using Docker Compose or Kubernetes:

```bash
# Scale the backend service
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

## Monitoring

The application includes monitoring capabilities:

### Health Check

A health check endpoint is available at `/health` to verify the application status.

### Metrics

Prometheus metrics are exposed at `/metrics` for monitoring system performance.

### Logging

Logs are output in JSON format for easy integration with log aggregation systems like ELK stack or Graylog.

### Error Tracking

Integration with Sentry for error tracking and performance monitoring is available by setting the `SENTRY_DSN` environment variable.

## Contributing

Please refer to the main project's CONTRIBUTING.md file for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.