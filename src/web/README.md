# Freight Price Movement Agent - Web Frontend

## Overview

This is the web frontend for the Freight Price Movement Agent application, a system designed to track, analyze, and report changes in freight charges over specified time periods. The frontend provides an intuitive user interface for logistics professionals to analyze freight price movements and make data-driven decisions.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material UI (MUI)
- **State Management**: React Query for server state, Zustand for client state
- **Form Handling**: Formik with Yup validation
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Data Visualization**: Chart.js with react-chartjs-2
- **Testing**: Jest, React Testing Library, Cypress
- **Internationalization**: i18next

## Prerequisites

- Node.js >= 16.0.0
- npm >= 8.0.0

## Getting Started

### Installation

```bash
# Clone the repository (if not already done)
git clone [repository-url]
cd [repository-directory]/src/web

# Install dependencies
npm install
```

### Environment Setup

Create the following environment files as needed:

- `.env.development` - Development environment variables
- `.env.production` - Production environment variables
- `.env.test` - Test environment variables

Example `.env.development` file:

```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Freight Price Movement Agent (Dev)
```

## Available Scripts

### Development

```bash
# Start development server
npm run dev

# Preview production build locally
npm run preview
```

### Building

```bash
# Create production build
npm run build
```

### Testing

```bash
# Run unit and integration tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate test coverage report
npm run test:coverage

# Run end-to-end tests
npm run test:e2e

# Open Cypress test runner
npm run test:e2e:open
```

### Code Quality

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format

# Type check without emitting files
npm run typecheck
```

## Project Structure

```
src/
├── api/              # API client and service functions
├── components/       # Reusable UI components
│   ├── common/       # Generic UI components
│   ├── layout/       # Layout components
│   ├── charts/       # Data visualization components
│   ├── forms/        # Form components
│   ├── dashboard/    # Dashboard-specific components
│   ├── analysis/     # Analysis-specific components
│   ├── data-sources/ # Data source management components
│   └── reports/      # Report-related components
├── config/           # Application configuration
├── contexts/         # React context providers
├── hooks/            # Custom React hooks
├── pages/            # Page components
├── routes/           # Routing configuration
├── styles/           # Global styles and themes
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

## Development Guidelines

### Code Style

This project uses ESLint and Prettier for code formatting and style enforcement. Configuration is provided in `.eslintrc.js` and `.prettierrc`. The project is set up with pre-commit hooks using Husky and lint-staged to ensure code quality.

### Component Development

- Follow the component structure with separate files for the component, tests, and index export
- Use TypeScript interfaces for component props
- Write unit tests for components using React Testing Library
- Document complex components with JSDoc comments

### State Management

- Use React Query for server state (API data)
- Use Zustand for global client state
- Use React Context for theme, authentication, and notifications
- Use local component state for UI-specific state

### Testing Strategy

- **Unit Tests**: Test individual components and utilities in isolation
- **Integration Tests**: Test component interactions and context providers
- **End-to-End Tests**: Test complete user flows with Cypress

## Building for Production

The production build process optimizes the application for performance:

1. TypeScript compilation and type checking
2. Code bundling and minification with Vite
3. CSS optimization and extraction
4. Asset optimization
5. Code splitting for efficient loading

The build output is generated in the `dist` directory and can be deployed to any static hosting service.

## Deployment

The application can be deployed using various methods:

### Docker

A Dockerfile is provided for containerized deployment. Build and run the container:

```bash
# Build the Docker image
docker build -t freight-price-movement-web .

# Run the container
docker run -p 80:80 freight-price-movement-web
```

### Static Hosting

The built application can be deployed to any static hosting service like Netlify, Vercel, AWS S3, or GitHub Pages.

## Browser Support

The application supports the following browsers:

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Troubleshooting

### Common Issues

- **API Connection Issues**: Verify the API URL in the environment variables
- **Build Failures**: Check for TypeScript errors with `npm run typecheck`
- **Test Failures**: Ensure the test environment is properly configured

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Contact

For questions or support, contact the Freight Price Movement Team.