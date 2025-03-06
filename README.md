# Freight Price Movement Agent

<p align="center">
  <img src="src/web/public/assets/images/logo-dark.svg" alt="Freight Price Movement Agent Logo" width="200">
</p>

> An automated system for tracking, analyzing, and reporting changes in freight charges over specified time periods.

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT">
  <img src="https://img.shields.io/badge/python-3.9+-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/typescript-4.5+-blue" alt="TypeScript 4.5+">
</p>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup](#docker-setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Testing](#testing)
  - [Contributing](#contributing)
- [Deployment](#deployment)
- [License](#license)

## Overview

The Freight Price Movement Agent is a comprehensive solution designed to track, analyze, and report changes in freight charges across different time periods. This tool enables logistics professionals to make data-driven decisions by providing clear visibility into price trends and fluctuations.

The system addresses the critical business need for timely, accurate insights into logistics cost fluctuations to support data-driven decision-making in supply chain management. It enables cost optimization, improved budget forecasting, and strategic carrier selection through data-driven insights.

## Features

- **Data Collection & Ingestion**: Automated collection of freight pricing data from multiple sources (CSV, databases, APIs)
- **Time Period Analysis**: Flexible selection of time periods with customizable granularity (daily, weekly, monthly)
- **Price Movement Calculation**: Calculation of absolute and percentage changes in freight prices
- **Trend Identification**: Automatic detection of increasing, decreasing, or stable price trends
- **Visualization**: Interactive charts and graphs for visualizing price movements
- **Multiple Output Formats**: Export results in JSON, CSV, or text summary formats
- **Integration Capabilities**: Connect with TMS and ERP systems for seamless data flow
- **User-friendly Interface**: Intuitive web interface for easy analysis configuration and result viewing

## System Architecture

The Freight Price Movement Agent follows a modular, layered architecture:

- **Frontend**: React/TypeScript web application
- **Backend**: Python Flask API with modular components
- **Database**: PostgreSQL with TimescaleDB extension for time-series data
- **Caching**: Redis for performance optimization
- **Infrastructure**: Docker containers orchestrated with AWS ECS/Kubernetes

![Architecture Diagram](docs/architecture/component-diagram.md)

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+ with TimescaleDB extension
- Redis 6+
- Docker and Docker Compose (optional)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-organization/freight-price-movement-agent.git
cd freight-price-movement-agent

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd src/backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize the database
flask db upgrade

# Run the development server
flask run
```

### Frontend Setup

```bash
# Navigate to the web directory
cd src/web

# Install dependencies
npm install

# Set up environment variables
cp .env.development .env

# Run the development server
npm run dev
```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application at http://localhost:3000
```

## Usage

1. **Configure Data Sources**: Set up connections to your freight data sources (CSV files, databases, APIs)
2. **Create Analysis**: Select time periods, data filters, and analysis options
3. **View Results**: Examine price movements through visualizations and detailed tables
4. **Export Data**: Download results in your preferred format for further analysis or reporting

For detailed usage instructions, please refer to the [User Manual](docs/user/user-manual.md).

## API Documentation

The Freight Price Movement Agent exposes a RESTful API for integration with other systems. The API allows you to:

- Manage data sources
- Configure and run analyses
- Retrieve results in various formats

For detailed API documentation, please refer to the [API Reference](docs/api/api-reference.md) and [API Examples](docs/api/api-examples.md).

## Development

### Project Structure

```
├── src/
│   ├── backend/         # Python Flask backend
│   │   ├── api/         # API endpoints
│   │   ├── connectors/  # Data source connectors
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utility functions
│   └── web/            # React/TypeScript frontend
│       ├── public/      # Static assets
│       └── src/         # Source code
├── infrastructure/     # Deployment configurations
└── docs/              # Documentation
```

### Testing

```bash
# Backend tests
cd src/backend
pytest

# Frontend tests
cd src/web
npm test

# End-to-end tests
cd src/web
npm run cypress:run
```

For more information on testing, see [Testing Documentation](docs/development/testing.md).

### Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Deployment

The application can be deployed using Docker containers on various platforms:

- AWS ECS/Fargate
- Kubernetes
- Self-hosted Docker environments

Detailed deployment instructions are available in the [Deployment Documentation](docs/operations/deployment.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.