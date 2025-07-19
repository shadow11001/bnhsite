#!/usr/bin/env python3
"""
Database Reorganization CLI Runner
Command-line interface for running database reorganization operations
with comprehensive logging and error handling.
"""

import os
import sys
import asyncio
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database_reorganizer import DatabaseReorganizer
from database_backup import DatabaseBackup
from schema_migration import SchemaMigration

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        print(f"📝 Logging to file: {log_file}")

async def run_full_reorganization(args):
    """Run full database reorganization"""
    reorganizer = DatabaseReorganizer(args.mongo_url, args.db_name, args.backup_dir)
    
    try:
        await reorganizer.connect()
        
        print("🚀 Starting database reorganization...")
        print(f"📊 Database: {args.db_name}")
        print(f"💾 Backup directory: {args.backup_dir}")
        print(f"🔄 Force mode: {args.force}")
        print()
        
        # Run reorganization
        results = await reorganizer.perform_full_reorganization(force=args.force)
        
        # Generate and display report
        report = reorganizer.generate_reorganization_report(results)
        print(report)
        
        # Save report if requested
        if args.report_file:
            with open(args.report_file, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {args.report_file}")
        
        # Save results as JSON if requested
        if args.results_file:
            with open(args.results_file, 'w') as f:
                # Convert datetime objects to strings for JSON serialization
                json_results = json.loads(json.dumps(results, default=str))
                json.dump(json_results, f, indent=2)
            print(f"📊 Results saved to: {args.results_file}")
        
        if results.get("success"):
            print("\n🎉 Database reorganization completed successfully!")
            return 0
        else:
            print(f"\n❌ Database reorganization failed: {results.get('error')}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Reorganization interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.exception("Unexpected error during reorganization")
        return 1
    finally:
        await reorganizer.disconnect()

async def run_backup_operation(args):
    """Run backup operation"""
    backup_system = DatabaseBackup(args.mongo_url, args.db_name, args.backup_dir)
    
    try:
        await backup_system.connect()
        
        if args.backup_command == "create":
            if args.collections:
                # Backup specific collections
                print(f"💾 Creating backup for collections: {', '.join(args.collections)}")
                results = await backup_system.backup_multiple_collections(args.collections)
                
                successful = [c for c, r in results.items() if "error" not in r]
                failed = [c for c, r in results.items() if "error" in r]
                
                print(f"✅ Successfully backed up: {', '.join(successful)}")
                if failed:
                    print(f"❌ Failed to backup: {', '.join(failed)}")
                    return 1
                
            else:
                # Backup single collection
                collection = args.collection or "hosting_plans"
                print(f"💾 Creating backup for collection: {collection}")
                backup_file, metadata = await backup_system.backup_collection(collection)
                print(f"✅ Backup created: {backup_file}")
                print(f"📊 Documents backed up: {metadata['document_count']}")
        
        elif args.backup_command == "list":
            # List backups
            backups = backup_system.list_backups(args.collection)
            if not backups:
                print("📁 No backups found")
            else:
                print(f"📁 Found {len(backups)} backup(s):")
                for backup in backups:
                    print(f"  • {backup['file_name']}")
                    print(f"    Collection: {backup.get('collection_name', 'unknown')}")
                    print(f"    Documents: {backup.get('document_count', '?')}")
                    print(f"    Created: {backup.get('backup_created_at', backup['created_at'])}")
                    print(f"    Size: {backup['file_size']:,} bytes")
                    print()
        
        elif args.backup_command == "restore":
            # Restore from backup
            if not args.backup_file:
                print("❌ Backup file path required for restore operation")
                return 1
            
            print(f"🔄 Restoring from: {args.backup_file}")
            print(f"Target collection: {args.target_collection or 'original'}")
            print(f"Mode: {args.restore_mode}")
            
            metadata = await backup_system.restore_collection(
                args.backup_file, 
                args.target_collection, 
                args.restore_mode
            )
            
            print(f"✅ Restore completed")
            print(f"📊 Documents restored: {metadata['documents_restored']}")
            print(f"📊 Final document count: {metadata['final_document_count']}")
        
        elif args.backup_command == "verify":
            # Verify backup
            if not args.backup_file:
                print("❌ Backup file path required for verify operation")
                return 1
            
            verification = await backup_system.verify_backup(args.backup_file)
            
            if verification["is_valid"]:
                print("✅ Backup file is valid")
                print(f"📊 Documents: {verification['documents_count']}")
                print(f"📁 File size: {verification['file_size']:,} bytes")
            else:
                print("❌ Backup file is invalid:")
                for error in verification["verification_errors"]:
                    print(f"  • {error}")
                return 1
        
        elif args.backup_command == "cleanup":
            # Cleanup old backups
            deleted_count = backup_system.cleanup_old_backups(args.keep_count, args.collection)
            print(f"🧹 Deleted {deleted_count} old backup files")
        
        return 0
        
    except Exception as e:
        print(f"❌ Backup operation failed: {e}")
        logging.exception("Backup operation failed")
        return 1
    finally:
        await backup_system.disconnect()

async def run_migration_operation(args):
    """Run schema migration operation"""
    migration = SchemaMigration(args.mongo_url, args.db_name)
    
    try:
        await migration.connect()
        
        if args.migration_command == "analyze":
            # Analyze schema
            collection = args.collection or "hosting_plans"
            print(f"🔍 Analyzing schema for collection: {collection}")
            
            results = await migration.analyze_collection_schema(collection)
            print(f"\n📊 Schema Analysis for '{collection}':")
            print(f"Total documents: {results['total_documents']}")
            print(f"Sample size: {results['sample_size']}")
            print("\nField Analysis:")
            
            for field_name, info in results['field_analysis'].items():
                print(f"\n  {field_name}:")
                print(f"    Coverage: {info['coverage']:.1f}%")
                print(f"    Predominant type: {info['predominant_type']}")
                if len(info['sample_values']) > 0:
                    print(f"    Sample values: {info['sample_values'][:3]}")
        
        elif args.migration_command == "validate":
            # Validate against schema
            collection = args.collection or "hosting_plans"
            
            if collection == "hosting_plans":
                print(f"✅ Validating {collection} against standard schema...")
                results = await migration.validate_collection_against_schema(
                    collection, migration.standard_hosting_plan_schema
                )
                
                print(f"\n📊 Validation Results:")
                print(f"Total documents: {results['total_documents']}")
                print(f"Valid documents: {results['valid_documents']}")
                print(f"Invalid documents: {results['invalid_documents']}")
                print(f"Validation percentage: {results['validation_percentage']:.1f}%")
                
                if results['validation_errors'] and args.show_errors:
                    print(f"\n❌ Validation Errors (showing first 10):")
                    for doc_id, errors in list(results['validation_errors'].items())[:10]:
                        print(f"  Document {doc_id}:")
                        for error in errors:
                            print(f"    - {error}")
                
                return 0 if results['invalid_documents'] == 0 else 1
            else:
                print(f"❌ Validation not implemented for collection '{collection}'")
                return 1
        
        elif args.migration_command == "migrate":
            # Perform migration
            print(f"🔄 Migrating hosting plans collection (dry_run={args.dry_run})")
            
            results = await migration.migrate_hosting_plans_collection(dry_run=args.dry_run)
            
            print(f"\n📊 Migration Results:")
            print(f"Total documents: {results['total_documents']}")
            print(f"Migrated documents: {results['migrated_documents']}")
            print(f"Errors: {results['error_count']}")
            print(f"Changes: {len(results['changes_preview'])}")
            
            if args.dry_run:
                print("\n📋 This was a dry run. No changes were made.")
                if results['changes_preview'] and args.show_changes:
                    print("\nSample changes that would be made:")
                    for doc_id, changes in list(results['changes_preview'].items())[:5]:
                        print(f"\n  Document {doc_id}:")
                        for field, change in changes.items():
                            print(f"    {field}: {change['old']} → {change['new']}")
            else:
                print("\n✅ Migration completed.")
                
                # Validate after migration
                if args.validate_after:
                    print("\n🔍 Running post-migration validation...")
                    validation_results = await migration.validate_collection_against_schema(
                        "hosting_plans", migration.standard_hosting_plan_schema
                    )
                    print(f"Validation: {validation_results['valid_documents']}/{validation_results['total_documents']} documents valid")
        
        elif args.migration_command == "deduplicate":
            # Remove duplicates
            print(f"🔍 Removing duplicate hosting plans (dry_run={args.dry_run})")
            
            results = await migration.remove_duplicate_hosting_plans(dry_run=args.dry_run)
            
            print(f"\n📊 Deduplication Results:")
            print(f"Duplicates found: {results['duplicates_found']}")
            print(f"Duplicate groups: {results['duplicate_groups']}")
            
            if args.dry_run:
                print("\n📋 This was a dry run. No changes were made.")
                if results['duplicate_details']:
                    print("\nDuplicate groups found:")
                    for group_key, details in results['duplicate_details'].items():
                        print(f"  {group_key}: {details['total_count']} duplicates")
                        print(f"    Keeping: {details['keeping']['id']}")
                        print(f"    Removing: {', '.join(details['removing'])}")
            else:
                print(f"Duplicates removed: {results['duplicates_removed']}")
        
        elif args.migration_command == "schema-doc":
            # Generate schema documentation
            doc = migration.generate_schema_documentation(migration.standard_hosting_plan_schema)
            print("\n📚 Hosting Plans Schema Documentation:")
            print("=" * 60)
            print(doc)
        
        return 0
        
    except Exception as e:
        print(f"❌ Migration operation failed: {e}")
        logging.exception("Migration operation failed")
        return 1
    finally:
        await migration.disconnect()

async def run_status_check(args):
    """Check database reorganization status"""
    reorganizer = DatabaseReorganizer(args.mongo_url, args.db_name, args.backup_dir)
    
    try:
        await reorganizer.connect()
        
        # Check reorganization status
        status = await reorganizer.check_reorganization_status()
        
        if status.get("reorganized"):
            print("✅ Database has been reorganized")
            print(f"📅 Last reorganization: {status.get('last_reorganization')}")
            print(f"🏷️  Version: {status.get('reorganization_version')}")
            print(f"📂 Collections: {', '.join(status.get('collections_reorganized', []))}")
        else:
            print("❌ Database has not been reorganized")
            if "error" in status:
                print(f"⚠️ Error checking status: {status['error']}")
        
        # Additional analysis if requested
        if args.detailed:
            print("\n🔍 Running detailed analysis...")
            analysis = await reorganizer.pre_reorganization_analysis()
            
            print(f"\n📊 Database Analysis:")
            print(f"Total documents: {analysis.get('total_documents', 0)}")
            print(f"Collections: {len(analysis.get('collections', {}))}")
            
            # Show collection details
            for collection_name, info in analysis.get("collections", {}).items():
                print(f"\n  {collection_name}:")
                if info.get("exists"):
                    print(f"    📊 Documents: {info.get('document_count', 0)}")
                    if collection_name == "hosting_plans":
                        print(f"    ⚠️  Field inconsistencies: {info.get('field_inconsistencies', 0)}")
                        print(f"    ❌ Missing required fields: {info.get('missing_required_fields', 0)}")
                        print(f"    🔧 Data type issues: {info.get('data_type_issues', 0)}")
                else:
                    print("    📭 Not found or empty")
            
            # Show recommendations
            if analysis.get("recommendations"):
                print(f"\n📝 Recommendations:")
                for rec in analysis["recommendations"]:
                    print(f"  • {rec}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        logging.exception("Status check failed")
        return 1
    finally:
        await reorganizer.disconnect()

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Database Reorganization CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full reorganization
  python run_db_reorganization.py reorganize --force
  
  # Check status
  python run_db_reorganization.py status --detailed
  
  # Create backup
  python run_db_reorganization.py backup create --collections hosting_plans
  
  # Migrate schema (dry run)
  python run_db_reorganization.py migrate migrate --dry-run
  
  # Analyze current schema
  python run_db_reorganization.py migrate analyze
        """
    )
    
    # Global options
    parser.add_argument("--mongo-url", 
                       default=os.environ.get('MONGO_URL', 
                                             'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@dev.bluenebulahosting.com:27018/blue_nebula_hosting?authSource=admin'),
                       help="MongoDB connection string")
    parser.add_argument("--db-name", default=os.environ.get('DB_NAME', 'blue_nebula_hosting'),
                       help="Database name")
    parser.add_argument("--backup-dir", default="/tmp/database_backups",
                       help="Backup directory")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Logging level")
    parser.add_argument("--log-file", help="Log to file")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Reorganization command
    reorg_parser = subparsers.add_parser("reorganize", help="Perform full database reorganization")
    reorg_parser.add_argument("--force", action="store_true", 
                             help="Force reorganization even if already completed")
    reorg_parser.add_argument("--report-file", help="Save detailed report to file")
    reorg_parser.add_argument("--results-file", help="Save results as JSON")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check reorganization status")
    status_parser.add_argument("--detailed", action="store_true", 
                              help="Show detailed analysis")
    
    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Backup operations")
    backup_subparsers = backup_parser.add_subparsers(dest="backup_command", help="Backup commands")
    
    # Backup create
    backup_create = backup_subparsers.add_parser("create", help="Create backup")
    backup_create.add_argument("--collection", help="Single collection to backup")
    backup_create.add_argument("--collections", nargs="+", help="Multiple collections to backup")
    
    # Backup list
    backup_list = backup_subparsers.add_parser("list", help="List backups")
    backup_list.add_argument("--collection", help="Filter by collection")
    
    # Backup restore
    backup_restore = backup_subparsers.add_parser("restore", help="Restore from backup")
    backup_restore.add_argument("backup_file", help="Backup file to restore")
    backup_restore.add_argument("--target-collection", help="Target collection name")
    backup_restore.add_argument("--restore-mode", choices=["replace", "append", "update"], 
                               default="replace", help="Restore mode")
    
    # Backup verify
    backup_verify = backup_subparsers.add_parser("verify", help="Verify backup file")
    backup_verify.add_argument("backup_file", help="Backup file to verify")
    
    # Backup cleanup
    backup_cleanup = backup_subparsers.add_parser("cleanup", help="Clean up old backups")
    backup_cleanup.add_argument("--keep-count", type=int, default=10, 
                               help="Number of recent backups to keep")
    backup_cleanup.add_argument("--collection", help="Filter by collection")
    
    # Migration commands
    migrate_parser = subparsers.add_parser("migrate", help="Schema migration operations")
    migrate_subparsers = migrate_parser.add_subparsers(dest="migration_command", help="Migration commands")
    
    # Migration analyze
    migrate_analyze = migrate_subparsers.add_parser("analyze", help="Analyze collection schema")
    migrate_analyze.add_argument("--collection", default="hosting_plans", help="Collection to analyze")
    
    # Migration validate
    migrate_validate = migrate_subparsers.add_parser("validate", help="Validate against schema")
    migrate_validate.add_argument("--collection", default="hosting_plans", help="Collection to validate")
    migrate_validate.add_argument("--show-errors", action="store_true", help="Show validation errors")
    
    # Migration migrate
    migrate_migrate = migrate_subparsers.add_parser("migrate", help="Perform schema migration")
    migrate_migrate.add_argument("--dry-run", action="store_true", help="Dry run mode")
    migrate_migrate.add_argument("--show-changes", action="store_true", help="Show sample changes")
    migrate_migrate.add_argument("--validate-after", action="store_true", help="Validate after migration")
    
    # Migration deduplicate
    migrate_dedup = migrate_subparsers.add_parser("deduplicate", help="Remove duplicates")
    migrate_dedup.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    # Migration schema documentation
    migrate_schema_doc = migrate_subparsers.add_parser("schema-doc", help="Generate schema documentation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Run appropriate command
    try:
        if args.command == "reorganize":
            return asyncio.run(run_full_reorganization(args))
        elif args.command == "status":
            return asyncio.run(run_status_check(args))
        elif args.command == "backup":
            return asyncio.run(run_backup_operation(args))
        elif args.command == "migrate":
            return asyncio.run(run_migration_operation(args))
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logging.exception("Unexpected error")
        return 1

if __name__ == "__main__":
    sys.exit(main())