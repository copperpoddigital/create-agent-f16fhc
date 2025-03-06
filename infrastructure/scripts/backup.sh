#!/bin/bash
#
# Freight Price Movement Agent Backup Script
#
# This script creates backups of the Freight Price Movement Agent database,
# Redis cache, and configuration files. It supports automated backup scheduling,
# retention policies, and optional upload to S3 for disaster recovery.
#
# Usage: backup.sh [options]
#   Options:
#     -h, --help           Show this help message
#     -d, --database-only  Backup only the database
#     -r, --redis-only     Backup only Redis data
#     -c, --config-only    Backup only configuration files
#     -s, --s3             Upload backups to S3
#     -w, --wal-archive    Enable WAL archiving for point-in-time recovery
#     -k, --keep-days      Number of days to retain backups
#     -n, --no-cleanup     Skip cleanup of old backups
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
#   BACKUP_DB               - Whether to backup the database (true)
#   BACKUP_REDIS            - Whether to backup Redis data (true)
#   BACKUP_CONFIG           - Whether to backup configuration files (true)
#   BACKUP_RETENTION_DAYS   - Number of days to retain backups (30)
#   S3_BUCKET               - S3 bucket for remote backup storage
#   S3_PREFIX               - Prefix for S3 backup paths (backups)
#   AWS_PROFILE             - AWS CLI profile to use for S3 uploads (default)
#   COMPRESSION_LEVEL       - Compression level for backups (1-9) (9)
#   WAL_ARCHIVING           - Whether to enable WAL archiving (false)

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
BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DB=${BACKUP_DB:-true}
BACKUP_REDIS=${BACKUP_REDIS:-true}
BACKUP_CONFIG=${BACKUP_CONFIG:-true}
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
S3_BUCKET=${S3_BUCKET:-}
S3_PREFIX=${S3_PREFIX:-backups}
AWS_PROFILE=${AWS_PROFILE:-default}
COMPRESSION_LEVEL=${COMPRESSION_LEVEL:-9}
WAL_ARCHIVING=${WAL_ARCHIVING:-false}

# Flag to indicate whether S3 upload is required
S3_UPLOAD=false
# Flag to skip cleanup
SKIP_CLEANUP=false

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

    # Check for pg_dump if database backup is enabled
    if [ "$BACKUP_DB" = true ] && ! command -v pg_dump &> /dev/null; then
        log_message "ERROR" "pg_dump command not found, required for database backups"
        missing_deps=1
    fi

    # Check for redis-cli if Redis backup is enabled
    if [ "$BACKUP_REDIS" = true ] && ! command -v redis-cli &> /dev/null; then
        log_message "ERROR" "redis-cli command not found, required for Redis backups"
        missing_deps=1
    fi

    # Check for tar
    if ! command -v tar &> /dev/null; then
        log_message "ERROR" "tar command not found, required for backups"
        missing_deps=1
    fi

    # Check for aws cli if S3 upload is enabled
    if [ "$S3_UPLOAD" = true ] && ! command -v aws &> /dev/null; then
        log_message "ERROR" "aws command not found, required for S3 uploads"
        missing_deps=1
    fi

    if [ $missing_deps -ne 0 ]; then
        return 1
    fi

    return 0
}

# Create backup directories
create_backup_directories() {
    log_message "INFO" "Creating backup directories"
    
    # Create main backup directory
    mkdir -p "$BACKUP_DIR" || {
        log_message "ERROR" "Failed to create backup directory: $BACKUP_DIR"
        return 1
    }
    
    # Create subdirectories for each backup type
    if [ "$BACKUP_DB" = true ]; then
        mkdir -p "$BACKUP_DIR/database" || {
            log_message "ERROR" "Failed to create database backup directory"
            return 1
        }
    fi
    
    if [ "$BACKUP_REDIS" = true ]; then
        mkdir -p "$BACKUP_DIR/redis" || {
            log_message "ERROR" "Failed to create Redis backup directory"
            return 1
        }
    fi
    
    if [ "$BACKUP_CONFIG" = true ]; then
        mkdir -p "$BACKUP_DIR/config" || {
            log_message "ERROR" "Failed to create config backup directory"
            return 1
        }
    fi
    
    # Set appropriate permissions (restrictive by default)
    chmod -R 750 "$BACKUP_DIR" || {
        log_message "WARN" "Failed to set permissions on backup directory"
    }
    
    log_message "INFO" "Backup directories created successfully"
    return 0
}

# Database backup function
backup_database() {
    if [ "$BACKUP_DB" != true ]; then
        log_message "INFO" "Skipping database backup"
        return 0
    fi
    
    log_message "INFO" "Starting database backup"
    
    local db_backup_file="$BACKUP_DIR/database/${DB_NAME}_${BACKUP_TIMESTAMP}.pgdump"
    
    # Set PGPASSWORD environment variable
    export PGPASSWORD="$DB_PASSWORD"
    
    # Create database backup using pg_dump
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -F c -Z "$COMPRESSION_LEVEL" -f "$db_backup_file" || {
        log_message "ERROR" "Database backup failed"
        unset PGPASSWORD
        return 1
    }
    
    # Unset PGPASSWORD for security
    unset PGPASSWORD
    
    # Check if WAL archiving is enabled
    if [ "$WAL_ARCHIVING" = true ]; then
        log_message "INFO" "WAL archiving is enabled, triggering WAL switch"
        
        # Create WAL archive directory if it doesn't exist
        local wal_backup_dir="$BACKUP_DIR/database/wal"
        mkdir -p "$wal_backup_dir" || {
            log_message "ERROR" "Failed to create WAL backup directory"
        }
        
        # Trigger WAL switch and archive
        export PGPASSWORD="$DB_PASSWORD"
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            -c "SELECT pg_switch_wal();" > /dev/null 2>&1 || {
            log_message "WARN" "WAL switch failed, point-in-time recovery may not be available"
        }
        unset PGPASSWORD
    fi
    
    # Upload to S3 if enabled
    if [ "$S3_UPLOAD" = true ]; then
        upload_to_s3 "$db_backup_file" "database"
    fi
    
    log_message "INFO" "Database backup completed: $db_backup_file"
    return 0
}

# Redis backup function
backup_redis() {
    if [ "$BACKUP_REDIS" != true ]; then
        log_message "INFO" "Skipping Redis backup"
        return 0
    fi
    
    log_message "INFO" "Starting Redis backup"
    
    local redis_backup_file="$BACKUP_DIR/redis/redis_${BACKUP_TIMESTAMP}.rdb.gz"
    local temp_dir
    temp_dir=$(mktemp -d)
    
    # Trigger SAVE command in Redis
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" SAVE || {
        log_message "ERROR" "Failed to trigger Redis SAVE command"
        rm -rf "$temp_dir"
        return 1
    }
    
    # Get the Redis dump.rdb file via redis-cli CONFIG GET
    local redis_dir
    redis_dir=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" CONFIG GET dir | grep -A 1 "dir" | tail -n 1)
    local redis_dump_file=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" CONFIG GET dbfilename | grep -A 1 "dbfilename" | tail -n 1)
    local redis_dump_path="${redis_dir}/${redis_dump_file}"
    
    # If we can't access the Redis dump file directly, try to use SYNC command
    if [ ! -f "$redis_dump_path" ] || [ ! -r "$redis_dump_path" ]; then
        log_message "WARN" "Could not access Redis dump file directly, trying alternative method"
        
        # Use redis-cli --rdb to create a dump
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" --rdb "$temp_dir/dump.rdb" || {
            log_message "ERROR" "Failed to create Redis dump file"
            rm -rf "$temp_dir"
            return 1
        }
        
        # Compress the dump file
        gzip -c -"$COMPRESSION_LEVEL" "$temp_dir/dump.rdb" > "$redis_backup_file" || {
            log_message "ERROR" "Failed to compress Redis dump file"
            rm -rf "$temp_dir"
            return 1
        }
    else
        # Copy and compress the dump file
        gzip -c -"$COMPRESSION_LEVEL" "$redis_dump_path" > "$redis_backup_file" || {
            log_message "ERROR" "Failed to compress Redis dump file"
            rm -rf "$temp_dir"
            return 1
        }
    fi
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    # Upload to S3 if enabled
    if [ "$S3_UPLOAD" = true ]; then
        upload_to_s3 "$redis_backup_file" "redis"
    fi
    
    log_message "INFO" "Redis backup completed: $redis_backup_file"
    return 0
}

# Configuration backup function
backup_config() {
    if [ "$BACKUP_CONFIG" != true ]; then
        log_message "INFO" "Skipping configuration backup"
        return 0
    fi
    
    log_message "INFO" "Starting configuration backup"
    
    # Check if config directory exists
    if [ ! -d "$CONFIG_DIR" ]; then
        log_message "ERROR" "Configuration directory not found: $CONFIG_DIR"
        return 1
    fi
    
    local config_backup_file="$BACKUP_DIR/config/config_${BACKUP_TIMESTAMP}.tar.gz"
    
    # Create tar archive of config directory
    tar -czf "$config_backup_file" -C "$(dirname "$CONFIG_DIR")" "$(basename "$CONFIG_DIR")" || {
        log_message "ERROR" "Failed to create configuration backup"
        return 1
    }
    
    # Upload to S3 if enabled
    if [ "$S3_UPLOAD" = true ]; then
        upload_to_s3 "$config_backup_file" "config"
    fi
    
    log_message "INFO" "Configuration backup completed: $config_backup_file"
    return 0
}

# Upload to S3 function
upload_to_s3() {
    local backup_file=$1
    local backup_type=$2
    
    # Check if S3 bucket is configured
    if [ -z "$S3_BUCKET" ]; then
        log_message "WARN" "S3 bucket not configured, skipping upload"
        return 0
    fi
    
    log_message "INFO" "Uploading $backup_type backup to S3"
    
    # S3 path with year/month subfolders for better organization
    local year_month
    year_month=$(date +"%Y/%m")
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${backup_type}/${year_month}/$(basename "$backup_file")"
    
    # Upload to S3
    aws s3 cp --profile "$AWS_PROFILE" "$backup_file" "$s3_path" || {
        log_message "ERROR" "Failed to upload backup to S3: $s3_path"
        return 1
    }
    
    log_message "INFO" "Backup uploaded to S3: $s3_path"
    return 0
}

# Cleanup old backups
cleanup_old_backups() {
    if [ "$SKIP_CLEANUP" = true ]; then
        log_message "INFO" "Skipping cleanup of old backups as requested"
        return 0
    fi
    
    log_message "INFO" "Cleaning up backups older than $BACKUP_RETENTION_DAYS days"
    
    # Calculate cutoff date (current date minus retention days)
    local cutoff_date
    cutoff_date=$(date -d "-${BACKUP_RETENTION_DAYS} days" +%s)
    
    # Function to remove old files of a specific type
    cleanup_type() {
        local backup_type=$1
        local backup_pattern=$2
        
        if [ ! -d "$BACKUP_DIR/$backup_type" ]; then
            return 0
        fi
        
        # Find and remove files older than cutoff date
        find "$BACKUP_DIR/$backup_type" -name "$backup_pattern" -type f | while read -r file; do
            local file_date
            file_date=$(stat -c %Y "$file")
            
            if [ "$file_date" -lt "$cutoff_date" ]; then
                log_message "INFO" "Removing old backup: $file"
                rm -f "$file" || {
                    log_message "WARN" "Failed to remove old backup: $file"
                }
            fi
        done
    }
    
    # Clean up old database backups
    if [ "$BACKUP_DB" = true ]; then
        cleanup_type "database" "*.pgdump"
        
        # Clean up WAL archives if enabled
        if [ "$WAL_ARCHIVING" = true ] && [ -d "$BACKUP_DIR/database/wal" ]; then
            cleanup_type "database/wal" "*.gz"
        fi
    fi
    
    # Clean up old Redis backups
    if [ "$BACKUP_REDIS" = true ]; then
        cleanup_type "redis" "*.rdb.gz"
    fi
    
    # Clean up old config backups
    if [ "$BACKUP_CONFIG" = true ]; then
        cleanup_type "config" "*.tar.gz"
    fi
    
    log_message "INFO" "Backup cleanup completed"
    return 0
}

# Show usage function
show_usage() {
    cat << EOF
Freight Price Movement Agent Backup Script

This script creates backups of the Freight Price Movement Agent database,
Redis cache, and configuration files. It supports automated backup scheduling,
retention policies, and optional upload to S3 for disaster recovery.

Usage: $(basename "$0") [options]

Options:
  -h, --help           Show this help message
  -d, --database-only  Backup only the database
  -r, --redis-only     Backup only Redis data
  -c, --config-only    Backup only configuration files
  -s, --s3             Upload backups to S3
  -w, --wal-archive    Enable WAL archiving for point-in-time recovery
  -k, --keep-days N    Number of days to retain backups (default: $BACKUP_RETENTION_DAYS)
  -n, --no-cleanup     Skip cleanup of old backups

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
  AWS_PROFILE             - AWS CLI profile for S3 uploads ($AWS_PROFILE)
  COMPRESSION_LEVEL       - Compression level for backups (1-9) ($COMPRESSION_LEVEL)

Examples:
  $(basename "$0")                     # Backup everything with default settings
  $(basename "$0") -d                  # Backup only the database
  $(basename "$0") -s                  # Backup everything and upload to S3
  $(basename "$0") -k 7                # Backup everything and keep for 7 days
  $(basename "$0") -d -s -w -k 14      # Backup database with WAL archiving, upload to S3, keep for 14 days

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
                BACKUP_DB=true
                BACKUP_REDIS=false
                BACKUP_CONFIG=false
                exclusive_mode=true
                ;;
            -r|--redis-only)
                if [ "$exclusive_mode" = true ]; then
                    log_message "ERROR" "Cannot combine -d, -r, or -c options"
                    return 1
                fi
                BACKUP_DB=false
                BACKUP_REDIS=true
                BACKUP_CONFIG=false
                exclusive_mode=true
                ;;
            -c|--config-only)
                if [ "$exclusive_mode" = true ]; then
                    log_message "ERROR" "Cannot combine -d, -r, or -c options"
                    return 1
                fi
                BACKUP_DB=false
                BACKUP_REDIS=false
                BACKUP_CONFIG=true
                exclusive_mode=true
                ;;
            -s|--s3)
                S3_UPLOAD=true
                if [ -z "$S3_BUCKET" ]; then
                    log_message "ERROR" "S3_BUCKET environment variable must be set when using -s option"
                    return 1
                fi
                ;;
            -w|--wal-archive)
                WAL_ARCHIVING=true
                ;;
            -k|--keep-days)
                if [ -z "$2" ] || ! [[ "$2" =~ ^[0-9]+$ ]]; then
                    log_message "ERROR" "Invalid value for -k option, must be a positive integer"
                    return 1
                fi
                BACKUP_RETENTION_DAYS="$2"
                shift
                ;;
            -n|--no-cleanup)
                SKIP_CLEANUP=true
                ;;
            *)
                log_message "ERROR" "Unknown option: $1"
                show_usage
                return 1
                ;;
        esac
        shift
    done
    
    return 0
}

# Main function
main() {
    local rc=0
    
    # Parse command line arguments
    parse_arguments "$@" || {
        return 3  # Invalid arguments
    }
    
    log_message "INFO" "Starting Freight Price Movement Agent backup process"
    
    # Check dependencies
    check_dependencies || {
        log_message "ERROR" "Missing required dependencies"
        return 2  # Missing dependencies
    }
    
    # Create backup directories
    create_backup_directories || {
        log_message "ERROR" "Failed to create backup directories"
        return 1
    }
    
    # Perform database backup if enabled
    if [ "$BACKUP_DB" = true ]; then
        backup_database || {
            log_message "ERROR" "Database backup failed"
            rc=1
        }
    fi
    
    # Perform Redis backup if enabled
    if [ "$BACKUP_REDIS" = true ]; then
        backup_redis || {
            log_message "ERROR" "Redis backup failed"
            rc=1
        }
    fi
    
    # Perform configuration backup if enabled
    if [ "$BACKUP_CONFIG" = true ]; then
        backup_config || {
            log_message "ERROR" "Configuration backup failed"
            rc=1
        }
    fi
    
    # Clean up old backups according to retention policy
    cleanup_old_backups || {
        log_message "WARN" "Backup cleanup failed"
        # Don't fail the entire backup process for cleanup issues
    }
    
    if [ $rc -eq 0 ]; then
        log_message "INFO" "Freight Price Movement Agent backup completed successfully"
    else
        log_message "ERROR" "Freight Price Movement Agent backup completed with errors"
    fi
    
    return $rc
}

# Execute main function with provided arguments
main "$@"
exit $?