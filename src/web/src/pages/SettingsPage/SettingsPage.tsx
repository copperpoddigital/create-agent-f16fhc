# src/web/src/pages/SettingsPage/SettingsPage.tsx
```typescript
import React, { useState } from 'react'; // v18.2.0
import MainLayout from '../../components/layout/MainLayout';
import PageHeader from '../../components/layout/PageHeader';
import Tabs from '../../components/common/Tabs';
import UserPreferences from '../../components/settings/UserPreferences';
import NotificationSettings from '../../components/settings/NotificationSettings';
import SystemSettings from '../../components/settings/SystemSettings';
import useAuth from '../../hooks/useAuth';
import { Permission } from '../../types/auth.types';

/**
 * Component that renders the settings page with tabs for different settings categories
 * @returns The rendered settings page
 */
const SettingsPage: React.FC = () => {
  // Get authentication state and user information using useAuth hook
  const { state: authState } = useAuth();
  const user = authState.user;

  // Set up state for active tab using useState hook
  const [activeTab, setActiveTab] = useState('user-preferences');

  // Define a function to handle tab changes
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  // Create tabs configuration array with user preferences, notification settings, and system settings (if user has permission)
  const tabs = [
    {
      id: 'user-preferences',
      label: 'User Preferences',
      content: <UserPreferences />,
    },
    {
      id: 'notification-settings',
      label: 'Notifications',
      content: <NotificationSettings />,
    },
    // System settings tab is only visible to users with CONFIGURE_SYSTEM permission
    ...(authState.user?.role === 'admin' || authState.user?.permissions?.includes(Permission.CONFIGURE_SYSTEM)
      ? [
          {
            id: 'system-settings',
            label: 'System Settings',
            content: <SystemSettings />,
          },
        ]
      : []),
  ];

  // Render the page using MainLayout component
  return (
    <MainLayout>
      {/* Include PageHeader with 'Settings' title */}
      <PageHeader title="Settings" />

      {/* Render Tabs component with the configured tabs */}
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={handleTabChange}
      />

      {/* Each tab content renders the corresponding settings component */}
    </MainLayout>
  );
};

// Export the SettingsPage component as the default export
export default SettingsPage;