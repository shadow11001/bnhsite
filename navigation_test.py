#!/usr/bin/env python3
"""
Navigation Menu Admin Endpoints Test
Tests the specific Navigation Menu admin endpoints that were just fixed
"""

import requests
import sys
import json
from datetime import datetime

class NavigationMenuTester:
    def __init__(self):
        self.api_url = "http://localhost:8001"
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        self.auth_token = None

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.errors.append(f"{name}: {details}")
        
        if details and success:
            print(f"   ℹ️  {details}")

    def authenticate(self):
        """Authenticate with admin/admin123 credentials"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{self.api_url}/login", json=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('access_token')
                self.log_test("Authentication", True, f"Successfully authenticated as admin")
                return True
            else:
                self.log_test("Authentication", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", False, str(e))
            return False

    def test_get_navigation_empty(self):
        """Test GET /api/admin/navigation - Should return navigation items (may be empty initially)"""
        if not self.auth_token:
            self.log_test("GET Navigation (Empty)", False, "No auth token available")
            return False, []
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{self.api_url}/admin/navigation", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                nav_items = response.json()
                success = isinstance(nav_items, list)
                details = f"Returned {len(nav_items)} navigation items"
            else:
                details = f"HTTP {response.status_code}"
                nav_items = []
                
            self.log_test("GET Navigation (Initial)", success, details)
            return success, nav_items
            
        except Exception as e:
            self.log_test("GET Navigation (Initial)", False, str(e))
            return False, []

    def test_post_navigation_sample_data(self):
        """Test POST /api/admin/navigation - Should accept a JSON array of navigation items and save them"""
        if not self.auth_token:
            self.log_test("POST Navigation (Sample Data)", False, "No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Sample navigation data from the review request
        sample_navigation = [
            {
                "id": "1",
                "label": "Home", 
                "href": "/",
                "order": 1,
                "is_external": False
            },
            {
                "id": "2",
                "label": "Hosting",
                "href": "#hosting", 
                "order": 2,
                "is_external": False
            }
        ]
        
        try:
            response = requests.post(f"{self.api_url}/admin/navigation", 
                                   json=sample_navigation, headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                success = "message" in result and "successfully" in result.get("message", "").lower()
                details = f"Saved {len(sample_navigation)} navigation items: {result.get('message', 'Success')}"
            else:
                details = f"HTTP {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', response.text)}"
                    except:
                        details += f" - {response.text[:100]}"
                
            self.log_test("POST Navigation (Sample Data)", success, details)
            return success
            
        except Exception as e:
            self.log_test("POST Navigation (Sample Data)", False, str(e))
            return False

    def test_get_navigation_after_save(self):
        """Test GET /api/admin/navigation after saving - Should return the saved navigation items"""
        if not self.auth_token:
            self.log_test("GET Navigation (After Save)", False, "No auth token available")
            return False, []
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{self.api_url}/admin/navigation", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                nav_items = response.json()
                success = isinstance(nav_items, list) and len(nav_items) > 0
                
                if success:
                    # Verify the saved data matches what we sent
                    expected_labels = ["Home", "Hosting"]
                    actual_labels = [item.get("label") for item in nav_items]
                    
                    labels_match = all(label in actual_labels for label in expected_labels)
                    
                    # Check for required fields
                    required_fields = ["label", "href", "order", "is_external"]
                    all_have_fields = all(
                        all(field in item for field in required_fields) 
                        for item in nav_items
                    )
                    
                    success = labels_match and all_have_fields
                    details = f"Found {len(nav_items)} items with labels: {actual_labels}, Fields complete: {all_have_fields}"
                else:
                    details = "No navigation items returned or invalid format"
            else:
                details = f"HTTP {response.status_code}"
                nav_items = []
                
            self.log_test("GET Navigation (After Save)", success, details)
            return success, nav_items
            
        except Exception as e:
            self.log_test("GET Navigation (After Save)", False, str(e))
            return False, []

    def test_put_navigation_alternative(self):
        """Test PUT /api/admin/navigation - Should also work as an alternative method"""
        if not self.auth_token:
            self.log_test("PUT Navigation (Alternative Method)", False, "No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Updated navigation data to test PUT method
        updated_navigation = [
            {
                "id": "1",
                "label": "Home", 
                "href": "/",
                "order": 1,
                "is_external": False
            },
            {
                "id": "2",
                "label": "Services",
                "href": "#services", 
                "order": 2,
                "is_external": False
            },
            {
                "id": "3",
                "label": "Contact",
                "href": "#contact", 
                "order": 3,
                "is_external": False
            }
        ]
        
        try:
            response = requests.put(f"{self.api_url}/admin/navigation", 
                                  json=updated_navigation, headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                success = "message" in result and "successfully" in result.get("message", "").lower()
                details = f"Updated with {len(updated_navigation)} navigation items: {result.get('message', 'Success')}"
            else:
                details = f"HTTP {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', response.text)}"
                    except:
                        details += f" - {response.text[:100]}"
                
            self.log_test("PUT Navigation (Alternative Method)", success, details)
            return success
            
        except Exception as e:
            self.log_test("PUT Navigation (Alternative Method)", False, str(e))
            return False

    def test_navigation_persistence(self):
        """Test that navigation data persists between requests"""
        if not self.auth_token:
            self.log_test("Navigation Data Persistence", False, "No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Get navigation items after PUT update
            response = requests.get(f"{self.api_url}/admin/navigation", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                nav_items = response.json()
                success = isinstance(nav_items, list) and len(nav_items) > 0
                
                if success:
                    # Verify the updated data is persisted
                    expected_labels = ["Home", "Services", "Contact"]
                    actual_labels = [item.get("label") for item in nav_items]
                    
                    labels_match = all(label in actual_labels for label in expected_labels)
                    correct_count = len(nav_items) == 3
                    
                    success = labels_match and correct_count
                    details = f"Persisted {len(nav_items)} items: {actual_labels}, Expected count: {correct_count}"
                else:
                    details = "No navigation items found or invalid format"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Navigation Data Persistence", success, details)
            return success
            
        except Exception as e:
            self.log_test("Navigation Data Persistence", False, str(e))
            return False

    def test_navigation_error_resolution(self):
        """Test that the 'Error updating navigation: [object Object]' issue is resolved"""
        # This test verifies that the navigation endpoints are working and not returning
        # the "Not Found" error that was previously reported
        
        if not self.auth_token:
            self.log_test("Navigation Error Resolution", False, "No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test with a simple navigation update that should work
        test_navigation = [
            {
                "id": "test1",
                "label": "Test Page", 
                "href": "/test",
                "order": 1,
                "is_external": False
            }
        ]
        
        try:
            # Test POST method
            post_response = requests.post(f"{self.api_url}/admin/navigation", 
                                        json=test_navigation, headers=headers, timeout=10)
            post_success = post_response.status_code == 200
            
            # Test PUT method  
            put_response = requests.put(f"{self.api_url}/admin/navigation", 
                                      json=test_navigation, headers=headers, timeout=10)
            put_success = put_response.status_code == 200
            
            # Test GET method
            get_response = requests.get(f"{self.api_url}/admin/navigation", headers=headers, timeout=10)
            get_success = get_response.status_code == 200
            
            # All methods should work without "Not Found" errors
            success = post_success and put_success and get_success
            
            if success:
                details = "All navigation endpoints working correctly - 'Error updating navigation: Not Found' issue resolved"
            else:
                error_details = []
                if not post_success:
                    error_details.append(f"POST failed: {post_response.status_code}")
                if not put_success:
                    error_details.append(f"PUT failed: {put_response.status_code}")
                if not get_success:
                    error_details.append(f"GET failed: {get_response.status_code}")
                details = f"Some endpoints still failing: {', '.join(error_details)}"
                
            self.log_test("Navigation Error Resolution", success, details)
            return success
            
        except Exception as e:
            self.log_test("Navigation Error Resolution", False, str(e))
            return False

    def run_navigation_tests(self):
        """Run all navigation menu tests"""
        print("🧭 Starting Navigation Menu Admin Endpoints Test")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed, stopping tests")
            return False
        
        print("\n📋 Testing Navigation Menu Admin Endpoints...")
        
        # Test 1: GET /api/admin/navigation (initial state)
        initial_success, initial_items = self.test_get_navigation_empty()
        
        # Test 2: POST /api/admin/navigation with sample data
        post_success = self.test_post_navigation_sample_data()
        
        # Test 3: GET /api/admin/navigation after saving
        if post_success:
            get_after_save_success, saved_items = self.test_get_navigation_after_save()
        
        # Test 4: PUT /api/admin/navigation (alternative method)
        put_success = self.test_put_navigation_alternative()
        
        # Test 5: Verify data persistence
        if put_success:
            persistence_success = self.test_navigation_persistence()
        
        # Test 6: Verify error resolution
        error_resolution_success = self.test_navigation_error_resolution()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Navigation Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.errors:
            print(f"\n❌ Errors found ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("✅ All navigation tests passed successfully!")
            print("\n🎉 Navigation Menu admin endpoints are working correctly!")
            print("   • GET /api/admin/navigation - Returns navigation items")
            print("   • POST /api/admin/navigation - Accepts and saves navigation data")
            print("   • PUT /api/admin/navigation - Alternative method works")
            print("   • Navigation data persists between requests")
            print("   • 'Error updating navigation: [object Object]' issue is resolved")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = NavigationMenuTester()
    success = tester.run_navigation_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())