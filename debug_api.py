#!/usr/bin/env python3
import requests

# Debug API calls step by step
base_url = "http://localhost:8001"

# Test 1: Basic API health
print("1. Testing API health...")
try:
    health_response = requests.get(f"{base_url}/")
    print(f"Status: {health_response.status_code}")
    print(f"Response: {health_response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 2: Content endpoint
print("2. Testing content endpoint...")
try:
    content_response = requests.get(f"{base_url}/content/hero")
    print(f"Status: {content_response.status_code}")
    print(f"Response: {content_response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test 3: Login
print("3. Testing login...")
try:
    login_response = requests.post(f"{base_url}/login", json={
        "username": "admin", 
        "password": "admin123"
    })
    print(f"Status: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n4. Testing admin content endpoint...")
        admin_response = requests.get(f"{base_url}/admin/content/hero", headers=headers)
        print(f"Status: {admin_response.status_code}")
        print(f"Response: {admin_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
