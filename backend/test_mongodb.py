"""
Test script for MongoDB Atlas connection and functionality.
Run this to verify MongoDB setup before deploying the application.

Usage:
    cd backend
    python test_mongodb.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("⚠ python-dotenv not installed, check that MONGODB_URL is accessible")

# Configuration
MONGODB_URL = os.environ.get('MONGODB_URL')
if not MONGODB_URL:
    print("❌ MONGODB_URL not found in environment variables")
    print("   Create a .env file in the project root with:")
    print("   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/")
    sys.exit(1)

DB_NAME = 'cad_prediction_db'
COLLECTIONS = ['users', 'assessments', 'patient_profiles', 'doctor_profiles']

# ===== TEST FUNCTIONS =====

def test_connection():
    """Test MongoDB Atlas connection."""
    print("\n" + "="*80)
    print("TEST 1: MongoDB Atlas Connection")
    print("="*80)
    
    try:
        print(f"🔍 Connecting to MongoDB Atlas...")
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        print(f"🔍 Sending ping command...")
        result = client.admin.command('ping')
        
        if result.get('ok') == 1.0:
            print(f"✅ Connection successful!")
            return client
        else:
            print(f"❌ Ping failed: {result}")
            return None
            
    except ServerSelectionTimeoutError as e:
        print(f"❌ Connection timeout")
        print(f"   Check: Network access, cluster status, internet connection")
        return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_database(client):
    """Test database access and collection creation."""
    print("\n" + "="*80)
    print("TEST 2: Database Access")
    print("="*80)
    
    try:
        db = client[DB_NAME]
        
        print(f"✅ Database '{DB_NAME}' accessible")
        
        # Create indexes
        print(f"🔍 Creating indexes...")
        db['users'].create_index('username', unique=True)
        db['users'].create_index('email', unique=True)
        db['assessments'].create_index('user_id')
        db['assessments'].create_index('created_at')
        
        print(f"✅ Indexes created successfully")
        return db
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def test_user_registration(db):
    """Test user registration and password hashing."""
    print("\n" + "="*80)
    print("TEST 3: User Registration & Password Security")
    print("="*80)
    
    try:
        # Clean up any existing test user
        db['users'].delete_one({'username': 'test_patient_mongodb'})
        print(f"🔍 Cleaned up existing test user")
        
        # Register test user
        username = 'test_patient_mongodb'
        email = 'test@mongodb.local'
        password = 'testpass123'
        
        password_hash = generate_password_hash(password)
        
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': 'patient',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db['users'].insert_one(user_doc)
        user_id = result.inserted_id
        
        print(f"✅ User registered: {username}")
        print(f"   User ID: {user_id}")
        print(f"   Password hash: {password_hash[:30]}...")
        
        # Verify password
        stored_user = db['users'].find_one({'_id': user_id})
        is_valid = check_password_hash(stored_user['password_hash'], password)
        
        if is_valid:
            print(f"✅ Password verification successful")
        else:
            print(f"❌ Password verification failed")
            return None
        
        # Also verify wrong password fails
        is_wrong = check_password_hash(stored_user['password_hash'], 'wrongpassword')
        if not is_wrong:
            print(f"✅ Wrong password correctly rejected")
        else:
            print(f"❌ Wrong password incorrectly accepted")
            return None
        
        return user_id
        
    except DuplicateKeyError:
        print(f"❌ Duplicate key error - try changing the test username")
        return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_assessment(db, user_id):
    """Test saving and retrieving assessments."""
    print("\n" + "="*80)
    print("TEST 4: Assessment Storage & Retrieval")
    print("="*80)
    
    try:
        # Create test assessment
        assessment = {
            'user_id': user_id,
            'age': 65.0,
            'anaemia': 0,
            'creatinine_phosphokinase': 250.0,
            'diabetes': 1,
            'ejection_fraction': 40.0,
            'high_blood_pressure': 0,
            'platelets': 350000.0,
            'serum_creatinine': 1.2,
            'serum_sodium': 140.0,
            'sex': 1,
            'smoking': 0,
            'time': 130.0,
            'probability': 0.75,
            'risk_category': 'HIGH',
            'created_at': datetime.utcnow()
        }
        
        result = db['assessments'].insert_one(assessment)
        assessment_id = result.inserted_id
        
        print(f"✅ Assessment saved")
        print(f"   Assessment ID: {assessment_id}")
        print(f"   Risk Category: {assessment['risk_category']}")
        print(f"   Probability: {assessment['probability']}")
        
        # Retrieve assessment
        retrieved = db['assessments'].find_one({'_id': assessment_id})
        
        if retrieved and retrieved['probability'] == 0.75:
            print(f"✅ Assessment retrieved successfully")
        else:
            print(f"❌ Assessment retrieval failed")
            return False
        
        # Query assessments for patient
        patient_assessments = list(db['assessments'].find({
            'user_id': user_id
        }).sort('created_at', -1))
        
        print(f"✅ Found {len(patient_assessments)} assessment(s) for patient")
        
        return True
        
    except Exception as e:
        print(f"❌ Assessment error: {e}")
        return False

def test_profiles(db, user_id):
    """Test patient profile creation."""
    print("\n" + "="*80)
    print("TEST 5: Profile Collections")
    print("="*80)
    
    try:
        # Clean up
        db['patient_profiles'].delete_one({'user_id': user_id})
        
        # Create patient profile
        profile = {
            'user_id': user_id,
            'age': 65,
            'gender': 'M',
            'medical_history': ['Hypertension (2020)', 'Diabetes (2018)'],
            'created_at': datetime.utcnow()
        }
        
        result = db['patient_profiles'].insert_one(profile)
        
        print(f"✅ Patient profile created")
        print(f"   Profile ID: {result.inserted_id}")
        
        # Retrieve profile
        retrieved = db['patient_profiles'].find_one({'user_id': user_id})
        
        if retrieved:
            print(f"✅ Patient profile retrieved")
            print(f"   Gender: {retrieved.get('gender')}")
            print(f"   Medical history: {retrieved.get('medical_history')}")
        else:
            print(f"❌ Patient profile retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Profile error: {e}")
        return False

def test_queries(db, user_id):
    """Test various database queries."""
    print("\n" + "="*80)
    print("TEST 6: Query Examples")
    print("="*80)
    
    try:
        # Count users
        user_count = db['users'].count_documents({})
        print(f"✅ Total users in database: {user_count}")
        
        # Count assessments
        assessment_count = db['assessments'].count_documents({})
        print(f"✅ Total assessments in database: {assessment_count}")
        
        # Find high-risk assessments
        high_risk = list(db['assessments'].find({
            'risk_category': 'HIGH'
        }))
        print(f"✅ High-risk assessments: {len(high_risk)}")
        
        # Aggregation example
        risk_summary = list(db['assessments'].aggregate([
            {
                '$group': {
                    '_id': '$risk_category',
                    'count': {'$sum': 1}
                }
            }
        ]))
        
        print(f"✅ Risk category summary:")
        for item in risk_summary:
            print(f"   {item['_id']}: {item['count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

def test_update(db, user_id):
    """Test profile updating."""
    print("\n" + "="*80)
    print("TEST 7: Update Operations")
    print("="*80)
    
    try:
        # Update user
        result = db['users'].update_one(
            {'_id': user_id},
            {'$set': {
                'email': 'newemail@mongodb.local',
                'updated_at': datetime.utcnow()
            }}
        )
        
        if result.matched_count > 0:
            print(f"✅ User updated successfully")
            
            # Verify update
            updated_user = db['users'].find_one({'_id': user_id})
            print(f"   New email: {updated_user['email']}")
        else:
            print(f"❌ User update failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False

def test_cleanup(db, user_id):
    """Clean up test data."""
    print("\n" + "="*80)
    print("TEST 8: Cleanup")
    print("="*80)
    
    try:
        # Delete test user
        result1 = db['users'].delete_one({'_id': user_id})
        print(f"✅ Test user deleted: {result1.deleted_count} document(s)")
        
        # Delete test assessments
        result2 = db['assessments'].delete_many({'user_id': user_id})
        print(f"✅ Test assessments deleted: {result2.deleted_count} document(s)")
        
        # Delete test profile
        result3 = db['patient_profiles'].delete_one({'user_id': user_id})
        print(f"✅ Test profile deleted: {result3.deleted_count} document(s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        return False

def print_summary(results):
    """Print test summary."""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! MongoDB is properly configured.")
        print("\nYou can now:")
        print("  1. Activate the MongoDB version:")
        print("     cd backend")
        print("     move app.py app_sqlite.py")
        print("     move app_mongodb.py app.py")
        print("\n  2. Run the application:")
        print("     python app.py")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return False

# ===== MAIN EXECUTION =====

if __name__ == '__main__':
    print("\n" + "="*80)
    print("MongoDB Atlas Configuration Test Suite")
    print("="*80)
    print(f"\nTesting MongoDB URL: {MONGODB_URL[:60]}...")
    
    results = []
    
    # Test 1: Connection
    client = test_connection()
    results.append(client is not None)
    
    if not client:
        print("\n❌ Cannot proceed - connection failed")
        print_summary(results)
        sys.exit(1)
    
    # Test 2: Database
    db = test_database(client)
    results.append(db is not None)
    
    if db is None:
        print("\n❌ Cannot proceed - database access failed")
        print_summary(results)
        sys.exit(1)
    
    # Test 3: User Registration
    user_id = test_user_registration(db)
    results.append(user_id is not None)
    
    if not user_id:
        print("\n⚠️  Skipping dependent tests")
        print_summary(results)
        sys.exit(1)
    
    # Test 4: Assessment
    results.append(test_assessment(db, user_id))
    
    # Test 5: Profiles
    results.append(test_profiles(db, user_id))
    
    # Test 6: Queries
    results.append(test_queries(db, user_id))
    
    # Test 7: Update
    results.append(test_update(db, user_id))
    
    # Test 8: Cleanup
    results.append(test_cleanup(db, user_id))
    
    # Print summary and exit
    success = print_summary(results)
    
    # Close connection
    client.close()
    print("\n✅ MongoDB connection closed")
    
    sys.exit(0 if success else 1)
