"""
Test script for CAD Prediction System
Demonstrates both web form and JSON API usage
"""

import json
import urllib.parse
import urllib.request
import time

# Test Case 1: Example patient for web form testing
EXAMPLE_PATIENT = {
    'age': '55',
    'sex': '1',
    'anaemia': '0',
    'creatinine_phosphokinase': '500',
    'diabetes': '0',
    'ejection_fraction': '40',
    'high_blood_pressure': '1',
    'platelets': '250000',
    'serum_creatinine': '1.2',
    'serum_sodium': '137',
    'smoking': '0',
    'time': '7'
}

# Test Case 2: Example for JSON API testing
EXAMPLE_JSON_PATIENT = {
    'age': 55,
    'sex': 1,
    'anaemia': 0,
    'creatinine_phosphokinase': 500,
    'diabetes': 0,
    'ejection_fraction': 40,
    'high_blood_pressure': 1,
    'platelets': 250000,
    'serum_creatinine': 1.2,
    'serum_sodium': 137,
    'smoking': 0,
    'time': 7
}

def test_web_prediction():
    """Test prediction using web form"""
    print("\n" + "="*80)
    print("TEST 1: Web Form Prediction")
    print("="*80)
    
    url = 'http://127.0.0.1:5000/predict'
    enc = urllib.parse.urlencode(EXAMPLE_PATIENT).encode()
    req = urllib.request.Request(url, data=enc)
    
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode(errors='replace')
                print(f"\n✓ Web Prediction Status: {resp.status}")
                print(f"  Response Length: {len(body)} bytes")
                
                # Extract risk category from HTML
                if 'LOW' in body:
                    print("  Risk Category: LOW")
                elif 'MEDIUM' in body:
                    print("  Risk Category: MEDIUM")
                elif 'HIGH' in body:
                    print("  Risk Category: HIGH")
                
                return True
        except Exception as e:
            print(f"  Retry {i+1}: {str(e)}")
            time.sleep(1)
    
    print("✗ Failed to reach web prediction endpoint")
    return False

def test_json_api():
    """Test prediction using JSON API"""
    print("\n" + "="*80)
    print("TEST 2: JSON API Prediction")
    print("="*80)
    
    url = 'http://127.0.0.1:5000/api/predict'
    json_data = json.dumps(EXAMPLE_JSON_PATIENT).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    for i in range(5):
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                response = json.loads(resp.read().decode('utf-8'))
                print(f"\n✓ JSON API Status: {resp.status}")
                print(f"  Success: {response.get('success', False)}")
                print(f"  Probability: {response.get('probability', 'N/A')}%")
                print(f"  Risk Category: {response.get('risk_category', 'N/A')}")
                
                if 'recommendation' in response:
                    print(f"  Recommendation: {response['recommendation']['text']}")
                
                if 'contributing_features' in response:
                    print(f"  Top Features: {len(response['contributing_features'])} identified")
                
                return True
        except Exception as e:
            print(f"  Retry {i+1}: {str(e)}")
            time.sleep(1)
    
    print("✗ Failed to reach JSON API endpoint")
    return False

def test_features_endpoint():
    """Test features endpoint"""
    print("\n" + "="*80)
    print("TEST 3: Features Information Endpoint")
    print("="*80)
    
    url = 'http://127.0.0.1:5000/api/features'
    req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            response = json.loads(resp.read().decode('utf-8'))
            print(f"\n✓ Features Endpoint Status: {resp.status}")
            print(f"  Total Features: {len(response.get('features', []))}")
            print(f"  Features: {', '.join(response.get('features', [])[:5])}...")
            return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

def test_predictions_log():
    """Test predictions log endpoint"""
    print("\n" + "="*80)
    print("TEST 4: Predictions Log Endpoint")
    print("="*80)
    
    url = 'http://127.0.0.1:5000/api/predictions-log'
    req = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            response = json.loads(resp.read().decode('utf-8'))
            print(f"\n✓ Predictions Log Status: {resp.status}")
            print(f"  Total Predictions: {len(response) if isinstance(response, list) else 0}")
            if isinstance(response, list) and len(response) > 0:
                print(f"  Latest Prediction: {response[-1].get('timestamp', 'N/A')}")
            return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

def test_pages():
    """Test page loading"""
    print("\n" + "="*80)
    print("TEST 5: Page Loading")
    print("="*80)
    
    pages = {
        'Home': 'http://127.0.0.1:5000/',
        'About': 'http://127.0.0.1:5000/about'
    }
    
    for page_name, url in pages.items():
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                print(f"\n✓ {page_name}: {resp.status}")
        except Exception as e:
            print(f"\n✗ {page_name}: {str(e)}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CAD PREDICTION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting endpoints:")
    print("- Web form prediction")
    print("- JSON API prediction")
    print("- Features information")
    print("- Predictions log")
    print("- Page loading")
    
    results = []
    
    # Run tests
    results.append(("Web Form Prediction", test_web_prediction()))
    results.append(("JSON API Prediction", test_json_api()))
    results.append(("Features Endpoint", test_features_endpoint()))
    results.append(("Predictions Log", test_predictions_log()))
    test_pages()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("\n" + "="*80)
