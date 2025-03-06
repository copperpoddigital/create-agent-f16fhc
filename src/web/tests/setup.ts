/**
 * Jest setup file for the Freight Price Movement Agent web application.
 * 
 * This file configures the testing environment by:
 * 1. Setting up Mock Service Worker (MSW) to intercept API requests during tests
 * 2. Importing testing library extensions for DOM testing
 * 3. Establishing global test setup and teardown procedures
 */

// Import MSW server for API mocking
import { server } from './mocks/server';

// Import jest-dom for DOM testing extensions
import '@testing-library/jest-dom'; // v5.16.5

// Set up MSW server before tests with strict handling of unhandled requests
// This ensures all API requests are explicitly mocked
global.beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

// Reset request handlers after each test to ensure clean state
// This prevents test pollution between tests
global.afterEach(() => server.resetHandlers());

// Clean up after all tests are done
// This prevents memory leaks and hanging connections
global.afterAll(() => server.close());