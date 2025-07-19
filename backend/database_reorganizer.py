#!/usr/bin/env python3
"""
Database Reorganizer
Main script for comprehensive database reorganization including backup, migration,
validation, and restoration capabilities for Blue Nebula Hosting database.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient

# Import our custom modules
from database_backup import DatabaseBackup
from schema_migration import SchemaMigration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseReorganizer:
    def __init__(self, mongo_url: str, db_name: str, backup_dir: str = "/tmp/database_backups"):
        """
        Initialize the database reorganizer
        
        Args:
            mongo_url: MongoDB connection string
            db_name: Database name
            backup_dir: Directory for backups
        """
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.backup_dir = Path(backup_dir)
        
        # Initialize subsystems
        self.backup_system = DatabaseBackup(mongo_url, db_name, backup_dir)
        self.migration_system = SchemaMigration(mongo_url, db_name)
        
        self.client = None
        self.db = None
        
        # Collections to reorganize
        self.target_collections = [
            "hosting_plans",
            "hosting_categories", 
            "website_content",
            "navigation_items",
            "company_info",
            "site_settings"
        ]
        
        # Reorganization state tracking
        self.reorganization_status = {
            "started_at": None,
            "completed_at": None,
            "status": "not_started",  # not_started, in_progress, completed, failed
            "backup_files": {},
            "migration_results": {},
            "validation_results": {},
            "errors": []
        }
    
    async def connect(self):
        """Establish database connections"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.client.admin.command('ping')
            
            # Connect subsystems
            await self.backup_system.connect()
            await self.migration_system.connect()
            
            logger.info("✅ Connected to MongoDB and initialized subsystems")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connections"""
        try:
            await self.backup_system.disconnect()
            await self.migration_system.disconnect()
            
            if self.client:
                self.client.close()
            
            logger.info("📡 Disconnected from MongoDB")
        except Exception as e:
            logger.warning(f"⚠️ Error during disconnect: {e}")
    
    async def check_reorganization_status(self) -> Dict:
        """
        Check if database has already been reorganized
        
        Returns:
            Status information
        """
        try:
            # Check for reorganization marker
            marker = await self.db.reorganization_status.find_one({"type": "reorganization_marker"})
            
            if marker:
                return {
                    "reorganized": True,
                    "last_reorganization": marker.get("completed_at"),
                    "reorganization_version": marker.get("version", "unknown"),
                    "collections_reorganized": marker.get("collections", [])
                }
            else:
                return {
                    "reorganized": False,
                    "requires_reorganization": True
                }
        except Exception as e:
            logger.warning(f"⚠️ Could not check reorganization status: {e}")
            return {"reorganized": False, "error": str(e)}
    
    async def create_reorganization_marker(self, results: Dict):
        """
        Create a marker indicating successful reorganization
        
        Args:
            results: Reorganization results
        """
        try:
            marker = {
                "type": "reorganization_marker",
                "version": "1.0",
                "completed_at": datetime.now(timezone.utc),
                "collections": list(results.get("migration_results", {}).keys()),
                "backup_files": results.get("backup_files", {}),
                "validation_passed": results.get("validation_passed", False),
                "reorganization_summary": {
                    "total_collections": len(self.target_collections),
                    "successful_migrations": len([r for r in results.get("migration_results", {}).values() if r.get("success", False)]),
                    "backup_count": len(results.get("backup_files", {}))
                }
            }
            
            await self.db.reorganization_status.update_one(
                {"type": "reorganization_marker"},
                {"$set": marker},
                upsert=True
            )
            
            logger.info("✅ Created reorganization completion marker")
        except Exception as e:
            logger.error(f"❌ Failed to create reorganization marker: {e}")
    
    async def pre_reorganization_analysis(self) -> Dict:
        """
        Analyze database state before reorganization
        
        Returns:
            Analysis results
        """
        logger.info("🔍 Starting pre-reorganization analysis...")
        
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collections": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # Check each target collection
        for collection_name in self.target_collections:
            try:
                collection = self.db[collection_name]
                doc_count = await collection.count_documents({})
                
                collection_analysis = {
                    "exists": doc_count > 0,
                    "document_count": doc_count,
                    "issues": []
                }
                
                if collection_name == "hosting_plans":
                    # Special analysis for hosting plans
                    plans_analysis = await self._analyze_hosting_plans()
                    collection_analysis.update(plans_analysis)
                
                analysis["collections"][collection_name] = collection_analysis
                
            except Exception as e:
                logger.warning(f"⚠️ Could not analyze collection {collection_name}: {e}")
                analysis["collections"][collection_name] = {
                    "exists": False,
                    "error": str(e)
                }
        
        # Generate recommendations
        hosting_plans_analysis = analysis["collections"].get("hosting_plans", {})
        if hosting_plans_analysis.get("field_inconsistencies", 0) > 0:
            analysis["recommendations"].append("Field mapping inconsistencies detected in hosting_plans")
        
        if hosting_plans_analysis.get("missing_required_fields", 0) > 0:
            analysis["recommendations"].append("Missing required fields detected in hosting_plans")
        
        total_docs = sum([c.get("document_count", 0) for c in analysis["collections"].values()])
        analysis["total_documents"] = total_docs
        
        logger.info(f"📊 Analysis complete: {len(self.target_collections)} collections, {total_docs} total documents")
        return analysis
    
    async def _analyze_hosting_plans(self) -> Dict:
        """Analyze hosting plans collection for specific issues"""
        collection = self.db.hosting_plans
        
        analysis = {
            "field_inconsistencies": 0,
            "missing_required_fields": 0,
            "data_type_issues": 0,
            "duplicate_plans": 0,
            "field_distribution": {}
        }
        
        # Sample documents for analysis
        sample_size = min(100, await collection.count_documents({}))
        documents = await collection.find().limit(sample_size).to_list(sample_size)
        
        # Track field usage
        field_counts = {}
        for doc in documents:
            for field in doc.keys():
                if field != "_id":
                    field_counts[field] = field_counts.get(field, 0) + 1
        
        analysis["field_distribution"] = field_counts
        
        # Check for common issues
        for doc in documents:
            # Check for old vs new field names
            if "plan_name" in doc and "name" not in doc:
                analysis["field_inconsistencies"] += 1
            if "base_price" in doc and "price" not in doc:
                analysis["field_inconsistencies"] += 1
            if "plan_type" in doc and "type" not in doc:
                analysis["field_inconsistencies"] += 1
            
            # Check for required fields
            if "name" not in doc and "plan_name" not in doc:
                analysis["missing_required_fields"] += 1
            if "price" not in doc and "base_price" not in doc:
                analysis["missing_required_fields"] += 1
            
            # Check data types
            price_field = doc.get("price") or doc.get("base_price")
            if price_field is not None:
                try:
                    float(price_field)
                except (ValueError, TypeError):
                    analysis["data_type_issues"] += 1
        
        return analysis
    
    async def create_comprehensive_backup(self) -> Dict:
        """
        Create comprehensive backup of all target collections
        
        Returns:
            Backup results
        """
        logger.info("💾 Creating comprehensive backup...")
        
        backup_results = await self.backup_system.backup_multiple_collections(self.target_collections)
        
        # Store backup information in reorganization status
        self.reorganization_status["backup_files"] = {
            collection: results.get("backup_file") 
            for collection, results in backup_results.items() 
            if "error" not in results
        }
        
        successful_backups = len([r for r in backup_results.values() if "error" not in r])
        total_collections = len(self.target_collections)
        
        logger.info(f"✅ Backup complete: {successful_backups}/{total_collections} collections backed up")
        
        return backup_results
    
    async def perform_schema_migration(self) -> Dict:
        """
        Perform schema migration on hosting plans
        
        Returns:
            Migration results
        """
        logger.info("🔄 Starting schema migration...")
        
        migration_results = {}
        
        # Migrate hosting plans
        try:
            # First, remove duplicates
            dedup_results = await self.migration_system.remove_duplicate_hosting_plans(dry_run=False)
            migration_results["deduplication"] = dedup_results
            
            # Then migrate schema
            migration_results["hosting_plans"] = await self.migration_system.migrate_hosting_plans_collection(dry_run=False)
            migration_results["hosting_plans"]["success"] = True
            
        except Exception as e:
            logger.error(f"❌ Schema migration failed: {e}")
            migration_results["hosting_plans"] = {"success": False, "error": str(e)}
        
        self.reorganization_status["migration_results"] = migration_results
        
        return migration_results
    
    async def validate_reorganized_data(self) -> Dict:
        """
        Validate the reorganized data
        
        Returns:
            Validation results
        """
        logger.info("✅ Validating reorganized data...")
        
        validation_results = {}
        
        # Validate hosting plans against standard schema
        try:
            validation_results["hosting_plans"] = await self.migration_system.validate_collection_against_schema(
                "hosting_plans", self.migration_system.standard_hosting_plan_schema
            )
            
            # Check that all plans can be retrieved via API format
            api_validation = await self._validate_api_compatibility()
            validation_results["api_compatibility"] = api_validation
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            validation_results["error"] = str(e)
        
        self.reorganization_status["validation_results"] = validation_results
        
        return validation_results
    
    async def _validate_api_compatibility(self) -> Dict:
        """Validate that reorganized data is compatible with API expectations"""
        collection = self.db.hosting_plans
        
        validation = {
            "total_plans": 0,
            "api_compatible_plans": 0,
            "missing_fields": {},
            "field_type_errors": {},
            "success": False
        }
        
        # Required fields for API compatibility
        required_api_fields = ["id", "name", "type", "price"]
        
        async for plan in collection.find():
            validation["total_plans"] += 1
            
            api_compatible = True
            
            # Check required fields
            for field in required_api_fields:
                if field not in plan:
                    api_compatible = False
                    validation["missing_fields"][field] = validation["missing_fields"].get(field, 0) + 1
            
            # Check field types
            if "price" in plan:
                try:
                    float(plan["price"])
                except (ValueError, TypeError):
                    api_compatible = False
                    validation["field_type_errors"]["price"] = validation["field_type_errors"].get("price", 0) + 1
            
            if api_compatible:
                validation["api_compatible_plans"] += 1
        
        validation["success"] = validation["api_compatible_plans"] == validation["total_plans"]
        validation["compatibility_percentage"] = (
            validation["api_compatible_plans"] / validation["total_plans"] * 100 
            if validation["total_plans"] > 0 else 0
        )
        
        return validation
    
    async def perform_full_reorganization(self, force: bool = False) -> Dict:
        """
        Perform complete database reorganization
        
        Args:
            force: Force reorganization even if already completed
            
        Returns:
            Reorganization results
        """
        logger.info("🚀 Starting complete database reorganization...")
        
        self.reorganization_status["started_at"] = datetime.now(timezone.utc)
        self.reorganization_status["status"] = "in_progress"
        
        try:
            # 1. Check if already reorganized
            if not force:
                status = await self.check_reorganization_status()
                if status.get("reorganized"):
                    logger.info("✅ Database already reorganized. Use --force to reorganize again.")
                    return {
                        "already_reorganized": True,
                        "last_reorganization": status.get("last_reorganization"),
                        "skip_reason": "Already completed"
                    }
            
            # 2. Pre-reorganization analysis
            analysis_results = await self.pre_reorganization_analysis()
            
            # 3. Create comprehensive backup
            backup_results = await self.create_comprehensive_backup()
            
            # Check if all backups succeeded
            failed_backups = [c for c, r in backup_results.items() if "error" in r]
            if failed_backups:
                raise Exception(f"Backup failed for collections: {failed_backups}")
            
            # 4. Perform schema migration
            migration_results = await self.perform_schema_migration()
            
            # 5. Validate reorganized data
            validation_results = await self.validate_reorganized_data()
            
            # 6. Check overall success
            migration_success = migration_results.get("hosting_plans", {}).get("success", False)
            validation_success = validation_results.get("api_compatibility", {}).get("success", False)
            
            overall_success = migration_success and validation_success
            
            # 7. Create completion marker
            results = {
                "success": overall_success,
                "started_at": self.reorganization_status["started_at"],
                "completed_at": datetime.now(timezone.utc),
                "analysis_results": analysis_results,
                "backup_results": backup_results,
                "migration_results": migration_results,
                "validation_results": validation_results,
                "backup_files": self.reorganization_status["backup_files"]
            }
            
            if overall_success:
                await self.create_reorganization_marker(results)
                self.reorganization_status["status"] = "completed"
                logger.info("🎉 Database reorganization completed successfully!")
            else:
                self.reorganization_status["status"] = "failed"
                logger.error("❌ Database reorganization failed validation")
            
            self.reorganization_status["completed_at"] = datetime.now(timezone.utc)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Database reorganization failed: {e}")
            self.reorganization_status["status"] = "failed"
            self.reorganization_status["errors"].append(str(e))
            self.reorganization_status["completed_at"] = datetime.now(timezone.utc)
            
            return {
                "success": False,
                "error": str(e),
                "reorganization_status": self.reorganization_status
            }
    
    async def emergency_restore(self, backup_manifest_file: str) -> Dict:
        """
        Emergency restore from backup manifest
        
        Args:
            backup_manifest_file: Path to backup manifest file
            
        Returns:
            Restore results
        """
        logger.info(f"🚨 Starting emergency restore from {backup_manifest_file}")
        
        try:
            # Load backup manifest
            with open(backup_manifest_file, 'r') as f:
                manifest = json.load(f)
            
            restore_results = {}
            
            for collection_name, collection_info in manifest["collections"].items():
                if "error" in collection_info:
                    logger.warning(f"⚠️ Skipping {collection_name} - backup had error: {collection_info['error']}")
                    continue
                
                backup_file = collection_info["backup_file"]
                
                try:
                    result = await self.backup_system.restore_collection(
                        backup_file, collection_name, mode="replace"
                    )
                    restore_results[collection_name] = result
                    logger.info(f"✅ Restored {collection_name} from {backup_file}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to restore {collection_name}: {e}")
                    restore_results[collection_name] = {"error": str(e)}
            
            # Remove reorganization marker if restore was successful
            successful_restores = len([r for r in restore_results.values() if "error" not in r])
            if successful_restores > 0:
                await self.db.reorganization_status.delete_one({"type": "reorganization_marker"})
                logger.info("🔄 Removed reorganization marker after restore")
            
            return {
                "success": successful_restores > 0,
                "restored_collections": successful_restores,
                "total_collections": len(manifest["collections"]),
                "restore_results": restore_results,
                "manifest_file": backup_manifest_file
            }
            
        except Exception as e:
            logger.error(f"❌ Emergency restore failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_reorganization_report(self, results: Dict) -> str:
        """
        Generate a comprehensive reorganization report
        
        Args:
            results: Reorganization results
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "# Database Reorganization Report",
            "=" * 50,
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            ""
        ]
        
        if results.get("success"):
            report_lines.extend([
                "## ✅ REORGANIZATION SUCCESSFUL",
                "",
                f"Started: {results.get('started_at')}",
                f"Completed: {results.get('completed_at')}",
                ""
            ])
        else:
            report_lines.extend([
                "## ❌ REORGANIZATION FAILED",
                "",
                f"Error: {results.get('error', 'Unknown error')}",
                ""
            ])
        
        # Analysis summary
        analysis = results.get("analysis_results", {})
        if analysis:
            report_lines.extend([
                "## 📊 Pre-Analysis Summary",
                f"Total documents analyzed: {analysis.get('total_documents', 0)}",
                f"Collections analyzed: {len(analysis.get('collections', {}))}",
                ""
            ])
        
        # Backup summary
        backup_results = results.get("backup_results", {})
        if backup_results:
            successful_backups = len([r for r in backup_results.values() if "error" not in r])
            report_lines.extend([
                "## 💾 Backup Summary", 
                f"Collections backed up: {successful_backups}/{len(backup_results)}",
                ""
            ])
            
            for collection, result in backup_results.items():
                if "error" not in result:
                    report_lines.append(f"✅ {collection}: {result.get('document_count', 0)} documents")
                else:
                    report_lines.append(f"❌ {collection}: {result['error']}")
            report_lines.append("")
        
        # Migration summary
        migration_results = results.get("migration_results", {})
        if migration_results:
            report_lines.extend([
                "## 🔄 Migration Summary",
                ""
            ])
            
            hosting_plans_migration = migration_results.get("hosting_plans", {})
            if hosting_plans_migration:
                report_lines.extend([
                    f"Hosting Plans Migration:",
                    f"  Total documents: {hosting_plans_migration.get('total_documents', 0)}",
                    f"  Migrated: {hosting_plans_migration.get('migrated_documents', 0)}",
                    f"  Errors: {hosting_plans_migration.get('error_count', 0)}",
                    ""
                ])
            
            dedup_results = migration_results.get("deduplication", {})
            if dedup_results:
                report_lines.extend([
                    f"Deduplication:",
                    f"  Duplicates found: {dedup_results.get('duplicates_found', 0)}",
                    f"  Duplicates removed: {dedup_results.get('duplicates_removed', 0)}",
                    ""
                ])
        
        # Validation summary
        validation_results = results.get("validation_results", {})
        if validation_results:
            report_lines.extend([
                "## ✅ Validation Summary",
                ""
            ])
            
            hosting_plans_validation = validation_results.get("hosting_plans", {})
            if hosting_plans_validation:
                report_lines.extend([
                    f"Schema Validation:",
                    f"  Total documents: {hosting_plans_validation.get('total_documents', 0)}",
                    f"  Valid documents: {hosting_plans_validation.get('valid_documents', 0)}",
                    f"  Validation percentage: {hosting_plans_validation.get('validation_percentage', 0):.1f}%",
                    ""
                ])
            
            api_validation = validation_results.get("api_compatibility", {})
            if api_validation:
                report_lines.extend([
                    f"API Compatibility:",
                    f"  Total plans: {api_validation.get('total_plans', 0)}",
                    f"  API compatible: {api_validation.get('api_compatible_plans', 0)}",
                    f"  Compatibility: {api_validation.get('compatibility_percentage', 0):.1f}%",
                    ""
                ])
        
        # Backup files
        backup_files = results.get("backup_files", {})
        if backup_files:
            report_lines.extend([
                "## 📁 Backup Files Created",
                ""
            ])
            for collection, backup_file in backup_files.items():
                report_lines.append(f"{collection}: {backup_file}")
            report_lines.append("")
        
        return "\n".join(report_lines)


async def main():
    """Command-line interface for database reorganization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Reorganization System")
    parser.add_argument("--mongo-url", 
                       default=os.environ.get('MONGO_URL', 'mongodb://admin:WEvSMiUiYlASPYN4Pqb7zLO8E@dev.bluenebulahosting.com:27018/blue_nebula_hosting?authSource=admin'),
                       help="MongoDB connection string")
    parser.add_argument("--db-name", default=os.environ.get('DB_NAME', 'blue_nebula_hosting'),
                       help="Database name")
    parser.add_argument("--backup-dir", default="/tmp/database_backups",
                       help="Backup directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Full reorganization command
    reorganize_parser = subparsers.add_parser("reorganize", help="Perform full database reorganization")
    reorganize_parser.add_argument("--force", action="store_true", 
                                  help="Force reorganization even if already completed")
    reorganize_parser.add_argument("--report-file", help="Save report to file")
    
    # Status check command
    status_parser = subparsers.add_parser("status", help="Check reorganization status")
    
    # Analysis command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze database state")
    
    # Emergency restore command
    restore_parser = subparsers.add_parser("emergency-restore", help="Emergency restore from backup")
    restore_parser.add_argument("manifest_file", help="Path to backup manifest file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    reorganizer = DatabaseReorganizer(args.mongo_url, args.db_name, args.backup_dir)
    
    try:
        await reorganizer.connect()
        
        if args.command == "reorganize":
            results = await reorganizer.perform_full_reorganization(force=args.force)
            
            # Generate report
            report = reorganizer.generate_reorganization_report(results)
            print(report)
            
            # Save report to file if requested
            if args.report_file:
                with open(args.report_file, 'w') as f:
                    f.write(report)
                print(f"\n📄 Report saved to: {args.report_file}")
            
            # Exit with appropriate code
            sys.exit(0 if results.get("success") else 1)
            
        elif args.command == "status":
            status = await reorganizer.check_reorganization_status()
            if status.get("reorganized"):
                print("✅ Database has been reorganized")
                print(f"Last reorganization: {status.get('last_reorganization')}")
                print(f"Version: {status.get('reorganization_version')}")
                print(f"Collections: {', '.join(status.get('collections_reorganized', []))}")
            else:
                print("❌ Database has not been reorganized")
                if "error" in status:
                    print(f"Error checking status: {status['error']}")
                    
        elif args.command == "analyze":
            analysis = await reorganizer.pre_reorganization_analysis()
            print("📊 Database Analysis Results:")
            print(f"Total documents: {analysis.get('total_documents', 0)}")
            print(f"Collections analyzed: {len(analysis.get('collections', {}))}")
            
            for collection_name, info in analysis.get("collections", {}).items():
                if info.get("exists"):
                    print(f"\n{collection_name}:")
                    print(f"  Documents: {info.get('document_count', 0)}")
                    if collection_name == "hosting_plans":
                        print(f"  Field inconsistencies: {info.get('field_inconsistencies', 0)}")
                        print(f"  Missing required fields: {info.get('missing_required_fields', 0)}")
                        print(f"  Data type issues: {info.get('data_type_issues', 0)}")
                else:
                    print(f"\n{collection_name}: Not found or empty")
            
            if analysis.get("recommendations"):
                print(f"\n📝 Recommendations:")
                for rec in analysis["recommendations"]:
                    print(f"  • {rec}")
                    
        elif args.command == "emergency-restore":
            results = await reorganizer.emergency_restore(args.manifest_file)
            if results.get("success"):
                print(f"✅ Emergency restore completed")
                print(f"Restored collections: {results.get('restored_collections')}/{results.get('total_collections')}")
            else:
                print(f"❌ Emergency restore failed: {results.get('error')}")
                sys.exit(1)
                
    finally:
        await reorganizer.disconnect()


if __name__ == "__main__":
    asyncio.run(main())