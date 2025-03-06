#!/bin/bash
#
# Freight Price Movement Agent Restore Script
#
# This script restores the Freight Price Movement Agent from backups.
# It supports database, Redis cache, and configuration file restoration
# with options for point-in-time recovery and S3 backup retrieval.
#
# Usage: restore.sh [options]
#   Options:
#     -h, --help           Show this help message
#     -d, --database-only  Restore only the database
#     -r, --redis-only     Restore only Redis data
#     -c, --config-only    Restore only configuration files
#     -f, --file FILE      Specify backup file to restore from
#     -s, --s3             Download backups from S3
#     -p, --point-in-time  Perform point-in-time recovery
#     -t, --timestamp TS   Recovery timestamp for point-in-time recovery
#     -n, --no-verify      Skip restore verification
#
# Environment variables:
#   BACKUP_ROOT             - Root directory for backups (/var/backups/freight-price-agent)
#   DB_HOST                 - PostgreSQL database host (db)
#   DB_PORT                 - PostgreSQL database port (5432)
#   DB_NAME                 - PostgreSQL database name (freight_price_agent)
#   DB_USER                 - PostgreSQL database user (postgres)
#   DB_PASSWORD             - PostgreSQL database password (postgres)
#   REDIS_HOST              - Redis host (redis)
#   REDIS_PORT              - Redis port (6379)
#   REDIS_DB                - Redis database number (0)
#   CONFIG_DIR              - Configuration directory (/etc/freight-price-agent)
#   RESTORE_DB              - Whether to restore the database (true)
#   RESTORE_REDIS           - Whether to restore Redis data (true)
#   RESTORE_CONFIG          - Whether to restore configuration files (true)
#   S3_BUCKET               - S3 bucket for remote backup storage
#   S3_PREFIX               - Prefix for S3 backup paths (backups)
#   AWS_PROFILE             - AWS CLI profile to use for S3 downloads (default)
#   POINT_IN_TIME_RECOVERY  - Whether to perform point-in-time recovery (false)
#   RECOVERY_TIMESTAMP      - Timestamp for point-in-time recovery
#   BACKUP_FILE             - Specific backup file to restore from
#   VERIFY_RESTORE          - Whether to verify the restoration (true)

set -e  # Exit immediately if a command exits with a non-zero status
set -o pipefail  # Return value of a pipeline is the value of the last command

# Script directory
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

# Default configuration
BACKUP_DIR=${BACKUP_ROOT:-/var/backups/freight-price-agent}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-freight_price_agent}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_DB=${REDIS_DB:-0}
CONFIG_DIR=${CONFIG_DIR:-/etc/freight-price-agent}
RESTORE_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESTORE_DB=${RESTORE_DB:-true}
RESTORE_REDIS=${RESTORE_REDIS:-true}
RESTORE_CONFIG=${RESTORE_CONFIG:-true}
S3_BUCKET=${S3_BUCKET:-}
S3_PREFIX=${S3_PREFIX:-backups}
AWS_PROFILE=${AWS_PROFILE:-default}
POINT_IN_TIME_RECOVERY=${POINT_IN_TIME_RECOVERY:-false}
RECOVERY_TIMESTAMP=${RECOVERY_TIMESTAMP:-}
BACKUP_FILE=${BACKUP_FILE:-}
VERIFY_RESTORE=${VERIFY_RESTORE:-true}
TEMP_DIR=/tmp/freight-price-agent-restore-${RESTORE_TIMESTAMP}

# Logging function
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message"
}

# Check if required tools are installed
check_dependencies() {
    local missing_deps=0

    # Check for pg_restore if database restore is enabled
    if [ "$RESTORE_DB" = true ] && ! command -v pg_restore &> /dev/null; then
        log_message "ERROR" "pg_restore command not found, required for database restoration"
        missing_deps=1
    fi

    # Check for redis-cli if Redis restore is enabled
    if [ "$RESTORE_REDIS" = true ] && ! command -v redis-cli &> /dev/null; then
        log_message "ERROR" "redis-cli command not found, required for Redis restoration"
        missing_deps=1
    fi

    # Check for tar
    if ! command -v tar &> /dev/null; then
        log_message "ERROR" "tar command not found, required for restoration"
        missing_deps=1
    fi

    # Check for aws cli if S3 bucket is specified
    if [ -n "$S3_BUCKET" ] && ! command -v aws &> /dev/null; then
        log_message "ERROR" "aws command not found, required for S3 downloads"
        missing_deps=1
    fi

    if [ $missing_deps -ne 0 ]; then
        return 1
    fi

    return 0
}

# Create temporary directory for restore operations
create_temp_directory() {
    log_message "INFO" "Creating temporary directory for restore: $TEMP_DIR"
    
    mkdir -p "$TEMP_DIR" || {
        log_message "ERROR" "Failed to create temporary directory: $TEMP_DIR"
        return 1
    }
    
    # Set appropriate permissions (restrictive)
    chmod 700 "$TEMP_DIR" || {
        log_message "WARN" "Failed to set permissions on temporary directory"
    }
    
    log_message "INFO" "Temporary directory created successfully"
    return 0
}

# Download backup file from S3 if specified
download_from_s3() {
    local backup_file=$1
    local backup_type=$2
    
    # Check if S3 bucket is configured
    if [ -z "$S3_BUCKET" ]; then
        return 0  # No S3 bucket configured, skip download
    fi
    
    log_message "INFO" "Downloading $backup_type backup from S3"
    
    # Extract filename from path
    local filename=$(basename "$backup_file")
    
    # Determine S3 path - we don't know the exact path, so we need to search
    # The S3 structure follows: s3://<bucket>/<prefix>/<type>/<year>/<month>/<filename>
    
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${backup_type}"
    
    # Use aws s3 cp to download the file
    aws s3 cp --profile "$AWS_PROFILE" "${s3_path}/${filename}" "${TEMP_DIR}/${filename}" || {
        # If direct download fails, we might need to search for the file
        log_message "WARN" "Could not find file directly, searching in S3 bucket"
        
        # Get the list of all files in the backup type directory and filter by filename
        local s3_file=$(aws s3 ls --profile "$AWS_PROFILE" --recursive "${s3_path}/" | grep "${filename}" | awk '{print $4}')
        
        if [ -z "$s3_file" ]; then
            log_message "ERROR" "Could not find backup file in S3: $filename"
            return 1
        fi
        
        # Download the file
        aws s3 cp --profile "$AWS_PROFILE" "s3://${S3_BUCKET}/${s3_file}" "${TEMP_DIR}/${filename}" || {
            log_message "ERROR" "Failed to download backup from S3: $s3_file"
            return 1
        }
    }
    
    log_message "INFO" "Backup file downloaded from S3: ${TEMP_DIR}/${filename}"
    return 0
}

# List available backups for selection
list_available_backups() {
    local backup_type=$1
    local backup_dir="${BACKUP_DIR}/${backup_type}"
    local backup_files=()
    local backup_pattern="*"
    
    # Determine appropriate file pattern based on backup type
    case "$backup_type" in
        database)
            backup_pattern="*.pgdump"
            ;;
        redis)
            backup_pattern="*.rdb.gz"
            ;;
        config)
            backup_pattern="*.tar.gz"
            ;;
    esac
    
    # Check if we should list from S3 or local directory
    if [ -n "$S3_BUCKET" ]; then
        log_message "INFO" "Listing available $backup_type backups from S3"
        
        # S3 path
        local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${backup_type}"
        
        # List all backup files from S3
        backup_files=($(aws s3 ls --profile "$AWS_PROFILE" --recursive "${s3_path}/" | grep "${backup_pattern}" | awk '{print $4}' | sort -r))
        
        if [ ${#backup_files[@]} -eq 0 ]; then
            log_message "ERROR" "No $backup_type backups found in S3"
            return 1
        fi
        
        # Display the list of backups
        echo "Available $backup_type backups in S3:"
        for i in "${!backup_files[@]}"; do
            echo "$((i+1)). $(basename "${backup_files[$i]}")"
        done
    else
        log_message "INFO" "Listing available $backup_type backups from local directory"
        
        # Check if backup directory exists
        if [ ! -d "$backup_dir" ]; then
            log_message "ERROR" "Backup directory not found: $backup_dir"
            return 1
        fi
        
        # List all backup files from local directory
        backup_files=($(find "$backup_dir" -name "$backup_pattern" -type f | sort -r))
        
        if [ ${#backup_files[@]} -eq 0 ]; then
            log_message "ERROR" "No $backup_type backups found in $backup_dir"
            return 1
        fi
        
        # Display the list of backups
        echo "Available $backup_type backups:"
        for i in "${!backup_files[@]}"; do
            echo "$((i+1)). $(basename "${backup_files[$i]}")"
        done
    fi
    
    # Prompt for selection
    local selection
    read -p "Enter backup number to restore: " selection
    
    # Validate selection
    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#backup_files[@]} ]; then
        log_message "ERROR" "Invalid selection: $selection"
        return 1
    fi
    
    # Set the selected backup file
    BACKUP_FILE="${backup_files[$((selection-1))]}"
    
    # If it's from S3, we need to download it
    if [ -n "$S3_BUCKET" ]; then
        # Extract just the filename
        local filename=$(basename "$BACKUP_FILE")
        
        # Download the selected file
        aws s3 cp --profile "$AWS_PROFILE" "s3://${S3_BUCKET}/${BACKUP_FILE}" "${TEMP_DIR}/${filename}" || {
            log_message "ERROR" "Failed to download backup from S3: $BACKUP_FILE"
            return 1
        }
        
        # Update BACKUP_FILE to point to the downloaded file
        BACKUP_FILE="${TEMP_DIR}/${filename}"
    fi
    
    log_message "INFO" "Selected backup file: $BACKUP_FILE"
    return 0
}

# Restore database function
restore_database() {
    if [ "$RESTORE_DB" != true ]; then
        log_message "INFO" "Skipping database restoration"
        return 0
    fi
    
    log_message "INFO" "Starting database restoration"
    
    local db_backup_file=""
    
    # If backup file is not specified, prompt for selection
    if [ -z "$BACKUP_FILE" ]; then
        if ! list_available_backups "database"; then
            return 1
        fi
        db_backup_file="$BACKUP_FILE"
    else
        # Use the specified backup file
        db_backup_file="$BACKUP_FILE"
        
        # If S3 bucket is specified, download the file
        if [ -n "$S3_BUCKET" ]; then
            if ! download_from_s3 "$db_backup_file" "database"; then
                return 1
            fi
            # Update path to the downloaded file
            db_backup_file="${TEMP_DIR}/$(basename "$db_backup_file")"
        fi
    fi
    
    # Check if the backup file exists
    if [ ! -f "$db_backup_file" ]; then
        log_message "ERROR" "Database backup file not found: $db_backup_file"
        return 1
    fi
    
    # Set PGPASSWORD environment variable
    export PGPASSWORD="$DB_PASSWORD"
    
    # Check if we should perform point-in-time recovery
    if [ "$POINT_IN_TIME_RECOVERY" = true ]; then
        log_message "INFO" "Performing point-in-time recovery to timestamp: $RECOVERY_TIMESTAMP"
        
        # For point-in-time recovery, we need:
        # 1. A base backup
        # 2. WAL files up to the recovery point
        # 3. A recovery.conf file
        
        if [ -z "$RECOVERY_TIMESTAMP" ]; then
            log_message "ERROR" "Recovery timestamp must be specified for point-in-time recovery"
            unset PGPASSWORD
            return 1
        fi
        
        # Create recovery configuration
        local recovery_file="${TEMP_DIR}/recovery.conf"
        cat > "$recovery_file" << EOF
restore_command = 'cp ${BACKUP_DIR}/database/wal/%f %p'
recovery_target_time = '$RECOVERY_TIMESTAMP'
recovery_target_inclusive = true
EOF
        
        # Stop PostgreSQL server if we have control over it
        # This is environment-specific and might need adjustment
        if command -v pg_ctl &> /dev/null && [ -n "$PGDATA" ]; then
            log_message "INFO" "Stopping PostgreSQL server"
            pg_ctl stop -D "$PGDATA" -m fast || {
                log_message "ERROR" "Failed to stop PostgreSQL server"
                unset PGPASSWORD
                return 1
            }
            
            # Restore the base backup
            log_message "INFO" "Restoring base backup"
            pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c -C "$db_backup_file" || {
                log_message "ERROR" "Failed to restore database backup"
                unset PGPASSWORD
                return 1
            }
            
            # Copy recovery configuration
            log_message "INFO" "Setting up recovery configuration"
            cp "$recovery_file" "$PGDATA/recovery.conf" || {
                log_message "ERROR" "Failed to copy recovery configuration"
                unset PGPASSWORD
                return 1
            }
            
            # Start PostgreSQL server to begin recovery
            log_message "INFO" "Starting PostgreSQL server for recovery"
            pg_ctl start -D "$PGDATA" || {
                log_message "ERROR" "Failed to start PostgreSQL server for recovery"
                unset PGPASSWORD
                return 1
            }
            
            # Wait for recovery to complete
            log_message "INFO" "Waiting for recovery to complete..."
            
            # Check if recovery is complete by querying pg_is_in_recovery
            local recovery_complete=false
            local timeout=300  # 5 minutes timeout
            local start_time=$(date +%s)
            
            while [ "$recovery_complete" = false ]; do
                if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT pg_is_in_recovery();" | grep -q "f"; then
                    recovery_complete=true
                else
                    sleep 5
                    local current_time=$(date +%s)
                    if [ $((current_time - start_time)) -gt $timeout ]; then
                        log_message "ERROR" "Recovery timeout after $timeout seconds"
                        unset PGPASSWORD
                        return 1
                    fi
                fi
            done
            
            log_message "INFO" "Point-in-time recovery completed successfully"
        else
            log_message "ERROR" "Cannot perform point-in-time recovery: missing pg_ctl command or PGDATA environment variable"
            unset PGPASSWORD
            return 1
        fi
    else
        # Regular database restore
        
        # Drop and recreate the database
        log_message "INFO" "Dropping and recreating database: $DB_NAME"
        
        # Check if the database exists
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
            # Drop existing database if it exists
            psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS $DB_NAME;" || {
                log_message "ERROR" "Failed to drop database: $DB_NAME"
                unset PGPASSWORD
                return 1
            }
        fi
        
        # Create new database
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" || {
            log_message "ERROR" "Failed to create database: $DB_NAME"
            unset PGPASSWORD
            return 1
        }
        
        # Restore from backup file
        log_message "INFO" "Restoring database from backup: $db_backup_file"
        pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" "$db_backup_file" || {
            log_message "ERROR" "Failed to restore database from backup"
            unset PGPASSWORD
            return 1
        }
    fi
    
    # Unset PGPASSWORD for security
    unset PGPASSWORD
    
    log_message "INFO" "Database restoration completed successfully"
    return 0
}

# Restore Redis function
restore_redis() {
    if [ "$RESTORE_REDIS" != true ]; then
        log_message "INFO" "Skipping Redis restoration"
        return 0
    fi
    
    log_message "INFO" "Starting Redis restoration"
    
    local redis_backup_file=""
    
    # If backup file is not specified, prompt for selection
    if [ -z "$BACKUP_FILE" ]; then
        if ! list_available_backups "redis"; then
            return 1
        fi
        redis_backup_file="$BACKUP_FILE"
    else
        # Use the specified backup file
        redis_backup_file="$BACKUP_FILE"
        
        # If S3 bucket is specified, download the file
        if [ -n "$S3_BUCKET" ]; then
            if ! download_from_s3 "$redis_backup_file" "redis"; then
                return 1
            fi
            # Update path to the downloaded file
            redis_backup_file="${TEMP_DIR}/$(basename "$redis_backup_file")"
        fi
    fi
    
    # Check if the backup file exists
    if [ ! -f "$redis_backup_file" ]; then
        log_message "ERROR" "Redis backup file not found: $redis_backup_file"
        return 1
    fi
    
    # Extract the Redis dump file
    log_message "INFO" "Extracting Redis dump file from backup"
    gunzip -c "$redis_backup_file" > "${TEMP_DIR}/dump.rdb" || {
        log_message "ERROR" "Failed to extract Redis dump file"
        return 1
    }
    
    # Get Redis configuration
    log_message "INFO" "Getting Redis configuration"
    local redis_dir
    redis_dir=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" CONFIG GET dir | grep -A 1 "dir" | tail -n 1)
    local redis_dbfilename
    redis_dbfilename=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" CONFIG GET dbfilename | grep -A 1 "dbfilename" | tail -n 1)
    
    # Check if we could get the Redis configuration
    if [ -z "$redis_dir" ] || [ -z "$redis_dbfilename" ]; then
        log_message "ERROR" "Failed to get Redis configuration"
        return 1
    fi
    
    # Stop Redis server (environment-specific, might need adjustment)
    log_message "INFO" "Stopping Redis server"
    if command -v systemctl &> /dev/null && systemctl is-active --quiet redis; then
        systemctl stop redis || {
            log_message "ERROR" "Failed to stop Redis server using systemctl"
            return 1
        }
    elif command -v service &> /dev/null; then
        service redis stop || {
            log_message "ERROR" "Failed to stop Redis server using service"
            return 1
        }
    else
        # If we can't stop Redis using system methods, try using redis-cli
        log_message "WARN" "Could not stop Redis server using systemctl or service, trying redis-cli"
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SHUTDOWN SAVE || {
            log_message "ERROR" "Failed to stop Redis server using redis-cli"
            return 1
        }
    fi
    
    # Create backup of current Redis dump file
    log_message "INFO" "Creating backup of current Redis dump file"
    if [ -f "${redis_dir}/${redis_dbfilename}" ]; then
        cp "${redis_dir}/${redis_dbfilename}" "${redis_dir}/${redis_dbfilename}.bak.${RESTORE_TIMESTAMP}" || {
            log_message "WARN" "Failed to backup current Redis dump file"
        }
    fi
    
    # Replace the Redis dump file
    log_message "INFO" "Replacing Redis dump file"
    cp "${TEMP_DIR}/dump.rdb" "${redis_dir}/${redis_dbfilename}" || {
        log_message "ERROR" "Failed to replace Redis dump file"
        return 1
    }
    
    # Ensure proper permissions
    chown redis:redis "${redis_dir}/${redis_dbfilename}" 2>/dev/null || {
        log_message "WARN" "Failed to set ownership on Redis dump file, this might be normal if not running as root"
    }
    
    # Start Redis server
    log_message "INFO" "Starting Redis server"
    if command -v systemctl &> /dev/null; then
        systemctl start redis || {
            log_message "ERROR" "Failed to start Redis server using systemctl"
            return 1
        }
    elif command -v service &> /dev/null; then
        service redis start || {
            log_message "ERROR" "Failed to start Redis server using service"
            return 1
        }
    else
        log_message "WARN" "Could not start Redis server automatically, please start it manually"
    fi
    
    log_message "INFO" "Redis restoration completed successfully"
    return 0
}

# Restore configuration files function
restore_config() {
    if [ "$RESTORE_CONFIG" != true ]; then
        log_message "INFO" "Skipping configuration restoration"
        return 0
    fi
    
    log_message "INFO" "Starting configuration restoration"
    
    local config_backup_file=""
    
    # If backup file is not specified, prompt for selection
    if [ -z "$BACKUP_FILE" ]; then
        if ! list_available_backups "config"; then
            return 1
        fi
        config_backup_file="$BACKUP_FILE"
    else
        # Use the specified backup file
        config_backup_file="$BACKUP_FILE"
        
        # If S3 bucket is specified, download the file
        if [ -n "$S3_BUCKET" ]; then
            if ! download_from_s3 "$config_backup_file" "config"; then
                return 1
            fi
            # Update path to the downloaded file
            config_backup_file="${TEMP_DIR}/$(basename "$config_backup_file")"
        fi
    fi
    
    # Check if the backup file exists
    if [ ! -f "$config_backup_file" ]; then
        log_message "ERROR" "Configuration backup file not found: $config_backup_file"
        return 1
    fi
    
    # Create backup of current configuration
    log_message "INFO" "Creating backup of current configuration"
    if [ -d "$CONFIG_DIR" ]; then
        local config_backup="${TEMP_DIR}/config_backup_${RESTORE_TIMESTAMP}"
        mkdir -p "$config_backup" || {
            log_message "WARN" "Failed to create backup directory for current configuration"
        }
        cp -r "$CONFIG_DIR"/* "$config_backup"/ 2>/dev/null || {
            log_message "WARN" "Failed to backup current configuration"
        }
    fi
    
    # Extract configuration files
    log_message "INFO" "Extracting configuration files from backup"
    mkdir -p "$CONFIG_DIR" || {
        log_message "ERROR" "Failed to create configuration directory: $CONFIG_DIR"
        return 1
    }
    
    tar -xzf "$config_backup_file" -C "$(dirname "$CONFIG_DIR")" || {
        log_message "ERROR" "Failed to extract configuration backup"
        return 1
    }
    
    log_message "INFO" "Configuration restoration completed successfully"
    return 0
}

# Verify restore function
verify_restore() {
    if [ "$VERIFY_RESTORE" != true ]; then
        log_message "INFO" "Skipping restore verification"
        return 0
    fi
    
    log_message "INFO" "Starting restore verification"
    local verification_failed=0
    
    # Verify database restoration if enabled
    if [ "$RESTORE_DB" = true ]; then
        log_message "INFO" "Verifying database restoration"
        
        # Set PGPASSWORD environment variable
        export PGPASSWORD="$DB_PASSWORD"
        
        # Check if we can connect to the database
        if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" &> /dev/null; then
            log_message "ERROR" "Database verification failed: could not connect to database"
            verification_failed=1
        else
            log_message "INFO" "Database verification successful: connection established"
            
            # Check if we can query some basic tables
            if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT count(*) FROM information_schema.tables;" &> /dev/null; then
                log_message "WARN" "Database verification: could not query tables"
            else
                log_message "INFO" "Database verification successful: query executed"
            fi
        fi
        
        # Unset PGPASSWORD for security
        unset PGPASSWORD
    fi
    
    # Verify Redis restoration if enabled
    if [ "$RESTORE_REDIS" = true ]; then
        log_message "INFO" "Verifying Redis restoration"
        
        # Check if we can connect to Redis
        if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING &> /dev/null; then
            log_message "ERROR" "Redis verification failed: could not connect to Redis"
            verification_failed=1
        else
            log_message "INFO" "Redis verification successful: connection established"
            
            # Check if we can get some basic Redis info
            if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO &> /dev/null; then
                log_message "WARN" "Redis verification: could not get Redis info"
            else
                log_message "INFO" "Redis verification successful: info command executed"
            fi
        fi
    fi
    
    # Verify configuration restoration if enabled
    if [ "$RESTORE_CONFIG" = true ]; then
        log_message "INFO" "Verifying configuration restoration"
        
        # Check if the configuration directory exists
        if [ ! -d "$CONFIG_DIR" ]; then
            log_message "ERROR" "Configuration verification failed: directory not found"
            verification_failed=1
        else
            log_message "INFO" "Configuration verification successful: directory exists"
            
            # Check if there are files in the directory
            if [ -z "$(ls -A "$CONFIG_DIR" 2>/dev/null)" ]; then
                log_message "WARN" "Configuration verification: directory is empty"
            else
                log_message "INFO" "Configuration verification successful: files present"
            fi
        fi
    fi
    
    if [ $verification_failed -eq 0 ]; then
        log_message "INFO" "Restore verification completed successfully"
        return 0
    else
        log_message "ERROR" "Restore verification failed"
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_message "INFO" "Cleaning up temporary files"
    
    # Remove temporary directory
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR" || {
            log_message "WARN" "Failed to remove temporary directory: $TEMP_DIR"
        }
    fi
    
    log_message "INFO" "Cleanup completed"
}

# Show usage function
show_usage() {
    cat << EOF
Freight Price Movement Agent Restore Script

This script restores the Freight Price Movement Agent from backups.
It supports database, Redis cache, and configuration file restoration
with options for point-in-time recovery and S3 backup retrieval.

Usage: $(basename "$0") [options]

Options:
  -h, --help           Show this help message
  -d, --database-only  Restore only the database
  -r, --redis-only     Restore only Redis data
  -c, --config-only    Restore only configuration files
  -f, --file FILE      Specify backup file to restore from
  -s, --s3             Download backups from S3
  -p, --point-in-time  Perform point-in-time recovery
  -t, --timestamp TS   Recovery timestamp for point-in-time recovery
  -n, --no-verify      Skip restore verification

Environment variables:
  BACKUP_ROOT             - Root directory for backups ($BACKUP_DIR)
  DB_HOST                 - PostgreSQL database host ($DB_HOST)
  DB_PORT                 - PostgreSQL database port ($DB_PORT)
  DB_NAME                 - PostgreSQL database name ($DB_NAME)
  DB_USER                 - PostgreSQL database user ($DB_USER)
  REDIS_HOST              - Redis host ($REDIS_HOST)
  REDIS_PORT              - Redis port ($REDIS_PORT)
  REDIS_DB                - Redis database number ($REDIS_DB)
  CONFIG_DIR              - Configuration directory ($CONFIG_DIR)
  S3_BUCKET               - S3 bucket for remote backup storage ($S3_BUCKET)
  S3_PREFIX               - Prefix for S3 backup paths ($S3_PREFIX)
  AWS_PROFILE             - AWS CLI profile for S3 downloads ($AWS_PROFILE)
  POINT_IN_TIME_RECOVERY  - Whether to perform point-in-time recovery ($POINT_IN_TIME_RECOVERY)
  RECOVERY_TIMESTAMP      - Timestamp for point-in-time recovery ($RECOVERY_TIMESTAMP)
  BACKUP_FILE             - Specific backup file to restore from ($BACKUP_FILE)
  VERIFY_RESTORE          - Whether to verify the restoration ($VERIFY_RESTORE)

Examples:
  $(basename "$0")                    # Restore everything with interactive selection
  $(basename "$0") -d                 # Restore only the database
  $(basename "$0") -s                 # Restore with backups from S3
  $(basename "$0") -f backup.tar.gz   # Restore from specific backup file
  $(basename "$0") -p -t "2023-06-15 14:30:00"  # Point-in-time recovery to specified timestamp

EOF
}

# Parse arguments
parse_arguments() {
    local args=("$@")
    local exclusive_mode=false
    
    # If no arguments provided, use defaults
    if [ ${#args[@]} -eq 0 ]; then
        return 0
    fi
    
    # Process arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                show_usage
                exit 0
                ;;
            -d|--database-only)
                if [ "$exclusive_mode" = true ]; then
                    log_message "ERROR" "Cannot combine -d, -r, or -c options"
                    return 1
                fi
                RESTORE_DB=true
                RESTORE_REDIS=false
                RESTORE_CONFIG=false
                exclusive_mode=true
                ;;
            -r|--redis-only)
                if [ "$exclusive_mode" = true ]; then
                    log_message "ERROR" "Cannot combine -d, -r, or -c options"
                    return 1
                fi
                RESTORE_DB=false
                RESTORE_REDIS=true
                RESTORE_CONFIG=false
                exclusive_mode=true
                ;;
            -c|--config-only)
                if [ "$exclusive_mode" = true ]; then
                    log_message "ERROR" "Cannot combine -d, -r, or -c options"
                    return 1
                fi
                RESTORE_DB=false
                RESTORE_REDIS=false
                RESTORE_CONFIG=true
                exclusive_mode=true
                ;;
            -f|--file)
                if [ -z "$2" ]; then
                    log_message "ERROR" "No backup file specified for -f option"
                    return 1
                fi
                BACKUP_FILE="$2"
                shift
                ;;
            -s|--s3)
                if [ -z "$S3_BUCKET" ]; then
                    log_message "ERROR" "S3_BUCKET environment variable must be set when using -s option"
                    return 1
                fi
                ;;
            -p|--point-in-time)
                POINT_IN_TIME_RECOVERY=true
                ;;
            -t|--timestamp)
                if [ -z "$2" ]; then
                    log_message "ERROR" "No timestamp specified for -t option"
                    return 1
                fi
                RECOVERY_TIMESTAMP="$2"
                shift
                ;;
            -n|--no-verify)
                VERIFY_RESTORE=false
                ;;
            *)
                log_message "ERROR" "Unknown option: $1"
                show_usage
                return 1
                ;;
        esac
        shift
    done
    
    # Validate argument combinations
    if [ "$POINT_IN_TIME_RECOVERY" = true ] && [ -z "$RECOVERY_TIMESTAMP" ]; then
        log_message "ERROR" "Recovery timestamp must be specified when using -p option"
        return 1
    fi
    
    if [ "$POINT_IN_TIME_RECOVERY" = true ] && [ "$RESTORE_DB" != true ]; then
        log_message "ERROR" "Point-in-time recovery can only be used with database restoration"
        return 1
    fi
    
    return 0
}

# Main function
main() {
    local rc=0
    
    # Parse command line arguments
    parse_arguments "$@" || {
        return 3  # Invalid arguments
    }
    
    log_message "INFO" "Starting Freight Price Movement Agent restore process"
    
    # Check dependencies
    check_dependencies || {
        log_message "ERROR" "Missing required dependencies"
        return 2  # Missing dependencies
    }
    
    # Create temporary directory
    create_temp_directory || {
        log_message "ERROR" "Failed to create temporary directory"
        return 1
    }
    
    # Trap for cleanup on exit
    trap cleanup EXIT
    
    # Perform database restoration if enabled
    if [ "$RESTORE_DB" = true ]; then
        restore_database || {
            log_message "ERROR" "Database restoration failed"
            rc=1
        }
    fi
    
    # Perform Redis restoration if enabled
    if [ "$RESTORE_REDIS" = true ]; then
        restore_redis || {
            log_message "ERROR" "Redis restoration failed"
            rc=1
        }
    fi
    
    # Perform configuration restoration if enabled
    if [ "$RESTORE_CONFIG" = true ]; then
        restore_config || {
            log_message "ERROR" "Configuration restoration failed"
            rc=1
        }
    fi
    
    # Verify restoration if enabled
    if [ "$VERIFY_RESTORE" = true ]; then
        verify_restore || {
            log_message "WARN" "Restore verification failed"
            # Don't fail the entire restore process for verification issues
        }
    fi
    
    if [ $rc -eq 0 ]; then
        log_message "INFO" "Freight Price Movement Agent restore completed successfully"
    else
        log_message "ERROR" "Freight Price Movement Agent restore completed with errors"
    fi
    
    return $rc
}

# Execute main function with provided arguments
main "$@"
exit $?