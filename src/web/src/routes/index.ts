import React from 'react'; // version specified in the documentation
import AppRoutes from './AppRoutes';
import PrivateRoute from './PrivateRoute';
import PublicRoute from './PublicRoute';
import { RouteConfig } from '../config/routes';

// IE3: Export the AppRoutes component as the default export
export { AppRoutes };
export { PrivateRoute };
export { PublicRoute };

export type { RouteConfig };

export default { AppRoutes, PrivateRoute, PublicRoute };