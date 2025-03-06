#!/bin/bash
#
# init-db.sh - Initialize and configure PostgreSQL database with TimescaleDB
#
# This script handles database creation, user setup, schema initialization,
# and initial data loading to prepare the database for the Freight Price Movement Agent.
#

set -e

# Global variables with defaults from environment or hardcoded values
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-freight_price_agent}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_ADMIN_USER=${DB_ADMIN_USER:-postgres}
DB_ADMIN_PASSWORD=${DB_ADMIN_PASSWORD:-postgres}
APP_USER=${APP_USER:-freight_app}
APP_PASSWORD=${APP_PASSWORD:-freight_app_password}
SCHEMA_DIR=${SCHEMA_DIR:-$SCRIPT_DIR/../../src/backend/migrations}
INITIAL_DATA_DIR=${INITIAL_DATA_DIR:-$SCRIPT_DIR/../../src/backend/initial_data}
ENABLE_TIMESCALEDB=${ENABLE_TIMESCALEDB:-true}
CREATE_EXTENSIONS=${CREATE_EXTENSIONS:-true}
APPLY_MIGRATIONS=${APPLY_MIGRATIONS:-true}
LOAD_INITIAL_DATA=${LOAD_INITIAL_DATA:-true}
VERBOSE=${VERBOSE:-false}

# Log a message with timestamp and log level
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
}

# Check if required tools are installed
check_dependencies() {
    log_message "INFO" "Checking dependencies..."
    
    # Check for psql
    if ! command -v psql &> /dev/null; then
        log_message "ERROR" "psql command not found. Please install PostgreSQL client tools."
        return 1
    fi
    
    # Check for pg_isready
    if ! command -v pg_isready &> /dev/null; then
        log_message "ERROR" "pg_isready command not found. Please install PostgreSQL client tools."
        return 1
    fi
    
    # Check for alembic if we're applying migrations
    if [[ "$APPLY_MIGRATIONS" == "true" ]] && ! command -v alembic &> /dev/null; then
        log_message "ERROR" "alembic command not found. Please install alembic for database migrations."
        return 1
    fi
    
    log_message "INFO" "All dependencies are met."
    return 0
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log_message "INFO" "Waiting for PostgreSQL to be ready at $DB_HOST:$DB_PORT..."
    
    local timeout=60  # seconds
    local interval=2  # seconds
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" &> /dev/null; then
            log_message "INFO" "PostgreSQL is ready."
            return 0
        fi
        
        sleep $interval
        elapsed=$((elapsed + interval))
        
        if [[ "$VERBOSE" == "true" ]]; then
            log_message "DEBUG" "Still waiting for PostgreSQL... ($elapsed seconds elapsed)"
        fi
    done
    
    log_message "ERROR" "Timed out waiting for PostgreSQL to be ready."
    return 1
}

# Create the database if it doesn't exist
create_database() {
    log_message "INFO" "Creating database $DB_NAME if it doesn't exist..."
    
    # Check if database already exists
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log_message "INFO" "Database $DB_NAME already exists."
    else
        log_message "INFO" "Creating database $DB_NAME..."
        PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE DATABASE $DB_NAME WITH OWNER = $DB_ADMIN_USER ENCODING = 'UTF8' CONNECTION LIMIT = -1;" postgres
        
        if [[ $? -ne 0 ]]; then
            log_message "ERROR" "Failed to create database $DB_NAME."
            return 1
        fi
        
        log_message "INFO" "Database $DB_NAME created successfully."
    fi
    
    return 0
}

# Create application user with appropriate permissions
create_app_user() {
    log_message "INFO" "Creating application user $APP_USER if it doesn't exist..."
    
    # Check if user already exists
    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$APP_USER'" postgres | grep -q 1; then
        log_message "INFO" "User $APP_USER already exists."
    else
        log_message "INFO" "Creating user $APP_USER..."
        PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE USER $APP_USER WITH PASSWORD '$APP_PASSWORD';" postgres
        
        if [[ $? -ne 0 ]]; then
            log_message "ERROR" "Failed to create user $APP_USER."
            return 1
        fi
        
        log_message "INFO" "User $APP_USER created successfully."
    fi
    
    # Grant privileges to the application user
    log_message "INFO" "Granting privileges to $APP_USER on database $DB_NAME..."
    
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "GRANT CONNECT ON DATABASE $DB_NAME TO $APP_USER;" postgres
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "GRANT USAGE ON SCHEMA public TO $APP_USER;" "$DB_NAME"
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $APP_USER;" "$DB_NAME"
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO $APP_USER;" "$DB_NAME"
    
    log_message "INFO" "Privileges granted to $APP_USER."
    
    return 0
}

# Create required PostgreSQL extensions
create_extensions() {
    if [[ "$CREATE_EXTENSIONS" != "true" ]]; then
        log_message "INFO" "Skipping extension creation as requested."
        return 0
    fi
    
    log_message "INFO" "Creating required PostgreSQL extensions..."
    
    # Create TimescaleDB extension if requested
    if [[ "$ENABLE_TIMESCALEDB" == "true" ]]; then
        log_message "INFO" "Creating TimescaleDB extension..."
        
        PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;" "$DB_NAME"
        
        if [[ $? -ne 0 ]]; then
            log_message "ERROR" "Failed to create TimescaleDB extension."
            return 1
        fi
        
        log_message "INFO" "TimescaleDB extension created successfully."
    fi
    
    # Create other required extensions
    log_message "INFO" "Creating additional extensions..."
    
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" "$DB_NAME"
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" "$DB_NAME"
    
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to create additional extensions."
        return 1
    fi
    
    log_message "INFO" "Additional extensions created successfully."
    
    return 0
}

# Apply database migrations using Alembic
apply_migrations() {
    if [[ "$APPLY_MIGRATIONS" != "true" ]]; then
        log_message "INFO" "Skipping database migrations as requested."
        return 0
    fi
    
    log_message "INFO" "Applying database migrations..."
    
    if [[ ! -d "$SCHEMA_DIR" ]]; then
        log_message "ERROR" "Migration directory $SCHEMA_DIR does not exist."
        return 1
    fi
    
    # Change to the backend directory where alembic.ini is located
    cd $(dirname "$SCHEMA_DIR")
    
    # Set up database URL for alembic
    export SQLALCHEMY_DATABASE_URL="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
    
    # Run alembic migrations
    log_message "INFO" "Running alembic upgrade..."
    
    if [[ "$VERBOSE" == "true" ]]; then
        alembic upgrade head
    else
        alembic upgrade head > /dev/null
    fi
    
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to apply database migrations."
        return 1
    fi
    
    log_message "INFO" "Database migrations applied successfully."
    
    # Return to original directory
    cd - > /dev/null
    
    return 0
}

# Load initial reference data into the database
load_initial_data() {
    if [[ "$LOAD_INITIAL_DATA" != "true" ]]; then
        log_message "INFO" "Skipping initial data loading as requested."
        return 0
    fi
    
    log_message "INFO" "Loading initial reference data..."
    
    if [[ ! -d "$INITIAL_DATA_DIR" ]]; then
        log_message "WARN" "Initial data directory $INITIAL_DATA_DIR does not exist. Skipping data load."
        return 0
    fi
    
    # Find all SQL files in the initial data directory
    local sql_files=($(find "$INITIAL_DATA_DIR" -name "*.sql" | sort))
    
    if [[ ${#sql_files[@]} -eq 0 ]]; then
        log_message "WARN" "No SQL files found in $INITIAL_DATA_DIR. Skipping data load."
        return 0
    fi
    
    # Execute each SQL file
    for sql_file in "${sql_files[@]}"; do
        local file_name=$(basename "$sql_file")
        log_message "INFO" "Executing $file_name..."
        
        if [[ "$VERBOSE" == "true" ]]; then
            PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -f "$sql_file" "$DB_NAME"
        else
            PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -f "$sql_file" "$DB_NAME" > /dev/null
        fi
        
        if [[ $? -ne 0 ]]; then
            log_message "ERROR" "Failed to execute $file_name."
            return 1
        fi
        
        log_message "INFO" "$file_name executed successfully."
    done
    
    log_message "INFO" "Initial reference data loaded successfully."
    
    return 0
}

# Configure TimescaleDB hypertables for time-series data
configure_timescaledb() {
    if [[ "$ENABLE_TIMESCALEDB" != "true" ]]; then
        log_message "INFO" "Skipping TimescaleDB configuration as requested."
        return 0
    fi
    
    log_message "INFO" "Configuring TimescaleDB hypertables..."
    
    # Check if freight_data table exists
    if ! PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -tAc "SELECT to_regclass('public.freight_data');" "$DB_NAME" | grep -q "freight_data"; then
        log_message "WARN" "Table freight_data does not exist. Skipping TimescaleDB configuration."
        return 0
    fi
    
    # Check if the table is already a hypertable
    if PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -tAc "SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'freight_data';" "$DB_NAME" | grep -q "1"; then
        log_message "INFO" "Table freight_data is already a hypertable."
    else
        # Create hypertable for freight_data
        log_message "INFO" "Converting freight_data to a hypertable..."
        
        PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "SELECT create_hypertable('freight_data', 'record_date');" "$DB_NAME"
        
        if [[ $? -ne 0 ]]; then
            log_message "ERROR" "Failed to create hypertable for freight_data."
            return 1
        fi
        
        log_message "INFO" "freight_data converted to a hypertable successfully."
    fi
    
    # Set chunk time interval to 1 month (30 days)
    log_message "INFO" "Setting chunk time interval..."
    
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "SELECT set_chunk_time_interval('freight_data', INTERVAL '30 days');" "$DB_NAME"
    
    # Create additional time-series optimized indexes
    log_message "INFO" "Creating time-series optimized indexes..."
    
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE INDEX IF NOT EXISTS idx_freight_data_origin_dest_time ON freight_data(origin_id, destination_id, record_date DESC);" "$DB_NAME"
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "CREATE INDEX IF NOT EXISTS idx_freight_data_carrier_time ON freight_data(carrier_id, record_date DESC);" "$DB_NAME"
    
    # Set up retention policy (keep data for 7 years as per requirements)
    log_message "INFO" "Setting up data retention policy (7 years)..."
    
    PGPASSWORD=$DB_ADMIN_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_ADMIN_USER" -c "SELECT add_retention_policy('freight_data', INTERVAL '7 years');" "$DB_NAME"
    
    log_message "INFO" "TimescaleDB configuration completed successfully."
    
    return 0
}

# Display script usage information
show_usage() {
    echo "Usage: $(basename "$0") [options]"
    echo
    echo "Initialize and configure PostgreSQL database with TimescaleDB for the Freight Price Movement Agent."
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message and exit"
    echo "  -H, --host HOST            PostgreSQL host (default: $DB_HOST)"
    echo "  -p, --port PORT            PostgreSQL port (default: $DB_PORT)"
    echo "  -d, --database DB_NAME     Database name (default: $DB_NAME)"
    echo "  -u, --user USER            Database admin user (default: $DB_ADMIN_USER)"
    echo "  -P, --password PASSWORD    Database admin password"
    echo "  -a, --app-user USER        Application user to create (default: $APP_USER)"
    echo "  -A, --app-password PASS    Application user password"
    echo "  -s, --skip-extensions      Skip creating PostgreSQL extensions"
    echo "  -m, --skip-migrations      Skip applying database migrations"
    echo "  -t, --skip-timescaledb     Skip TimescaleDB configuration"
    echo "  -i, --skip-initial-data    Skip loading initial data"
    echo "  -v, --verbose              Enable verbose logging"
    echo
    echo "Environment variables:"
    echo "  DB_HOST                    PostgreSQL host (default: localhost)"
    echo "  DB_PORT                    PostgreSQL port (default: 5432)"
    echo "  DB_NAME                    Database name (default: freight_price_agent)"
    echo "  DB_ADMIN_USER              Database admin user (default: postgres)"
    echo "  DB_ADMIN_PASSWORD          Database admin password"
    echo "  APP_USER                   Application user (default: freight_app)"
    echo "  APP_PASSWORD               Application user password"
    echo "  SCHEMA_DIR                 Directory with migration scripts"
    echo "  INITIAL_DATA_DIR           Directory with initial data SQL files"
    echo "  ENABLE_TIMESCALEDB         Whether to enable TimescaleDB (default: true)"
    echo "  CREATE_EXTENSIONS          Whether to create extensions (default: true)"
    echo "  APPLY_MIGRATIONS           Whether to apply migrations (default: true)"
    echo "  LOAD_INITIAL_DATA          Whether to load initial data (default: true)"
    echo "  VERBOSE                    Enable verbose logging (default: false)"
    echo
    echo "Examples:"
    echo "  $(basename "$0") -H localhost -p 5432 -d freight_db -u postgres -P mypassword"
    echo "  DB_HOST=localhost DB_PORT=5432 DB_NAME=freight_db $(basename "$0")"
}

# Parse command line arguments
parse_arguments() {
    local args=("$@")
    
    # Process options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_usage
                exit 0
                ;;
            -H|--host)
                DB_HOST="$2"
                shift 2
                ;;
            -p|--port)
                DB_PORT="$2"
                shift 2
                ;;
            -d|--database)
                DB_NAME="$2"
                shift 2
                ;;
            -u|--user)
                DB_ADMIN_USER="$2"
                shift 2
                ;;
            -P|--password)
                DB_ADMIN_PASSWORD="$2"
                shift 2
                ;;
            -a|--app-user)
                APP_USER="$2"
                shift 2
                ;;
            -A|--app-password)
                APP_PASSWORD="$2"
                shift 2
                ;;
            -s|--skip-extensions)
                CREATE_EXTENSIONS="false"
                shift
                ;;
            -m|--skip-migrations)
                APPLY_MIGRATIONS="false"
                shift
                ;;
            -t|--skip-timescaledb)
                ENABLE_TIMESCALEDB="false"
                shift
                ;;
            -i|--skip-initial-data)
                LOAD_INITIAL_DATA="false"
                shift
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            *)
                log_message "ERROR" "Unknown option: $1"
                show_usage
                return 1
                ;;
        esac
    done
    
    # If TimescaleDB is disabled, make sure we don't try to configure it
    if [[ "$ENABLE_TIMESCALEDB" == "false" ]]; then
        # Don't create the extension if we're not using TimescaleDB
        if [[ "$CREATE_EXTENSIONS" == "true" ]]; then
            log_message "INFO" "TimescaleDB disabled, will create other extensions only."
        fi
    fi
    
    return 0
}

# Main function
main() {
    # Parse command line arguments
    parse_arguments "$@"
    if [[ $? -ne 0 ]]; then
        return 4  # Invalid arguments
    fi
    
    log_message "INFO" "Starting database initialization for Freight Price Movement Agent..."
    
    # Check dependencies
    check_dependencies
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Missing dependencies. Please install required tools."
        return 2  # Missing dependencies
    fi
    
    # Wait for PostgreSQL to be ready
    wait_for_postgres
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "PostgreSQL server not available. Initialization aborted."
        return 3  # PostgreSQL not available
    fi
    
    # Create database
    create_database
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to create database. Initialization aborted."
        return 1  # Database creation failed
    fi
    
    # Create application user
    create_app_user
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to create application user. Initialization aborted."
        return 1  # User creation failed
    fi
    
    # Create extensions
    create_extensions
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to create extensions. Initialization aborted."
        return 1  # Extension creation failed
    fi
    
    # Apply migrations
    apply_migrations
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to apply migrations. Initialization aborted."
        return 1  # Migration failed
    fi
    
    # Configure TimescaleDB
    configure_timescaledb
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to configure TimescaleDB. Initialization aborted."
        return 1  # TimescaleDB configuration failed
    fi
    
    # Load initial data
    load_initial_data
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to load initial data. Initialization aborted."
        return 1  # Data loading failed
    fi
    
    log_message "INFO" "Database initialization completed successfully."
    
    return 0  # Initialization successful
}

# Run the main function with all script arguments
main "$@"
exit $?