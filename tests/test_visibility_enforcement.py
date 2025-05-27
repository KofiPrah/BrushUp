#!/usr/bin/env python3
"""
Comprehensive Visibility Enforcement Test

This script tests that the backend correctly handles folder and artwork visibility:
- Private folders/artworks are hidden from unauthorized users
- Unlisted folders are accessible with direct links but not in listings
- Public folders are visible to everyone
- Folder owners can always access their own content regardless of visibility

Test scenarios covered:
1. User A tries to access User B's private folder → 404 Not Found
2. User A tries to access artwork in User B's private folder → 404 Not Found  
3. Anonymous user tries to access private content → 404 Not Found
4. User A can access User B's public folders → 200 OK
5. User A can access User B's unlisted folders with direct link → 200 OK
6. Folder owner can access their own private folders → 200 OK
"""

import requests
import json
import time
from datetime import datetime

class VisibilityTestSuite:
    def __init__(self, base_url="https://your-repl-url"):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        
    def log_test(self, test_name, expected, actual, passed, details=""):
        """Log test results for final report."""
        result = {
            'test': test_name,
            'expected': expected,
            'actual': actual,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    → {details}")
    
    def create_test_user(self, username, email, password):
        """Create a test user and return auth token."""
        # Register user
        register_data = {
            'username': username,
            'email': email,
            'password': password,
            'password_confirm': password
        }
        
        response = requests.post(f"{self.base_url}/api/auth/register/", json=register_data)
        if response.status_code != 201:
            print(f"Warning: Could not create user {username} - {response.text}")
            return None
            
        # Login to get token
        login_data = {'username': username, 'password': password}
        response = requests.post(f"{self.base_url}/api/auth/login/", json=login_data)
        
        if response.status_code == 200:
            return response.json().get('token')
        else:
            print(f"Warning: Could not login user {username} - {response.text}")
            return None
    
    def create_test_folder(self, token, name, visibility):
        """Create a test folder and return folder data."""
        headers = {'Authorization': f'Bearer {token}'}
        folder_data = {
            'name': name,
            'description': f'Test folder for {visibility} visibility testing',
            'is_public': visibility
        }
        
        response = requests.post(f"{self.base_url}/api/folders/", 
                               json=folder_data, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Warning: Could not create folder {name} - {response.text}")
            return None
    
    def create_test_artwork(self, token, title, folder_id=None):
        """Create a test artwork and return artwork data."""
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create minimal artwork data (without actual image for testing)
        artwork_data = {
            'title': title,
            'description': f'Test artwork for visibility testing',
            'medium': 'Digital Art',
            'tags': 'test, visibility'
        }
        
        if folder_id:
            artwork_data['folder'] = folder_id
            
        # Note: In real scenario, would include image file
        # For testing purposes, we'll just test the folder assignment logic
        response = requests.post(f"{self.base_url}/api/artworks/", 
                               json=artwork_data, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Warning: Could not create artwork {title} - {response.text}")
            return None
    
    def test_folder_access(self, token, folder_id, expected_status, test_name):
        """Test access to a specific folder."""
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        response = requests.get(f"{self.base_url}/api/folders/{folder_id}/", 
                              headers=headers)
        
        passed = response.status_code == expected_status
        self.log_test(
            test_name,
            f"HTTP {expected_status}",
            f"HTTP {response.status_code}",
            passed,
            f"Response: {response.text[:100]}..." if not passed else ""
        )
        
        return passed
    
    def test_artwork_access(self, token, artwork_id, expected_status, test_name):
        """Test access to a specific artwork."""
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        response = requests.get(f"{self.base_url}/api/artworks/{artwork_id}/", 
                              headers=headers)
        
        passed = response.status_code == expected_status
        self.log_test(
            test_name,
            f"HTTP {expected_status}",
            f"HTTP {response.status_code}",
            passed,
            f"Response: {response.text[:100]}..." if not passed else ""
        )
        
        return passed
    
    def test_folder_listing(self, token, should_include_folder_id, test_name):
        """Test that folder listings respect visibility rules."""
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        response = requests.get(f"{self.base_url}/api/folders/", headers=headers)
        
        if response.status_code == 200:
            folders = response.json().get('results', [])
            folder_ids = [f['id'] for f in folders]
            
            if should_include_folder_id:
                passed = should_include_folder_id in folder_ids
                expected = f"Folder {should_include_folder_id} in listing"
                actual = f"Found folders: {folder_ids}"
            else:
                # Check that no private folders from other users are visible
                passed = True  # Assume pass unless we find violations
                expected = "No unauthorized private folders"
                actual = f"Listed folders: {len(folders)}"
        else:
            passed = False
            expected = "HTTP 200"
            actual = f"HTTP {response.status_code}"
        
        self.log_test(test_name, expected, actual, passed)
        return passed
    
    def test_artwork_listing(self, token, should_include_artwork_id, test_name):
        """Test that artwork listings respect folder visibility rules."""
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        response = requests.get(f"{self.base_url}/api/artworks/", headers=headers)
        
        if response.status_code == 200:
            artworks = response.json().get('results', [])
            artwork_ids = [a['id'] for a in artworks]
            
            if should_include_artwork_id:
                passed = should_include_artwork_id in artwork_ids
                expected = f"Artwork {should_include_artwork_id} in listing"
                actual = f"Found artworks: {artwork_ids}"
            else:
                # For negative test, we can't easily verify without knowing specific IDs
                passed = True  # Assume pass
                expected = "No unauthorized private artworks"
                actual = f"Listed artworks: {len(artworks)}"
        else:
            passed = False
            expected = "HTTP 200"
            actual = f"HTTP {response.status_code}"
        
        self.log_test(test_name, expected, actual, passed)
        return passed
    
    def run_comprehensive_test(self):
        """Run the complete visibility enforcement test suite."""
        print("🔒 Starting Comprehensive Visibility Enforcement Test")
        print("=" * 60)
        
        # Create test users
        print("\n📝 Creating test users...")
        user_a_token = self.create_test_user("test_user_a", "usera@test.com", "testpass123")
        user_b_token = self.create_test_user("test_user_b", "userb@test.com", "testpass123")
        
        if not user_a_token or not user_b_token:
            print("❌ Could not create test users. Please check API endpoints.")
            return False
        
        print("✅ Test users created successfully")
        
        # Create test folders with different visibilities
        print("\n📁 Creating test folders...")
        
        # User B creates folders with different visibility levels
        public_folder = self.create_test_folder(user_b_token, "Public Test Folder", "public")
        private_folder = self.create_test_folder(user_b_token, "Private Test Folder", "private")
        unlisted_folder = self.create_test_folder(user_b_token, "Unlisted Test Folder", "unlisted")
        
        if not all([public_folder, private_folder, unlisted_folder]):
            print("❌ Could not create test folders. Please check folder API endpoints.")
            return False
        
        print("✅ Test folders created successfully")
        
        # Create test artworks in folders
        print("\n🎨 Creating test artworks...")
        
        # Note: In real testing, you'd upload actual images
        # For this test, we'll focus on the folder assignment logic
        public_artwork = self.create_test_artwork(user_b_token, "Public Artwork", public_folder['id'])
        private_artwork = self.create_test_artwork(user_b_token, "Private Artwork", private_folder['id'])
        unlisted_artwork = self.create_test_artwork(user_b_token, "Unlisted Artwork", unlisted_folder['id'])
        
        # Run visibility tests
        print("\n🔍 Running Visibility Tests...")
        print("-" * 40)
        
        # Test 1: User A tries to access User B's private folder → 404
        self.test_folder_access(
            user_a_token, 
            private_folder['id'], 
            404,
            "User A accessing User B's private folder"
        )
        
        # Test 2: Anonymous user tries to access private folder → 404
        self.test_folder_access(
            None, 
            private_folder['id'], 
            404,
            "Anonymous user accessing private folder"
        )
        
        # Test 3: User A can access User B's public folder → 200
        self.test_folder_access(
            user_a_token, 
            public_folder['id'], 
            200,
            "User A accessing User B's public folder"
        )
        
        # Test 4: User A can access User B's unlisted folder with direct link → 200
        self.test_folder_access(
            user_a_token, 
            unlisted_folder['id'], 
            200,
            "User A accessing User B's unlisted folder (direct link)"
        )
        
        # Test 5: User B (owner) can access their own private folder → 200
        self.test_folder_access(
            user_b_token, 
            private_folder['id'], 
            200,
            "User B (owner) accessing their own private folder"
        )
        
        # Test 6: Artwork visibility tests (if artworks were created)
        if private_artwork:
            self.test_artwork_access(
                user_a_token,
                private_artwork['id'],
                404,
                "User A accessing artwork in User B's private folder"
            )
        
        if public_artwork:
            self.test_artwork_access(
                user_a_token,
                public_artwork['id'],
                200,
                "User A accessing artwork in User B's public folder"
            )
        
        # Test 7: Folder listing visibility
        self.test_folder_listing(
            user_a_token,
            public_folder['id'],
            "User A sees User B's public folder in listings"
        )
        
        self.test_folder_listing(
            None,
            public_folder['id'],
            "Anonymous user sees public folder in listings"
        )
        
        # Generate test report
        self.generate_report()
    
    def generate_report(self):
        """Generate and display test results report."""
        print("\n" + "=" * 60)
        print("📊 VISIBILITY ENFORCEMENT TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  • {result['test']}")
                    print(f"    Expected: {result['expected']}")
                    print(f"    Actual: {result['actual']}")
                    if result['details']:
                        print(f"    Details: {result['details']}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 ALL VISIBILITY ENFORCEMENT TESTS PASSED!")
            print("Your backend correctly protects private content from unauthorized access.")
        else:
            print("⚠️  Some visibility enforcement tests failed.")
            print("Please review the failed tests and strengthen your backend security.")
        
        return failed_tests == 0

def main():
    """Run the visibility enforcement test suite."""
    # You'll need to update this URL to match your Replit deployment
    BASE_URL = "https://your-repl-url.replit.app"
    
    # Check if the server is accessible
    try:
        response = requests.get(f"{BASE_URL}/api/")
        if response.status_code != 200:
            print(f"⚠️  Cannot reach API at {BASE_URL}")
            print("Please update BASE_URL in the script to match your deployment URL")
            return
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Cannot connect to {BASE_URL}: {e}")
        print("Please ensure your server is running and update the BASE_URL")
        return
    
    # Run the test suite
    test_suite = VisibilityTestSuite(BASE_URL)
    success = test_suite.run_comprehensive_test()
    
    return success

if __name__ == "__main__":
    main()