import LoginForm, { LoginFormProps } from './LoginForm';
import AnalysisForm, { AnalysisFormProps } from './AnalysisForm';
import DataSourceForm, { DataSourceFormProps } from './DataSourceForm';
import PasswordChangeForm, { PasswordChangeFormProps } from './PasswordChangeForm';
import ReportForm, { ReportFormProps } from './ReportForm';
import UserProfileForm, { UserProfileFormProps } from './UserProfileForm';

/**
 * Barrel file that exports all form components from the forms directory,
 * providing a centralized import point for form components used throughout the
 * Freight Price Movement Agent application.
 */

// Export LoginForm component and its props
export { LoginForm };
export type { LoginFormProps };

// Export AnalysisForm component and its props
export { AnalysisForm };
export type { AnalysisFormProps };

// Export DataSourceForm component and its props
export { DataSourceForm };
export type { DataSourceFormProps };

// Export PasswordChangeForm component and its props
export { PasswordChangeForm };
export type { PasswordChangeFormProps };

// Export ReportForm component and its props
export { ReportForm };
export type { ReportFormProps };

// Export UserProfileForm component and its props
export { UserProfileForm };
export type { UserProfileFormProps };