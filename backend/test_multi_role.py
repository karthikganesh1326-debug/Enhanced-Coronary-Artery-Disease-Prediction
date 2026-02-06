"""
Multi-Role System Test Suite - Updated for Tuple Returns
Tests for patient and doctor registration, login, dashboards, and predictions
"""

import unittest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module
from app import (
    register_user, login_user, save_prediction, get_patient_predictions,
    get_all_patients, get_patient_with_predictions, get_risk_category, init_db
)


class TestMultiRoleSystem(unittest.TestCase):
    """Test suite for patient and doctor multi-role system"""
    
    def setUp(self):
        """Clear test database before each test"""
        self.test_db = 'test_cad_system.db'
        # Configure the app to use an isolated test DB path inside the backend folder
        from pathlib import Path
        test_db_path = Path(os.path.dirname(os.path.abspath(__file__))) / self.test_db
        app_module.DB_PATH = test_db_path
        # Remove test database if it exists
        if test_db_path.exists():
            test_db_path.unlink()
        # Initialize fresh database at test DB path
        init_db()
    
    def tearDown(self):
        """Clean up test database after each test"""
        from pathlib import Path
        test_db_path = Path(os.path.dirname(os.path.abspath(__file__))) / self.test_db
        if test_db_path.exists():
            test_db_path.unlink()
    
    # ============ PATIENT REGISTRATION TESTS ============
    
    def test_patient_registration_valid(self):
        """Test valid patient registration"""
        success, message = register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        self.assertTrue(success, message)
    
    def test_patient_registration_short_username(self):
        """Test patient registration with username too short"""
        success, message = register_user('ab', 'patient1@email.com', 'pass123', 'patient')
        self.assertFalse(success)
        self.assertIn('Username must be', message)
    
    def test_patient_registration_short_password(self):
        """Test patient registration with password too short"""
        success, message = register_user('patient1', 'patient1@email.com', 'pass', 'patient')
        self.assertFalse(success)
        self.assertIn('least 6', message)
    
    def test_patient_registration_duplicate_username(self):
        """Test patient registration with duplicate username"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        success, message = register_user('patient1', 'patient2@email.com', 'pass123', 'patient')
        self.assertFalse(success)
        self.assertIn('already exists', message)
    
    # ============ DOCTOR REGISTRATION TESTS ============
    
    def test_doctor_registration_valid(self):
        """Test valid doctor registration"""
        success, message = register_user('doctor1', 'doctor1@hospital.com', 'pass123', 'doctor')
        self.assertTrue(success, message)
    
    def test_doctor_registration_short_username(self):
        """Test doctor registration with username too short"""
        success, message = register_user('ab', 'doctor1@hospital.com', 'pass123', 'doctor')
        self.assertFalse(success)
    
    def test_doctor_registration_duplicate_username(self):
        """Test doctor registration with duplicate username"""
        register_user('doctor1', 'doctor1@hospital.com', 'pass123', 'doctor')
        success, message = register_user('doctor1', 'doctor2@hospital.com', 'pass123', 'doctor')
        self.assertFalse(success)
    
    # ============ LOGIN TESTS ============
    
    def test_login_patient_success(self):
        """Test successful patient login"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        success, user_info = login_user('patient1', 'pass123')
        self.assertTrue(success)
        self.assertEqual(user_info['role'], 'patient')
        self.assertIn('user_id', user_info)
    
    def test_login_doctor_success(self):
        """Test successful doctor login"""
        register_user('doctor1', 'doctor1@hospital.com', 'pass123', 'doctor')
        success, user_info = login_user('doctor1', 'pass123')
        self.assertTrue(success)
        self.assertEqual(user_info['role'], 'doctor')
        self.assertIn('user_id', user_info)
    
    def test_login_invalid_password(self):
        """Test login with wrong password"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        success, user_info = login_user('patient1', 'wrongpass')
        self.assertFalse(success)
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent username"""
        success, user_info = login_user('nonexistent', 'pass123')
        self.assertFalse(success)
    
    # ============ RISK CATEGORY TESTS ============
    
    def test_risk_category_low(self):
        """Test low risk category"""
        risk_level, color = get_risk_category(0.2)
        self.assertEqual(risk_level, 'LOW')
        self.assertEqual(color, '#27ae60')
    
    def test_risk_category_medium(self):
        """Test medium risk category"""
        risk_level, color = get_risk_category(0.5)
        self.assertEqual(risk_level, 'MEDIUM')
        self.assertEqual(color, '#f39c12')
    
    def test_risk_category_high(self):
        """Test high risk category"""
        risk_level, color = get_risk_category(0.8)
        self.assertEqual(risk_level, 'HIGH')
        self.assertEqual(color, '#e74c3c')
    
    # ============ PREDICTION STORAGE TESTS ============
    
    def test_save_prediction_patient(self):
        """Test saving prediction for patient"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        _, user_info = login_user('patient1', 'pass123')
        user_id = user_info['user_id']
        
        features = {
            'age': 50, 'anaemia': 0, 'creatinine_phosphokinase': 500,
            'diabetes': 1, 'ejection_fraction': 38, 'high_blood_pressure': 1,
            'platelets': 250000, 'serum_creatinine': 1.2, 'serum_sodium': 137,
            'sex': 1, 'smoking': 1, 'time': 100
        }
        result = save_prediction(user_id, features, 0.45, 'MEDIUM')
        self.assertTrue(result)
    
    def test_get_patient_predictions(self):
        """Test retrieving patient predictions"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        _, user_info = login_user('patient1', 'pass123')
        user_id = user_info['user_id']
        
        features1 = {
            'age': 50, 'anaemia': 0, 'creatinine_phosphokinase': 500,
            'diabetes': 1, 'ejection_fraction': 38, 'high_blood_pressure': 1,
            'platelets': 250000, 'serum_creatinine': 1.2, 'serum_sodium': 137,
            'sex': 1, 'smoking': 1, 'time': 100
        }
        save_prediction(user_id, features1, 0.25, 'LOW')
        
        features2 = {
            'age': 60, 'anaemia': 1, 'creatinine_phosphokinase': 600,
            'diabetes': 1, 'ejection_fraction': 25, 'high_blood_pressure': 1,
            'platelets': 300000, 'serum_creatinine': 1.5, 'serum_sodium': 135,
            'sex': 0, 'smoking': 0, 'time': 150
        }
        save_prediction(user_id, features2, 0.75, 'HIGH')
        
        predictions = get_patient_predictions(user_id)
        self.assertEqual(len(predictions), 2)
        self.assertEqual(predictions[0]['risk_category'], 'LOW')
        self.assertEqual(predictions[1]['risk_category'], 'HIGH')
    
    # ============ DOCTOR QUERY TESTS ============
    
    def test_get_all_patients(self):
        """Test getting all patients"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        register_user('patient2', 'patient2@email.com', 'pass123', 'patient')
        
        patients = get_all_patients()
        self.assertEqual(len(patients), 2)
        usernames = [p['username'] for p in patients]
        self.assertIn('patient1', usernames)
        self.assertIn('patient2', usernames)
    
    def test_get_all_patients_with_prediction_counts(self):
        """Test getting patients with prediction counts"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        _, user_info = login_user('patient1', 'pass123')
        user_id = user_info['user_id']
        
        features = {
            'age': 50, 'anaemia': 0, 'creatinine_phosphokinase': 500,
            'diabetes': 1, 'ejection_fraction': 38, 'high_blood_pressure': 1,
            'platelets': 250000, 'serum_creatinine': 1.2, 'serum_sodium': 137,
            'sex': 1, 'smoking': 1, 'time': 100
        }
        save_prediction(user_id, features, 0.3, 'LOW')
        save_prediction(user_id, features, 0.5, 'MEDIUM')
        
        patients = get_all_patients()
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0]['prediction_count'], 2)
    
    def test_get_patient_with_predictions(self):
        """Test getting detailed patient view"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        _, user_info = login_user('patient1', 'pass123')
        user_id = user_info['user_id']
        
        features = {
            'age': 50, 'anaemia': 0, 'creatinine_phosphokinase': 500,
            'diabetes': 1, 'ejection_fraction': 38, 'high_blood_pressure': 1,
            'platelets': 250000, 'serum_creatinine': 1.2, 'serum_sodium': 137,
            'sex': 1, 'smoking': 1, 'time': 100
        }
        save_prediction(user_id, features, 0.45, 'MEDIUM')
        
        patient_data = get_patient_with_predictions(user_id)
        self.assertIsNotNone(patient_data)
        self.assertEqual(patient_data['username'], 'patient1')
        self.assertEqual(len(patient_data['predictions']), 1)
    
    def test_patient_data_isolation(self):
        """Test that patients can't access other patients data"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        register_user('patient2', 'patient2@email.com', 'pass123', 'patient')
        _, p1_info = login_user('patient1', 'pass123')
        _, p2_info = login_user('patient2', 'pass123')
        
        features = {
            'age': 50, 'anaemia': 0, 'creatinine_phosphokinase': 500,
            'diabetes': 1, 'ejection_fraction': 38, 'high_blood_pressure': 1,
            'platelets': 250000, 'serum_creatinine': 1.2, 'serum_sodium': 137,
            'sex': 1, 'smoking': 1, 'time': 100
        }
        save_prediction(p1_info['user_id'], features, 0.3, 'LOW')
        
        p1_predictions = get_patient_predictions(p1_info['user_id'])
        p2_predictions = get_patient_predictions(p2_info['user_id'])
        
        self.assertEqual(len(p1_predictions), 1)
        self.assertEqual(len(p2_predictions), 0)
    
    def test_user_roles(self):
        """Test that roles are assigned correctly"""
        register_user('patient1', 'patient1@email.com', 'pass123', 'patient')
        register_user('doctor1', 'doctor1@hospital.com', 'pass123', 'doctor')
        
        _, p_info = login_user('patient1', 'pass123')
        _, d_info = login_user('doctor1', 'pass123')
        
        self.assertEqual(p_info['role'], 'patient')
        self.assertEqual(d_info['role'], 'doctor')


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestMultiRoleSystem))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
