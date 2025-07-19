#!/bin/bash
#
# Database Reorganization Shell Script
# Wrapper script for database reorganization operations with environment handling
# and comprehensive error checking.
#

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")/backend"
LOG_DIR="/tmp/db_reorganization_logs"
BACKUP_DIR="/tmp/database_backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p "$LOG_DIR"
    mkdir -p "$BACKUP_DIR"
    log_success "Directories created"
}

# Check Python environment
check_python_environment() {
    log_info "Checking Python environment..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Python version: $python_version"
    
    # Check required Python packages
    local required_packages=("motor" "pymongo" "asyncio")
    for package in "${required_packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            log_warning "Python package '$package' not found. Installing..."
            pip3 install $package || {
                log_error "Failed to install $package"
                exit 1
            }
        fi
    done
    
    log_success "Python environment ready"
}

# Set environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    # MongoDB connection string (can be overridden by environment)
    export MONGO_URL="${MONGO_URL:-mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@dev.bluenebulahosting.com:27018/blue_nebula_hosting?authSource=admin}"
    export DB_NAME="${DB_NAME:-blue_nebula_hosting}"
    
    # Paths
    export BACKUP_DIR="$BACKUP_DIR"
    export LOG_DIR="$LOG_DIR"
    
    log_success "Environment configured"
    log_info "Database: $DB_NAME"
    log_info "Backup directory: $BACKUP_DIR"
}

# Test database connection
test_connection() {
    log_info "Testing database connection..."
    
    python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def test():
    try:
        client = AsyncIOMotorClient(os.environ['MONGO_URL'])
        await client.admin.command('ping')
        print('Connection successful')
        client.close()
        return True
    except Exception as e:
        print(f'Connection failed: {e}')
        return False

result = asyncio.run(test())
exit(0 if result else 1)
" || {
        log_error "Database connection failed"
        exit 1
    }
    
    log_success "Database connection successful"
}

# Run database reorganization
run_reorganization() {
    local force_flag=""
    local report_file=""
    local log_file=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force_flag="--force"
                shift
                ;;
            --report-file)
                report_file="$2"
                shift 2
                ;;
            --log-file)
                log_file="$2"
                shift 2
                ;;
            *)
                log_warning "Unknown argument: $1"
                shift
                ;;
        esac
    done
    
    # Set default log file if not specified
    if [[ -z "$log_file" ]]; then
        log_file="$LOG_DIR/reorganization_$(date +%Y%m%d_%H%M%S).log"
    fi
    
    # Set default report file if not specified
    if [[ -z "$report_file" ]]; then
        report_file="$LOG_DIR/reorganization_report_$(date +%Y%m%d_%H%M%S).txt"
    fi
    
    log_info "Starting database reorganization..."
    log_info "Log file: $log_file"
    log_info "Report file: $report_file"
    
    cd "$BACKEND_DIR"
    
    # Run reorganization
    python3 run_db_reorganization.py reorganize \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME" \
        --backup-dir "$BACKUP_DIR" \
        --log-file "$log_file" \
        --report-file "$report_file" \
        --results-file "${report_file%.txt}.json" \
        $force_flag || {
        log_error "Database reorganization failed"
        log_info "Check log file: $log_file"
        exit 1
    }
    
    log_success "Database reorganization completed"
    log_info "Report saved to: $report_file"
}

# Check reorganization status
check_status() {
    local detailed_flag=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed)
                detailed_flag="--detailed"
                shift
                ;;
            *)
                log_warning "Unknown argument: $1"
                shift
                ;;
        esac
    done
    
    log_info "Checking reorganization status..."
    
    cd "$BACKEND_DIR"
    
    python3 run_db_reorganization.py status \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME" \
        $detailed_flag
}

# Create backup
create_backup() {
    local collections=()
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --collections)
                shift
                while [[ $# -gt 0 && ! $1 == --* ]]; do
                    collections+=("$1")
                    shift
                done
                ;;
            *)
                log_warning "Unknown argument: $1"
                shift
                ;;
        esac
    done
    
    # Default collections if none specified
    if [[ ${#collections[@]} -eq 0 ]]; then
        collections=("hosting_plans" "hosting_categories" "website_content" "navigation_items" "company_info" "site_settings")
    fi
    
    log_info "Creating backup for collections: ${collections[*]}"
    
    cd "$BACKEND_DIR"
    
    python3 run_db_reorganization.py backup create \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME" \
        --backup-dir "$BACKUP_DIR" \
        --collections "${collections[@]}" || {
        log_error "Backup creation failed"
        exit 1
    }
    
    log_success "Backup created successfully"
}

# List backups
list_backups() {
    log_info "Listing available backups..."
    
    cd "$BACKEND_DIR"
    
    python3 run_db_reorganization.py backup list \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME" \
        --backup-dir "$BACKUP_DIR"
}

# Analyze database
analyze_database() {
    log_info "Analyzing database state..."
    
    cd "$BACKEND_DIR"
    
    python3 run_db_reorganization.py migrate analyze \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME"
}

# Validate schema
validate_schema() {
    log_info "Validating database schema..."
    
    cd "$BACKEND_DIR"
    
    python3 run_db_reorganization.py migrate validate \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME" \
        --show-errors
}

# Emergency restore
emergency_restore() {
    local manifest_file=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --manifest-file)
                manifest_file="$2"
                shift 2
                ;;
            *)
                manifest_file="$1"
                shift
                ;;
        esac
    done
    
    if [[ -z "$manifest_file" ]]; then
        log_error "Manifest file required for emergency restore"
        exit 1
    fi
    
    if [[ ! -f "$manifest_file" ]]; then
        log_error "Manifest file not found: $manifest_file"
        exit 1
    fi
    
    log_warning "EMERGENCY RESTORE: This will replace current data with backup data"
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "Emergency restore cancelled"
        exit 0
    fi
    
    log_info "Starting emergency restore from: $manifest_file"
    
    cd "$BACKEND_DIR"
    
    python3 run_db_reorganization.py emergency-restore \
        --mongo-url "$MONGO_URL" \
        --db-name "$DB_NAME" \
        "$manifest_file" || {
        log_error "Emergency restore failed"
        exit 1
    }
    
    log_success "Emergency restore completed"
}

# Show help
show_help() {
    cat << EOF
Database Reorganization Script

Usage: $0 <command> [options]

Commands:
  reorganize [--force] [--report-file FILE] [--log-file FILE]
      Perform full database reorganization
      
  status [--detailed]
      Check reorganization status
      
  backup [--collections COL1 COL2 ...]
      Create backup of specified collections
      
  list-backups
      List available backup files
      
  analyze
      Analyze current database state
      
  validate
      Validate database schema
      
  emergency-restore [--manifest-file FILE | FILE]
      Emergency restore from backup manifest
      
  help
      Show this help message

Environment Variables:
  MONGO_URL       MongoDB connection string
  DB_NAME         Database name (default: blue_nebula_hosting)

Examples:
  $0 reorganize --force
  $0 status --detailed
  $0 backup --collections hosting_plans hosting_categories
  $0 emergency-restore /tmp/database_backups/backup_manifest_20241210_123456.json

EOF
}

# Main script logic
main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 1
    fi
    
    local command="$1"
    shift
    
    # Always setup environment and check prerequisites
    create_directories
    setup_environment
    check_python_environment
    
    case "$command" in
        reorganize)
            test_connection
            run_reorganization "$@"
            ;;
        status)
            test_connection
            check_status "$@"
            ;;
        backup)
            test_connection
            create_backup "$@"
            ;;
        list-backups)
            list_backups
            ;;
        analyze)
            test_connection
            analyze_database
            ;;
        validate)
            test_connection
            validate_schema
            ;;
        emergency-restore)
            test_connection
            emergency_restore "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"