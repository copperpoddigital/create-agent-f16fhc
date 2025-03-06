# Contributing to Freight Price Movement Agent

Thank you for considering contributing to the Freight Price Movement Agent! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose
- PostgreSQL 13 with TimescaleDB extension
- Redis 6.x

### Backend Setup

1. Clone the repository
2. Navigate to `src/backend`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment
5. Install dependencies: `pip install -r requirements.txt` or `poetry install`
6. Copy `.env.example` to `.env` and configure environment variables
7. Run migrations: `flask db upgrade`
8. Start the development server: `flask run`

### Frontend Setup

1. Navigate to `src/web`
2. Install dependencies: `npm install`
3. Copy `.env.development` to `.env.local` and configure environment variables
4. Start the development server: `npm run dev`

### Docker Setup

1. Ensure Docker and Docker Compose are installed
2. Run `docker-compose up` from the project root
3. Access the application at http://localhost:3000

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints
- Document functions and classes with docstrings
- Format code with Black
- Sort imports with isort
- Validate with flake8

### TypeScript/JavaScript

- Follow the project's ESLint configuration
- Use TypeScript for type safety
- Format code with Prettier
- Use functional components with hooks for React

### CSS

- Follow BEM naming convention
- Use CSS variables for theming
- Ensure responsive design

### Documentation

- Document all public APIs
- Keep README and documentation up to date
- Use clear commit messages following conventional commits format

## Testing Requirements

### Backend Tests

- Write unit tests for all business logic
- Write integration tests for API endpoints
- Ensure minimum 85% code coverage
- Run tests with `pytest`

### Frontend Tests

- Write unit tests for components and hooks
- Write integration tests for pages
- Use React Testing Library and Jest
- Run tests with `npm test`

### End-to-End Tests

- Write E2E tests for critical user flows
- Use Cypress for E2E testing
- Run E2E tests with `npm run test:e2e`

## Pull Request Process

### Branch Naming

- `feature/short-description` for new features
- `bugfix/short-description` for bug fixes
- `hotfix/short-description` for critical fixes
- `docs/short-description` for documentation changes

### Commit Messages

Follow the Conventional Commits format:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `test: add tests`
- `refactor: improve code structure`
- `chore: update dependencies`

### Pull Request Submission

1. Ensure all tests pass
2. Update documentation if necessary
3. Fill out the pull request template
4. Request review from maintainers
5. Address review feedback

### Code Review

- All code changes require at least one review
- Address all review comments
- Ensure CI checks pass before merging

## Release Process

### Versioning

We follow Semantic Versioning (SemVer):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality
- PATCH version for backwards-compatible bug fixes

### Release Checklist

1. Update CHANGELOG.md
2. Update version numbers
3. Create a release tag
4. Deploy to staging for verification
5. Deploy to production

## Additional Resources

- [Project Documentation](docs/)
- [API Reference](docs/api/api-reference.md)
- [Architecture Overview](docs/architecture/)
- [Development Guide](docs/development/)