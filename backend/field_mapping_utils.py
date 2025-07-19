#!/usr/bin/env python3
"""
Field Mapping Utilities
Provides consistent bidirectional field mapping for hosting plans between 
different database schemas without external dependencies.
"""

def map_hosting_plan_fields(plan, to_frontend=True):
    """
    Bidirectional field mapping for hosting plans to handle both database schemas.
    
    Database might contain either:
    - Old schema: name, type, price, sub_type
    - New schema: plan_name, plan_type, base_price, popular
    
    Frontend expects: name, type, price, is_popular
    
    Args:
        plan (dict): Plan document from database
        to_frontend (bool): If True, map to frontend format. If False, map to database format.
    
    Returns:
        dict: Plan with correctly mapped field names
    """
    if not plan:
        return plan
    
    mapped_plan = plan.copy()
    
    if to_frontend:
        # Map database fields to frontend expected fields
        # Handle both old and new database schemas
        
        # Map plan name
        if "plan_name" in plan and "name" not in plan:
            mapped_plan["name"] = plan["plan_name"]
        elif "name" in plan:
            mapped_plan["name"] = plan["name"]
        
        # Map plan type 
        if "plan_type" in plan and "type" not in plan:
            mapped_plan["type"] = plan["plan_type"]
        elif "type" in plan:
            mapped_plan["type"] = plan["type"]
        
        # Map price
        if "base_price" in plan and "price" not in plan:
            mapped_plan["price"] = plan["base_price"]
        elif "price" in plan:
            mapped_plan["price"] = plan["price"]
        
        # Map popular flag
        if "popular" in plan:
            mapped_plan["is_popular"] = plan["popular"]
        elif "is_popular" in plan:
            mapped_plan["is_popular"] = plan["is_popular"]
        else:
            mapped_plan["is_popular"] = False
        
        # Ensure we have sub_type field for frontend filtering
        if "sub_type" in plan:
            mapped_plan["sub_type"] = plan["sub_type"]
            
    else:
        # Map frontend fields to database fields (for create/update operations)
        
        # Map name to plan_name for database storage
        if "name" in plan:
            mapped_plan["plan_name"] = plan["name"]
        elif "plan_name" in plan:
            mapped_plan["plan_name"] = plan["plan_name"]
        
        # Map type to plan_type for database storage
        if "type" in plan:
            mapped_plan["plan_type"] = plan["type"]
        elif "plan_type" in plan:
            mapped_plan["plan_type"] = plan["plan_type"]
        
        # Map price to base_price for database storage
        if "price" in plan:
            mapped_plan["base_price"] = plan["price"]
        elif "base_price" in plan:
            mapped_plan["base_price"] = plan["base_price"]
        
        # Map is_popular to popular for database storage
        if "is_popular" in plan:
            mapped_plan["popular"] = plan["is_popular"]
        elif "popular" in plan:
            mapped_plan["popular"] = plan["popular"]
    
    return mapped_plan