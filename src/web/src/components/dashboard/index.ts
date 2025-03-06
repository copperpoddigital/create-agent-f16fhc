/**
 * Dashboard Components Barrel File
 * 
 * This file exports all dashboard components to simplify imports throughout the application.
 * It implements the organization of dashboard-related components as specified in the wireframes
 * and follows the React pattern of using index files for cleaner component imports.
 */

import AlertsWidget from './AlertsWidget';
import PriceTrendChart from './PriceTrendChart';
import RecentPriceChanges from './RecentPriceChanges';
import SavedAnalyses from './SavedAnalyses';

export {
  AlertsWidget,
  PriceTrendChart,
  RecentPriceChanges,
  SavedAnalyses
};