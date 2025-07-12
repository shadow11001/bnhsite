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
        """Test getting all hosting plans"""
        try:
            response = requests.get(f"{self.api_url}/hosting-plans", timeout=10)
            success = response.status_code == 200
            
            if success:
                plans = response.json()
                success = isinstance(plans, list) and len(plans) > 0
                
                if success:
                    # Verify we have the expected 12 plans
                    expected_count = 12
                    actual_count = len(plans)
                    success = actual_count == expected_count
                    
                    if success:
                        # Check plan types distribution
                        plan_types = {}
                        for plan in plans:
                            plan_type = plan.get('plan_type')
                            plan_types[plan_type] = plan_types.get(plan_type, 0) + 1
                        
                        expected_types = {
                            'ssd_shared': 3,
                            'hdd_shared': 3, 
                            'standard_vps': 3,
                            'standard_gameserver': 3
                        }
                        
                        types_match = plan_types == expected_types
                        success = types_match
                        details = f"Found {actual_count} plans, Types: {plan_types}"
                    else:
                        details = f"Expected {expected_count} plans, got {actual_count}"
                else:
                    details = "Invalid response format or empty plans"
            else:
                details = f"HTTP {response.status_code}"
                
            self.log_test("Get All Hosting Plans", success, details)
            return success, plans if success else []
            
        except Exception as e:
            self.log_test("Get All Hosting Plans", False, str(e))
            return False, []

    def test_hosting_plans_filtered(self, plans):
        """Test filtering hosting plans by type"""
        plan_types = ['ssd_shared', 'hdd_shared', 'standard_vps', 'standard_gameserver']
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
                        expected_count = 3  # Each type should have 3 plans
                        actual_count = len(filtered_plans)
                        
                        success = correct_type and actual_count == expected_count
                        details = f"Type: {plan_type}, Count: {actual_count}/3"
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
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": "test@example.com",
            "subject": "API Test Contact",
            "message": "This is a test message from the API test suite."
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
            
            # Check pricing range ($1-$80)
            if not (1 <= price <= 80):
                pricing_valid = False
                self.errors.append(f"Plan {plan_name} price ${price} outside range $1-$80")
            
            # Track popular plans
            if plan.get('popular'):
                popular_plans.append(plan_name)
            
            # Track managed plans with markup
            if plan.get('markup_percentage', 0) > 0:
                markup_plans.append(f"{plan_name} ({plan.get('markup_percentage')}%)")
        
        # Verify expected popular plans
        expected_popular = ['Topaz', 'Venus', 'Solar']
        popular_correct = set(popular_plans) == set(expected_popular)
        
        # Verify markup percentages
        vps_plans = [p for p in plans if p.get('plan_type') == 'standard_vps']
        gameserver_plans = [p for p in plans if p.get('plan_type') == 'standard_gameserver']
        
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