# Freight Price Movement Agent - User Manual

![Freight Price Movement Agent Logo] (Logo placeholder)

**Version 1.0**  
**Last Updated: June 2023**

---

## Table of Contents

1. [Introduction](#1-introduction)
   - [Purpose of the System](#11-purpose-of-the-system)
   - [Key Benefits](#12-key-benefits)
   - [System Overview](#13-system-overview)

2. [Getting Started](#2-getting-started)
   - [System Requirements](#21-system-requirements)
   - [Accessing the System](#22-accessing-the-system)
   - [User Interface Overview](#23-user-interface-overview)
   - [Dashboard Elements](#24-dashboard-elements)

3. [Data Sources Management](#3-data-sources-management)
   - [Supported Data Source Types](#31-supported-data-source-types)
   - [Adding a New Data Source](#32-adding-a-new-data-source)
   - [Configuring CSV Data Sources](#33-configuring-csv-data-sources)
   - [Setting Up Database Connections](#34-setting-up-database-connections)
   - [Configuring API Integrations](#35-configuring-api-integrations)
   - [Managing Existing Data Sources](#36-managing-existing-data-sources)
   - [Troubleshooting Data Connections](#37-troubleshooting-data-connections)

4. [Performing Price Movement Analysis](#4-performing-price-movement-analysis)
   - [Creating a New Analysis](#41-creating-a-new-analysis)
   - [Time Period Selection](#42-time-period-selection)
   - [Data Filtering Options](#43-data-filtering-options)
   - [Analysis Options](#44-analysis-options)
   - [Running the Analysis](#45-running-the-analysis)
   - [Saving Analysis Configurations](#46-saving-analysis-configurations)

5. [Understanding Analysis Results](#5-understanding-analysis-results)
   - [Results Overview](#51-results-overview)
   - [Interpreting Absolute Changes](#52-interpreting-absolute-changes)
   - [Understanding Percentage Changes](#53-understanding-percentage-changes)
   - [Trend Direction Indicators](#54-trend-direction-indicators)
   - [Visualization Options](#55-visualization-options)
   - [Exporting Results](#56-exporting-results)

6. [Working with Reports](#6-working-with-reports)
   - [Report Types](#61-report-types)
   - [Creating Standard Reports](#62-creating-standard-reports)
   - [Scheduling Recurring Reports](#63-scheduling-recurring-reports)
   - [Managing Saved Reports](#64-managing-saved-reports)
   - [Sharing Reports](#65-sharing-reports)

7. [User Settings and Preferences](#7-user-settings-and-preferences)
   - [Personal Profile Settings](#71-personal-profile-settings)
   - [Display Preferences](#72-display-preferences)
   - [Notification Settings](#73-notification-settings)
   - [Administrator Settings](#74-administrator-settings)

8. [Troubleshooting](#8-troubleshooting)
   - [Common Data Import Issues](#81-common-data-import-issues)
   - [Analysis Errors](#82-analysis-errors)
   - [Report Generation Problems](#83-report-generation-problems)
   - [Connectivity Issues](#84-connectivity-issues)
   - [Getting Support](#85-getting-support)

9. [Glossary](#9-glossary)

10. [Appendices](#10-appendices)
    - [Keyboard Shortcuts](#101-keyboard-shortcuts)
    - [Supported File Formats](#102-supported-file-formats)
    - [Calculation Formulas](#103-calculation-formulas)
    - [Integration References](#104-integration-references)

---

## 1. Introduction

### 1.1 Purpose of the System

The Freight Price Movement Agent is a specialized analytics tool designed to track, analyze, and report changes in freight charges over specified time periods. The system addresses the critical business need for timely, accurate insights into logistics cost fluctuations to support data-driven decision-making in supply chain management.

By automating the collection and analysis of freight pricing data, the system enables logistics professionals to identify trends, spot anomalies, and make informed decisions about carrier selection, route optimization, and budget planning.

### 1.2 Key Benefits

**Comprehensive Price Visibility**
- Track freight price movements across all major modes (ocean, air, road, rail)
- Monitor global routes with support for multiple currencies
- Identify cost trends and anomalies with customizable time periods

**Data-Driven Decision Making**
- Support procurement negotiations with historical price insights
- Optimize transportation mode selection based on cost trends
- Improve budget forecasting with accurate cost movement data

**Operational Efficiency**
- Automate manual data collection and analysis processes
- Standardize price movement calculations across the organization
- Generate shareable reports for stakeholders

### 1.3 System Overview

The Freight Price Movement Agent consists of four main functional components:

**Data Collection & Ingestion**
- Import freight pricing data from multiple sources
- Validate and standardize data for analysis
- Manage data connections and synchronization

**Time Period Selection & Analysis**
- Select custom time periods for analysis
- Apply filters to focus on specific routes or carriers
- Configure analysis parameters and granularity

**Price Movement Calculation**
- Calculate absolute and percentage changes in freight prices
- Determine trend directions based on configurable thresholds
- Perform statistical analysis on price movements

**Result Presentation**
- Generate visual representations of price trends
- Format results in multiple output formats (JSON, CSV, text)
- Create and share customized reports

## 2. Getting Started

### 2.1 System Requirements

The Freight Price Movement Agent is a web-based application that supports the following browsers and devices:

**Supported Browsers:**
- Google Chrome (version 90 or later)
- Mozilla Firefox (version 88 or later)
- Microsoft Edge (version 90 or later)
- Apple Safari (version 14 or later)

**Supported Devices:**
- Desktop computers (Windows, macOS, Linux)
- Tablets (iOS 14+ or Android 10+)
- Mobile devices (responsive design with limited functionality)

**Network Requirements:**
- Stable internet connection (minimum 1 Mbps)
- Access to your organization's network (for internal data sources)

### 2.2 Accessing the System

To access the Freight Price Movement Agent:

1. Open your web browser and navigate to the system URL provided by your administrator.
2. On the login screen, enter your username and password.
3. Click the "Login" button to access the system.

![Login Screen] (Screenshot placeholder showing the login screen with username and password fields)

**First-time Login:**
- For first-time users, you may be prompted to change your password.
- Follow the on-screen instructions to set a new password that meets the security requirements.

**Password Recovery:**
- If you forget your password, click the "Forgot Password" link on the login screen.
- Follow the instructions to reset your password via email.

### 2.3 User Interface Overview

Upon successful login, you will be directed to the main dashboard. The user interface consists of the following key elements:

**Main Navigation Menu (Left Sidebar)**
- Dashboard: Overview of recent price changes and saved analyses
- Data Sources: Manage connections to freight pricing data
- Analysis: Create and run price movement analyses
- Reports: Access and manage saved reports
- Settings: Configure user preferences and system settings

**Top Header Bar**
- User profile: Access your account settings
- Notifications: View system alerts and notifications
- Help: Access this user manual and support resources
- Logout: End your session

**Main Content Area**
- Displays the content for the selected navigation item
- Contains interactive elements specific to each section

### 2.4 Dashboard Elements

The dashboard provides an at-a-glance view of freight price movements and system status.

![Dashboard] (Screenshot placeholder showing the main dashboard with key components)

**Recent Price Changes**
- Shows a summary of recent freight price movements by mode
- Displays trend indicators (up/down/stable) for quick reference
- Covers the last 7 days by default

**Price Trend Chart**
- Visualizes freight price trends over the past 30 days
- Allows quick identification of patterns and anomalies
- Provides interactive tooltips with detailed information

**Saved Analyses**
- Lists your recently saved or frequently used analyses
- Shows the last update time for each analysis
- Provides quick access to run or edit each analysis

**Alerts Section**
- Displays important notifications about significant price changes
- Shows data source status alerts
- Provides links to take appropriate action

**Quick Actions**
- Create New Analysis: Start a new price movement analysis
- Import Data: Quick access to data import functionality
- Generate Report: Create a new report based on existing analyses

## 3. Data Sources Management

### 3.1 Supported Data Source Types

The Freight Price Movement Agent supports multiple data source types to accommodate various freight pricing information:

**CSV Files**
- Upload freight pricing data in comma-separated value format
- Support for various delimiter options (comma, semicolon, tab)
- Flexible header mapping for different file structures

**Database Connections**
- Direct connection to internal databases containing freight data
- Support for major database systems (PostgreSQL, MySQL, SQL Server)
- Custom query configuration for data extraction

**API Integrations**
- Connect to external systems via REST or SOAP APIs
- TMS (Transportation Management System) integrations
- ERP (Enterprise Resource Planning) system connections
- External freight rate APIs

**Manual Data Entry**
- Input freight pricing data directly into the system
- Template-based entry for standardized information
- Bulk editing capabilities for existing data

### 3.2 Adding a New Data Source

To add a new data source to the system:

1. Navigate to the "Data Sources" section from the main menu.
2. Click the "+ Add Source" button in the top-right corner.
3. The "Add Data Source" form will appear.

**Basic Source Information:**
- Name: Enter a descriptive name for the data source
- Source Type: Select the type of data source (CSV, Database, API, etc.)
- Description: (Optional) Enter additional details about this data source

![Add Data Source Form] (Screenshot placeholder showing the Add Data Source form)

4. Fill in the connection details specific to your selected source type (see sections 3.3-3.5).
5. Click "Test Connection" to verify the system can access the data source.
6. If the test is successful, click "Save Source" to add it to your data sources.

### 3.3 Configuring CSV Data Sources

When adding a CSV data source, configure the following settings:

**File Upload:**
- Select "Upload File" and choose your CSV file, or
- Drag and drop your CSV file into the designated area
- Maximum file size: 100MB

**File Format Settings:**
- Delimiter: Select the character that separates values (comma, semicolon, tab)
- Text Qualifier: Specify the character that encloses text fields (double quote, single quote)
- Date Format: Choose the date format used in your file (YYYY-MM-DD, MM/DD/YYYY, etc.)
- Decimal Separator: Specify the decimal separator used (period, comma)

**Field Mapping:**
- The system will display a preview of your data and detected columns
- Map each required field to the corresponding column in your CSV:
  - Freight Charge: The column containing the freight price value
  - Currency: The column indicating the currency code
  - Origin: The column showing the starting location
  - Destination: The column showing the delivery location
  - Date/Time: The column containing the date or timestamp

**Advanced Options:**
- Skip Rows: Number of header rows to skip
- Encoding: Select file encoding (UTF-8, ISO-8859-1, etc.)
- Frequency: Set automatic refresh for recurring file uploads

### 3.4 Setting Up Database Connections

When adding a database connection, configure the following settings:

**Connection Details:**
- Database Type: Select your database system (PostgreSQL, MySQL, SQL Server, etc.)
- Server Address: Enter the hostname or IP address of the database server
- Port: Specify the port number (will auto-fill based on database type)
- Database Name: Enter the name of the database containing freight data
- Username: Enter the database username with appropriate read permissions
- Password: Enter the password for database access

**Security Options:**
- SSL Connection: Enable to use encrypted connection to the database
- Connection Timeout: Set maximum wait time for connection attempts
- Store Password: Select whether to save the password in the system

**Data Query:**
- Query Type:
  - Simple Table: Select a table and columns to import
  - Custom SQL: Write a custom SQL query to extract specific data

**For Simple Table:**
- Table Name: Select the table containing freight pricing data
- Column Mapping: Map database columns to required system fields

**For Custom SQL:**
- SQL Query: Enter your custom SQL statement
- Test Query: Verify the query returns the expected results
- Column Mapping: Map query result columns to required system fields

### 3.5 Configuring API Integrations

When adding an API integration, configure the following settings:

**API Connection Details:**
- API Type: Select from predefined integration types or choose "Custom API"
- Endpoint URL: Enter the base URL for the API
- Authentication Method: Select the authentication type:
  - No Authentication
  - API Key
  - OAuth 2.0
  - Basic Authentication
  - Bearer Token

**Authentication Credentials:**
- Enter the required credentials based on your selected authentication method
- For OAuth 2.0, you may need to complete an authorization flow

**Request Configuration:**
- Request Method: Select HTTP method (GET, POST)
- Headers: Add any required HTTP headers
- Request Body: Configure request body for POST requests
- Parameters: Add query parameters for GET requests

**Response Mapping:**
- Response Format: Select data format (JSON, XML)
- Data Path: Specify the JSON path or XPath to the freight data array
- Field Mapping: Map API response fields to required system fields

**Scheduling:**
- Refresh Frequency: Set how often to fetch new data from the API
- Retry Settings: Configure automatic retry behavior for failed requests

### 3.6 Managing Existing Data Sources

To manage your existing data sources:

1. Navigate to the "Data Sources" section from the main menu.
2. You will see a list of all configured data sources with the following information:
   - Name: The descriptive name of the data source
   - Type: The data source type (CSV, Database, API)
   - Last Update: When the data was last refreshed
   - Status: Current connection status (Active, Warning, Inactive)
   - Actions: Buttons for common operations

**Available Actions:**
- Edit: Modify the configuration of a data source
- Refresh: Manually trigger a data refresh
- View Data: Preview the data from this source
- Disable/Enable: Temporarily disable or enable a data source
- Delete: Permanently remove a data source from the system

**Filtering and Sorting:**
- Use the filter box to search for specific data sources
- Click column headers to sort the list by that column
- Use the status filter to view sources in a particular state

### 3.7 Troubleshooting Data Connections

If you encounter issues with your data sources, try these troubleshooting steps:

**CSV File Issues:**
- Verify the file is in the correct format and uses the specified delimiter
- Check that date formats match your configuration settings
- Ensure required columns contain valid data
- Check the file size is under the 100MB limit

**Database Connection Issues:**
- Verify the server address and port are correct
- Confirm the username and password are valid
- Check that the user has appropriate permissions to read the data
- Ensure the database is accessible from the network

**API Integration Issues:**
- Verify the API endpoint URL is correct and accessible
- Check that authentication credentials are valid and not expired
- Review API rate limits that might be affecting the connection
- Examine the API response for error messages

**General Troubleshooting:**
- Check the error message for specific details about the issue
- Review connection logs available in the "View Logs" option
- Test the connection using the "Test Connection" button
- Contact your system administrator for persistent issues

## 4. Performing Price Movement Analysis

### 4.1 Creating a New Analysis

To create a new freight price movement analysis:

1. From the Dashboard, click the "New Analysis" button, or
2. Navigate to the "Analysis" section from the main menu and click "+ New Analysis".
3. The analysis configuration screen will appear.

![New Analysis Screen] (Screenshot placeholder showing the New Analysis configuration screen)

The analysis configuration is divided into three main sections:
- Time Period Selection: Define when to analyze freight prices
- Data Filters: Select which data to include in the analysis
- Analysis Options: Configure calculation and output settings

### 4.2 Time Period Selection

The Time Period Selection determines the date range for your analysis:

**Start and End Dates:**
- Start Date: Click the calendar icon to select the beginning of the analysis period
- End Date: Click the calendar icon to select the end of the analysis period

**Granularity:**
Select how to group the data within your selected period:
- Daily: Compare prices on a day-by-day basis
- Weekly: Group data by weeks for week-over-week comparison
- Monthly: Group data by months for month-over-month comparison
- Custom: Define a custom interval (e.g., bi-weekly, quarterly)

**Custom Interval Settings:**
If you select "Custom" granularity, specify:
- Interval Type: Days, Weeks, Months
- Interval Value: Number of time units per interval

**Time Period Presets:**
For convenience, you can use the preset buttons for common time periods:
- Last 7 Days
- Last 30 Days
- Last Quarter
- Year to Date
- Custom Range (default)

**Time Zone Settings:**
- Select the time zone for date interpretation
- By default, the system uses your account's configured time zone

### 4.3 Data Filtering Options

Data filters allow you to focus your analysis on specific subsets of freight data:

**Data Source Filter:**
- All Sources: Include data from all configured data sources
- Selected Sources: Choose specific data sources to include
- Exclude Sources: Select data sources to exclude from the analysis

**Geographic Filters:**
- Origin: Filter by freight origin location
  - All Origins: Include all origin points
  - Selected Origins: Choose specific origins to include
  - Region Selection: Filter by geographic region
  
- Destination: Filter by freight destination location
  - All Destinations: Include all destination points
  - Selected Destinations: Choose specific destinations to include
  - Region Selection: Filter by geographic region

**Carrier Filters:**
- All Carriers: Include all carriers in the analysis
- Selected Carriers: Choose specific carriers to include
- Carrier Type: Filter by carrier category (ocean, air, road, rail)

**Additional Filters:**
- Transport Mode: Select specific transportation modes
- Service Level: Filter by service level (standard, express, etc.)
- Currency: Filter by original currency or convert to a selected currency
- Custom Filters: Create custom filters based on available data fields

**Adding Multiple Filters:**
- Click "+ Add Filter" to create additional filter conditions
- Specify the filter logic (AND/OR) between multiple conditions
- Preview the filtered data count before running the analysis

### 4.4 Analysis Options

Configure how the system calculates and presents the price movement analysis:

**Calculation Settings:**
- Calculate absolute change: Compute the numeric difference between periods
- Calculate percentage change: Compute the percentage difference between periods
- Identify trend direction: Determine if prices are increasing, decreasing, or stable
- Trend threshold: Set the percentage threshold for trend classification (default: 1%)

**Comparison Options:**
- Compare to historical baseline: Add a comparison to a reference period
- Baseline period: Select the reference period for comparison
- Seasonal comparison: Compare to the same period in the previous year

**Statistical Analysis:**
- Calculate average prices: Compute the mean freight charge
- Calculate minimum/maximum: Find the lowest and highest freight charges
- Calculate volatility: Measure price fluctuation over the period

**Output Format:**
- JSON: Structured data format for system integration
- CSV: Tabular format for spreadsheet analysis
- Text Summary: Human-readable summary report

**Visualization Settings:**
- Include visualization: Generate charts and visual representations
- Chart type: Select the preferred visualization type:
  - Line Chart: Show price trends over time
  - Bar Chart: Compare prices between periods
  - Comparison Chart: Show side-by-side period comparison
- Include trend indicators: Add visual indicators for trend direction

### 4.5 Running the Analysis

After configuring your analysis settings:

1. Review your configuration to ensure all settings are correct.
2. Click the "Run Analysis" button at the bottom of the screen.
3. The system will display a progress indicator while processing.
4. Once complete, you will be directed to the analysis results screen.

**Analysis Processing:**
- For small datasets, results typically appear within a few seconds.
- For large datasets or complex analyses, processing may take longer.
- You can navigate away during processing; the system will notify you when complete.

**Canceling an Analysis:**
- To cancel a running analysis, click the "Cancel" button on the progress screen.
- Canceled analyses are terminated immediately, and no partial results are saved.

### 4.6 Saving Analysis Configurations

To save your analysis configuration for future use:

1. Before or after running the analysis, click the "Save" button.
2. Enter a descriptive name for the analysis.
3. (Optional) Add tags to categorize the analysis.
4. (Optional) Add a description to provide context for the analysis.
5. Click "Save" to store the configuration.

**Saved Analysis Features:**
- Run the same analysis again with a single click
- Schedule recurring analysis runs
- Edit the configuration to make adjustments
- Share the analysis configuration with team members

**Accessing Saved Analyses:**
- From the Dashboard: View recently saved analyses
- From the Analysis section: View all saved analyses
- Use the search function to find specific analyses by name or tag

## 5. Understanding Analysis Results

### 5.1 Results Overview

After running an analysis, the system displays a comprehensive results screen:

![Analysis Results Screen] (Screenshot placeholder showing the Analysis Results screen)

The results page contains several key sections:

**Summary Section:**
- Analysis parameters: Time period, granularity, and applied filters
- Overall change: The aggregate price movement across the entire dataset
- Key metrics: Absolute change, percentage change, and trend direction

**Visualization Section:**
- Price movement chart: Visual representation of pricing trends
- Interactive elements: Hover over data points for detailed information
- Chart controls: Zoom, pan, and export options

**Detailed Results Section:**
- Tabular data showing price changes across time intervals
- Columns for date, price, absolute change, and percentage change
- Trend indicators showing direction of movement

### 5.2 Interpreting Absolute Changes

Absolute change represents the numeric difference in freight charges between time points:

**Understanding the Values:**
- Positive values (+): Indicate an increase in freight charges
- Negative values (-): Indicate a decrease in freight charges
- Zero values (0): Indicate no change in freight charges

**Contextual Information:**
- The absolute change is displayed in the original currency
- For currency conversions, the system indicates the conversion rate used
- The system handles different units appropriately (e.g., per container, per kg)

**Example Interpretation:**
- An absolute change of +$250 USD means freight charges increased by $250
- An absolute change of -€150 means freight charges decreased by €150

### 5.3 Understanding Percentage Changes

Percentage change shows the relative difference in freight charges as a percentage of the starting value:

**Understanding the Values:**
- Positive percentages (+%): Indicate a percentage increase
- Negative percentages (-%): Indicate a percentage decrease
- Zero percentage (0%): Indicates no change

**Special Cases:**
- When the starting value is zero:
  - If the ending value is positive: Shows as "New rate" or "∞%"
  - If the ending value is zero: Shows as "No change" or "0%"
- When the ending value is zero:
  - Shows as "-100%" (complete reduction to zero)
  
**Example Interpretation:**
- A percentage change of +5.2% means freight charges increased by 5.2%
- A percentage change of -3.7% means freight charges decreased by 3.7%

### 5.4 Trend Direction Indicators

The system uses visual indicators to show price movement trends:

**Trend Indicators:**
- Upward arrow [↑]: Indicates increasing freight charges
- Downward arrow [↓]: Indicates decreasing freight charges
- Horizontal arrow [→]: Indicates stable freight charges

**Trend Classification Rules:**
- Increasing: Percentage change greater than +1% (configurable)
- Decreasing: Percentage change less than -1% (configurable)
- Stable: Percentage change between -1% and +1%

**Color Coding:**
- Green: Typically used for decreasing freight charges (cost reduction)
- Red: Typically used for increasing freight charges (cost increase)
- Gray: Used for stable freight charges (minimal change)

**Note:** The color scheme can be customized in user preferences based on whether increases or decreases are favorable for your business context.

### 5.5 Visualization Options

The results screen offers various visualization options to help understand price trends:

**Changing Chart Types:**
1. Click the chart type selector above the visualization.
2. Choose from available chart types:
   - Line Chart: Best for showing trends over time
   - Bar Chart: Good for comparing distinct time periods
   - Candlestick Chart: Shows price range within periods
   - Comparison Chart: Side-by-side comparison of periods

**Chart Interactions:**
- Hover over data points to see detailed information
- Click and drag to zoom into a specific time range
- Use the reset button to return to the full view
- Toggle data series on/off by clicking their labels

**Customizing Visualizations:**
- Click "Customize Chart" to access additional options:
  - Chart title and axis labels
  - Color scheme selection
  - Data point markers and line styles
  - Inclusion of trend lines or moving averages
  - Reference lines for thresholds or targets

**Exporting Visualizations:**
- Click the "Export" button above the chart
- Select the desired format (PNG, JPG, SVG, PDF)
- Choose resolution options for image formats
- The exported file will download to your device

### 5.6 Exporting Results

To export your analysis results for use in other systems:

1. Click the "Export" button in the top-right corner of the results screen.
2. Select your preferred export format:
   - JSON: For system integration and data processing
   - CSV: For spreadsheet analysis and data manipulation
   - PDF: For formal reporting and presentation
   - Excel: For advanced spreadsheet analysis
   - Text Summary: For quick sharing via email or messaging

3. Configure export options specific to your chosen format:
   - JSON: Pretty print, include metadata
   - CSV: Delimiter selection, include headers
   - PDF: Paper size, orientation, include charts
   - Excel: Sheet formatting, include formulas
   - Text: Detail level, include summary statistics

4. Click "Export" to generate and download the file.

**Sharing Options:**
- Email: Send results directly via email
- Link: Generate a shareable link to the results
- Schedule: Set up regular exports to specified recipients

## 6. Working with Reports

### 6.1 Report Types

The Freight Price Movement Agent supports several report types to meet different business needs:

**Standard Price Movement Report:**
- Shows price changes over a specified time period
- Includes absolute and percentage changes
- Features trend indicators and visualizations

**Comparative Analysis Report:**
- Compares price movements across different timeframes
- Side-by-side comparison of multiple periods
- Highlights seasonal patterns or year-over-year changes

**Carrier Performance Report:**
- Analyzes price movements by carrier
- Compares rates and trends across multiple carriers
- Helps identify cost-effective carrier options

**Route Analysis Report:**
- Examines price trends for specific origin-destination pairs
- Compares costs across different routes
- Identifies opportunities for route optimization

**Custom Reports:**
- Build tailored reports using a flexible report builder
- Combine elements from different report types
- Add custom text, images, and annotations

### 6.2 Creating Standard Reports

To create a standard report:

1. Navigate to the "Reports" section from the main menu.
2. Click the "+ Create Report" button.
3. Select the report type from the available templates.
4. Configure the report parameters:
   - Report Title: Enter a descriptive name
   - Time Period: Select the reporting period
   - Data Filters: Apply filters to focus the report
   - Analysis Options: Configure calculation settings
   - Output Format: Select the report presentation style

5. Click "Generate Report" to create the report.
6. The system will display a preview of the generated report.
7. Review the report and make any necessary adjustments.
8. Click "Save Report" to store it for future access.

### 6.3 Scheduling Recurring Reports

To schedule a report to run automatically:

1. After creating a report, click the "Schedule" button.
2. Configure the scheduling options:
   - Frequency: Select how often to generate the report:
     - Daily: Select days of the week
     - Weekly: Select day of the week
     - Monthly: Select day of the month
     - Quarterly: Select month and day
   
   - Time: Set the time when the report should generate
   - Start Date: When to begin the schedule
   - End Date: (Optional) When to end the schedule, if applicable
   
   - Time Period Type:
     - Fixed: Always use the same date range
     - Relative: Dynamically adjust dates (e.g., last 30 days)
     - Custom: Use complex relative date logic

3. Configure delivery options:
   - Delivery Method:
     - Email: Send report to specified email addresses
     - File System: Save to a designated network location
     - Integration: Send to another system (e.g., SharePoint)
   
   - Format: Select the report file format for delivery
   - Recipient List: Add email addresses for report distribution
   - Message: Add an optional message to accompany the report

4. Click "Save Schedule" to activate the recurring report.

**Managing Scheduled Reports:**
- View all scheduled reports in the "Scheduled" tab
- Edit schedules to adjust frequency or recipients
- Pause or resume scheduled reports as needed
- View the execution history of scheduled reports

### 6.4 Managing Saved Reports

To manage your saved reports:

1. Navigate to the "Reports" section from the main menu.
2. The system displays a list of all your saved reports with:
   - Report Name: The title of the report
   - Created Date: When the report was first created
   - Last Run: When the report was last generated
   - Type: The report template type
   - Status: Current state (Active, Scheduled, Archived)
   - Actions: Buttons for common operations

**Available Actions:**
- View: Open the most recent version of the report
- Run: Generate a new version of the report
- Edit: Modify the report configuration
- Schedule: Set up or modify the report schedule
- Archive: Move the report to the archive for storage
- Delete: Permanently remove the report

**Filtering and Sorting:**
- Use the search box to find reports by name or content
- Filter by report type, date range, or status
- Sort by any column by clicking the column header

**Report Versions:**
- The system maintains version history for reports
- Access previous versions from the "History" tab
- Compare versions to see how data has changed over time

### 6.5 Sharing Reports

To share a report with other users:

1. From the Reports list, locate the report you want to share.
2. Click the "Share" button in the Actions column.
3. Configure sharing options:
   - Select Recipients: Choose users or groups
   - Permission Level:
     - View Only: Recipients can only view the report
     - Edit: Recipients can modify the report
     - Full Control: Recipients can edit, schedule, and delete

4. Add an optional message for the recipients.
5. Click "Share" to grant access to the selected users.

**Alternative Sharing Methods:**
- Generate Shareable Link: Create a URL that provides access to the report
- Export and Send: Export the report and send it manually
- Scheduled Delivery: Configure the report to be delivered regularly

**Managing Shared Reports:**
- View who has access to your reports in the "Sharing" tab
- Modify permissions or revoke access as needed
- See reports shared with you in the "Shared with Me" section

## 7. User Settings and Preferences

### 7.1 Personal Profile Settings

To access and update your user profile:

1. Click your username in the top-right corner of the screen.
2. Select "Profile Settings" from the dropdown menu.
3. The system displays your profile information.

**Editable Profile Information:**
- Display Name: How your name appears in the system
- Email Address: Your contact email for notifications
- Password: Change your account password
- Profile Picture: Upload or change your avatar image
- Contact Information: Update phone numbers or addresses

**Account Security:**
- Enable Two-Factor Authentication: Add an extra layer of security
- View Login History: See recent account access details
- Manage API Keys: Create and manage personal API access tokens

**Save Changes:**
- Click "Save Changes" to update your profile
- The system will confirm successful updates
- Some changes may require re-authentication

### 7.2 Display Preferences

To customize the user interface:

1. Navigate to Settings > Display Preferences.
2. Configure your preferred display options:

**Visual Theme:**
- Light Mode: Bright background with dark text (default)
- Dark Mode: Dark background with light text
- System: Automatically match your device's theme setting

**Date and Time Format:**
- Date Format: Choose how dates are displayed (MM/DD/YYYY, DD/MM/YYYY, etc.)
- Time Format: Select 12-hour or 24-hour time display
- Time Zone: Set your preferred time zone for all dates and times

**Number and Currency Format:**
- Decimal Separator: Choose period (.) or comma (,)
- Thousands Separator: Choose comma (,), period (.), or space ( )
- Default Currency: Set your preferred currency for display
- Currency Display: Symbol ($) or code (USD)

**Dashboard Configuration:**
- Default Dashboard View: Select what appears when you log in
- Widget Layout: Arrange dashboard components
- Data Refresh Rate: How often dashboard data updates

**Chart and Visualization Preferences:**
- Default Chart Type: Set your preferred visualization style
- Color Scheme: Select colors for charts and indicators
- Trend Direction Colors: Customize colors for up/down indicators

3. Click "Save Preferences" to apply your changes.

### 7.3 Notification Settings

To manage system notifications:

1. Navigate to Settings > Notifications.
2. Configure notification preferences:

**Notification Channels:**
- Email Notifications: Receive alerts via email
- In-App Notifications: Receive alerts within the system
- SMS Notifications: Receive text message alerts (if configured)

**Notification Types:**
- Price Movement Alerts: Notifications about significant price changes
  - Threshold: Set the percentage change that triggers an alert
  - Frequency: How often to check for significant changes
  
- Data Source Alerts: Notifications about data connection issues
  - Data Update Failures: Alerts when data doesn't update as scheduled
  - Connection Problems: Alerts about connectivity issues
  
- System Notifications: Alerts about system maintenance or updates
  - Scheduled Maintenance: Notifications about planned downtime
  - Feature Updates: Alerts about new functionality
  
- Report Notifications: Alerts related to reports
  - Completion Alerts: Notifications when reports finish generating
  - Schedule Failures: Alerts when scheduled reports fail

**Notification Schedule:**
- Business Hours Only: Restrict notifications to working hours
- Quiet Hours: Define times when notifications are suppressed
- Day Selection: Choose which days to receive notifications

3. Click "Save Notification Settings" to apply your changes.

### 7.4 Administrator Settings

**Note:** This section is only available to users with administrator privileges.

To access administrator settings:

1. Navigate to Settings > System Administration.
2. The system displays the administration dashboard.

**User Management:**
- View all system users
- Create new user accounts
- Edit user details and permissions
- Deactivate or reactivate user accounts
- Reset user passwords

**Role Management:**
- View existing roles
- Create new roles with custom permissions
- Assign roles to users
- Modify permission sets for each role

**System Configuration:**
- Data Retention: Configure how long to keep historical data
- Default Settings: Set system-wide defaults for new users
- Integration Settings: Configure global integration parameters
- API Settings: Manage API access and rate limits

**Audit and Compliance:**
- View system activity logs
- Export audit trails for compliance purposes
- Configure compliance-related settings
- Manage data privacy settings

**Maintenance Operations:**
- View system health status
- Schedule system maintenance
- Manage database operations
- Configure backup and recovery settings

## 8. Troubleshooting

### 8.1 Common Data Import Issues

**CSV File Import Problems:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Invalid file format" | The file is not a valid CSV | Ensure the file is saved as CSV format and uses the correct delimiter |
| "Column mapping failed" | Required columns missing or mismapped | Check that all required fields exist and are correctly mapped |
| "Date format error" | Dates in the file don't match expected format | Adjust the date format setting to match your file |
| "Upload size exceeded" | File is larger than the 100MB limit | Split the file into smaller files or compress the data |
| "Character encoding issue" | File uses unsupported encoding | Convert the file to UTF-8 encoding |

**Database Connection Issues:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Connection refused" | Database server unreachable or wrong address | Verify server address and that the server is running |
| "Authentication failed" | Incorrect username or password | Check credentials and ensure the user has access |
| "Query timeout" | Query takes too long to execute | Optimize the query or increase timeout setting |
| "Invalid SQL syntax" | Error in custom SQL query | Review and correct the SQL statement |
| "Insufficient permissions" | User lacks necessary database permissions | Grant required permissions to the database user |

**API Integration Issues:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "API endpoint not found" | Incorrect URL or endpoint doesn't exist | Verify the API URL and endpoint path |
| "Authentication error" | Invalid or expired API credentials | Update the API key or refresh OAuth token |
| "Rate limit exceeded" | Too many requests to the API | Reduce request frequency or contact API provider |
| "Response format error" | API response doesn't match expected format | Verify the API response structure and update mapping |
| "Connection timeout" | API server slow or unreachable | Check network connection and API server status |

### 8.2 Analysis Errors

**Configuration Errors:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Invalid time period" | Start date is after end date | Ensure start date is before end date |
| "No data available" | No data exists for the selected period | Adjust time period or check data source |
| "Filter returns no results" | Filters too restrictive | Modify filters to include more data |
| "Invalid granularity" | Custom granularity setting is invalid | Adjust the granularity to a valid setting |

**Calculation Errors:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Division by zero" | Starting value is zero for percentage calculation | System will handle this case, but be aware of "infinite" percentage changes |
| "Data point missing" | Incomplete data for some intervals | Check data source for gaps or adjust granularity |
| "Currency conversion error" | Exchange rate data missing | Verify currency settings or use original currency |
| "Calculation timeout" | Analysis too complex or dataset too large | Simplify analysis or reduce data volume |

**Result Errors:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Visualization failed" | Data structure not suitable for selected chart | Try a different chart type or adjust data selection |
| "Export format error" | Issues generating the selected export format | Try an alternative export format |
| "Results truncated" | Dataset too large for complete display | Export results or apply additional filters |

### 8.3 Report Generation Problems

**Scheduling Issues:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Schedule creation failed" | Invalid schedule parameters | Review and correct the schedule settings |
| "Scheduled report failed" | Error during automatic report generation | Check the error log and adjust report configuration |
| "Delivery failure" | Email or destination unreachable | Verify recipient addresses or destination settings |

**Content Issues:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Missing report sections" | Report template configuration issue | Edit the report to ensure all sections are included |
| "Chart generation error" | Visualization couldn't be created | Check the data and try an alternative chart type |
| "Formatting inconsistency" | Template or style issue | Adjust report formatting settings |

**Performance Issues:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Report timeout" | Report takes too long to generate | Simplify the report or reduce the data volume |
| "Memory limit exceeded" | Report too complex for available resources | Remove unnecessary elements or split into multiple reports |
| "Slow report loading" | Large report size or complex visualizations | Optimize report design or reduce complexity |

### 8.4 Connectivity Issues

**General Connectivity Problems:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Session expired" | Inactivity timeout or authentication issue | Log in again to start a new session |
| "Cannot connect to server" | Network or server availability problem | Check your internet connection and system status |
| "Slow performance" | Network latency or system load | Try again during off-peak hours or check your connection |

**Browser-Specific Issues:**

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| "Page not rendering correctly" | Browser compatibility or cache issue | Try clearing cache or using a different supported browser |
| "Features not working" | JavaScript disabled or incompatible browser | Enable JavaScript or update to a supported browser version |
| "Cannot download files" | Browser download settings | Check browser download permissions and settings |

### 8.5 Getting Support

If you encounter issues that you cannot resolve using the troubleshooting information:

**In-App Help:**
- Click the "Help" icon in the top navigation bar
- Search the knowledge base for relevant articles
- View video tutorials for common tasks
- Access this user manual for detailed instructions

**Contacting Support:**
- Click "Contact Support" in the Help menu
- Fill out the support request form with:
  - Issue description
  - Steps to reproduce
  - Error messages received
  - Screenshots (if applicable)
- Support tickets are typically responded to within 24 business hours

**Emergency Support:**
For critical issues affecting business operations:
- Use the "Emergency Support" option in the Help menu
- Call the dedicated support phone number
- Provide your account ID and emergency details

## 9. Glossary

| Term | Definition |
|------|------------|
| **Absolute Change** | The numerical difference between freight charges at two points in time (End Value - Start Value). |
| **API** | Application Programming Interface; a set of rules allowing different software applications to communicate with each other. |
| **Baseline Period** | A historical time period used as a reference point for comparison with current data. |
| **CSV** | Comma-Separated Values; a file format that stores tabular data as plain text with values separated by commas. |
| **Data Source** | Any system, file, or service that provides freight pricing data to the Freight Price Movement Agent. |
| **Destination** | The final delivery location for transported freight. |
| **ERP** | Enterprise Resource Planning; integrated management of main business processes, often in real-time. |
| **Freight Charge** | The cost associated with transporting goods from origin to destination, typically excluding insurance and other ancillary services. |
| **Granularity** | The level of detail or time interval used for analysis (e.g., daily, weekly, monthly). |
| **JSON** | JavaScript Object Notation; a lightweight data interchange format that is easy for humans to read and write and easy for machines to parse and generate. |
| **Origin** | The starting location from which freight is transported. |
| **Percentage Change** | The relative change between two values, expressed as a percentage of the start value ((End Value - Start Value) / Start Value × 100). |
| **Price Movement** | The change in freight charges over a specified time period, expressed as absolute value and/or percentage. |
| **Report** | A formatted presentation of analysis results, which may include tables, charts, and explanatory text. |
| **Time Period** | The date range over which price movement is analyzed. |
| **Time Series** | A sequence of data points indexed in time order, typically used for trend analysis. |
| **TMS** | Transportation Management System; software designed to manage and optimize the daily operations of transportation fleets. |
| **Trend Direction** | The general movement pattern of freight prices (increasing, decreasing, or stable). |
| **Volatility** | The degree of variation in freight prices over time. |

## 10. Appendices

### 10.1 Keyboard Shortcuts

| Function | Windows/Linux Shortcut | Mac Shortcut |
|----------|------------------------|-------------|
| **General Navigation** | | |
| Dashboard | Alt+H | Option+H |
| Data Sources | Alt+D | Option+D |
| Analysis | Alt+A | Option+A |
| Reports | Alt+R | Option+R |
| Settings | Alt+S | Option+S |
| Help | Alt+? | Option+? |
| **Analysis Functions** | | |
| New Analysis | Ctrl+N | Command+N |
| Save Analysis | Ctrl+S | Command+S |
| Run Analysis | Ctrl+Enter | Command+Enter |
| Export Results | Ctrl+E | Command+E |
| **Data Source Functions** | | |
| New Data Source | Ctrl+Alt+N | Command+Option+N |
| Refresh Data | F5 | F5 |
| **Report Functions** | | |
| New Report | Ctrl+Alt+R | Command+Option+R |
| Print Report | Ctrl+P | Command+P |
| **General Editing** | | |
| Undo | Ctrl+Z | Command+Z |
| Redo | Ctrl+Y | Command+Y |
| Cut | Ctrl+X | Command+X |
| Copy | Ctrl+C | Command+C |
| Paste | Ctrl+V | Command+V |

### 10.2 Supported File Formats

**Import Formats:**

| Format | File Extension | Maximum Size | Notes |
|--------|---------------|--------------|-------|
| CSV | .csv | 100MB | Supports various delimiters (comma, semicolon, tab) |
| Excel | .xlsx, .xls | 50MB | Supports multiple worksheets |
| JSON | .json | 50MB | Must conform to expected schema |
| XML | .xml | 50MB | Must conform to expected schema |
| Text | .txt | 50MB | Must be in delimited format |

**Export Formats:**

| Format | File Extension | Features |
|--------|---------------|----------|
| CSV | .csv | Tabular data, configurable delimiter |
| Excel | .xlsx | Formatted spreadsheets, multiple sheets |
| JSON | .json | Structured data with metadata |
| PDF | .pdf | Formatted report with charts and tables |
| Text | .txt | Plain text summary |
| PNG | .png | Chart and visualization export |
| SVG | .svg | Vector format for visualizations |

### 10.3 Calculation Formulas

**Absolute Change Calculation:**
```
Absolute Change = End Value - Start Value
```

Where:
- End Value = Freight charge at the end of the selected time period
- Start Value = Freight charge at the start of the selected time period

**Percentage Change Calculation:**
```
Percentage Change = (Absolute Change / Start Value) × 100
```

Special cases:
- If Start Value = 0 and End Value > 0: Report as "New rate established"
- If Start Value = 0 and End Value = 0: Report as "No change (0%)"
- If Start Value > 0 and End Value = 0: Report as "-100%"

**Trend Direction Determination:**
```
If Percentage Change > +1%: Trend = "Increasing"
If Percentage Change < -1%: Trend = "Decreasing"
If -1% ≤ Percentage Change ≤ +1%: Trend = "Stable"
```
Note: The threshold values (±1%) are configurable in the analysis settings.

**Average Calculation:**
```
Average Price = Sum of all prices in period / Number of data points
```

**Volatility Calculation:**
```
Volatility = Standard Deviation of prices in period
```

**Moving Average:**
```
n-period Moving Average = Sum of n most recent prices / n
```

### 10.4 Integration References

**TMS Integration Endpoints:**

| TMS System | Integration Method | Documentation Link |
|------------|-------------------|-------------------|
| SAP TM | REST API | [SAP TM Integration Guide] |
| Oracle TMS | SOAP API | [Oracle TMS API Reference] |
| JDA TMS | Database | [JDA Database Schema] |
| BluJay | REST API | [BluJay API Documentation] |
| MercuryGate | REST API | [MercuryGate Integration Guide] |

**ERP Integration Endpoints:**

| ERP System | Integration Method | Documentation Link |
|------------|-------------------|-------------------|
| SAP ERP | RFC/BAPI | [SAP RFC Integration Guide] |
| Oracle ERP | REST API | [Oracle ERP Cloud API] |
| Microsoft Dynamics | REST API | [Dynamics 365 Integration] |
| NetSuite | SOAP/REST API | [NetSuite API Documentation] |

**External Rate API References:**

| Rate Source | API Type | Documentation |
|-------------|----------|--------------|
| Freightos Baltic Index | REST | [FBX API Documentation] |
| World Container Index | REST | [WCI API Guide] |
| DAT | REST | [DAT API Reference] |
| Xeneta | REST | [Xeneta API Documentation] |

**File Format Specifications:**

| Format | Version | Specification Link |
|--------|---------|-------------------|
| CSV | RFC 4180 | [CSV Specification] |
| JSON | ECMA-404 | [JSON Specification] |
| XML | 1.0 | [XML Specification] |
| Excel | XLSX | [Office Open XML] |

---

*End of User Manual*