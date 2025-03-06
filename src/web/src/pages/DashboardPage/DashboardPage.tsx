import React, { useState, useEffect } from 'react'; // ^18.2.0
import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import RecentPriceChanges from '../../components/dashboard/RecentPriceChanges';
import PriceTrendChart from '../../components/dashboard/PriceTrendChart';
import SavedAnalyses from '../../components/dashboard/SavedAnalyses';
import AlertsWidget from '../../components/dashboard/AlertsWidget';
import useApi from '../../hooks/useApi';
import { getRecentAnalysisResults } from '../../api/analysis-api';
import useMediaQuery from '../../hooks/useMediaQuery';
import { AnalysisRequest } from '../../types/analysis.types';

/**
 * Main dashboard page component that displays an overview of freight price movements
 * @returns {JSX.Element} The rendered dashboard page
 */
const DashboardPage: React.FC = () => {
  // Initialize API hook for recent analysis results
  const { state, actions } = useApi(getRecentAnalysisResults);
  const { data, isLoading, isError } = state;
  const { execute } = actions;

  // Initialize state for dashboard data
  const [recentAnalyses, setRecentAnalyses] = useState<any[]>([]);

  // Check if screen is mobile using useMediaQuery hook
  const isMobile = useMediaQuery('(max-width: 767px)');

  // Fetch recent analysis results on component mount
  useEffect(() => {
    execute(7); // Fetch last 7 days of data
  }, [execute]);

  // Handle loading and error states
  if (isLoading) {
    return (
      <MainLayout>
        <PageHeader title="Dashboard" />
        <div>Loading dashboard data...</div>
      </MainLayout>
    );
  }

  if (isError) {
    return (
      <MainLayout>
        <PageHeader title="Dashboard" />
        <div>Error loading dashboard data. Please try again later.</div>
      </MainLayout>
    );
  }

  // Render the main layout with appropriate page header
  return (
    <MainLayout>
      <PageHeader title="Dashboard" />

      {/* Render dashboard widgets in a responsive grid layout */}
      <div className="dashboard-grid">
        {/* Display RecentPriceChanges widget with recent price movements */}
        <RecentPriceChanges onViewDetails={() => console.log('View details clicked')} />

        {/* Display PriceTrendChart widget with 30-day price trend */}
        <PriceTrendChart days={30} />

        {/* Display SavedAnalyses widget with user's saved analyses */}
        <SavedAnalyses
          limit={5}
          onViewAnalysis={(analysis: AnalysisRequest) =>
            console.log('View analysis clicked', analysis)
          }
          onNewAnalysis={() => console.log('New analysis clicked')}
        />

        {/* Display AlertsWidget with system alerts and notifications */}
        <AlertsWidget />
      </div>
    </MainLayout>
  );
};

export default DashboardPage;