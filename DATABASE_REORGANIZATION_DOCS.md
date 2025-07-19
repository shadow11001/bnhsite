# Database Reorganization System Documentation

## Overview

The Database Reorganization System is a comprehensive solution for fixing hosting plans display issues caused by database schema inconsistencies and field mapping problems. It provides automated backup, schema migration, validation, and restoration capabilities for the Blue Nebula Hosting database.

## Problem Statement

The hosting plans collection had several critical issues:

1. **Schema Inconsistencies**: Mixed field naming conventions
   - Database uses `plan_type` but frontend expects `type`
   - Database uses `plan_name` but frontend expects `name`
   - Database uses `base_price` but frontend expects `price`
   - Inconsistent field mapping between old and new schema

2. **Data Structure Issues**: 
   - Mixed field naming conventions
   - Inconsistent data types (strings vs numbers vs booleans)
   - Missing required fields in some records
   - Potential duplicate or corrupted entries

3. **No Backup System**: No automated backup system to protect against data loss

## Architecture

The system consists of several interconnected components:

```
┌─────────────────────────────────────────────────────────────┐
│                Database Reorganization System              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Database Backup │  │ Schema Migration│  │ Database        │ │
│  │ System          │  │ System          │  │ Reorganizer     │ │
│  │                 │  │                 │  │ (Main)          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ CLI Runner      │  │ Shell Script    │  │ Admin API       │ │
│  │ Interface       │  │ Wrapper         │  │ Endpoints       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Database Backup System (`database_backup.py`)

Provides comprehensive backup and restore functionality:

- **Timestamped Backups**: Creates compressed, timestamped backups
- **Integrity Verification**: Validates backup files before and after creation
- **Multiple Restore Modes**: Replace, append, or update modes
- **Metadata Tracking**: Stores backup metadata for easy management
- **Cleanup Utilities**: Automatic cleanup of old backup files

#### Key Features:
```python
# Create backup
backup_file, metadata = await backup_system.backup_collection("hosting_plans")

# Restore from backup  
await backup_system.restore_collection(backup_file, mode="replace")

# List available backups
backups = backup_system.list_backups("hosting_plans")

# Verify backup integrity
verification = await backup_system.verify_backup(backup_file)
```

### 2. Schema Migration System (`schema_migration.py`)

Handles schema migration and validation:

- **Standardized Schema**: Defines the target schema for hosting plans
- **Field Mapping**: Maps old field names to new standardized names
- **Data Type Normalization**: Converts data types to expected formats
- **Duplicate Detection**: Identifies and removes duplicate records
- **Validation Engine**: Validates documents against the standard schema

#### Standard Schema Fields:
```python
{
    # Core fields
    "id": str,           # Unique identifier
    "name": str,         # Plan name (was plan_name)
    "type": str,         # Plan type (was plan_type)
    "price": float,      # Base price (was base_price)
    "is_popular": bool,  # Popular flag (was popular)
    
    # Technical specs
    "cpu": str,          # CPU specification
    "ram": str,          # RAM specification  
    "disk_space": str,   # Disk space specification
    "bandwidth": str,    # Bandwidth specification
    
    # Shared hosting fields
    "websites": str,     # Number of websites
    "databases": str,    # Database limit
    "email_accounts": str, # Email accounts limit
    
    # Other fields
    "features": list,    # List of features
    "order_url": str,    # Order URL
    # ... and more
}
```

### 3. Database Reorganizer (`database_reorganizer.py`)

Main orchestration system that coordinates all operations:

- **Pre-Analysis**: Analyzes current database state
- **Comprehensive Backup**: Creates backups of all target collections
- **Schema Migration**: Applies field mappings and data normalization
- **Validation**: Ensures data integrity after migration
- **Status Tracking**: Tracks reorganization completion status
- **Emergency Restore**: Provides emergency restoration capabilities

### 4. CLI Runner (`run_db_reorganization.py`)

Command-line interface for all operations:

```bash
# Full reorganization
python3 run_db_reorganization.py reorganize --force

# Check status
python3 run_db_reorganization.py status --detailed

# Create backup
python3 run_db_reorganization.py backup create --collections hosting_plans

# Schema operations
python3 run_db_reorganization.py migrate analyze
python3 run_db_reorganization.py migrate validate
python3 run_db_reorganization.py migrate migrate --dry-run
```

### 5. Shell Script Wrapper (`scripts/reorganize_database.sh`)

User-friendly shell script wrapper:

```bash
# Complete reorganization
./scripts/reorganize_database.sh reorganize --force

# Check status with details
./scripts/reorganize_database.sh status --detailed

# Create backup
./scripts/reorganize_database.sh backup --collections hosting_plans hosting_categories

# Emergency restore
./scripts/reorganize_database.sh emergency-restore /path/to/backup_manifest.json
```

### 6. Admin API Endpoints (`server.py`)

Web interface endpoints for monitoring and management:

- `GET /api/admin/database-status` - Database health and status
- `POST /api/admin/database-reorganization` - Trigger reorganization
- `GET /api/admin/database-backup-status` - Backup status and history

## Installation & Setup

### Prerequisites

- Python 3.7+
- MongoDB connection
- Required Python packages: `motor`, `pymongo`

### Installation

1. Install dependencies:
```bash
pip install motor pymongo
```

2. Set environment variables:
```bash
export MONGO_URL="mongodb://admin:password@host:port/database?authSource=admin"
export DB_NAME="blue_nebula_hosting"
```

3. Make shell script executable:
```bash
chmod +x scripts/reorganize_database.sh
```

## Usage

### Quick Start

1. **Check current status:**
```bash
./scripts/reorganize_database.sh status --detailed
```

2. **Run complete reorganization:**
```bash
./scripts/reorganize_database.sh reorganize --force
```

3. **Verify results:**
```bash
./scripts/reorganize_database.sh validate
```

### Detailed Operations

#### Backup Operations

```bash
# Create backup of hosting plans
python3 run_db_reorganization.py backup create --collection hosting_plans

# Create backup of multiple collections
python3 run_db_reorganization.py backup create --collections hosting_plans hosting_categories

# List available backups
python3 run_db_reorganization.py backup list

# Verify backup integrity
python3 run_db_reorganization.py backup verify /path/to/backup.json.gz

# Restore from backup
python3 run_db_reorganization.py backup restore /path/to/backup.json.gz --mode replace
```

#### Schema Migration

```bash
# Analyze current schema
python3 run_db_reorganization.py migrate analyze

# Validate against standard schema
python3 run_db_reorganization.py migrate validate --show-errors

# Dry run migration (see what would change)
python3 run_db_reorganization.py migrate migrate --dry-run --show-changes

# Perform actual migration
python3 run_db_reorganization.py migrate migrate --validate-after

# Remove duplicates
python3 run_db_reorganization.py migrate deduplicate --dry-run
```

#### Emergency Operations

```bash
# Emergency restore from backup manifest
./scripts/reorganize_database.sh emergency-restore /tmp/database_backups/backup_manifest_20241210_123456.json
```

## Field Mappings

The system applies the following field mappings to standardize the schema:

| Old Field Name | New Field Name | Data Type | Notes |
|----------------|----------------|-----------|-------|
| `plan_name` | `name` | string | Plan display name |
| `plan_type` | `type` | string | Plan type (shared, vps, gameserver) |
| `base_price` | `price` | float | Base price per billing cycle |
| `popular` | `is_popular` | boolean | Popular plan flag |
| `cpu_cores` | `cpu_cores` | integer | Number of CPU cores |
| `memory_gb` | `memory_gb` | integer | Memory in GB |
| `disk_gb` | `disk_gb` | integer | Disk space in GB |

## Data Normalization

The system performs the following data normalizations:

1. **Price Fields**: Convert string prices to float
2. **Boolean Fields**: Convert string booleans ("true"/"false") to actual booleans
3. **Feature Lists**: Convert comma-separated strings to arrays
4. **CPU/RAM Specs**: Generate human-readable specifications from numeric values
5. **Required Fields**: Ensure all required fields are present with defaults

## Safety Features

### Idempotent Operations
- All operations can be run multiple times safely
- Reorganization status tracking prevents duplicate operations
- Dry-run modes allow preview of changes

### Comprehensive Backups
- Timestamped, compressed backups
- Metadata tracking and verification
- Multiple restore modes (replace, append, update)
- Automatic backup cleanup

### Validation System
- Pre and post-migration validation
- Schema compliance checking
- API compatibility verification
- Detailed error reporting

### Emergency Procedures
- Emergency restore from backup manifests
- Rollback capabilities
- Status monitoring and health checks

## Monitoring & Management

### CLI Status Checks
```bash
# Basic status
python3 run_db_reorganization.py status

# Detailed analysis
python3 run_db_reorganization.py status --detailed
```

### Web Interface (Admin Panel)
Access via the admin panel at `/admin` to:
- View database status and health
- Monitor reorganization progress
- Check backup status
- Trigger reorganization operations

### Log Files
The system creates detailed logs in `/tmp/db_reorganization_logs/`:
- `reorganization_YYYYMMDD_HHMMSS.log` - Full operation logs
- `reorganization_report_YYYYMMDD_HHMMSS.txt` - Human-readable reports

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify MongoDB connection string
   - Check network connectivity
   - Ensure authentication credentials are correct

2. **Permission Errors**
   - Ensure write permissions to backup directory
   - Verify database user has required permissions

3. **Schema Validation Failures**
   - Run analysis to identify specific issues
   - Use dry-run mode to preview changes
   - Check for missing required fields

### Recovery Procedures

1. **If reorganization fails mid-process:**
   ```bash
   # Check for backup files
   python3 run_db_reorganization.py backup list
   
   # Restore from latest backup
   python3 run_db_reorganization.py backup restore /path/to/backup.json.gz
   ```

2. **If data appears corrupted:**
   ```bash
   # Use emergency restore
   ./scripts/reorganize_database.sh emergency-restore /path/to/manifest.json
   ```

3. **If hosting plans not displaying:**
   ```bash
   # Validate current schema
   python3 run_db_reorganization.py migrate validate --show-errors
   
   # Check API compatibility
   curl -X GET "http://localhost:8000/api/hosting-plans"
   ```

## Performance Considerations

- **Large Collections**: For collections with >10,000 documents, consider running during low-traffic periods
- **Backup Storage**: Backups are compressed but monitor disk space usage
- **Memory Usage**: Migration processes entire collections in memory; ensure adequate RAM
- **Network Timeouts**: Increase timeout values for slow database connections

## Security Notes

- Backup files contain sensitive data - store securely
- Database credentials should be stored in environment variables
- Admin API endpoints require authentication
- Log files may contain sensitive information

## Version History

- **v1.0**: Initial implementation with backup, migration, and validation systems
- Comprehensive CLI and shell script interfaces
- Admin API endpoints for web management
- Full documentation and safety features

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files for detailed error information
3. Run validation to identify specific problems
4. Use dry-run modes to preview changes before applying

## Demo

Run the included demo to see how the system works:
```bash
cd backend
python3 demo_reorganization.py
```

This demo uses mock data to show all system features without requiring a database connection.