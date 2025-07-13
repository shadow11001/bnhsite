#!/usr/bin/env python3
"""
Script to add order_url fields to all hosting plans in init_database.py
"""

import re

def add_order_urls():
    # Read the original file
    with open('init_database.py', 'r') as f:
        content = f.read()
    
    # Plan names and their corresponding product IDs
    plan_mapping = {
        # Already have order_url (1-7)
        # Need to add:
        'Asteroid': 8,
        'Planet': 9, 
        'Star': 10,
        'Cluster': 11,
        'Galaxy': 12,
        # Performance VPS
        'Probe': 13,
        'Rover': 14,
        'Lander': 15,
        'Satellite': 16,
        'Station': 17,
        'Outpost': 18,
        'Base': 19,
        'Colony': 20,
        'Spaceport': 21,
        # Standard GameServers
        'Stardust': 22,
        'Flare': 23,
        'Comet': 24,
        'Nova': 25,
        'White Dwarf': 26,
        'Red Giant': 27,
        # Performance GameServers
        'Supernova': 28,
        'Neutron Star': 29,
        'Pulsar': 30,
        'Magnetar': 31,
        'Black Hole': 32,
        'Quasar': 33,
        'Nebula': 34,
        'Star Cluster': 35,
        'Cosmos': 36
    }
    
    # For each plan that needs order_url
    for plan_name, pid in plan_mapping.items():
        # Pattern to find the plan and add order_url
        pattern = rf'("name": "{plan_name}".*?"markup_percentage": \d+,\s*"is_popular": (?:True|False))'
        
        def replace_func(match):
            original = match.group(1)
            return original + f',\n            "order_url": "https://billing.bluenebulahosting.com/cart.php?a=add&pid={pid}"'
        
        content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    # Write the updated content
    with open('init_database.py', 'w') as f:
        f.write(content)
    
    print("Successfully added order_url fields to all plans!")

if __name__ == "__main__":
    add_order_urls()