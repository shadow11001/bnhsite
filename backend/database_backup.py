#!/usr/bin/env python3
"""
Database Backup and Restore System
Provides comprehensive backup and restore functionality for MongoDB collections
with timestamped backups and integrity verification.
"""

import os
import json
import gzip
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    def __init__(self, mongo_url: str, db_name: str, backup_dir: str = "/tmp/database_backups"):
        """
        Initialize database backup system
        
        Args:
            mongo_url: MongoDB connection string
            db_name: Database name to backup
            backup_dir: Directory to store backups
        """
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.db = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            # Test connection
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
    
    def _serialize_document(self, doc: Dict) -> Dict:
        """Convert MongoDB document to JSON-serializable format"""
        if isinstance(doc, dict):
            result = {}
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    result[key] = {"__type": "ObjectId", "__value": str(value)}
                elif isinstance(value, datetime):
                    result[key] = {"__type": "datetime", "__value": value.isoformat()}
                elif isinstance(value, dict):
                    result[key] = self._serialize_document(value)
                elif isinstance(value, list):
                    result[key] = [self._serialize_document(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        return doc
    
    def _deserialize_document(self, doc: Dict) -> Dict:
        """Convert JSON document back to MongoDB format"""
        if isinstance(doc, dict):
            result = {}
            for key, value in doc.items():
                if isinstance(value, dict) and "__type" in value and "__value" in value:
                    if value["__type"] == "ObjectId":
                        result[key] = ObjectId(value["__value"])
                    elif value["__type"] == "datetime":
                        result[key] = datetime.fromisoformat(value["__value"])
                    else:
                        result[key] = value["__value"]
                elif isinstance(value, dict):
                    result[key] = self._deserialize_document(value)
                elif isinstance(value, list):
                    result[key] = [self._deserialize_document(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        return doc
    
    async def backup_collection(self, collection_name: str, timestamp: str = None) -> Tuple[str, Dict]:
        """
        Backup a single collection
        
        Args:
            collection_name: Name of collection to backup
            timestamp: Optional timestamp string for backup naming
            
        Returns:
            Tuple of (backup_file_path, backup_metadata)
        """
        if not timestamp:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        backup_file = self.backup_dir / f"{collection_name}_{timestamp}.json.gz"
        
        try:
            collection = self.db[collection_name]
            
            # Get collection stats
            stats = await self.db.command("collStats", collection_name)
            document_count = stats.get("count", 0)
            
            # Get all documents
            documents = []
            async for doc in collection.find():
                documents.append(self._serialize_document(doc))
            
            # Create backup metadata
            metadata = {
                "collection_name": collection_name,
                "timestamp": timestamp,
                "document_count": len(documents),
                "original_count": document_count,
                "backup_file": str(backup_file),
                "db_name": self.db_name,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Write compressed backup
            with gzip.open(backup_file, 'wt', encoding='utf-8') as f:
                json.dump({
                    "metadata": metadata,
                    "documents": documents
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup created for collection '{collection_name}': {backup_file}")
            logger.info(f"📊 Backed up {len(documents)} documents")
            
            return str(backup_file), metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to backup collection '{collection_name}': {e}")
            raise
    
    async def backup_multiple_collections(self, collection_names: List[str]) -> Dict[str, Dict]:
        """
        Backup multiple collections with the same timestamp
        
        Args:
            collection_names: List of collection names to backup
            
        Returns:
            Dictionary mapping collection names to their backup metadata
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        results = {}
        
        logger.info(f"🔄 Starting backup of {len(collection_names)} collections")
        
        for collection_name in collection_names:
            try:
                backup_file, metadata = await self.backup_collection(collection_name, timestamp)
                results[collection_name] = metadata
            except Exception as e:
                logger.error(f"❌ Failed to backup collection '{collection_name}': {e}")
                results[collection_name] = {"error": str(e)}
        
        # Create overall backup manifest
        manifest = {
            "timestamp": timestamp,
            "collections": results,
            "backup_dir": str(self.backup_dir),
            "total_collections": len(collection_names),
            "successful_backups": len([r for r in results.values() if "error" not in r]),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        manifest_file = self.backup_dir / f"backup_manifest_{timestamp}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"✅ Backup manifest created: {manifest_file}")
        return results
    
    async def restore_collection(self, backup_file: str, target_collection: str = None, 
                                mode: str = "replace") -> Dict:
        """
        Restore a collection from backup
        
        Args:
            backup_file: Path to backup file
            target_collection: Target collection name (defaults to original)
            mode: Restore mode ('replace', 'append', 'update')
            
        Returns:
            Restore operation metadata
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        try:
            # Read backup file
            with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            metadata = backup_data["metadata"]
            documents = backup_data["documents"]
            
            collection_name = target_collection or metadata["collection_name"]
            collection = self.db[collection_name]
            
            logger.info(f"🔄 Restoring collection '{collection_name}' from {backup_file}")
            logger.info(f"📊 Backup contains {len(documents)} documents")
            
            # Deserialize documents
            restored_docs = [self._deserialize_document(doc) for doc in documents]
            
            if mode == "replace":
                # Drop existing collection and recreate
                await collection.drop()
                if restored_docs:
                    await collection.insert_many(restored_docs)
                inserted_count = len(restored_docs)
                
            elif mode == "append":
                # Insert all documents (may create duplicates)
                if restored_docs:
                    await collection.insert_many(restored_docs)
                inserted_count = len(restored_docs)
                
            elif mode == "update":
                # Update existing documents by ID or insert new ones
                inserted_count = 0
                updated_count = 0
                
                for doc in restored_docs:
                    if "_id" in doc:
                        result = await collection.replace_one(
                            {"_id": doc["_id"]}, doc, upsert=True
                        )
                        if result.upserted_id:
                            inserted_count += 1
                        else:
                            updated_count += 1
                    else:
                        await collection.insert_one(doc)
                        inserted_count += 1
            
            else:
                raise ValueError(f"Invalid restore mode: {mode}")
            
            # Verify restoration
            final_count = await collection.count_documents({})
            
            restore_metadata = {
                "collection_name": collection_name,
                "backup_file": backup_file,
                "restore_mode": mode,
                "documents_restored": len(restored_docs),
                "final_document_count": final_count,
                "restored_at": datetime.now(timezone.utc).isoformat(),
                "original_backup_timestamp": metadata.get("timestamp"),
                "success": True
            }
            
            if mode == "update":
                restore_metadata["inserted_count"] = inserted_count
                restore_metadata["updated_count"] = updated_count
            
            logger.info(f"✅ Collection '{collection_name}' restored successfully")
            logger.info(f"📊 Final document count: {final_count}")
            
            return restore_metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to restore collection: {e}")
            raise
    
    async def verify_backup(self, backup_file: str) -> Dict:
        """
        Verify backup file integrity and contents
        
        Args:
            backup_file: Path to backup file to verify
            
        Returns:
            Verification results dictionary
        """
        backup_path = Path(backup_file)
        
        verification = {
            "backup_file": backup_file,
            "file_exists": backup_path.exists(),
            "file_size": 0,
            "is_readable": False,
            "metadata_valid": False,
            "documents_count": 0,
            "verification_errors": [],
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            if not backup_path.exists():
                verification["verification_errors"].append("Backup file does not exist")
                return verification
            
            verification["file_size"] = backup_path.stat().st_size
            
            # Try to read and parse the backup file
            with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            verification["is_readable"] = True
            
            # Verify structure
            if "metadata" not in backup_data:
                verification["verification_errors"].append("Missing metadata section")
            else:
                metadata = backup_data["metadata"]
                required_fields = ["collection_name", "timestamp", "document_count"]
                for field in required_fields:
                    if field not in metadata:
                        verification["verification_errors"].append(f"Missing metadata field: {field}")
                
                if not verification["verification_errors"]:
                    verification["metadata_valid"] = True
            
            if "documents" not in backup_data:
                verification["verification_errors"].append("Missing documents section")
            else:
                documents = backup_data["documents"]
                verification["documents_count"] = len(documents)
                
                # Verify document count matches metadata
                if verification["metadata_valid"]:
                    expected_count = backup_data["metadata"]["document_count"]
                    if len(documents) != expected_count:
                        verification["verification_errors"].append(
                            f"Document count mismatch: expected {expected_count}, found {len(documents)}"
                        )
            
            verification["is_valid"] = len(verification["verification_errors"]) == 0
            
        except Exception as e:
            verification["verification_errors"].append(f"Error reading backup file: {str(e)}")
        
        return verification
    
    def list_backups(self, collection_name: str = None) -> List[Dict]:
        """
        List available backups
        
        Args:
            collection_name: Optional filter by collection name
            
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        for backup_file in self.backup_dir.glob("*.json.gz"):
            if collection_name and not backup_file.name.startswith(f"{collection_name}_"):
                continue
            
            try:
                stat = backup_file.stat()
                backup_info = {
                    "file_name": backup_file.name,
                    "file_path": str(backup_file),
                    "file_size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                
                # Try to read metadata
                try:
                    with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    if "metadata" in backup_data:
                        metadata = backup_data["metadata"]
                        backup_info.update({
                            "collection_name": metadata.get("collection_name"),
                            "timestamp": metadata.get("timestamp"),
                            "document_count": metadata.get("document_count"),
                            "backup_created_at": metadata.get("created_at")
                        })
                    
                except Exception:
                    backup_info["metadata_error"] = "Could not read backup metadata"
                
                backups.append(backup_info)
                
            except Exception as e:
                logger.warning(f"⚠️ Could not read backup file {backup_file}: {e}")
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x.get("backup_created_at", x["created_at"]), reverse=True)
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10, collection_name: str = None) -> int:
        """
        Remove old backup files, keeping only the most recent ones
        
        Args:
            keep_count: Number of recent backups to keep
            collection_name: Optional filter by collection name
            
        Returns:
            Number of files deleted
        """
        backups = self.list_backups(collection_name)
        deleted_count = 0
        
        if len(backups) <= keep_count:
            logger.info(f"📁 No cleanup needed. Found {len(backups)} backups, keeping {keep_count}")
            return 0
        
        backups_to_delete = backups[keep_count:]
        
        for backup in backups_to_delete:
            try:
                backup_path = Path(backup["file_path"])
                backup_path.unlink()
                deleted_count += 1
                logger.info(f"🗑️ Deleted old backup: {backup['file_name']}")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete backup {backup['file_name']}: {e}")
        
        logger.info(f"🧹 Cleanup complete. Deleted {deleted_count} old backup files")
        return deleted_count


async def main():
    """Command-line interface for backup operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Backup and Restore System")
    parser.add_argument("--mongo-url", default=os.environ.get('MONGO_URL', 'mongodb://localhost:27017'),
                       help="MongoDB connection string")
    parser.add_argument("--db-name", default=os.environ.get('DB_NAME', 'blue_nebula_hosting'),
                       help="Database name")
    parser.add_argument("--backup-dir", default="/tmp/database_backups",
                       help="Backup directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Create backup")
    backup_parser.add_argument("collection", help="Collection name to backup")
    
    # Backup multiple command
    backup_multi_parser = subparsers.add_parser("backup-multi", help="Backup multiple collections")
    backup_multi_parser.add_argument("collections", nargs="+", help="Collection names to backup")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup_file", help="Path to backup file")
    restore_parser.add_argument("--target-collection", help="Target collection name")
    restore_parser.add_argument("--mode", choices=["replace", "append", "update"], default="replace",
                               help="Restore mode")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available backups")
    list_parser.add_argument("--collection", help="Filter by collection name")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify backup file")
    verify_parser.add_argument("backup_file", help="Path to backup file to verify")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old backups")
    cleanup_parser.add_argument("--keep", type=int, default=10, help="Number of recent backups to keep")
    cleanup_parser.add_argument("--collection", help="Filter by collection name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    backup_system = DatabaseBackup(args.mongo_url, args.db_name, args.backup_dir)
    
    try:
        if args.command in ["backup", "backup-multi", "restore"]:
            await backup_system.connect()
        
        if args.command == "backup":
            backup_file, metadata = await backup_system.backup_collection(args.collection)
            print(f"✅ Backup created: {backup_file}")
            print(f"📊 Documents backed up: {metadata['document_count']}")
            
        elif args.command == "backup-multi":
            results = await backup_system.backup_multiple_collections(args.collections)
            successful = [c for c, r in results.items() if "error" not in r]
            failed = [c for c, r in results.items() if "error" in r]
            
            print(f"✅ Successfully backed up {len(successful)} collections: {', '.join(successful)}")
            if failed:
                print(f"❌ Failed to backup {len(failed)} collections: {', '.join(failed)}")
            
        elif args.command == "restore":
            metadata = await backup_system.restore_collection(
                args.backup_file, args.target_collection, args.mode
            )
            print(f"✅ Restore completed for collection '{metadata['collection_name']}'")
            print(f"📊 Documents restored: {metadata['documents_restored']}")
            print(f"📊 Final document count: {metadata['final_document_count']}")
            
        elif args.command == "list":
            backups = backup_system.list_backups(args.collection)
            if not backups:
                print("📁 No backups found")
            else:
                print(f"📁 Found {len(backups)} backup(s):")
                for backup in backups:
                    print(f"  • {backup['file_name']} - {backup.get('collection_name', 'unknown')} "
                          f"({backup.get('document_count', '?')} docs) - {backup.get('backup_created_at', backup['created_at'])}")
                          
        elif args.command == "verify":
            verification = await backup_system.verify_backup(args.backup_file)
            if verification["is_valid"]:
                print(f"✅ Backup file is valid")
                print(f"📊 Collection: {verification.get('collection_name', 'unknown')}")
                print(f"📊 Documents: {verification['documents_count']}")
            else:
                print(f"❌ Backup file is invalid:")
                for error in verification["verification_errors"]:
                    print(f"  • {error}")
                    
        elif args.command == "cleanup":
            deleted_count = backup_system.cleanup_old_backups(args.keep, args.collection)
            print(f"🧹 Deleted {deleted_count} old backup files")
            
    finally:
        await backup_system.disconnect()


if __name__ == "__main__":
    asyncio.run(main())