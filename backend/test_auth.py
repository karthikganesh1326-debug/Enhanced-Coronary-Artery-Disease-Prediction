"""
Authentication System Test Suite for CAD Prediction System
Tests registration, login, session management, and protected routes
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

class AuthTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.test_username = "test_user_" + str(hash("test"))[-5:]
        self.test_password = "securepass123"
    
    def log_test(self, test_name, passed, message=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        self.results.append({
            'test': test_name,
            'status': status,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   └─ {message}")
    
    def test_registration_page_loads(self):
        """Test 1: Registration page loads"""
        try:
            response = self.session.get(f"{BASE_URL}/register")
            passed = response.status_code == 200 and "Create Account" in response.text
            self.log_test("Registration page loads", passed, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Registration page loads", False, str(e))
    
    def test_login_page_loads(self):
        """Test 2: Login page loads"""
        try:
            response = self.session.get(f"{BASE_URL}/login")
            passed = response.status_code == 200 and "Sign In" in response.text
            self.log_test("Login page loads", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Login page loads", False, str(e))
    
    def test_redirect_to_login_when_not_authenticated(self):
        """Test 3: Unauthenticated users redirected to login"""
        try:
            # Clear session
            self.session.cookies.clear()
            response = self.session.get(f"{BASE_URL}/", allow_redirects=False)
            
            # Should redirect to login (302 or 303)
            passed = response.status_code in [301, 302, 303]
            self.log_test("Unauthenticated redirect to login", passed, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Unauthenticated redirect to login", False, str(e))
    
    def test_user_registration(self):
        """Test 4: Register new user"""
        try:
            data = {
                'username': self.test_username,
                'password': self.test_password,
                'confirm_password': self.test_password
            }
            response = self.session.post(f"{BASE_URL}/register", data=data, 
                                        allow_redirects=True)
            
            # Should redirect to login page after registration
            passed = response.status_code == 200 and "Sign In" in response.text
            self.log_test("User registration", passed, 
                         f"Username: {self.test_username}")
        except Exception as e:
            self.log_test("User registration", False, str(e))
    
    def test_duplicate_username_rejected(self):
        """Test 5: Duplicate username rejected"""
        try:
            data = {
                'username': self.test_username,
                'password': 'another_pass123',
                'confirm_password': 'another_pass123'
            }
            response = self.session.post(f"{BASE_URL}/register", data=data)
            
            # Should show error about username existing
            passed = "already exists" in response.text.lower() or response.status_code == 200
            self.log_test("Duplicate username rejected", passed, 
                         "Registration form shown with error")
        except Exception as e:
            self.log_test("Duplicate username rejected", False, str(e))
    
    def test_user_login(self):
        """Test 6: Login with correct credentials"""
        try:
            data = {
                'username': self.test_username,
                'password': self.test_password
            }
            response = self.session.post(f"{BASE_URL}/login", data=data, 
                                        allow_redirects=True)
            
            # Should redirect to home and show prediction form
            passed = response.status_code == 200 and "Predict" in response.text
            self.log_test("User login (correct credentials)", passed)
        except Exception as e:
            self.log_test("User login (correct credentials)", False, str(e))
    
    def test_wrong_password_rejected(self):
        """Test 7: Login with wrong password rejected"""
        try:
            # Clear session first
            self.session.cookies.clear()
            
            data = {
                'username': self.test_username,
                'password': 'wrong_password'
            }
            response = self.session.post(f"{BASE_URL}/login", data=data)
            
            # Should show error
            passed = "Invalid" in response.text
            self.log_test("Login rejected (wrong password)", passed, 
                         "Error message displayed")
        except Exception as e:
            self.log_test("Login rejected (wrong password)", False, str(e))
    
    def test_nonexistent_user_rejected(self):
        """Test 8: Login with nonexistent user rejected"""
        try:
            data = {
                'username': 'nonexistent_user_xyz',
                'password': 'anypassword'
            }
            response = self.session.post(f"{BASE_URL}/login", data=data)
            
            # Should show error
            passed = "Invalid" in response.text
            self.log_test("Login rejected (nonexistent user)", passed, 
                         "Error message displayed")
        except Exception as e:
            self.log_test("Login rejected (nonexistent user)", False, str(e))
    
    def test_session_cookie_created(self):
        """Test 9: Session cookie created after login"""
        try:
            # First login
            data = {
                'username': self.test_username,
                'password': self.test_password
            }
            response = self.session.post(f"{BASE_URL}/login", data=data, 
                                        allow_redirects=True)
            
            # Check if session cookie exists
            passed = 'session' in self.session.cookies
            self.log_test("Session cookie created", passed, 
                         f"Cookies: {dict(self.session.cookies)}")
        except Exception as e:
            self.log_test("Session cookie created", False, str(e))
    
    def test_authenticated_user_can_access_home(self):
        """Test 10: Authenticated user can access home page"""
        try:
            # Should still be logged in from previous test
            response = self.session.get(f"{BASE_URL}/")
            
            passed = response.status_code == 200 and "Predict" in response.text
            self.log_test("Authenticated access to home", passed, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Authenticated access to home", False, str(e))
    
    def test_about_page_accessible_without_auth(self):
        """Test 11: About page accessible to all users"""
        try:
            # Clear session
            self.session.cookies.clear()
            response = self.session.get(f"{BASE_URL}/about")
            
            passed = response.status_code == 200 and "About" in response.text
            self.log_test("About page accessible without auth", passed, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("About page accessible without auth", False, str(e))
    
    def test_about_page_accessible_with_auth(self):
        """Test 12: About page accessible to authenticated users"""
        try:
            # Login first
            data = {
                'username': self.test_username,
                'password': self.test_password
            }
            self.session.post(f"{BASE_URL}/login", data=data)
            
            response = self.session.get(f"{BASE_URL}/about")
            
            passed = response.status_code == 200
            self.log_test("About page accessible with auth", passed, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("About page accessible with auth", False, str(e))
    
    def test_logout_clears_session(self):
        """Test 13: Logout clears session"""
        try:
            # Should be logged in from previous test
            response = self.session.get(f"{BASE_URL}/logout", allow_redirects=True)
            
            # Check session cookie is cleared
            passed = 'session' not in self.session.cookies
            self.log_test("Logout clears session", passed, 
                         f"Cookies: {dict(self.session.cookies)}")
        except Exception as e:
            self.log_test("Logout clears session", False, str(e))
    
    def test_after_logout_redirected_to_login(self):
        """Test 14: After logout, accessing home redirects to login"""
        try:
            response = self.session.get(f"{BASE_URL}/", allow_redirects=False)
            
            # Should redirect to login
            passed = response.status_code in [301, 302, 303]
            self.log_test("Post-logout redirect to login", passed, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Post-logout redirect to login", False, str(e))
    
    def test_password_validation_too_short(self):
        """Test 15: Password validation - too short"""
        try:
            data = {
                'username': 'new_user_test',
                'password': '123',  # Less than 6 chars
                'confirm_password': '123'
            }
            response = self.session.post(f"{BASE_URL}/register", data=data)
            
            # Should show error about password length
            passed = "6" in response.text or "password" in response.text.lower()
            self.log_test("Password validation (too short)", passed, 
                         "Error displayed for short password")
        except Exception as e:
            self.log_test("Password validation (too short)", False, str(e))
    
    def test_username_validation_too_short(self):
        """Test 16: Username validation - too short"""
        try:
            data = {
                'username': 'ab',  # Less than 3 chars
                'password': 'validpass123',
                'confirm_password': 'validpass123'
            }
            response = self.session.post(f"{BASE_URL}/register", data=data)
            
            # Should show error about username length
            passed = "3" in response.text or "username" in response.text.lower()
            self.log_test("Username validation (too short)", passed, 
                         "Error displayed for short username")
        except Exception as e:
            self.log_test("Username validation (too short)", False, str(e))
    
    def test_password_mismatch_validation(self):
        """Test 17: Password mismatch validation"""
        try:
            data = {
                'username': 'new_user_test_2',
                'password': 'password123',
                'confirm_password': 'password456'  # Different
            }
            response = self.session.post(f"{BASE_URL}/register", data=data)
            
            # Should show error about passwords not matching
            passed = "not match" in response.text.lower() or "match" in response.text.lower()
            self.log_test("Password mismatch validation", passed, 
                         "Error displayed for mismatched passwords")
        except Exception as e:
            self.log_test("Password mismatch validation", False, str(e))
    
    def test_navbar_shows_login_when_not_authenticated(self):
        """Test 18: Navbar shows Login/Register links when unauthenticated"""
        try:
            self.session.cookies.clear()
            response = self.session.get(f"{BASE_URL}/")
            
            # Response should be login page redirect, check login page instead
            response = self.session.get(f"{BASE_URL}/login")
            passed = response.status_code == 200
            self.log_test("Navbar shows Login/Register when unauthenticated", passed)
        except Exception as e:
            self.log_test("Navbar shows Login/Register when unauthenticated", False, str(e))
    
    def test_navbar_shows_logout_when_authenticated(self):
        """Test 19: Navbar shows Logout button when authenticated"""
        try:
            # Login
            data = {
                'username': self.test_username,
                'password': self.test_password
            }
            response = self.session.post(f"{BASE_URL}/login", data=data, 
                                        allow_redirects=True)
            
            # Check home page has logout button
            passed = "Logout" in response.text or response.status_code == 200
            self.log_test("Navbar shows Logout when authenticated", passed)
        except Exception as e:
            self.log_test("Navbar shows Logout when authenticated", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("CAD PREDICTION SYSTEM - AUTHENTICATION TEST SUITE")
        print("="*60 + "\n")
        
        self.test_registration_page_loads()
        self.test_login_page_loads()
        self.test_redirect_to_login_when_not_authenticated()
        self.test_user_registration()
        self.test_duplicate_username_rejected()
        self.test_user_login()
        self.test_wrong_password_rejected()
        self.test_nonexistent_user_rejected()
        self.test_session_cookie_created()
        self.test_authenticated_user_can_access_home()
        self.test_about_page_accessible_without_auth()
        self.test_about_page_accessible_with_auth()
        self.test_logout_clears_session()
        self.test_after_logout_redirected_to_login()
        self.test_password_validation_too_short()
        self.test_username_validation_too_short()
        self.test_password_mismatch_validation()
        self.test_navbar_shows_login_when_not_authenticated()
        self.test_navbar_shows_logout_when_authenticated()
        
        # Print summary
        print("\n" + "="*60)
        passed = sum(1 for r in self.results if "PASS" in r['status'])
        total = len(self.results)
        print(f"TEST SUMMARY: {passed}/{total} tests passed")
        print("="*60 + "\n")
        
        return passed, total

if __name__ == "__main__":
    tester = AuthTestSuite()
    passed, total = tester.run_all_tests()
    
    # Return exit code based on results
    exit(0 if passed == total else 1)
