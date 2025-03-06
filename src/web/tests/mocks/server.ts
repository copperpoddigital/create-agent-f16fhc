import { setupServer } from 'msw/node'; // v1.0.0
import { handlers } from './handlers';

/**
 * Mock Service Worker (MSW) server for testing the Freight Price Movement Agent web application.
 * 
 * This server intercepts all HTTP requests during tests and responds with mock data
 * defined in handlers.ts. It provides consistent mock responses for all API endpoints
 * including authentication, data sources, freight price analysis, and reporting.
 * 
 * Using this server allows testing components that depend on API data without making
 * actual network requests, ensuring consistent test behavior regardless of backend state.
 * 
 * Usage in test setup:
 * ```
 * // In setupTests.ts
 * import { server } from './tests/mocks/server';
 * 
 * beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
 * afterEach(() => server.resetHandlers());
 * afterAll(() => server.close());
 * ```
 * 
 * For testing error scenarios in individual tests:
 * ```
 * import { rest } from 'msw';
 * import { server } from '../../tests/mocks/server';
 * import { API_CONFIG } from '../../src/config/api-config';
 * 
 * test('handles error scenario', () => {
 *   const apiPath = `${API_CONFIG.BASE_URL}${API_CONFIG.API_PATH}/${API_CONFIG.VERSION}`;
 *   server.use(
 *     rest.post(`${apiPath}/analysis/requests`, (req, res, ctx) => {
 *       return res(ctx.status(500));
 *     })
 *   );
 *   // Test code that should handle the 500 error...
 * });
 * ```
 */
export const server = setupServer(...handlers);