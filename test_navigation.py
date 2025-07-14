#!/usr/bin/env python3
import requests
import json

def test_navigation():
    base_url = "http://localhost:8001"
    
    # 1. Login to get JWT token
    print("🔑 Logging in...")
    login_response = requests.post(f"{base_url}/login", json={
        "username": "admin", 
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful")
    
    # 2. Get current navigation
    print("📖 Getting current navigation...")
    try:
        nav_response = requests.get(f"{base_url}/admin/navigation", headers=headers)
        print(f"GET Status: {nav_response.status_code}")
        print(f"GET Response: {nav_response.text}")
    except Exception as e:
        print(f"GET Error: {e}")
    
    # 3. Test posting navigation data
    print("✏️ Testing navigation update...")
    test_nav_data = [
        {
            "id": "1",
            "label": "Home",
            "href": "/",
            "order": 1,
            "is_external": False
        },
        {
            "id": "2", 
            "label": "Test Menu",
            "href": "/test",
            "order": 2,
            "is_external": False
        }
    ]
    
    try:
        update_response = requests.post(f"{base_url}/admin/navigation", 
                                       json=test_nav_data, headers=headers)
        print(f"POST Status: {update_response.status_code}")
        print(f"POST Response: {update_response.text}")
        
        if update_response.status_code != 200:
            print("❌ Navigation update failed")
            # Try to get more details from the error
            try:
                error_data = update_response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {update_response.text}")
        else:
            print("✅ Navigation updated successfully")
            
    except Exception as e:
        print(f"POST Error: {e}")

if __name__ == "__main__":
    test_navigation()
