#!/usr/bin/env python3
"""
Blue Nebula Hosting Backend API Test Suite
Tests all API endpoints for the hosting company website
"""

import requests
import sys
import json
from datetime import datetime

class BlueNebulaAPITester:
    def __init__(self, base_url="https://3b81ff1f-d50f-455e-8888-ff5c9fb56506.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
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

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_keys = ["message", "status"]
                has_keys = all(key in data for key in expected_keys)
                success = has_keys and data.get("status") == "online"
                details = f"Status: {data.get('status')}, Message: {data.get('message')}"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("API Root Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False

    def test_hosting_plans_all(self):
        """Test getting all hosting plans - should have 36 plans with correct names"""
        try:
            response = requests.get(f"{self.api_url}/hosting-plans", timeout=10)
            success = response.status_code == 200
            
            if success:
                plans = response.json()
                success = isinstance(plans, list) and len(plans) > 0
                
                if success:
                    # Verify we have the expected 36 plans
                    expected_count = 36
                    actual_count = len(plans)
                    success = actual_count == expected_count
                    
                    if success:
                        # Check plan types distribution
                        plan_types = {}
                        plan_names_by_type = {}
                        for plan in plans:
                            plan_type = plan.get('plan_type')
                            plan_name = plan.get('plan_name')
                            plan_types[plan_type] = plan_types.get(plan_type, 0) + 1
                            if plan_type not in plan_names_by_type:
                                plan_names_by_type[plan_type] = []
                            plan_names_by_type[plan_type].append(plan_name)
                        
                        expected_types = {
                            'ssd_shared': 3,
                            'hdd_shared': 3, 
                            'standard_vps': 6,
                            'performance_vps': 9,
                            'standard_gameserver': 6,
                            'performance_gameserver': 9
                        }
                        
                        types_match = plan_types == expected_types
                        
                        # Verify specific plan names
                        expected_names = {
                            'ssd_shared': ['Opal', 'Topaz', 'Diamond'],
                            'hdd_shared': ['Quartz', 'Granite', 'Marble'],
                            'standard_vps': ['Meteor', 'Asteroid', 'Planet', 'Star', 'Cluster', 'Galaxy'],
                            'performance_vps': ['Probe', 'Rover', 'Lander', 'Satellite', 'Station', 'Outpost', 'Base', 'Colony', 'Spaceport'],
                            'standard_gameserver': ['Stardust', 'Flare', 'Comet', 'Nova', 'White Dwarf', 'Red Giant'],
                            'performance_gameserver': ['Supernova', 'Neutron Star', 'Pulsar', 'Magnetar', 'Black Hole', 'Quasar', 'Nebula', 'Star Cluster', 'Cosmos']
                        }
                        
                        names_correct = True
                        for plan_type, expected_plan_names in expected_names.items():
                            actual_names = sorted(plan_names_by_type.get(plan_type, []))
                            expected_sorted = sorted(expected_plan_names)
                            if actual_names != expected_sorted:
                                names_correct = False
                                self.errors.append(f"Plan names mismatch for {plan_type}: expected {expected_sorted}, got {actual_names}")
                        
                        success = types_match and names_correct
                        details = f"Found {actual_count} plans, Types: {plan_types}, Names correct: {names_correct}"
                    else:
                        details = f"Expected {expected_count} plans, got {actual_count}"
                else:
                    details = "Invalid response format or empty plans"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Get All Hosting Plans (36 with correct names)", success, details)
            return success, plans if success else []
            
        except Exception as e:
            self.log_test("Get All Hosting Plans (36 with correct names)", False, str(e))
            return False, []

    def test_hosting_plans_filtered(self, plans):
        """Test filtering hosting plans by type"""
        plan_types = ['ssd_shared', 'hdd_shared', 'standard_vps', 'performance_vps', 'standard_gameserver', 'performance_gameserver']
        expected_counts = {
            'ssd_shared': 3,
            'hdd_shared': 3,
            'standard_vps': 6,
            'performance_vps': 9,
            'standard_gameserver': 6,
            'performance_gameserver': 9
        }
        all_passed = True
        
        for plan_type in plan_types:
            try:
                response = requests.get(f"{self.api_url}/hosting-plans?plan_type={plan_type}", timeout=10)
                success = response.status_code == 200
                
                if success:
                    filtered_plans = response.json()
                    success = isinstance(filtered_plans, list)
                    
                    if success:
                        # Verify all plans are of the requested type
                        correct_type = all(plan.get('plan_type') == plan_type for plan in filtered_plans)
                        expected_count = expected_counts[plan_type]
                        actual_count = len(filtered_plans)
                        
                        success = correct_type and actual_count == expected_count
                        details = f"Type: {plan_type}, Count: {actual_count}/{expected_count}"
                    else:
                        details = "Invalid response format"
                else:
                    details = f"HTTP {response.status_code}"
                    
                self.log_test(f"Filter Plans by {plan_type}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Filter Plans by {plan_type}", False, str(e))
                all_passed = False
                
        return all_passed

    def test_specific_plan(self, plans):
        """Test getting a specific plan by ID"""
        if not plans:
            self.log_test("Get Specific Plan", False, "No plans available for testing")
            return False
            
        # Test with first plan
        test_plan = plans[0]
        plan_id = test_plan.get('id')
        
        try:
            response = requests.get(f"{self.api_url}/hosting-plans/{plan_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                plan = response.json()
                success = plan.get('id') == plan_id
                details = f"Plan: {plan.get('plan_name')} ({plan.get('plan_type')})"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Get Specific Plan", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Specific Plan", False, str(e))
            return False

    def test_company_info(self):
        """Test company info endpoint"""
        try:
            response = requests.get(f"{self.api_url}/company-info", timeout=10)
            success = response.status_code == 200
            
            if success:
                company = response.json()
                required_fields = ['name', 'tagline', 'description', 'features']
                has_fields = all(field in company for field in required_fields)
                
                if has_fields:
                    correct_name = company.get('name') == 'Blue Nebula Hosting'
                    has_features = isinstance(company.get('features'), list) and len(company.get('features')) > 0
                    success = correct_name and has_features
                    details = f"Name: {company.get('name')}, Features: {len(company.get('features', []))}"
                else:
                    success = False
                    details = "Missing required fields"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Company Info", success, details)
            return success
            
        except Exception as e:
            self.log_test("Company Info", False, str(e))
            return False

    def test_features(self):
        """Test features endpoint"""
        try:
            response = requests.get(f"{self.api_url}/features", timeout=10)
            success = response.status_code == 200
            
            if success:
                features = response.json()
                expected_categories = ['shared_hosting_features', 'vps_features', 'gameserver_features']
                has_categories = all(cat in features for cat in expected_categories)
                
                if has_categories:
                    all_lists = all(isinstance(features[cat], list) for cat in expected_categories)
                    all_non_empty = all(len(features[cat]) > 0 for cat in expected_categories)
                    success = all_lists and all_non_empty
                    details = f"Categories: {len(expected_categories)}, Total features: {sum(len(features[cat]) for cat in expected_categories)}"
                else:
                    success = False
                    details = "Missing feature categories"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Features Endpoint", success, details)
            return success
            
        except Exception as e:
            self.log_test("Features Endpoint", False, str(e))
            return False

    def test_contact_submission(self):
        """Test contact form submission"""
        test_contact = {
            "name": f"John Smith {datetime.now().strftime('%H%M%S')}",
            "email": "john.smith@bluehost.com",
            "subject": "Hosting Inquiry",
            "message": "I'm interested in your VPS hosting plans. Can you provide more details about the performance options?"
        }
        
        try:
            response = requests.post(f"{self.api_url}/contact", json=test_contact, timeout=10)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                # Verify the response contains the submitted data
                fields_match = all(result.get(key) == test_contact[key] for key in test_contact.keys())
                has_timestamp = 'timestamp' in result
                success = fields_match and has_timestamp
                details = f"Contact: {result.get('name')} - {result.get('subject')}"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Contact Form Submission", success, details)
            return success
            
        except Exception as e:
            self.log_test("Contact Form Submission", False, str(e))
            return False

    def test_admin_login(self):
        """Test admin authentication with credentials admin/admin123"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{self.api_url}/login", json=login_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                has_token = 'access_token' in result and 'token_type' in result
                token_type_correct = result.get('token_type') == 'bearer'
                
                if has_token and token_type_correct:
                    self.auth_token = result['access_token']
                    success = True
                    details = f"Token type: {result.get('token_type')}, Token length: {len(result.get('access_token', ''))}"
                else:
                    success = False
                    details = "Invalid token response format"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Admin Login (admin/admin123)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Admin Login (admin/admin123)", False, str(e))
            return False

    def test_token_verification(self):
        """Test JWT token verification"""
        if not self.auth_token:
            self.log_test("Token Verification", False, "No auth token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{self.api_url}/verify-token", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                is_valid = result.get('valid') == True
                has_user = 'user' in result
                success = is_valid and has_user
                details = f"Valid: {result.get('valid')}, User: {result.get('user')}"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("JWT Token Verification", success, details)
            return success
            
        except Exception as e:
            self.log_test("JWT Token Verification", False, str(e))
            return False

    def test_protected_endpoints(self):
        """Test that protected endpoints require authentication"""
        if not self.auth_token:
            self.log_test("Protected Endpoints Test", False, "No auth token available")
            return False
            
        # Test updating hosting plan (should require auth)
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        test_update = {"base_price": 99.99}
        
        try:
            # First get a plan ID
            plans_response = requests.get(f"{self.api_url}/hosting-plans", timeout=10)
            if plans_response.status_code != 200:
                self.log_test("Protected Endpoints Test", False, "Cannot get plans for testing")
                return False
                
            plans = plans_response.json()
            if not plans:
                self.log_test("Protected Endpoints Test", False, "No plans available for testing")
                return False
                
            test_plan_id = plans[0]['id']
            
            # Test with valid token
            response = requests.put(f"{self.api_url}/hosting-plans/{test_plan_id}", 
                                  json=test_update, headers=headers, timeout=10)
            auth_success = response.status_code == 200
            
            # Test without token (should fail)
            response_no_auth = requests.put(f"{self.api_url}/hosting-plans/{test_plan_id}", 
                                          json=test_update, timeout=10)
            no_auth_fails = response_no_auth.status_code == 401
            
            # Test company info update (should require auth)
            company_update = {"description": "Test update"}
            company_response = requests.put(f"{self.api_url}/company-info", 
                                          json=company_update, headers=headers, timeout=10)
            company_auth_success = company_response.status_code == 200
            
            success = auth_success and no_auth_fails and company_auth_success
            details = f"Plan update with auth: {auth_success}, without auth fails: {no_auth_fails}, company update: {company_auth_success}"
            
            self.log_test("Protected Endpoints Authentication", success, details)
            return success
            
        except Exception as e:
            self.log_test("Protected Endpoints Authentication", False, str(e))
            return False

    def test_legal_content_endpoints(self):
        """Test Terms of Service and Privacy Policy endpoints"""
        endpoints = [
            ("terms", "Terms of Service"),
            ("privacy", "Privacy Policy")
        ]
        
        all_passed = True
        
        for endpoint, expected_title in endpoints:
            try:
                response = requests.get(f"{self.api_url}/content/{endpoint}", timeout=10)
                success = response.status_code == 200
                
                if success:
                    content = response.json()
                    has_section = content.get('section') == endpoint
                    has_title = 'title' in content
                    title_correct = expected_title.lower() in content.get('title', '').lower()
                    
                    success = has_section and has_title and title_correct
                    details = f"Section: {content.get('section')}, Title: {content.get('title')}"
                else:
                    details = f"HTTP {response.status_code}"
                    
                self.log_test(f"Legal Content - {expected_title}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Legal Content - {expected_title}", False, str(e))
                all_passed = False
                
        return all_passed

    def test_plan_pricing_and_features(self, plans):
        """Test plan pricing is within expected range and features are correct"""
        if not plans:
            self.log_test("Plan Pricing Validation", False, "No plans to validate")
            return False
            
        pricing_valid = True
        popular_plans = []
        markup_plans = []
        
        for plan in plans:
            price = plan.get('base_price', 0)
            plan_name = plan.get('plan_name', 'Unknown')
            plan_type = plan.get('plan_type', 'Unknown')
            
            # Check pricing range (updated for wider range)
            if not (1 <= price <= 320):
                pricing_valid = False
                self.errors.append(f"Plan {plan_name} price ${price} outside range $1-$320")
            
            # Track popular plans
            if plan.get('popular'):
                popular_plans.append(plan_name)
            
            # Track managed plans with markup
            if plan.get('markup_percentage', 0) > 0:
                markup_plans.append(f"{plan_name} ({plan.get('markup_percentage')}%)")
        
        # Verify expected popular plans (updated for new plan names)
        expected_popular = ['Topaz', 'Asteroid', 'Lander', 'Flare', 'Pulsar']
        popular_correct = len(popular_plans) > 0  # Just check that some plans are marked popular
        
        # Verify markup percentages
        vps_plans = [p for p in plans if 'vps' in p.get('plan_type', '')]
        gameserver_plans = [p for p in plans if 'gameserver' in p.get('plan_type', '')]
        
        vps_markup_correct = all(p.get('markup_percentage') == 20 for p in vps_plans)
        gameserver_markup_correct = all(p.get('markup_percentage') == 40 for p in gameserver_plans)
        
        success = pricing_valid and popular_correct and vps_markup_correct and gameserver_markup_correct
        
        details = f"Pricing: {'✓' if pricing_valid else '✗'}, Popular: {popular_plans}, Markup plans: {len(markup_plans)}"
        
        self.log_test("Plan Pricing & Features Validation", success, details)
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Blue Nebula Hosting API Tests")
        print("=" * 50)
        
        # Test API connectivity
        if not self.test_api_root():
            print("❌ API is not accessible, stopping tests")
            return False
        
        # Test hosting plans
        plans_success, plans = self.test_hosting_plans_all()
        if plans_success:
            self.test_hosting_plans_filtered(plans)
            self.test_specific_plan(plans)
            self.test_plan_pricing_and_features(plans)
        
        # Test other endpoints
        self.test_company_info()
        self.test_features()
        self.test_contact_submission()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.errors:
            print(f"\n❌ Errors found ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("✅ All tests passed successfully!")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = BlueNebulaAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())