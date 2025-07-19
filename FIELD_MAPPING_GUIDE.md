# Field Mapping and Database Reorganization Guide

## Overview

The hosting plans field mapping system has been updated to ensure consistency between the server API and database reorganization tools. This system provides **bidirectional field mapping** that preserves data integrity while handling different database schemas.

## Key Features

### 🔄 **Bidirectional Field Mapping**
- Maps between old schema (`plan_name`, `plan_type`, `base_price`, `popular`) and new schema (`name`, `type`, `price`, `is_popular`)
- Preserves all original data values - only field names are changed
- Handles mixed schemas and edge cases gracefully

### 🛡️ **Data Safety**
- **Default operation preserves data** - only field names are changed, not values
- Comprehensive backup system before any changes
- Dry-run mode for testing changes before applying them
- Validation after changes to ensure data integrity

### 🎯 **Consistent API**
- Server API and database reorganization use the same field mapping logic
- Centralized field mapping utility ensures consistency across all tools
- Frontend always receives expected field names regardless of database schema

## Updated Files

### Core Changes
- **`backend/field_mapping_utils.py`** - Centralized field mapping utility (NEW)
- **`backend/server.py`** - Updated to use centralized field mapping
- **`backend/schema_migration.py`** - Enhanced with consistent mapping and data preservation
- **`backend/database_reorganizer.py`** - Updated to use safe field mapping
- **`backend/run_db_reorganization.py`** - Enhanced CLI with new safety options

### Test Files
- **`tests/test_simple_field_mapping.py`** - Field mapping validation tests (NEW)
- **`tests/test_field_mapping_consistency.py`** - Comprehensive consistency tests (NEW)

## Usage Guide

### Safe Field Mapping (Recommended)

This is the **default and recommended** approach that only renames fields without changing data values:

```bash
# Dry run to preview changes (safe to run)
python backend/run_db_reorganization.py migrate migrate --dry-run --show-changes

# Apply field mapping changes (preserves all data)
python backend/run_db_reorganization.py migrate migrate

# Check results
python backend/run_db_reorganization.py status --detailed
```

### Full Migration (Advanced)

Only use this if you need data normalization and understand the implications:

```bash
# Dry run with full migration
python backend/run_db_reorganization.py migrate migrate --full-migration --dry-run --show-changes

# Apply full migration (may modify data values)
python backend/run_db_reorganization.py migrate migrate --full-migration --validate-after
```

### Database Backup

Always create backups before making changes:

```bash
# Create backup of hosting plans
python backend/run_db_reorganization.py backup create --collections hosting_plans

# List available backups
python backend/run_db_reorganization.py backup list

# Restore from backup if needed
python backend/run_db_reorganization.py backup restore /path/to/backup.json
```

### Schema Analysis

Analyze your current database schema:

```bash
# Analyze hosting plans collection
python backend/run_db_reorganization.py migrate analyze

# Validate against standard schema
python backend/run_db_reorganization.py migrate validate --show-errors
```

## Field Mapping Rules

### Frontend Expected Fields
```json
{
  "id": "unique_identifier",
  "name": "Plan Display Name",
  "type": "plan_type_code", 
  "price": 29.99,
  "is_popular": false,
  "sub_type": "plan_subtype"
}
```

### Database Storage Fields
```json
{
  "id": "unique_identifier",
  "plan_name": "Plan Display Name",
  "plan_type": "plan_type_code",
  "base_price": 29.99,
  "popular": false,
  "sub_type": "plan_subtype"
}
```

### Bidirectional Mapping
- `name` ↔ `plan_name`
- `type` ↔ `plan_type`
- `price` ↔ `base_price`
- `is_popular` ↔ `popular`

## Safety Guarantees

### Data Preservation
✅ **Field mapping preserves all original data values**  
✅ **Only field names are changed, not content**  
✅ **All original fields are maintained**  
✅ **Backward compatibility is preserved**  

### Backup Protection
✅ **Automatic backups before major changes**  
✅ **Backup verification and restoration tools**  
✅ **Multiple backup retention**  

### Validation
✅ **Schema validation after changes**  
✅ **Data integrity checks**  
✅ **Error reporting and rollback capabilities**  

## Testing

Run the field mapping tests to verify everything works correctly:

```bash
# Simple field mapping tests
python tests/test_simple_field_mapping.py

# Comprehensive consistency tests (requires MongoDB dependencies)
python tests/test_field_mapping_consistency.py
```

## Example Output

### Field Mapping (Safe Mode)
```
🔄 Field mapping (preserve data) for hosting plans collection (dry_run=True)

📊 Field mapping (preserve data) Results:
Total documents: 15
Processed documents: 15
Errors: 0
Documents with changes: 8

📋 This was a dry run. No changes were made.

Sample changes that would be made:

  Document basic_shared_1:
    + name: Basic Shared Plan (new field)
    + type: shared (new field)  
    + price: 9.99 (new field)
    + is_popular: false (new field)
```

### Full Migration (Advanced)
```
🔄 Full migration with data normalization for hosting plans collection (dry_run=True)

📊 Full migration with data normalization Results:
Total documents: 15
Processed documents: 15
Errors: 0
Documents with changes: 12

Sample changes that would be made:

  Document vps_standard_1:
    + name: VPS Standard (new field)
    cpu: 2 vCPU → 2 vCPU (value normalized)
    ram: 4 GB RAM → 4 GB RAM (value normalized)
```

## Important Notes

1. **Default is Safe**: The system defaults to field mapping only (preserves data)
2. **Always Test First**: Use `--dry-run` to preview changes before applying
3. **Backup First**: Create backups before making any changes
4. **Validate After**: Run validation after changes to ensure integrity
5. **Gradual Approach**: Start with field mapping, then consider full migration if needed

## Troubleshooting

### If Field Mapping Fails
1. Check the error logs for specific issues
2. Verify database connectivity
3. Ensure proper permissions
4. Run validation to identify schema issues

### If Data Seems Changed
1. Field mapping should only add new fields, not change existing ones
2. Use `--show-changes` to see exactly what would be modified
3. Restore from backup if unexpected changes occurred
4. Report the issue for investigation

### If Frontend Still Shows Issues
1. Verify the server is using the updated field mapping
2. Check API responses with browser dev tools
3. Clear browser cache and refresh
4. Restart the backend server

This updated system ensures that hosting plans display correctly on the frontend while maintaining complete data safety and consistency across all tools.