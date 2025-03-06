import React, { useState, useEffect } from 'react';
import Card from '../../common/Card';
import Button from '../../common/Button';
import TrendIndicator from '../../charts/TrendIndicator';
import useApi from '../../../hooks/useApi';
import { getRecentAnalysisResults } from '../../../api/analysis-api';
import { AnalysisResultSummary, TrendDirection } from '../../../types/analysis.types';

/**
 * Props interface for the RecentPriceChanges component
 */
interface RecentPriceChangesProps {
  className?: string;
  onViewDetails?: () => void;
  testId?: string;
}

/**
 * Summary of price changes for a specific freight mode
 */
interface FreightModeSummary {
  mode: string;
  percentageChange: number;
  trendDirection: TrendDirection;
}

/**
 * Component that displays recent freight price changes on the dashboard
 * Shows price movements across different freight modes with trend indicators
 * and percentage changes for the last 7 days.
 */
const RecentPriceChanges: React.FC<RecentPriceChangesProps> = ({
  className = '',
  onViewDetails,
  testId = 'recent-price-changes',
}) => {
  // Initialize API hook for fetching recent analysis results
  const { state, actions } = useApi(getRecentAnalysisResults);
  const { data, isLoading, isError } = state;
  const { execute } = actions;
  
  // State to store processed freight mode summaries
  const [modeSummaries, setModeSummaries] = useState<FreightModeSummary[]>([]);
  
  // Fetch data when component mounts
  useEffect(() => {
    // Get the last 7 days of data
    execute(7);
  }, [execute]);
  
  // Process analysis results to extract mode-specific data
  useEffect(() => {
    if (!data || !Array.isArray(data)) {
      return;
    }
    
    // Define the standard modes we want to display (based on wireframe)
    const standardModes = ['Ocean', 'Air', 'Road', 'Rail'];
    
    // Create a mapping of mode -> results
    const modeResults: Record<string, AnalysisResultSummary[]> = {};
    
    // Categorize each result by mode
    data.forEach(result => {
      // Find which mode this result belongs to
      const matchedMode = standardModes.find(mode => 
        result.analysis_name.toLowerCase().includes(mode.toLowerCase())
      );
      
      if (matchedMode) {
        if (!modeResults[matchedMode]) {
          modeResults[matchedMode] = [];
        }
        modeResults[matchedMode].push(result);
      }
    });
    
    // Create summaries for each mode
    const summaries: FreightModeSummary[] = [];
    
    standardModes.forEach(mode => {
      const results = modeResults[mode];
      if (results && results.length > 0) {
        // Sort by calculation date (newest first)
        results.sort((a, b) => 
          new Date(b.calculated_at).getTime() - new Date(a.calculated_at).getTime()
        );
        
        // Use the most recent result for this mode
        const latestResult = results[0];
        
        summaries.push({
          mode,
          percentageChange: latestResult.percentage_change,
          trendDirection: latestResult.trend_direction
        });
      }
    });
    
    setModeSummaries(summaries);
  }, [data]);
  
  // Handle view details button click
  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails();
    }
  };
  
  return (
    <Card
      title="Recent Price Changes"
      subtitle="Last 7 days"
      className={`recent-price-changes ${className}`}
      footer={
        <Button onClick={handleViewDetails}>View Details</Button>
      }
      testId={testId}
    >
      {isLoading ? (
        <div className="recent-price-changes__loading">Loading price changes...</div>
      ) : isError ? (
        <div className="recent-price-changes__error">
          Unable to load recent price changes. Please try again later.
        </div>
      ) : modeSummaries.length === 0 ? (
        <div className="recent-price-changes__empty">No recent price changes available.</div>
      ) : (
        <ul className="recent-price-changes__list">
          {modeSummaries.map(summary => (
            <li key={summary.mode} className="recent-price-changes__item">
              <span className="recent-price-changes__mode">{summary.mode}: </span>
              <span className="recent-price-changes__value">
                {summary.percentageChange > 0 ? '+' : ''}
                {summary.percentageChange.toFixed(1)}%
              </span>
              <TrendIndicator direction={summary.trendDirection} />
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
};

export default RecentPriceChanges;