import React from 'react'; // version specified in the documentation
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'; // version specified in the documentation
import PrivateRoute from './PrivateRoute';
import PublicRoute from './PublicRoute';
import { ROUTES } from '../config/routes';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import DataSourcesPage from '../pages/DataSourcesPage';
import AddDataSourcePage from '../pages/AddDataSourcePage';
import EditDataSourcePage from '../pages/EditDataSourcePage';
import AnalysisPage from '../pages/AnalysisPage';
import NewAnalysisPage from '../pages/NewAnalysisPage';
import AnalysisResultsPage from '../pages/AnalysisResultsPage';
import ReportsPage from '../pages/ReportsPage';
import CreateReportPage from '../pages/CreateReportPage';
import ReportDetailsPage from '../pages/ReportDetailsPage';
import SettingsPage from '../pages/SettingsPage';
import NotFoundPage from '../pages/NotFoundPage';

/**
 * Main routing component that defines all application routes and their access control
 * @returns The rendered routing structure with all application routes
 */
const AppRoutes: React.FC = () => {
  return (
    // LD1: Wrap the entire routing structure with BrowserRouter
    <BrowserRouter>
      {/* LD1: Define the main Routes component to contain all route definitions */}
      <Routes>
        {/* LD1: Set up a root route that redirects to the dashboard */}
        <Route path="/" element={<Navigate to={ROUTES.DASHBOARD.path} replace />} />

        {/* LD1: Define public routes using the PublicRoute component */}
        <Route
          path={ROUTES.LOGIN.path}
          element={
            <PublicRoute routeConfig={ROUTES.LOGIN}>
              <LoginPage />
            </PublicRoute>
          }
        />

        {/* LD1: Define private routes using the PrivateRoute component */}
        <Route element={<PrivateRoute routeConfig={ROUTES.DASHBOARD} />}>
          <Route path={ROUTES.DASHBOARD.path} element={<DashboardPage />} />
        </Route>

        {/* LD1: Set up nested routes for authenticated sections of the application */}
        <Route element={<PrivateRoute routeConfig={ROUTES.DATA_SOURCES} />}>
          <Route path={ROUTES.DATA_SOURCES.path} element={<DataSourcesPage />} />
          <Route path={ROUTES.ADD_DATA_SOURCE.path} element={<AddDataSourcePage />} />
          {/* IE1: The EditDataSourcePage component is used to edit existing data sources */}
          <Route path={ROUTES.EDIT_DATA_SOURCE.path} element={<EditDataSourcePage />} />
        </Route>

        <Route element={<PrivateRoute routeConfig={ROUTES.ANALYSIS} />}>
          <Route path={ROUTES.ANALYSIS.path} element={<AnalysisPage />} />
          <Route path={ROUTES.NEW_ANALYSIS.path} element={<NewAnalysisPage />} />
          {/* IE1: The AnalysisResultsPage component is used to display analysis results */}
          <Route path={ROUTES.ANALYSIS_RESULTS.path} element={<AnalysisResultsPage />} />
        </Route>

        <Route element={<PrivateRoute routeConfig={ROUTES.REPORTS} />}>
          <Route path={ROUTES.REPORTS.path} element={<ReportsPage />} />
          <Route path={ROUTES.CREATE_REPORT.path} element={<CreateReportPage />} />
          {/* IE1: The ReportDetailsPage component is used to display report details */}
          <Route path={ROUTES.REPORT_DETAILS.path} element={<ReportDetailsPage />} />
        </Route>

        <Route element={<PrivateRoute routeConfig={ROUTES.SETTINGS} />}>
          {/* IE1: The SettingsPage component is used to manage user settings */}
          <Route path={ROUTES.SETTINGS.path} element={<SettingsPage />} />
        </Route>

        {/* LD1: Define a catch-all route for handling 404 errors */}
        <Route
          path="*"
          element={<NotFoundPage />}
        />
      </Routes>
    </BrowserRouter>
  );
};

// IE3: Export the AppRoutes component as the default export
export default AppRoutes;