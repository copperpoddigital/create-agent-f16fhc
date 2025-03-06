import React, { useEffect } from 'react';
import Card from '../../common/Card';
import Button from '../../common/Button';
import Spinner from '../../common/Spinner';
import useApi from '../../../hooks/useApi';
import { getAnalysisRequests } from '../../../api/analysis-api';
import { AnalysisRequest } from '../../../types/analysis.types';
import { formatRelativeDate } from '../../../utils/date-utils';

/**
 * Props interface for the SavedAnalyses component
 */
interface SavedAnalysesProps {
  /** Maximum number of analyses to display */
  limit?: number;
  /** Callback when user selects an analysis to view */
  onViewAnalysis: (analysis: AnalysisRequest) => void;
  /** Callback when user wants to create a new analysis */
  onNewAnalysis: () => void;
}

/**
 * A dashboard widget component that displays a list of saved freight price movement analyses
 * with their last update times. It allows users to view existing analyses or create
 * new ones directly from the dashboard.
 */
const SavedAnalyses: React.FC<SavedAnalysesProps> = ({ 
  limit = 5, 
  onViewAnalysis, 
  onNewAnalysis 
}) => {
  const { 
    state: { data, isLoading, isError },
    actions: { execute }
  } = useApi(getAnalysisRequests);

  useEffect(() => {
    execute({ 
      page: 1, 
      pageSize: limit, 
      sortBy: null, 
      sortDirection: null 
    });
  }, [execute, limit]);

  const handleAnalysisClick = (analysis: AnalysisRequest) => {
    onViewAnalysis(analysis);
  };

  const handleAnalysisKeyDown = (e: React.KeyboardEvent, analysis: AnalysisRequest) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onViewAnalysis(analysis);
    }
  };

  return (
    <Card title="Saved Analyses">
      <div className="saved-analyses">
        {isLoading ? (
          <div className="saved-analyses__loading">
            <Spinner />
          </div>
        ) : isError ? (
          <div className="saved-analyses__error">
            <p>Failed to load saved analyses. Please try again later.</p>
          </div>
        ) : !data?.data || data.data.length === 0 ? (
          <div className="saved-analyses__empty">
            <p>No saved analyses found.</p>
          </div>
        ) : (
          <ul className="saved-analyses__list" aria-label="Saved analyses">
            {data.data.slice(0, limit).map((analysis: AnalysisRequest) => (
              <li 
                key={analysis.id} 
                className="saved-analyses__item"
                onClick={() => handleAnalysisClick(analysis)}
                onKeyDown={(e) => handleAnalysisKeyDown(e, analysis)}
                tabIndex={0}
                role="button"
                aria-label={`View ${analysis.name}`}
              >
                <div className="saved-analyses__item-name">{analysis.name}</div>
                <div className="saved-analyses__item-date">
                  Last updated: {formatRelativeDate(analysis.updated_at || analysis.created_at)}
                </div>
              </li>
            ))}
          </ul>
        )}
        <div className="saved-analyses__footer">
          <Button 
            onClick={onNewAnalysis}
            aria-label="Create new analysis"
          >
            + New Analysis
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default SavedAnalyses;