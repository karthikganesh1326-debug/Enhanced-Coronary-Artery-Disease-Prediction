# MongoDB Atlas Technical Documentation

## 🏗️ Architecture Overview

```
┌─────────────────────┐
│   Flask App         │
│  (app_mongodb.py)   │
└──────────┬──────────┘
           │ pymongo
           ↓
┌─────────────────────┐
│  MongoDB Atlas      │
│   Cloud Database    │
└──────────┬──────────┘
           │
      ┌────┴────┬────────┬──────────┐
      ↓         ↓        ↓          ↓
   users  assessments  patient_  doctor_
                      profiles  profiles
```

---

## 📚 Database Collections

### 1. **users** Collection

Stores all user accounts (patients and doctors).

**Schema:**
```json
{
  "_id": ObjectId,              // Auto-generated unique ID
  "username": "john_doe",       // Unique username
  "email": "john@example.com",  // Unique email
  "password_hash": "pbkdf2:...", // Werkzeug-hashed password
  "role": "patient",             // "patient" or "doctor"
  "created_at": ISODate(),       // Account creation timestamp
  "updated_at": ISODate()        // Last update timestamp
}
```

**Indexes:**
- `username` (unique): Fast login queries
- `email` (unique): Prevent duplicate registrations

**Operations:**
```python
# Insert (register)
db['users'].insert_one({...})

# Find (login)
db['users'].find_one({'username': 'john_doe'})

# Update (profile change)
db['users'].update_one({'_id': ObjectId(...)}, {'$set': {...}})
```

---

### 2. **assessments** Collection

CAD prediction results for all patients.

**Schema:**
```json
{
  "_id": ObjectId,                      // Unique assessment ID
  "user_id": ObjectId,                  // Foreign key to users._id
  "age": 65.0,                          // Medical feature
  "anaemia": 0,                         // Medical feature (0/1)
  "creatinine_phosphokinase": 250.0,   // Medical feature
  "diabetes": 1,                        // Medical feature (0/1)
  "ejection_fraction": 40.0,            // Medical feature
  "high_blood_pressure": 0,             // Medical feature (0/1)
  "platelets": 350000.0,                // Medical feature
  "serum_creatinine": 1.2,              // Medical feature
  "serum_sodium": 140.0,                // Medical feature
  "sex": 1,                             // Medical feature (0/1)
  "smoking": 0,                         // Medical feature (0/1)
  "time": 130.0,                        // Follow-up time
  "probability": 0.75,                  // ML prediction (0-1)
  "risk_category": "HIGH",              // "LOW", "MEDIUM", "HIGH"
  "created_at": ISODate()               // Assessment timestamp
}
```

**Indexes:**
- `user_id`: Fast queries per patient
- `created_at`: Fast date-range queries

**Operations:**
```python
# Insert (save prediction)
db['assessments'].insert_one({...})

# Find patient assessments
db['assessments'].find({'user_id': ObjectId(...)}).sort('created_at', -1)

# Find filtered assessments (for doctor dashboard)
db['assessments'].find({'risk_category': 'HIGH'}).sort('created_at', -1)

# Count assessments
db['assessments'].count_documents({'user_id': ObjectId(...)})
```

---

### 3. **patient_profiles** Collection

Extended patient information (optional).

**Schema:**
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,        // Reference to users
  "age": 45,
  "gender": "M",
  "medical_history": [
    "Hypertension (2015)",
    "Diabetes (2018)"
  ],
  "created_at": ISODate()
}
```

---

### 4. **doctor_profiles** Collection

Extended doctor information (optional).

**Schema:**
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,        // Reference to users
  "license_number": "LIC123456",
  "specialization": "Cardiology",
  "hospital": "City Medical Center",
  "created_at": ISODate()
}
```

---

## 🔐 Authentication Flow

### Registration

```python
# 1. User submits form
username, email, password, role = request.form

# 2. Validation
if len(username) < 3: return error
if len(password) < 6: return error

# 3. Hash password (Werkzeug)
password_hash = generate_password_hash(password)

# 4. Check duplicates
if db['users'].find_one({'username': username}): return "Username exists"

# 5. Insert user document
user_id = db['users'].insert_one({
    'username': username,
    'email': email,
    'password_hash': password_hash,
    'role': role,
    'created_at': datetime.utcnow()
})

# 6. Create role-specific profile
if role == 'patient':
    db['patient_profiles'].insert_one({
        'user_id': user_id,
        'created_at': datetime.utcnow()
    })

return redirect('/login')
```

### Login

```python
# 1. User submits form
username, password = request.form

# 2. Find user
user = db['users'].find_one({'username': username})
if not user: return "User not found"

# 3. Verify password hash
if not check_password_hash(user['password_hash'], password):
    return "Invalid password"

# 4. Create session
session['user_id'] = str(user['_id'])  # Store as string
session['role'] = user['role']
session['username'] = user['username']

# 5. Redirect based on role
if user['role'] == 'doctor':
    return redirect('/doctor/dashboard')
else:
    return redirect('/patient/dashboard')
```

---

## 🧬 Prediction & Assessment Flow

### Making a Prediction (Patient)

```
1. Patient fills form with medical features
                ↓
2. Flask collects data: age, anaemia, diabetes, etc.
                ↓
3. Call ML model with scaled features
                ↓
4. Get probability (0-1) from model
                ↓
5. Categorize risk: LOW/MEDIUM/HIGH
                ↓
6. Save assessment to MongoDB
   db['assessments'].insert_one({...})
                ↓
7. Display result to patient
                ↓
8. Doctor sees it instantly in dashboard
```

### Doctor Viewing Assessments

```
Doctor Dashboard
    ↓
Query all patients:
    db['users'].find({'role': 'patient'})
    ↓
For each patient, count assessments:
    db['assessments'].count_documents({'user_id': patient_id})
    ↓
Display patient list with counts Click patient:
    ↓
Query all their assessments:
    db['assessments'].find({'user_id': patient_id})
    ↓
Display assessment history with risk colors
```

---

## 🔌 Connection Management

### Initialization

```python
# At app startup
def init_mongodb():
    global mongoclient, db
    
    # Create connection
    mongoclient = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    
    # Test connection with ping
    mongoclient.admin.command('ping')
    
    # Select database
    db = mongoclient['cad_prediction_db']
    
    # Create indexes
    db['users'].create_index('username', unique=True)
    db['users'].create_index('email', unique=True)
    db['assessments'].create_index('user_id')
    db['assessments'].create_index('created_at')
```

### Usage in Routes

```python
# In any route
db = get_db()  # Returns singleton database instance
db['users'].find_one(...)
db['assessments'].insert_one(...)
```

---

## 📊 Query Examples

### Find a User by Username
```python
user = db['users'].find_one({
    'username': 'john_doe'
})
```

### Get All Assessments for a Patient
```python
assessments = db['assessments'].find({
    'user_id': ObjectId('...')
}).sort('created_at', -1)
```

### Count Assessments by Risk Category
```python
high_risk = db['assessments'].count_documents({
    'risk_category': 'HIGH'
})
```

### Find Assessments in Date Range
```python
recent = db['assessments'].find({
    'created_at': {
        '$gte': datetime(2024, 1, 1),
        '$lte': datetime(2024, 12, 31)
    }
}).sort('created_at', -1)
```

### Find Patient by ID and Get Assessments
```python
patient_id = ObjectId('...')
patient = db['users'].find_one({'_id': patient_id})
assessments = db['assessments'].find({
    'user_id': patient_id
}).sort('created_at', -1)
```

---

## 🚀 Performance Considerations

### Indexes
Automatically created:
- `users.username` (unique)
- `users.email` (unique)
- `assessments.user_id`
- `assessments.created_at`

These ensure:
- ✅ Fast login queries
- ✅ Fast assessment retrieval
- ✅ Fast date filtering

### Query Optimization
```python
# ❌ Bad: O(n) - scans all documents
for doc in db['assessments'].find({}):
    if doc['user_id'] == patient_id:
        process(doc)

# ✅ Good: O(log n) - uses index
docs = db['assessments'].find({'user_id': patient_id})
```

---

## 🔄 Data Relationships

```
users (1) ─────────── (many) assessments
  │
  └─────────── (1) patient_profiles
  │
  └─────────── (1) doctor_profiles
```

**Relationships enforced via:**
- `user_id` field in assessments
- `_id` matching in profile collections
- Application logic (NOT MongoDB foreign keys)

---

## 🛡️ Security Implementation

### Password Hashing
```python
from werkzeug.security import generate_password_hash, check_password_hash

# On registration
hash = generate_password_hash(plain_password)
# Result: pbkdf2:sha256:600000$...

# On login
is_valid = check_password_hash(stored_hash, user_input)
# True or False - constant time comparison
```

### Never Store Plain Passwords
```python
# ❌ NEVER
db['users'].insert_one({'password': 'secret123'})

# ✅ ALWAYS
db['users'].insert_one({
    'password_hash': generate_password_hash('secret123')
})
```

### Session Management
```python
# XSS Prevention
session['user_id'] = str(user['_id'])  # String, not ObjectId

# CSRF Prevention
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

---

## 📈 Scalability

### Free Tier Capacity
- **Storage**: 512 MB
- **Connections**: 100 concurrent
- **RAM**: Shared

**Sufficient for:**
- Up to 5,000-10,000 patient assessments
- 100+ concurrent users
- Academic projects

### Upgrade Path
- M2 Tier: 2 GB, $9/month
- M5 Tier: 5 GB, $25/month
- M10+ Tier: Production grade

---

## 🐛 Debugging

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Connection
```python
python
>>> from pymongo import MongoClient
>>> client = MongoClient('mongodb+srv://...')
>>> client.admin.command('ping')
{'ok': 1.0}  # Success!
```

### View Collections
```
Atlas UI → Clusters → Collections → cad_prediction_db
```

### Check Database Stats
```python
db.command('dbStats')
# Returns: storage size, data size, index size, etc.
```

---

## 📋 Migration Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] IP whitelist configured
- [ ] Connection string obtained
- [ ] `.env` file created
- [ ] `requirements.txt` updated
- [ ] `app_mongodb.py` tested
- [ ] All routes working
- [ ] Data persists in cloud
- [ ] Multiple machines can access same data
- [ ] Passwords are hashed
- [ ] Indexes are created

---

## 🎯 Production Considerations

1. **Environment Variables**
   - Never hardcode credentials
   - Use .env file in development
   - Use system environment in production

2. **Connection Pooling**
   - MongoClient handles automatically
   - Reuse single global instance (singleton pattern)

3. **Error Handling**
   - Wrap all DB operations in try-except
   - Log errors without exposing sensitive info
   - Return user-friendly error messages

4. **Backup Strategy**
   - MongoDB Atlas: Automated daily backups
   - CSV Export: Doctor dashboard → Export

5. **Monitoring**
   - Check Atlas dashboard regularly
   - Monitor: connections, operations, storage
   - Set up alerts for issues

---

This document covers all MongoDB operations in the CAD Prediction System. For more details, see MongoDB official documentation.
