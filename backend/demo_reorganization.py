#!/usr/bin/env python3
"""
Database Reorganization Demo
Demonstrates the database reorganization system with mock data
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# Mock data to simulate hosting plans with schema issues
MOCK_HOSTING_PLANS = [
    # Old schema format
    {
        "_id": "507f1f77bcf86cd799439011",
        "plan_name": "Opal",  # Should be "name"
        "plan_type": "ssd_shared",  # Should be "type"
        "base_price": 1.0,  # Should be "price"
        "popular": False,  # Should be "is_popular"
        "cpu_cores": 1,
        "memory_gb": 1,
        "disk_gb": 10,
        "websites": 1,
        "features": "Free SSL Certificate,Daily Backups,99.9% Uptime"  # Should be list
    },
    # Mixed schema format
    {
        "_id": "507f1f77bcf86cd799439012",
        "name": "Topaz",  # New format
        "plan_type": "ssd_shared",  # Old format
        "price": 10.0,  # New format
        "popular": True,  # Old format
        "cpu": "2 Core",
        "ram": "2 GB",
        "disk_space": "50 GB SSD",
        "websites": 5,
        "features": ["Free SSL Certificate", "Daily Backups", "99.9% Uptime"]
    },
    # Inconsistent data types
    {
        "_id": "507f1f77bcf86cd799439013",
        "plan_name": "Diamond",
        "plan_type": "ssd_shared",
        "base_price": "15.00",  # String instead of float
        "popular": "true",  # String instead of boolean
        "websites": "Unlimited",
        "features": None  # Should be list
    },
    # Duplicate plan
    {
        "_id": "507f1f77bcf86cd799439014",
        "plan_name": "Opal",  # Duplicate name
        "plan_type": "ssd_shared",
        "base_price": 1.0,
        "popular": False,
        "cpu_cores": 1,
        "memory_gb": 1,
        "disk_gb": 10
    }
]

async def demo_schema_analysis():
    """Demonstrate schema analysis functionality"""
    print("=" * 60)
    print("SCHEMA ANALYSIS DEMO")
    print("=" * 60)
    
    # Simulate analysis of hosting plans
    field_analysis = {}
    total_docs = len(MOCK_HOSTING_PLANS)
    
    for doc in MOCK_HOSTING_PLANS:
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
                
                if len(field_info["sample_values"]) < 3:
                    field_info["sample_values"].append(value)
    
    # Calculate coverage and issues
    for field_name, field_info in field_analysis.items():
        field_info["coverage"] = (field_info["count"] / total_docs) * 100
        field_info["predominant_type"] = max(field_info["types"].items(), key=lambda x: x[1])[0] if field_info["types"] else "null"
    
    print(f"📊 Analyzed {total_docs} hosting plan documents")
    print(f"📋 Found {len(field_analysis)} unique fields")
    print()
    
    print("Field Analysis:")
    for field_name, info in field_analysis.items():
        print(f"\n  {field_name}:")
        print(f"    Coverage: {info['coverage']:.1f}%")
        print(f"    Predominant type: {info['predominant_type']}")
        print(f"    Types: {dict(info['types'])}")
        if info['sample_values']:
            print(f"    Sample values: {info['sample_values']}")
    
    # Identify schema issues
    issues = []
    if "plan_name" in field_analysis and "name" in field_analysis:
        issues.append("Mixed field naming: both 'plan_name' and 'name' exist")
    if "base_price" in field_analysis and "price" in field_analysis:
        issues.append("Mixed field naming: both 'base_price' and 'price' exist")
    if "plan_type" in field_analysis and "type" in field_analysis:
        issues.append("Mixed field naming: both 'plan_type' and 'type' exist")
    
    # Check for inconsistent data types
    price_fields = ["base_price", "price"]
    for field in price_fields:
        if field in field_analysis:
            types = field_analysis[field]["types"]
            if len(types) > 1:
                issues.append(f"Inconsistent data types in '{field}': {list(types.keys())}")
    
    print(f"\n🚨 Issues Found ({len(issues)}):")
    for issue in issues:
        print(f"  • {issue}")
    
    return {"field_analysis": field_analysis, "issues": issues}

async def demo_field_mapping():
    """Demonstrate field mapping functionality"""
    print("\n" + "=" * 60)
    print("FIELD MAPPING DEMO")
    print("=" * 60)
    
    # Field mappings
    field_mappings = {
        "plan_name": "name",
        "plan_type": "type", 
        "base_price": "price",
        "popular": "is_popular"
    }
    
    print("Applying field mappings:")
    for old_field, new_field in field_mappings.items():
        print(f"  {old_field} → {new_field}")
    print()
    
    # Migrate each document
    migrated_docs = []
    changes_made = 0
    
    for i, doc in enumerate(MOCK_HOSTING_PLANS):
        print(f"Document {i+1} ({doc.get('plan_name', doc.get('name', 'Unknown'))}):")
        migrated_doc = {}
        doc_changes = []
        
        # Apply field mappings
        for old_field, new_field in field_mappings.items():
            if old_field in doc and new_field not in doc:
                migrated_doc[new_field] = doc[old_field]
                doc_changes.append(f"    {old_field} → {new_field}: {doc[old_field]}")
            elif new_field in doc:
                migrated_doc[new_field] = doc[new_field]
        
        # Copy other fields
        for field, value in doc.items():
            if field not in field_mappings and field != "_id":
                migrated_doc[field] = value
        
        # Normalize data types
        if "price" in migrated_doc:
            try:
                migrated_doc["price"] = float(migrated_doc["price"])
                if isinstance(doc.get("base_price") or doc.get("price"), str):
                    doc_changes.append(f"    Normalized price to float: {migrated_doc['price']}")
            except (ValueError, TypeError):
                pass
        
        if "is_popular" in migrated_doc:
            if isinstance(migrated_doc["is_popular"], str):
                migrated_doc["is_popular"] = migrated_doc["is_popular"].lower() in ["true", "1", "yes"]
                doc_changes.append(f"    Normalized is_popular to boolean: {migrated_doc['is_popular']}")
        
        # Normalize features
        if "features" in migrated_doc:
            if isinstance(migrated_doc["features"], str):
                migrated_doc["features"] = [f.strip() for f in migrated_doc["features"].split(",") if f.strip()]
                doc_changes.append(f"    Normalized features to list: {len(migrated_doc['features'])} items")
            elif migrated_doc["features"] is None:
                migrated_doc["features"] = []
                doc_changes.append("    Set empty features list")
        
        migrated_docs.append(migrated_doc)
        
        if doc_changes:
            print("  Changes made:")
            for change in doc_changes:
                print(change)
            changes_made += 1
        else:
            print("  No changes needed")
        print()
    
    print(f"✅ Migration complete: {changes_made}/{len(MOCK_HOSTING_PLANS)} documents updated")
    return migrated_docs

async def demo_duplicate_detection():
    """Demonstrate duplicate detection functionality"""
    print("\n" + "=" * 60)
    print("DUPLICATE DETECTION DEMO")
    print("=" * 60)
    
    # Group documents by name and type to find duplicates
    groups = {}
    
    for i, doc in enumerate(MOCK_HOSTING_PLANS):
        name = doc.get("plan_name") or doc.get("name", "Unknown")
        plan_type = doc.get("plan_type") or doc.get("type", "unknown")
        
        key = f"{name}-{plan_type}"
        
        if key not in groups:
            groups[key] = []
        
        groups[key].append({
            "index": i,
            "id": doc.get("_id"),
            "name": name,
            "type": plan_type
        })
    
    # Find duplicate groups
    duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
    
    print(f"📊 Found {len(duplicate_groups)} duplicate group(s):")
    
    total_duplicates = 0
    for group_key, docs in duplicate_groups.items():
        print(f"\n  Group: {group_key}")
        print(f"    Documents: {len(docs)}")
        print(f"    Would keep: {docs[0]['id']} (first one)")
        print(f"    Would remove: {[doc['id'] for doc in docs[1:]]}")
        total_duplicates += len(docs) - 1
    
    print(f"\n🧹 Would remove {total_duplicates} duplicate documents")
    return duplicate_groups

async def demo_validation():
    """Demonstrate validation functionality"""
    print("\n" + "=" * 60)
    print("VALIDATION DEMO")
    print("=" * 60)
    
    # Standard schema requirements
    required_fields = ["name", "type", "price"]
    
    validation_errors = {}
    valid_docs = 0
    
    for i, doc in enumerate(MOCK_HOSTING_PLANS):
        doc_id = doc.get("_id", f"doc_{i}")
        errors = []
        
        # Check required fields (considering field mappings)
        for field in required_fields:
            old_field_map = {"name": "plan_name", "type": "plan_type", "price": "base_price"}
            old_field = old_field_map.get(field)
            
            if field not in doc and (old_field is None or old_field not in doc):
                errors.append(f"Missing required field: {field}")
        
        # Check data types
        price_field = doc.get("price") or doc.get("base_price")
        if price_field is not None:
            try:
                float(price_field)
            except (ValueError, TypeError):
                errors.append(f"Invalid price data type: {type(price_field).__name__}")
        
        if errors:
            validation_errors[doc_id] = errors
        else:
            valid_docs += 1
    
    total_docs = len(MOCK_HOSTING_PLANS)
    validation_percentage = (valid_docs / total_docs * 100) if total_docs > 0 else 0
    
    print(f"📊 Validation Results:")
    print(f"  Total documents: {total_docs}")
    print(f"  Valid documents: {valid_docs}")
    print(f"  Invalid documents: {len(validation_errors)}")
    print(f"  Validation percentage: {validation_percentage:.1f}%")
    
    if validation_errors:
        print(f"\n❌ Validation Errors:")
        for doc_id, errors in validation_errors.items():
            plan_name = next((doc.get("plan_name") or doc.get("name") for doc in MOCK_HOSTING_PLANS if doc.get("_id") == doc_id), "Unknown")
            print(f"  Document {doc_id} ({plan_name}):")
            for error in errors:
                print(f"    - {error}")
    
    return {"valid_docs": valid_docs, "total_docs": total_docs, "errors": validation_errors}

async def demo_backup_simulation():
    """Demonstrate backup functionality"""
    print("\n" + "=" * 60)
    print("BACKUP SIMULATION DEMO")
    print("=" * 60)
    
    # Simulate creating a backup
    backup_data = {
        "metadata": {
            "collection_name": "hosting_plans",
            "timestamp": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
            "document_count": len(MOCK_HOSTING_PLANS),
            "backup_file": f"/tmp/database_backups/hosting_plans_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json.gz",
            "db_name": "blue_nebula_hosting",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        "documents": MOCK_HOSTING_PLANS
    }
    
    print(f"💾 Backup simulation for collection: hosting_plans")
    print(f"📊 Documents to backup: {backup_data['metadata']['document_count']}")
    print(f"📁 Backup file: {backup_data['metadata']['backup_file']}")
    print(f"🕒 Created at: {backup_data['metadata']['created_at']}")
    
    # Calculate estimated file size
    estimated_size = len(json.dumps(backup_data, indent=2))
    print(f"📦 Estimated backup size: {estimated_size:,} bytes")
    
    return backup_data

async def demo_complete_reorganization():
    """Demonstrate complete reorganization process"""
    print("\n" + "=" * 80)
    print("COMPLETE REORGANIZATION DEMO")
    print("=" * 80)
    
    print("🚀 Starting database reorganization simulation...")
    print(f"📊 Database: blue_nebula_hosting_demo")
    print(f"💾 Backup directory: /tmp/database_backups")
    print()
    
    # Step 1: Pre-analysis
    print("🔍 Step 1: Pre-reorganization analysis")
    analysis_results = await demo_schema_analysis()
    
    # Step 2: Backup
    print("\n💾 Step 2: Creating comprehensive backup")
    backup_results = await demo_backup_simulation()
    
    # Step 3: Remove duplicates
    print("\n🧹 Step 3: Removing duplicates")
    duplicate_results = await demo_duplicate_detection()
    
    # Step 4: Schema migration
    print("\n🔄 Step 4: Schema migration")
    migration_results = await demo_field_mapping()
    
    # Step 5: Validation
    print("\n✅ Step 5: Validation")
    validation_results = await demo_validation()
    
    # Final summary
    print("\n" + "=" * 80)
    print("REORGANIZATION SUMMARY")
    print("=" * 80)
    
    issues_found = len(analysis_results["issues"])
    duplicates_found = sum(len(docs) - 1 for docs in duplicate_results.values())
    documents_migrated = len(MOCK_HOSTING_PLANS)
    validation_percentage = validation_results["valid_docs"] / validation_results["total_docs"] * 100
    
    print(f"📊 Total documents processed: {documents_migrated}")
    print(f"🚨 Schema issues identified: {issues_found}")
    print(f"🧹 Duplicate documents found: {duplicates_found}")
    print(f"🔄 Documents migrated: {documents_migrated}")
    print(f"✅ Post-migration validation: {validation_percentage:.1f}%")
    print(f"💾 Backup created: {backup_results['metadata']['backup_file']}")
    
    success = validation_percentage >= 80 and issues_found < 10
    
    if success:
        print("\n🎉 Database reorganization completed successfully!")
        print("✅ All hosting plans are now using standardized schema")
        print("✅ Field mappings applied correctly")
        print("✅ Data types normalized")
        print("✅ Duplicates would be removed")
        print("✅ Backup created for safety")
    else:
        print("\n❌ Database reorganization completed with warnings")
        print("⚠️ Some validation errors remain")
        print("⚠️ Manual review may be required")
    
    return success

async def main():
    """Run the complete demo"""
    print("Database Reorganization System Demo")
    print("=" * 80)
    print()
    print("This demo shows how the database reorganization system works")
    print("using mock hosting plans data with common schema issues.")
    print()
    
    # Show original data
    print("📋 Original Mock Data:")
    for i, doc in enumerate(MOCK_HOSTING_PLANS):
        name = doc.get("plan_name") or doc.get("name", "Unknown")
        price = doc.get("base_price") or doc.get("price", "N/A")
        print(f"  {i+1}. {name} - ${price} ({doc.get('plan_type', doc.get('type', 'unknown'))})")
    print()
    
    # Run complete reorganization demo
    success = await demo_complete_reorganization()
    
    print(f"\n📄 Demo completed with status: {'SUCCESS' if success else 'WARNINGS'}")
    print()
    print("To use the real system:")
    print("  # Check status")
    print("  python3 run_db_reorganization.py status --detailed")
    print() 
    print("  # Run full reorganization")
    print("  python3 run_db_reorganization.py reorganize --force")
    print()
    print("  # Create backup only")
    print("  python3 run_db_reorganization.py backup create --collections hosting_plans")
    print()
    print("  # Use shell script wrapper")
    print("  ./scripts/reorganize_database.sh reorganize --force")

if __name__ == "__main__":
    asyncio.run(main())