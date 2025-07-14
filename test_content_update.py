#!/usr/bin/env python3
import requests
import json

# Test admin panel content functionality
def test_content_update():
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
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # 2. Get current hero content
    print("📖 Getting current hero content...")
    hero_response = requests.get(f"{base_url}/content/hero")
    print(f"Current hero content: {hero_response.json()}")
    
    # 3. Update hero content via admin API
    print("✏️ Updating hero content...")
    new_content = {
        "title": "🚀 UPDATED via API Test!",
        "subtitle": "This content was changed via admin API",
        "description": "If you see this message, the admin panel content updating is working correctly!",
        "button_text": "Test Successful",
        "button_url": "#test"
    }
    
    update_response = requests.post(f"{base_url}/admin/content/hero", 
                                   json=new_content, headers=headers)
    
    if update_response.status_code != 200:
        print(f"❌ Update failed: {update_response.text}")
        return
    
    print("✅ Content updated successfully")
    
    # 4. Verify the update by getting content again
    print("🔍 Verifying update...")
    updated_response = requests.get(f"{base_url}/content/hero")
    updated_content = updated_response.json()
    
    if updated_content["title"] == new_content["title"]:
        print("🎉 SUCCESS! Content update is working correctly!")
        print(f"New title: {updated_content['title']}")
    else:
        print("❌ Update verification failed")
        print(f"Expected: {new_content['title']}")
        print(f"Got: {updated_content['title']}")

if __name__ == "__main__":
    test_content_update()
