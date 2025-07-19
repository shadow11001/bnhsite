# Database Reorganization Quick Reference

## Problem Solved
Hosting plans not displaying properly due to database schema inconsistencies:
- Field name mismatches (`plan_name` vs `name`, `base_price` vs `price`)
- Inconsistent data types (strings vs numbers vs booleans)
- Missing required fields
- Duplicate entries
- No backup system for safe operations

## Quick Start

### 1. Check Current Status
```bash
./scripts/reorganize_database.sh status --detailed
```

### 2. Run Complete Reorganization
```bash
./scripts/reorganize_database.sh reorganize --force
```

### 3. Verify Results
```bash
./scripts/reorganize_database.sh validate
```

## Command Reference

### Shell Script Interface (Recommended)
```bash
# Complete reorganization
./scripts/reorganize_database.sh reorganize --force

# Check status with analysis
./scripts/reorganize_database.sh status --detailed

# Create backup
./scripts/reorganize_database.sh backup --collections hosting_plans

# List available backups
./scripts/reorganize_database.sh list-backups

# Analyze database issues
./scripts/reorganize_database.sh analyze

# Validate schema compliance
./scripts/reorganize_database.sh validate

# Emergency restore (if needed)
./scripts/reorganize_database.sh emergency-restore /path/to/backup_manifest.json
```

### Python CLI Interface
```bash
# Full reorganization with detailed output
python3 run_db_reorganization.py reorganize --force --report-file report.txt

# Status check
python3 run_db_reorganization.py status --detailed

# Backup operations
python3 run_db_reorganization.py backup create --collections hosting_plans
python3 run_db_reorganization.py backup list
python3 run_db_reorganization.py backup verify /path/to/backup.json.gz

# Schema migration operations
python3 run_db_reorganization.py migrate analyze
python3 run_db_reorganization.py migrate validate --show-errors
python3 run_db_reorganization.py migrate migrate --dry-run --show-changes
python3 run_db_reorganization.py migrate deduplicate --dry-run
```

## What Gets Fixed

### Field Name Standardization
| Old Field | New Field | Type | Description |
|-----------|-----------|------|-------------|
| `plan_name` | `name` | string | Plan display name |
| `plan_type` | `type` | string | Plan type |
| `base_price` | `price` | float | Base price |
| `popular` | `is_popular` | boolean | Popular flag |

### Data Normalization
- Convert string prices to float numbers
- Convert string booleans ("true"/"false") to actual booleans
- Convert comma-separated features to arrays
- Generate human-readable CPU/RAM specs
- Ensure all required fields exist

### Cleanup Operations
- Remove duplicate hosting plans
- Fix missing required fields
- Standardize data types
- Validate API compatibility

## Safety Features

### Automatic Backups
- Timestamped, compressed backups created before any changes
- Backup verification ensures integrity
- Multiple collections backed up simultaneously
- Easy restore from any backup

### Idempotent Operations
- Can run multiple times safely
- Tracks completion status to prevent duplicates
- Dry-run modes for preview

### Validation
- Pre-migration analysis identifies issues
- Post-migration validation ensures success
- API compatibility verification
- Detailed error reporting

## Emergency Procedures

### If Something Goes Wrong
1. **Check backup files:**
   ```bash
   ./scripts/reorganize_database.sh list-backups
   ```

2. **Emergency restore:**
   ```bash
   ./scripts/reorganize_database.sh emergency-restore /path/to/backup_manifest.json
   ```

3. **Validate current state:**
   ```bash
   ./scripts/reorganize_database.sh validate
   ```

## Admin Panel Integration

Access via admin panel at `/admin` to:
- View database status and health
- Monitor reorganization progress  
- Check backup status
- Trigger reorganization operations

### API Endpoints
- `GET /api/admin/database-status` - Database health check
- `POST /api/admin/database-reorganization` - Trigger reorganization
- `GET /api/admin/database-backup-status` - Backup status

## Output Files

### Logs & Reports
- `/tmp/db_reorganization_logs/reorganization_YYYYMMDD_HHMMSS.log`
- `/tmp/db_reorganization_logs/reorganization_report_YYYYMMDD_HHMMSS.txt`

### Backups
- `/tmp/database_backups/hosting_plans_YYYYMMDD_HHMMSS.json.gz`
- `/tmp/database_backups/backup_manifest_YYYYMMDD_HHMMSS.json`

## Environment Variables

```bash
export MONGO_URL="mongodb://admin:password@host:port/database?authSource=admin"
export DB_NAME="blue_nebula_hosting"
```

## Demo
Test the system without a database connection:
```bash
cd backend
python3 demo_reorganization.py
```

## Need Help?
- Check `DATABASE_REORGANIZATION_DOCS.md` for full documentation
- Run any command with `--help` for detailed options
- Use `--dry-run` flags to preview changes
- Check log files for detailed error information