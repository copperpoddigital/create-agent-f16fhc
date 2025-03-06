# Coding Standards

This document outlines the coding standards and best practices for the Freight Price Movement Agent project. Adhering to these standards ensures code quality, maintainability, and consistency across the codebase.

## General Guidelines

- Write clean, readable, and self-documenting code
- Follow the DRY (Don't Repeat Yourself) principle
- Prioritize code readability over cleverness
- Document complex logic and business rules
- Write code that is testable and maintainable
- Use meaningful variable and function names
- Keep functions and methods focused on a single responsibility
- Limit function/method length to maintain readability (aim for < 50 lines)

## Version Control

### Branching Strategy
- Use feature branches for all new features and bug fixes
- Name branches with the format: `type/description` (e.g., `feature/add-price-calculation`, `bugfix/fix-date-parsing`)
- Keep branches short-lived and focused on a single feature or fix

### Commit Messages
- Write clear, concise commit messages that explain the change
- Use the imperative mood (e.g., "Add feature" not "Added feature")
- Structure commit messages with a summary line (max 50 chars) followed by a blank line and detailed explanation if needed
- Reference issue numbers in commit messages where applicable

### Pull Requests
- Create descriptive pull request titles and descriptions
- Link related issues in the pull request description
- Keep pull requests focused on a single feature or fix
- Ensure all tests pass before requesting review
- Require at least one code review before merging

## Python Standards (Backend)

### Style Guide
- Follow PEP 8 style guide for Python code
- Use Black for code formatting with a line length of 88 characters
- Use isort for import sorting
- Use Flake8 for linting

### Project Structure
- Organize code into logical modules and packages
- Keep module names short and descriptive
- Use `__init__.py` files to define package interfaces

### Imports
- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Use absolute imports for clarity

### Type Hints
- Use type hints for function parameters and return values
- Use Optional[] for parameters that can be None
- Use Union[] for parameters that can be multiple types

### Documentation
- Use docstrings for all public modules, functions, classes, and methods
- Follow Google-style docstrings format
- Include parameter descriptions, return values, and exceptions raised

### Error Handling
- Use specific exception types rather than catching generic exceptions
- Handle exceptions at the appropriate level
- Log exceptions with context information
- Use custom exception classes for application-specific errors

### Testing
- Write unit tests for all functions and methods
- Aim for at least 85% code coverage
- Use pytest for testing
- Use fixtures and parametrized tests where appropriate
- Mock external dependencies in tests

## TypeScript/React Standards (Frontend)

### Style Guide
- Follow the TypeScript ESLint recommended rules
- Use Prettier for code formatting
- Use a line length of 100 characters

### Project Structure
- Organize components by feature or domain
- Use a consistent file naming convention (e.g., PascalCase for component files)
- Keep components focused on a single responsibility

### TypeScript
- Use strict type checking
- Define interfaces for component props and state
- Use type aliases for complex types
- Avoid using `any` type
- Use enums for fixed sets of values

### React Components
- Prefer functional components with hooks over class components
- Use React.FC type for functional components
- Keep components small and focused
- Extract reusable logic into custom hooks
- Use React context for state that needs to be accessed by many components

### State Management
- Use React hooks (useState, useReducer) for local component state
- Use context API for shared state across components
- Keep state as close as possible to where it's used

### Styling
- Use CSS modules or styled-components for component styling
- Follow a consistent naming convention for CSS classes
- Use theme variables for colors, spacing, and typography

### Testing
- Write unit tests for all components and hooks
- Use React Testing Library for component testing
- Test component behavior, not implementation details
- Use mock data for API responses
- Test error states and loading states

## API Design Standards

### RESTful Principles
- Use resource-oriented URLs
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Use consistent URL patterns
- Return appropriate HTTP status codes

### Request/Response Format
- Use JSON for request and response bodies
- Use camelCase for JSON property names
- Include a root element in responses for future extensibility
- Use consistent error response format

### Versioning
- Include API version in the URL path (e.g., `/api/v1/resource`)
- Maintain backward compatibility within a major version

### Documentation
- Document all API endpoints using OpenAPI/Swagger
- Include request parameters, response format, and example responses
- Document error responses and status codes

## Database Standards

### Schema Design
- Use meaningful table and column names
- Use singular form for table names
- Use snake_case for table and column names
- Define appropriate indexes for query performance
- Use foreign key constraints for referential integrity

### SQL Queries
- Write readable SQL with consistent formatting
- Use parameterized queries to prevent SQL injection
- Optimize queries for performance
- Use transactions for operations that modify multiple tables

### Migrations
- Use database migration tools (Alembic for Python)
- Make migrations reversible when possible
- Include descriptive comments in migration files
- Test migrations in development before applying to production

## Security Standards

### Authentication and Authorization
- Use OAuth 2.0 / OIDC for authentication
- Implement role-based access control
- Validate user permissions for all operations
- Use secure password storage with appropriate hashing

### Data Protection
- Encrypt sensitive data at rest and in transit
- Use HTTPS for all API communications
- Implement proper input validation
- Sanitize user input to prevent injection attacks
- Follow the principle of least privilege

### Secrets Management
- Never commit secrets to version control
- Use environment variables or a secure vault for secrets
- Rotate secrets regularly
- Use different secrets for different environments

## Code Review Guidelines

### Process
- All code changes must be reviewed by at least one other developer
- Use pull requests for code reviews
- Provide constructive feedback
- Focus on code quality, not style preferences (which should be handled by automated tools)

### Review Checklist
- Does the code meet the requirements?
- Is the code well-structured and maintainable?
- Are there appropriate tests with good coverage?
- Are there any security concerns?
- Is the code performant and efficient?
- Is the documentation complete and accurate?

### Automated Checks
- CI pipeline must pass before merging
- All tests must pass
- Code coverage must meet minimum thresholds
- Linting and formatting checks must pass

## Performance Standards

### Backend
- Optimize database queries
- Use appropriate caching strategies
- Implement pagination for large datasets
- Use asynchronous processing for long-running tasks

### Frontend
- Minimize bundle size
- Implement code splitting
- Optimize rendering performance
- Use memoization for expensive calculations
- Implement lazy loading for components and routes

## Accessibility Standards

- Follow WCAG 2.1 AA guidelines
- Use semantic HTML elements
- Provide alternative text for images
- Ensure keyboard navigation works correctly
- Maintain sufficient color contrast
- Test with screen readers
- Support text resizing up to 200%

## Documentation Standards

### Code Documentation
- Document public APIs, classes, and functions
- Keep documentation close to the code
- Update documentation when code changes

### Project Documentation
- Maintain up-to-date README files
- Document setup and installation procedures
- Include troubleshooting guides
- Document architecture decisions

### User Documentation
- Provide clear user guides
- Include screenshots and examples
- Document all features and functionality
- Keep documentation up-to-date with new releases

## Continuous Integration and Deployment

### CI Pipeline
- Run automated tests on all pull requests
- Enforce code quality checks
- Build and verify artifacts

### CD Pipeline
- Automate deployments to development and staging environments
- Require manual approval for production deployments
- Implement canary deployments for production
- Include rollback procedures

## Conclusion

These coding standards are designed to ensure high-quality, maintainable code across the Freight Price Movement Agent project. All team members are expected to follow these standards and help enforce them through code reviews and mentoring.

Standards may evolve over time as new best practices emerge or as the project's needs change. Suggestions for improvements to these standards are welcome and should be discussed with the team.