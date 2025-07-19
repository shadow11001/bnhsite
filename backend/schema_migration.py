#!/usr/bin/env python3
"""
Schema Migration Utilities
Provides comprehensive schema migration and validation functionality for hosting plans
and other MongoDB collections with field mapping and data validation.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uuid

# Import the consistent field mapping function from utility module
from field_mapping_utils import map_hosting_plan_fields

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaMigration:
    def __init__(self, mongo_url: str, db_name: str):
        """
        Initialize schema migration system
        
        Args:
            mongo_url: MongoDB connection string
            db_name: Database name
        """
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.client = None
        self.db = None
        
        # Define the standardized schema for hosting plans
        self.standard_hosting_plan_schema = {
            # Core identification fields
            "id": {"type": str, "required": True, "description": "Unique plan identifier"},
            "name": {"type": str, "required": True, "description": "Plan display name"},
            "type": {"type": str, "required": True, "description": "Plan type (shared, vps, gameserver, custom)"},
            "sub_type": {"type": str, "required": False, "description": "Plan sub-type (ssd, hdd, standard, performance, etc.)"},
            "category_key": {"type": str, "required": False, "description": "Category reference key"},
            
            # Pricing fields
            "price": {"type": float, "required": True, "description": "Base price per billing cycle"},
            "billing_cycle": {"type": str, "required": False, "default": "monthly", "description": "Billing cycle"},
            "markup_percentage": {"type": int, "required": False, "default": 0, "description": "Internal markup percentage"},
            
            # Technical specifications
            "cpu": {"type": str, "required": False, "description": "CPU specification"},
            "cpu_cores": {"type": int, "required": False, "description": "Number of CPU cores"},
            "ram": {"type": str, "required": False, "description": "RAM specification"},
            "memory_gb": {"type": int, "required": False, "description": "Memory in GB"},
            "disk_space": {"type": str, "required": False, "description": "Disk space specification"},
            "disk_gb": {"type": int, "required": False, "description": "Disk space in GB"},
            "disk_type": {"type": str, "required": False, "default": "SSD", "description": "Storage type"},
            "bandwidth": {"type": str, "required": False, "description": "Bandwidth specification"},
            
            # Shared hosting specific fields
            "websites": {"type": [str, int], "required": False, "description": "Number of websites allowed"},
            "subdomains": {"type": str, "required": False, "description": "Subdomains limit"},
            "parked_domains": {"type": str, "required": False, "description": "Parked domains limit"},
            "addon_domains": {"type": str, "required": False, "description": "Addon domains limit"},
            "databases": {"type": [str, int], "required": False, "description": "Database limit"},
            "email_accounts": {"type": str, "required": False, "description": "Email accounts limit"},
            
            # VPS/GameServer specific fields
            "ip_addresses": {"type": str, "required": False, "description": "IP addresses specification"},
            "os_choices": {"type": str, "required": False, "description": "Operating system choices"},
            "max_players": {"type": str, "required": False, "description": "Maximum players (GameServer)"},
            
            # Additional fields
            "features": {"type": list, "required": False, "default": [], "description": "List of plan features"},
            "supported_games": {"type": list, "required": False, "description": "Supported games list"},
            "is_popular": {"type": bool, "required": False, "default": False, "description": "Popular plan flag"},
            "is_customizable": {"type": bool, "required": False, "default": False, "description": "Customizable plan flag"},
            "docker_image": {"type": str, "required": False, "description": "Docker image for containerized plans"},
            "managed_wordpress": {"type": bool, "required": False, "default": False, "description": "Managed WordPress flag"},
            "auto_scaling": {"type": bool, "required": False, "default": False, "description": "Auto-scaling support"},
            
            # SSL and backup fields
            "ssl_certificate": {"type": str, "required": False, "description": "SSL certificate information"},
            "backup": {"type": str, "required": False, "description": "Backup information"},
            "support": {"type": str, "required": False, "description": "Support level"},
            
            # External links
            "order_url": {"type": str, "required": False, "description": "Order/purchase URL"},
            
            # Metadata
            "created_at": {"type": datetime, "required": False, "description": "Creation timestamp"},
            "updated_at": {"type": datetime, "required": False, "description": "Last update timestamp"}
        }
        
        # Field mapping from old schema to new schema
        self.field_mappings = {
            # Core fields
            "plan_name": "name",
            "plan_type": "type", 
            "base_price": "price",
            "popular": "is_popular",
            
            # Keep these fields as-is but ensure they exist
            "id": "id",
            "type": "type",
            "sub_type": "sub_type", 
            "category_key": "category_key",
            "name": "name",
            "price": "price",
            "is_popular": "is_popular",
            
            # Technical specifications
            "cpu_cores": "cpu_cores",
            "memory_gb": "memory_gb",
            "disk_gb": "disk_gb",
            "disk_type": "disk_type",
            "bandwidth": "bandwidth",
            
            # Shared hosting fields
            "websites": "websites",
            "subdomains": "subdomains",
            "parked_domains": "parked_domains",
            "addon_domains": "addon_domains", 
            "databases": "databases",
            "email_accounts": "email_accounts",
            
            # Other fields
            "features": "features",
            "supported_games": "supported_games",
            "markup_percentage": "markup_percentage",
            "is_customizable": "is_customizable",
            "docker_image": "docker_image",
            "managed_wordpress": "managed_wordpress",
            "auto_scaling": "auto_scaling"
        }
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            await self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("📡 Disconnected from MongoDB")
    
    def validate_document(self, document: Dict, schema: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a document against a schema
        
        Args:
            document: Document to validate
            schema: Schema definition
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field_name, field_def in schema.items():
            if field_def.get("required", False) and field_name not in document:
                errors.append(f"Missing required field: {field_name}")
                continue
            
            if field_name in document:
                value = document[field_name]
                expected_type = field_def["type"]
                
                # Handle type checking
                if isinstance(expected_type, list):
                    # Multiple allowed types
                    if not any(isinstance(value, t) for t in expected_type):
                        errors.append(f"Field '{field_name}' has invalid type. Expected one of {expected_type}, got {type(value)}")
                else:
                    if not isinstance(value, expected_type):
                        errors.append(f"Field '{field_name}' has invalid type. Expected {expected_type}, got {type(value)}")
        
        return len(errors) == 0, errors
    
    def migrate_hosting_plan_document(self, document: Dict, preserve_data_only=True) -> Dict:
        """
        Migrate a single hosting plan document to the standard schema using consistent field mapping.
        
        Args:
            document: Original document
            preserve_data_only: If True, only rename fields without changing data values
            
        Returns:
            Migrated document with renamed fields
        """
        # Use the consistent field mapping function from server.py
        # First map from database format to frontend format (standard format)
        migrated = map_hosting_plan_fields(document, to_frontend=True)
        
        # Preserve original data - copy any fields that weren't mapped
        for field_name, value in document.items():
            if field_name not in migrated and field_name != "_id":
                migrated[field_name] = value
        
        # Only add essential missing fields without changing existing data
        if "id" not in migrated and "_id" in document:
            migrated["id"] = str(document["_id"])
        elif "id" not in migrated:
            migrated["id"] = str(uuid.uuid4())
        
        # Only add timestamps if they don't exist, without modifying existing ones
        now = datetime.now(timezone.utc)
        if "created_at" not in migrated:
            migrated["created_at"] = now
        if "updated_at" not in migrated:
            migrated["updated_at"] = now
        
        # If preserve_data_only is False, apply data normalization (optional)
        if not preserve_data_only:
            migrated = self._normalize_hosting_plan_data(migrated)
            
            # Set default values for missing fields
            for field_name, field_def in self.standard_hosting_plan_schema.items():
                if "default" in field_def and field_name not in migrated:
                    migrated[field_name] = field_def["default"]
        
        return migrated
    
    def _normalize_hosting_plan_data(self, document: Dict) -> Dict:
        """
        Normalize data types and values in a hosting plan document
        
        Args:
            document: Document to normalize
            
        Returns:
            Normalized document
        """
        normalized = document.copy()
        
        # Normalize price to float
        if "price" in normalized:
            try:
                normalized["price"] = float(normalized["price"])
            except (ValueError, TypeError):
                logger.warning(f"Could not convert price to float: {normalized['price']}")
                normalized["price"] = 0.0
        
        # Normalize CPU specifications
        if "cpu_cores" in normalized and "cpu" not in normalized:
            cores = normalized["cpu_cores"]
            if isinstance(cores, (int, float)):
                if normalized.get("type") == "shared":
                    normalized["cpu"] = f"{int(cores)} Core"
                else:
                    normalized["cpu"] = f"{int(cores)} vCPU"
        
        # Normalize RAM specifications
        if "memory_gb" in normalized and "ram" not in normalized:
            memory = normalized["memory_gb"]
            if isinstance(memory, (int, float)):
                normalized["ram"] = f"{int(memory)} GB RAM"
        
        # Normalize disk space specifications
        if "disk_gb" in normalized and "disk_space" not in normalized:
            disk = normalized["disk_gb"]
            disk_type = normalized.get("disk_type", "SSD")
            if isinstance(disk, (int, float)):
                normalized["disk_space"] = f"{int(disk)} GB {disk_type}"
        
        # Normalize boolean fields
        for bool_field in ["is_popular", "is_customizable", "managed_wordpress", "auto_scaling"]:
            if bool_field in normalized:
                if isinstance(normalized[bool_field], str):
                    normalized[bool_field] = normalized[bool_field].lower() in ["true", "1", "yes"]
                else:
                    normalized[bool_field] = bool(normalized[bool_field])
        
        # Normalize markup_percentage to int
        if "markup_percentage" in normalized:
            try:
                normalized["markup_percentage"] = int(normalized["markup_percentage"])
            except (ValueError, TypeError):
                normalized["markup_percentage"] = 0
        
        # Normalize features list
        if "features" in normalized and not isinstance(normalized["features"], list):
            if isinstance(normalized["features"], str):
                # Try to split string features
                normalized["features"] = [f.strip() for f in normalized["features"].split(",") if f.strip()]
            else:
                normalized["features"] = []
        
        # Ensure certain fields are strings
        string_fields = ["name", "type", "sub_type", "category_key", "bandwidth", "websites", 
                        "subdomains", "parked_domains", "addon_domains", "databases", "email_accounts"]
        for field in string_fields:
            if field in normalized and normalized[field] is not None:
                normalized[field] = str(normalized[field])
        
        return normalized
    
    async def analyze_collection_schema(self, collection_name: str) -> Dict:
        """
        Analyze the current schema of a collection
        
        Args:
            collection_name: Name of collection to analyze
            
        Returns:
            Schema analysis results
        """
        collection = self.db[collection_name]
        
        # Get sample documents
        sample_size = min(1000, await collection.count_documents({}))
        documents = await collection.find().limit(sample_size).to_list(sample_size)
        
        if not documents:
            return {"message": "Collection is empty", "field_analysis": {}}
        
        # Analyze fields
        field_analysis = {}
        total_docs = len(documents)
        
        for doc in documents:
            for field_name, value in doc.items():
                if field_name == "_id":
                    continue
                
                if field_name not in field_analysis:
                    field_analysis[field_name] = {
                        "count": 0,
                        "types": {},
                        "sample_values": [],
                        "null_count": 0
                    }
                
                field_info = field_analysis[field_name]
                field_info["count"] += 1
                
                if value is None:
                    field_info["null_count"] += 1
                else:
                    value_type = type(value).__name__
                    field_info["types"][value_type] = field_info["types"].get(value_type, 0) + 1
                    
                    if len(field_info["sample_values"]) < 5:
                        field_info["sample_values"].append(value)
        
        # Calculate coverage and predominant types
        for field_name, field_info in field_analysis.items():
            field_info["coverage"] = (field_info["count"] / total_docs) * 100
            field_info["predominant_type"] = max(field_info["types"].items(), key=lambda x: x[1])[0] if field_info["types"] else "null"
        
        return {
            "collection_name": collection_name,
            "total_documents": total_docs,
            "sample_size": sample_size,
            "field_analysis": field_analysis,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def validate_collection_against_schema(self, collection_name: str, schema: Dict) -> Dict:
        """
        Validate all documents in a collection against a schema
        
        Args:
            collection_name: Name of collection to validate
            schema: Schema definition to validate against
            
        Returns:
            Validation results
        """
        collection = self.db[collection_name]
        
        total_docs = await collection.count_documents({})
        valid_docs = 0
        invalid_docs = 0
        validation_errors = {}
        
        async for doc in collection.find():
            doc_id = str(doc.get("id", doc.get("_id", "unknown")))
            is_valid, errors = self.validate_document(doc, schema)
            
            if is_valid:
                valid_docs += 1
            else:
                invalid_docs += 1
                validation_errors[doc_id] = errors
        
        return {
            "collection_name": collection_name,
            "total_documents": total_docs,
            "valid_documents": valid_docs,
            "invalid_documents": invalid_docs,
            "validation_errors": validation_errors,
            "validation_percentage": (valid_docs / total_docs * 100) if total_docs > 0 else 0,
            "validated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def migrate_hosting_plans_collection(self, dry_run: bool = True, preserve_data_only: bool = True) -> Dict:
        """
        Migrate the entire hosting_plans collection to the standard schema using consistent field mapping.
        
        Args:
            dry_run: If True, only analyze what would be changed without making changes
            preserve_data_only: If True, only rename fields without changing data values
            
        Returns:
            Migration results
        """
        collection = self.db.hosting_plans
        
        total_docs = await collection.count_documents({})
        operation_type = "Field mapping" if preserve_data_only else "Full migration"
        logger.info(f"🔄 {operation_type} for {total_docs} hosting plans (dry_run={dry_run})")
        
        migrated_count = 0
        error_count = 0
        migration_errors = {}
        changes_preview = {}
        
        documents = await collection.find().to_list(total_docs)
        
        for doc in documents:
            doc_id = str(doc.get("id", doc.get("_id", "unknown")))
            
            try:
                # Migrate the document with field mapping consistency
                migrated_doc = self.migrate_hosting_plan_document(doc, preserve_data_only=preserve_data_only)
                
                # Track changes for preview
                changes = {}
                for field, new_value in migrated_doc.items():
                    if field not in doc or doc[field] != new_value:
                        old_value = doc.get(field, None)
                        # Skip internal MongoDB fields and timestamp updates
                        if field not in ["_id", "created_at", "updated_at"] or old_value is None:
                            changes[field] = {
                                "old": old_value,
                                "new": new_value,
                                "type": "field_rename" if preserve_data_only and old_value is None else "value_change"
                            }
                
                if changes:
                    changes_preview[doc_id] = changes
                
                if not dry_run:
                    # Remove MongoDB ObjectId for update
                    if "_id" in migrated_doc:
                        del migrated_doc["_id"]
                    
                    # Update the document
                    await collection.replace_one(
                        {"id": doc.get("id", doc["_id"])},
                        migrated_doc
                    )
                
                migrated_count += 1
                
            except Exception as e:
                error_count += 1
                migration_errors[doc_id] = str(e)
                logger.error(f"❌ Error migrating document {doc_id}: {e}")
        
        # Validate migrated collection
        if not dry_run:
            validation_results = await self.validate_collection_against_schema(
                "hosting_plans", self.standard_hosting_plan_schema
            )
        else:
            validation_results = None
        
        results = {
            "collection_name": "hosting_plans",
            "operation_type": operation_type,
            "total_documents": total_docs,
            "migrated_documents": migrated_count,
            "error_count": error_count,
            "migration_errors": migration_errors,
            "changes_preview": changes_preview,
            "dry_run": dry_run,
            "preserve_data_only": preserve_data_only,
            "validation_results": validation_results,
            "migrated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if dry_run:
            logger.info(f"📋 Dry run complete. Would process {migrated_count} documents with {len(changes_preview)} that have changes")
        else:
            logger.info(f"✅ {operation_type} complete. Processed {migrated_count} documents successfully")
            if validation_results:
                logger.info(f"📊 Validation: {validation_results['valid_documents']}/{validation_results['total_documents']} documents valid")
        
        return results
    
    async def remove_duplicate_hosting_plans(self, dry_run: bool = True) -> Dict:
        """
        Identify and remove duplicate hosting plans based on name and type
        
        Args:
            dry_run: If True, only identify duplicates without removing them
            
        Returns:
            Deduplication results
        """
        collection = self.db.hosting_plans
        
        # Find duplicates
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "name": "$name",
                        "type": "$type",
                        "sub_type": "$sub_type"
                    },
                    "count": {"$sum": 1},
                    "docs": {"$push": {"id": "$id", "_id": "$_id", "created_at": "$created_at"}}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}
                }
            }
        ]
        
        duplicate_groups = await collection.aggregate(pipeline).to_list(None)
        
        duplicates_found = 0
        duplicates_removed = 0
        removal_errors = {}
        duplicate_details = {}
        
        for group in duplicate_groups:
            group_key = f"{group['_id']['name']}-{group['_id']['type']}-{group['_id'].get('sub_type', 'none')}"
            docs = group["docs"]
            duplicates_found += len(docs)
            
            # Sort by created_at to keep the oldest one
            docs.sort(key=lambda x: x.get("created_at", datetime.min))
            
            # Keep the first (oldest) document, remove the rest
            to_keep = docs[0]
            to_remove = docs[1:]
            
            duplicate_details[group_key] = {
                "total_count": len(docs),
                "keeping": to_keep,
                "removing": [doc["id"] for doc in to_remove]
            }
            
            if not dry_run:
                for doc in to_remove:
                    try:
                        await collection.delete_one({"id": doc["id"]})
                        duplicates_removed += 1
                    except Exception as e:
                        removal_errors[doc["id"]] = str(e)
        
        results = {
            "duplicates_found": duplicates_found,
            "duplicates_removed": duplicates_removed,
            "duplicate_groups": len(duplicate_groups),
            "duplicate_details": duplicate_details,
            "removal_errors": removal_errors,
            "dry_run": dry_run,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        if dry_run:
            logger.info(f"📋 Found {duplicates_found} duplicate documents in {len(duplicate_groups)} groups")
        else:
            logger.info(f"✅ Removed {duplicates_removed} duplicate documents")
        
        return results
    
    def generate_schema_documentation(self, schema: Dict) -> str:
        """
        Generate human-readable documentation for a schema
        
        Args:
            schema: Schema definition
            
        Returns:
            Formatted documentation string
        """
        doc_lines = ["# Schema Documentation\n"]
        
        for field_name, field_def in schema.items():
            doc_lines.append(f"## {field_name}")
            
            # Type information
            field_type = field_def["type"]
            if isinstance(field_type, list):
                type_str = " | ".join([t.__name__ for t in field_type])
            else:
                type_str = field_type.__name__
            
            doc_lines.append(f"- **Type**: {type_str}")
            doc_lines.append(f"- **Required**: {field_def.get('required', False)}")
            
            if "default" in field_def:
                doc_lines.append(f"- **Default**: {field_def['default']}")
            
            if "description" in field_def:
                doc_lines.append(f"- **Description**: {field_def['description']}")
            
            doc_lines.append("")  # Empty line
        
        return "\n".join(doc_lines)


async def main():
    """Command-line interface for schema migration operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Schema Migration Utilities")
    parser.add_argument("--mongo-url", default=os.environ.get('MONGO_URL', 'mongodb://localhost:27017'),
                       help="MongoDB connection string")
    parser.add_argument("--db-name", default=os.environ.get('DB_NAME', 'blue_nebula_hosting'),
                       help="Database name")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze collection schema")
    analyze_parser.add_argument("collection", help="Collection name to analyze")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate collection against standard schema")
    validate_parser.add_argument("collection", help="Collection name to validate")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Migrate hosting plans collection")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    # Deduplicate command
    dedupe_parser = subparsers.add_parser("deduplicate", help="Remove duplicate hosting plans")
    dedupe_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    # Schema documentation command
    schema_parser = subparsers.add_parser("schema-doc", help="Generate schema documentation")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    migration = SchemaMigration(args.mongo_url, args.db_name)
    
    try:
        await migration.connect()
        
        if args.command == "analyze":
            results = await migration.analyze_collection_schema(args.collection)
            print(f"\n📊 Schema Analysis for '{args.collection}':")
            print(f"Total documents: {results['total_documents']}")
            print(f"Sample size: {results['sample_size']}")
            print("\nField Analysis:")
            
            for field_name, info in results['field_analysis'].items():
                print(f"\n  {field_name}:")
                print(f"    Coverage: {info['coverage']:.1f}%")
                print(f"    Predominant type: {info['predominant_type']}")
                if info['types']:
                    print(f"    Types: {dict(info['types'])}")
                
        elif args.command == "validate":
            if args.collection == "hosting_plans":
                results = await migration.validate_collection_against_schema(
                    args.collection, migration.standard_hosting_plan_schema
                )
                print(f"\n✅ Validation Results for '{args.collection}':")
                print(f"Total documents: {results['total_documents']}")
                print(f"Valid documents: {results['valid_documents']}")
                print(f"Invalid documents: {results['invalid_documents']}")
                print(f"Validation percentage: {results['validation_percentage']:.1f}%")
                
                if results['validation_errors']:
                    print(f"\n❌ Validation Errors ({len(results['validation_errors'])} documents):")
                    for doc_id, errors in list(results['validation_errors'].items())[:10]:  # Show first 10
                        print(f"  Document {doc_id}:")
                        for error in errors:
                            print(f"    - {error}")
            else:
                print(f"❌ Validation not implemented for collection '{args.collection}'")
                
        elif args.command == "migrate":
            results = await migration.migrate_hosting_plans_collection(dry_run=args.dry_run)
            print(f"\n🔄 Migration Results:")
            print(f"Total documents: {results['total_documents']}")
            print(f"Migrated documents: {results['migrated_documents']}")
            print(f"Errors: {results['error_count']}")
            print(f"Changes: {len(results['changes_preview'])}")
            
            if args.dry_run:
                print("\n📋 This was a dry run. No changes were made.")
                if results['changes_preview']:
                    print("\nSample changes that would be made:")
                    for doc_id, changes in list(results['changes_preview'].items())[:3]:
                        print(f"\n  Document {doc_id}:")
                        for field, change in changes.items():
                            print(f"    {field}: {change['old']} → {change['new']}")
            
        elif args.command == "deduplicate":
            results = await migration.remove_duplicate_hosting_plans(dry_run=args.dry_run)
            print(f"\n🔍 Deduplication Results:")
            print(f"Duplicates found: {results['duplicates_found']}")
            print(f"Duplicate groups: {results['duplicate_groups']}")
            
            if args.dry_run:
                print("\n📋 This was a dry run. No changes were made.")
                if results['duplicate_details']:
                    print("\nDuplicate groups found:")
                    for group_key, details in results['duplicate_details'].items():
                        print(f"  {group_key}: {details['total_count']} duplicates")
            else:
                print(f"Duplicates removed: {results['duplicates_removed']}")
                
        elif args.command == "schema-doc":
            doc = migration.generate_schema_documentation(migration.standard_hosting_plan_schema)
            print("\n📚 Hosting Plans Schema Documentation:")
            print("=" * 50)
            print(doc)
            
    finally:
        await migration.disconnect()


if __name__ == "__main__":
    asyncio.run(main())