/**
 * Interface defining the structure of route configuration objects
 */
export interface RouteConfig {
  /** URL path for the route */
  path: string;
  /** Whether authentication is required for accessing this route */
  requireAuth: boolean;
  /** User roles allowed to access this route, empty means any authenticated user */
  allowedRoles: string[];
  /** Display title for the route */
  title: string;
}

/**
 * Object containing all route configurations for the application
 */
export const ROUTES = {
  LOGIN: {
    path: '/login',
    requireAuth: false,
    allowedRoles: [],
    title: 'Login'
  },
  DASHBOARD: {
    path: '/dashboard',
    requireAuth: true,
    allowedRoles: ['Viewer', 'Analyst', 'Data Manager', 'Administrator'],
    title: 'Dashboard'
  },
  DATA_SOURCES: {
    path: '/data-sources',
    requireAuth: true,
    allowedRoles: ['Data Manager', 'Administrator'],
    title: 'Data Sources'
  },
  ADD_DATA_SOURCE: {
    path: '/data-sources/add',
    requireAuth: true,
    allowedRoles: ['Data Manager', 'Administrator'],
    title: 'Add Data Source'
  },
  EDIT_DATA_SOURCE: {
    path: '/data-sources/edit/:id',
    requireAuth: true,
    allowedRoles: ['Data Manager', 'Administrator'],
    title: 'Edit Data Source'
  },
  ANALYSIS: {
    path: '/analysis',
    requireAuth: true,
    allowedRoles: ['Viewer', 'Analyst', 'Data Manager', 'Administrator'],
    title: 'Analysis'
  },
  NEW_ANALYSIS: {
    path: '/analysis/new',
    requireAuth: true,
    allowedRoles: ['Analyst', 'Data Manager', 'Administrator'],
    title: 'New Analysis'
  },
  ANALYSIS_RESULTS: {
    path: '/analysis/results/:id',
    requireAuth: true,
    allowedRoles: ['Viewer', 'Analyst', 'Data Manager', 'Administrator'],
    title: 'Analysis Results'
  },
  REPORTS: {
    path: '/reports',
    requireAuth: true,
    allowedRoles: ['Viewer', 'Analyst', 'Data Manager', 'Administrator'],
    title: 'Reports'
  },
  CREATE_REPORT: {
    path: '/reports/create',
    requireAuth: true,
    allowedRoles: ['Analyst', 'Data Manager', 'Administrator'],
    title: 'Create Report'
  },
  REPORT_DETAILS: {
    path: '/reports/:id',
    requireAuth: true,
    allowedRoles: ['Viewer', 'Analyst', 'Data Manager', 'Administrator'],
    title: 'Report Details'
  },
  SETTINGS: {
    path: '/settings',
    requireAuth: true,
    allowedRoles: ['Viewer', 'Analyst', 'Data Manager', 'Administrator'],
    title: 'Settings'
  },
  NOT_FOUND: {
    path: '*',
    requireAuth: false,
    allowedRoles: [],
    title: 'Page Not Found'
  }
} as const;

/**
 * Checks if a user has permission to access a specific route based on their role
 * 
 * @param route - The route configuration to check
 * @param userRole - The user's role
 * @returns True if the user has access, false otherwise
 */
export function isRouteAccessible(route: RouteConfig, userRole: string | null): boolean {
  // Public routes don't require authentication
  if (!route.requireAuth) {
    return true;
  }
  
  // If authentication is required but no user role is provided, deny access
  if (!userRole) {
    return false;
  }

  // If no specific roles are required, any authenticated user can access
  if (route.allowedRoles.length === 0) {
    return true;
  }

  // Check if the user's role is included in the allowed roles
  return route.allowedRoles.includes(userRole);
}