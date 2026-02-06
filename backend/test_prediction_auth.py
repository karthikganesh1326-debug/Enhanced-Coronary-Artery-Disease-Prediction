"""
Prediction Integration Test with Authentication
Tests that predictions work with the new authentication system
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_prediction_requires_authentication():
    """Test that /predict endpoint requires authentication"""
    print("\n" + "="*60)
    print("PREDICTION INTEGRATION TESTS")
    print("="*60 + "\n")
    
    session = requests.Session()
    
    # Test 1: Try to make prediction without login
    print("Test 1: Prediction without authentication...")
    response = session.get(f"{BASE_URL}/", allow_redirects=False)
    assert response.status_code in [301, 302, 303], f"Expected redirect, got {response.status_code}"
    print("✓ PASS: Unauthenticated users redirected to login\n")
    
    # Test 2: Register a test user
    print("Test 2: Register test user...")
    test_user = f"pred_test_{hash('test')%1000000}"
    test_pass = "predtest123"
    
    data = {
        'username': test_user,
        'password': test_pass,
        'confirm_password': test_pass
    }
    response = session.post(f"{BASE_URL}/register", data=data, allow_redirects=True)
    assert "Sign In" in response.text, "Registration page not shown"
    print(f"✓ PASS: User registered: {test_user}\n")
    
    # Test 3: Login with the test user
    print("Test 3: Login with test user...")
    login_data = {
        'username': test_user,
        'password': test_pass
    }
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    assert response.status_code == 200, f"Login failed: {response.status_code}"
    assert "Predict" in response.text, "Prediction form not shown after login"
    print(f"✓ PASS: Successfully logged in\n")
    
    # Test 4: Make a prediction (form data)
    print("Test 4: Submit prediction form...")
    pred_data = {
        'age': '50',
        'sex': '1',
        'anaemia': '0',
        'creatinine_phosphokinase': '500',
        'diabetes': '1',
        'ejection_fraction': '40',
        'high_blood_pressure': '1',
        'platelets': '250000',
        'serum_creatinine': '1.2',
        'serum_sodium': '140',
        'smoking': '0',
        'time': '100'
    }
    
    response = session.post(f"{BASE_URL}/predict", data=pred_data, allow_redirects=True)
    assert response.status_code == 200, f"Prediction failed: {response.status_code}"
    assert "Risk" in response.text or "risk" in response.text.lower(), "Risk category not in response"
    print("✓ PASS: Form-based prediction successful\n")
    
    # Test 5: Make a prediction (JSON API)
    print("Test 5: Submit JSON API prediction...")
    json_data = {
        'age': 55,
        'sex': 1,
        'anaemia': 0,
        'creatinine_phosphokinase': 582,
        'diabetes': 1,
        'ejection_fraction': 40,
        'high_blood_pressure': 1,
        'platelets': 265000,
        'serum_creatinine': 1.5,
        'serum_sodium': 138,
        'smoking': 1,
        'time': 110
    }
    
    response = session.post(
        f"{BASE_URL}/api/predict",
        json=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 200, f"API prediction failed: {response.status_code}"
    result = response.json()
    assert 'probability' in result, "Probability not in response"
    assert 'risk_category' in result, "Risk category not in response"
    print(f"✓ PASS: JSON API prediction successful")
    print(f"  └─ Probability: {result['probability']}%")
    print(f"  └─ Risk Category: {result['risk_category']}\n")
    
    # Test 6: Verify session still active
    print("Test 6: Verify session still active...")
    response = session.get(f"{BASE_URL}/")
    assert response.status_code == 200, "Home page access failed"
    assert test_user in response.text, "Username not visible in navbar"
    print("✓ PASS: Session still active\n")
    
    # Test 7: Logout and verify can't make predictions
    print("Test 7: Logout and verify prediction access denied...")
    response = session.get(f"{BASE_URL}/logout", allow_redirects=True)
    
    # Try prediction after logout
    response = session.get(f"{BASE_URL}/", allow_redirects=False)
    assert response.status_code in [301, 302, 303], "Should redirect after logout"
    print("✓ PASS: Cannot access predictions after logout\n")
    
    print("="*60)
    print("ALL PREDICTION INTEGRATION TESTS PASSED ✓")
    print("="*60)

if __name__ == "__main__":
    try:
        test_prediction_requires_authentication()
    except AssertionError as e:
        print(f"\n✗ FAIL: {e}")
        exit(1)
    except requests.ConnectionError:
        print("\n✗ FAIL: Cannot connect to Flask server at http://127.0.0.1:5000")
        print("Make sure the Flask server is running!")
        exit(1)
    except Exception as e:
        print(f"\n✗ FAIL: {e}")
        exit(1)
