# Development Environment Setup Guide

## Introduction

This document provides comprehensive setup instructions for developers working on the Freight Price Movement Agent project. It covers environment setup, installation, configuration, and development workflows for both backend and frontend components.

## Prerequisites

Before setting up the development environment, ensure you have the following prerequisites installed on your system:

### Required Software

- Python 3.9 or higher
- Node.js 16.0.0 or higher
- npm 8.0.0 or higher
- Git 2.30 or higher
- Docker and Docker Compose
- PostgreSQL 13 or higher with TimescaleDB extension
- Redis 6.x or higher

### Recommended Tools

- Poetry for Python dependency management
- Visual Studio Code or PyCharm for development
- Postman or Insomnia for API testing
- pgAdmin or DBeaver for database management

### Access Requirements

- GitHub repository access
- AWS account access (for cloud deployments)
- Development environment credentials

## Repository Setup

Follow these steps to clone the repository and set up the project structure:

```bash
# Clone the repository
git clone https://github.com/organization/freight-price-movement-agent.git
cd freight-price-movement-agent

# Create development branches as needed
git checkout -b feature/your-feature-name
```

### Repository Structure

The repository is organized into the following main directories:

- `src/backend/`: Python backend application
- `src/web/`: React frontend application
- `infrastructure/`: Terraform and deployment configurations
- `docs/`: Project documentation
- `.github/`: GitHub Actions workflows and templates

### Branching Strategy

Follow these branching conventions:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `release/*`: Release preparation branches

Refer to [Coding Standards](coding-standards.md) for more details on the version control workflow.

## Backend Setup

The backend is a Python application built with Flask, SQLAlchemy, and other libraries.

### Using Poetry (Recommended)

Poetry is the recommended tool for managing Python dependencies:

```bash
# Navigate to the backend directory
cd src/backend

# Install Poetry if not already installed
# macOS / Linux / WSL
curl -sSL https://install.python-poetry.org | python3 -
# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip (Alternative)

If you prefer not to use Poetry, you can use pip with a virtual environment:

```bash
# Navigate to the backend directory
cd src/backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the `src/backend` directory with the following configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your local configuration
# Example .env file content:
ENV=development
APP_NAME=Freight Price Movement Agent
APP_VERSION=0.1.0
DEBUG=True
API_PREFIX=/api/v1
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Database settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/freight_db
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# Redis settings
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
RESULT_CACHE_TTL=3600
REFERENCE_CACHE_TTL=86400
QUERY_CACHE_TTL=900

# Authentication settings
JWT_SECRET_KEY=your-secret-key-for-development
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Logging settings
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Database Setup

Set up the PostgreSQL database with TimescaleDB extension:

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE freight_db;"

# Enable TimescaleDB extension (run within the freight_db database)
psql -U postgres -d freight_db -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

# Run database migrations
cd src/backend
alembic upgrade head
```

### Running the Backend

Start the backend development server:

```bash
# Make sure you're in the backend directory with the virtual environment activated
cd src/backend

# Using Poetry
poetry run uvicorn app:app --reload --port 8000

# Or directly if virtual environment is activated
uvicorn app:app --reload --port 8000
```

## Frontend Setup

The frontend is a React application built with TypeScript, Material UI, and other libraries.

### Installing Dependencies

Install the frontend dependencies:

```bash
# Navigate to the web directory
cd src/web

# Install dependencies
npm install
```

### Environment Configuration

Create environment files for development:

```bash
# Create development environment file
cp .env.example .env.development

# Example .env.development content:
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Freight Price Movement Agent (Dev)
```

### Running the Frontend

Start the frontend development server:

```bash
# Make sure you're in the web directory
cd src/web

# Start the development server
npm run dev

# The application will be available at http://localhost:3000
```

## Docker Setup

For a containerized development environment, you can use Docker Compose.

### Building and Starting Containers

Build and start the Docker containers:

```bash
# From the project root directory
docker-compose up -d

# The backend API will be available at http://localhost:8000
# The frontend will be available at http://localhost:3000
```

### Running Migrations in Docker

Run database migrations within the Docker container:

```bash
docker-compose exec backend alembic upgrade head
```

### Accessing Container Shells

Access the shell of a running container:

```bash
# Access backend container shell
docker-compose exec backend bash

# Access frontend container shell
docker-compose exec web sh
```

### Viewing Logs

View container logs:

```bash
# View logs for all containers
docker-compose logs

# View logs for a specific container
docker-compose logs backend
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f
```

## Development Workflow

This section describes the recommended development workflow.

### Backend Development

Follow these steps for backend development:

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Implement your changes following the [Coding Standards](coding-standards.md)
- Run tests to ensure your changes don't break existing functionality
- Format your code using Black and isort
- Commit your changes with descriptive commit messages
- Push your branch and create a pull request

```bash
# Run tests
cd src/backend
pytest

# Run tests with coverage
pytest --cov=src

# Format code
black .
isort .

# Run linting
flake8
```

### Frontend Development

Follow these steps for frontend development:

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Implement your changes following the [Coding Standards](coding-standards.md)
- Run tests to ensure your changes don't break existing functionality
- Format your code using Prettier
- Commit your changes with descriptive commit messages
- Push your branch and create a pull request

```bash
# Run tests
cd src/web
npm test

# Run tests with coverage
npm run test:coverage

# Format code
npm run format

# Run linting
npm run lint
```

### Database Migrations

When making changes to the database schema, create and apply migrations:

```bash
# Create a new migration
cd src/backend
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Working with API Endpoints

The backend API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Use these interfaces to explore and test the API endpoints during development.

## Testing

Testing is an essential part of the development process. This section provides an overview of testing procedures for the Freight Price Movement Agent project.

### Backend Testing

Run backend tests:

```bash
# Navigate to the backend directory
cd src/backend

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_services/test_analysis_engine.py

# Run tests with coverage report
pytest --cov=src
```

### Frontend Testing

Run frontend tests:

```bash
# Navigate to the web directory
cd src/web

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run end-to-end tests
npm run test:e2e
```

## Debugging

This section provides guidance on debugging the application.

### Backend Debugging

Debug the backend application:

- Use the built-in debugger in your IDE (VS Code or PyCharm)
- Add breakpoints in your code
- Use logging with different log levels
- Run the application with the `--debug` flag

```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")

# Run with debug flag
uvicorn app:app --reload --debug
```

### Frontend Debugging

Debug the frontend application:

- Use the React Developer Tools browser extension
- Use the browser's built-in developer tools
- Add console.log statements for debugging
- Use the debugger statement in your code

```javascript
// Add console logging
console.log('Debug value:', someValue);

// Use debugger statement
debugger;

// Use React DevTools for component inspection
```

### API Debugging

Debug API interactions:

- Use the Swagger UI to test API endpoints
- Use Postman or Insomnia for API testing
- Check the Network tab in browser developer tools
- Enable verbose logging in the backend

## Common Issues and Solutions

This section addresses common issues that developers might encounter.

### Database Connection Issues

If you encounter database connection issues:

- Verify that PostgreSQL is running: `pg_isready`
- Check the DATABASE_URL in your .env file
- Ensure the database exists: `psql -U postgres -c "\l"`
- Verify that the TimescaleDB extension is installed: `psql -U postgres -d freight_db -c "\dx"`

### Redis Connection Issues

If you encounter Redis connection issues:

- Verify that Redis is running: `redis-cli ping`
- Check the REDIS_URL in your .env file
- Try connecting manually: `redis-cli`

### Dependency Issues

If you encounter dependency issues:

- Update Poetry: `poetry self update`
- Update dependencies: `poetry update`
- Recreate the virtual environment: `poetry env remove python && poetry install`
- For npm issues: `npm clean-install`

### Docker Issues

If you encounter Docker issues:

- Verify Docker is running: `docker info`
- Check container status: `docker-compose ps`
- View container logs: `docker-compose logs`
- Rebuild containers: `docker-compose build --no-cache`
- Reset containers: `docker-compose down -v && docker-compose up -d`

## Development Tools

This section describes useful development tools and utilities.

### Code Quality Tools

Tools for maintaining code quality:

- Black: Code formatter for Python
- isort: Import sorter for Python
- Flake8: Linter for Python
- Prettier: Code formatter for JavaScript/TypeScript
- ESLint: Linter for JavaScript/TypeScript
- Husky: Git hooks for pre-commit checks

### Database Tools

Tools for working with the database:

- pgAdmin: GUI for PostgreSQL management
- DBeaver: Universal database tool
- psql: Command-line PostgreSQL client
- Alembic: Database migration tool

### API Testing Tools

Tools for testing APIs:

- Swagger UI: Interactive API documentation
- Postman: API development environment
- Insomnia: REST and GraphQL client
- curl: Command-line tool for API requests

### Monitoring Tools

Tools for monitoring the application:

- Prometheus: Metrics collection
- Grafana: Metrics visualization
- ELK Stack: Log aggregation and analysis
- Sentry: Error tracking and performance monitoring

## Continuous Integration

The project uses GitHub Actions for continuous integration.

### CI Workflows

The following CI workflows are configured:

- Backend CI: Runs tests and linting for the backend code
- Web CI: Runs tests and linting for the frontend code
- Infrastructure CI: Validates Terraform configurations

### CI Process

The CI process includes:

- Code checkout
- Dependency installation
- Linting and code quality checks
- Unit and integration tests
- Code coverage reporting
- Docker image building (for certain branches)

### Local CI Validation

You can validate CI checks locally before pushing:

```bash
# Backend checks
cd src/backend
poetry run format  # Runs black and isort
poetry run lint    # Runs flake8
poetry run test    # Runs pytest

# Frontend checks
cd src/web
npm run format
npm run lint
npm test
```

## Additional Resources

Additional resources for development:

- Project documentation: Located in the `docs/` directory
- Coding standards: [Coding Standards](coding-standards.md)
- Testing documentation: Available in the project documentation directory
- API documentation: Available at http://localhost:8000/docs when running the backend
- GitHub repository: https://github.com/organization/freight-price-movement-agent