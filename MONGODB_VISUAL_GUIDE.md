# MongoDB Atlas Migration - Visual Guide

## 🔄 System Architecture Comparison

### BEFORE: SQLite (Local Only)

```
        PC-A                        PC-B                      PC-C
    ┌─────────────┐             ┌─────────────┐           ┌─────────────┐
    │   Patient   │             │   Patient   │           │   Patient   │
    │   Browser   │             │   Browser   │           │   Browser   │
    └──────┬──────┘             └──────┬──────┘           └──────┬──────┘
           │                           │                        │
    ┌──────▼──────────────┐     ┌─────▼────────────────┐ ┌────▼──────────┐
    │   Flask App         │     │   Flask App          │ │  Flask App    │
    │ (app.py - SQLite)   │     │ (app.py - SQLite)    │ │ (app.py)      │
    └──────┬──────────────┘     └─────┬────────────────┘ └────┬──────────┘
           │                           │                      │
    ┌──────▼──────┐           ┌────────▼────┐        ┌────────▼────┐
    │cad_system.db│           │cad_system.db │       │cad_system.db │
    │(Local File) │           │ (Local File) │       │ (Local File) │
    └─────────────┘           └──────────────┘       └─────────────┘
    
❌ Problem: Data NOT shared
   - User registers on PC-A
   - PC-B has no access
   - Each PC has separate database
```

### AFTER: MongoDB Atlas (Global, Cloud-Connected)

```
        PC-A                        PC-B                      PC-C
    ┌─────────────┐             ┌─────────────┐           ┌─────────────┐
    │   Patient   │             │   Patient   │           │   Patient   │
    │   Browser   │             │   Browser   │           │   Browser   │
    └──────┬──────┘             └──────┬──────┘           └──────┬──────┘
           │                           │                        │
    ┌──────▼──────────────┐     ┌─────▼────────────────┐ ┌────▼──────────┐
    │   Flask App         │     │   Flask App          │ │  Flask App    │
    │(app_mongodb.py)     │     │(app_mongodb.py)      │ │(app_mongodb.py)
    └──────┬──────────────┘     └─────┬────────────────┘ └────┬──────────┘
           │                           │                      │
           │ INTERNET                  │ INTERNET             │ INTERNET
           │ (pymongo)                 │ (pymongo)            │ (pymongo)
           │                           │                      │
           │   ┌──────────────────────▼──────────────────────▼──┐
           └──▶│   MongoDB Atlas (Cloud)                        │
               │   cad_prediction_db                            │
               │   ┌─────────────────────────────────────┐      │
               │   │ collections:                        │      │
               │   │ ✓ users                            │      │
               │   │ ✓ assessments                       │      │
               │   │ ✓ patient_profiles                 │      │
               │   │ ✓ doctor_profiles                  │      │
               │   └─────────────────────────────────────┘      │
               │   Backups: Automatic Daily                     │
               │   Uptime: 99.5% SLA                            │
               └────────────────────────────────────────────────┘

✅ Solution: Data SHARED GLOBALLY
   - User registers on PC-A (also in cloud)
   - PC-B logs in with same credentials (gets data from cloud)
   - PC-C sees all assessments from both PCs
   - All users work with same database!
```

---

## 🗂️ Collection Structure

### users Collection
```javascript
{
  "_id": ObjectId,
  "username": "john_doe",          // Unique
  "email": "john@example.com",     // Unique
  "password_hash": "pbkdf2:...",   // Hashed!
  "role": "patient",               // "patient" or "doctor"
  "created_at": ISODate("2024-02-06T10:30:00Z"),
  "updated_at": ISODate("2024-02-06T10:30:00Z")
}
```

### assessments Collection
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,             // Links to users._id
  "age": 65.0,
  "anaemia": 0,
  "creatinine_phosphokinase": 250.0,
  "diabetes": 1,
  "ejection_fraction": 40.0,
  "high_blood_pressure": 0,
  "platelets": 350000.0,
  "serum_creatinine": 1.2,
  "serum_sodium": 140.0,
  "sex": 1,
  "smoking": 0,
  "time": 130.0,
  "probability": 0.75,             // ML prediction
  "risk_category": "HIGH",         // LOW, MEDIUM, HIGH
  "created_at": ISODate("2024-02-06T11:00:00Z")
}
```

### patient_profiles Collection
```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,             // Links to users._id
  "age": 65,
  "gender": "M",
  "medical_history": ["Hypertension (2015)", "Diabetes (2018)"],
  "created_at": ISODate("2024-02-06T10:30:00Z")
}
```

---

## 🔐 Authentication Flow

### Registration Flow
```
┌─────────────────────┐
│ User fills form     │
│ - username          │
│ - email             │
│ - password          │
│ - role (patient)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Input Validation                │
│ ✓ username ≥ 3 chars           │
│ ✓ password ≥ 6 chars           │
│ ✓ role ∈ [patient, doctor]     │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Check Uniqueness                │
│ db.users.find({username})       │
│ ✓ Not exists → Continue         │
│ ✗ Exists → Error "Already used" │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Hash Password                   │
│ hash = generate_password_hash() │
│ Result: pbkdf2:sha256:600000$..│
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Insert into MongoDB             │
│ db.users.insert_one({           │
│   username,                     │
│   email,                        │
│   password_hash,  ← NOT plain!  │
│   role,                         │
│   created_at                    │
│ })                              │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Create Role Profile             │
│ db.patient_profiles.insert_one()│
│ db.doctor_profiles.insert_one() │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│ Redirect to Login               │
│ "Registration successful"       │
└─────────────────────────────────┘
```

### Login Flow
```
┌──────────────────────────┐
│ User enters credentials  │
│ - username               │
│ - password               │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Find user by username            │
│ db.users.find_one({username})    │
│ ✓ Found → Continue               │
│ ✗ Not found → Error "User not ok │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Verify Password Hash             │
│ check_password_hash(stored, user)│
│ ✓ Valid → Continue               │
│ ✗ Invalid → Error "Bad password" │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Create Session                   │
│ session['user_id'] = user._id    │
│ session['role'] = user.role      │
│ session['username'] = user...    │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Redirect Based on Role           │
│ if role == 'doctor':             │
│   → /doctor/dashboard            │
│ else:                            │
│   → /patient/dashboard           │
└──────────────────────────────────┘
```

---

## 🔄 Data Flow: Making a Prediction

```
Patient fills form
│
├─ age: 65
├─ anaemia: 0
├─ diabetes: 1
├─ ejection_fraction: 40
└─ ... (other features)
│
▼
Flask collects data
│
▼
Scale features using scaler
│
▼
ML Model makes prediction
│
├─ probability: 0.75 (as decimal)
└─ Returns binary prediction
│
▼
Risk Categorization
│
├─ probability < 0.33 → LOW (green)
├─ 0.33 ≤ prob < 0.67 → MEDIUM (orange)
└─ probability ≥ 0.67 → HIGH (red)
│
▼
Save Assessment
│
db.assessments.insert_one({
  user_id: ObjectId(...),
  age, anaemia, diabetes, ...,
  probability,
  risk_category,
  created_at
})
│
▼
Display Result to Patient
│
├─ probability: 75%
├─ risk_category: HIGH (red)
├─ recommendation: "See cardiologist immediately"
└─ assessment saved globally
│
▼
Doctor sees it instantly
│
└─ /doctor/dashboard shows new assessment
```

---

## 📊 Query Examples

### Find User by Username
```javascript
db.users.find_one({username: "john_doe"})
↓
{
  _id: ObjectId(...),
  username: "john_doe",
  email: "john@...",
  password_hash: "pbkdf2:...",
  role: "patient",
  created_at: ...
}
```

### Get All Assessments for Patient
```javascript
db.assessments.find({user_id: ObjectId(...)}).sort({created_at: -1})
↓
[
  {_id, user_id, age, anaemia, ..., probability, risk_category, created_at},
  {_id, user_id, age, anaemia, ..., probability, risk_category, created_at},
  ...
]
```

### Count Assessments by Risk
```javascript
db.assessments.aggregate([
  {$group: {_id: "$risk_category", count: {$sum: 1}}}
])
↓
[
  {_id: "LOW", count: 25},
  {_id: "MEDIUM", count: 40},
  {_id: "HIGH", count: 15}
]
```

---

## 🗺️ File Structure

```
CAD_Prediction_System/
│
├── 📄 MONGODB_README.md                    ← START HERE
├── 📄 QUICK_START_MONGODB.md               ← 5-min setup
├── 📄 MONGODB_SETUP.md                     ← Complete guide
├── 📄 MONGODB_TECHNICAL_DOCS.md            ← Technical ref
├── 📄 MONGODB_INTEGRATION_GUIDE.md         ← Integration
├── 📄 MONGODB_MIGRATION_SUMMARY.md         ← Summary
├── 📄 .env.example                         ← Config template
│
├── backend/
│   ├── 📄 app.py                           ✅ Original (SQLite)
│   ├── 📄 app_mongodb.py                   ✅ NEW (MongoDB)
│   ├── 📄 app_sqlite_backup.py             (backup)
│   ├── 📄 test_mongodb.py                  ✅ NEW (8 tests)
│   │
│   ├── ml_model.py
│   ├── model.py
│   ├── best_cad_model.pkl
│   ├── scaler.pkl
│   ├── feature_importance.csv
│   ├── predictions.csv
│   └── __pycache__
│
├── frontend/
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── predict.html
│       ├── patient_dashboard.html
│       ├── doctor_dashboard.html
│       └── ...
│
├── dataset/
│   └── heart.csv
│
⚠️ NEW: requirements.txt (pymongo added)

```

---

## 🎯 Feature Comparison Matrix

| Feature | SQLite (app.py) | MongoDB (app_mongodb.py) |
|---------|-----------------|--------------------------|
| **Multi-PC Access** | ❌ No | ✅ Yes |
| **Data Sharing** | ❌ Manual | ✅ Automatic |
| **Cloud Hosted** | ❌ No | ✅ Yes |
| **Scalability** | 🟡 Limited | ✅ High |
| **Backup** | ❌ Manual | ✅ Automatic |
| **Uptime SLA** | 🟡 Depends | ✅ 99.5% |
| **Setup Time** | 5 min | 5 min |
| **Cost** | Free | Free (M0) |
| **Authentication** | ✅ Yes | ✅ Yes |
| **Password Hashing** | ✅ Yes | ✅ Yes |
| **Role-Based Access** | ✅ Yes | ✅ Yes |
| **CSV Export** | ✅ Yes | ✅ Yes |
| **Code Compatibility** | 100% | 95%+ |

---

## ⏱️ Setup Timeline

```
Start
 │
 ├─ 1 min     Create MongoDB Atlas account
 │
 ├─ 2 min     Create cluster (M0 Sandbox)
 │
 ├─ 1 min     Create database user
 │
 ├─ 1 min     Get connection string
 │
 ├─ 0.5 min   Create .env file
 │
 ├─ 1 min     Install dependencies (pip)
 │
 ├─ 1 min     Run tests (test_mongodb.py)
 │
 ├─ 0.5 min   Activate MongoDB (move files)
 │
 └─ 1 min     Start app
    ↓
   Ready! 🎉
   
   Total: ~9 minutes
```

---

## 🚀 Deployment Scenarios

### Scenario 1: Same Laptop During Development
```
Developer works on one laptop
┌──────────────────────┐
│ Laptop - Flask App   │ ─────┐
│          SQLite DB   │      │
└──────────────────────┘      │
                              │ Choose one
                              │ at a time
                         MongoDB Cloud
                              │
Result: Easy switching during dev ✅
```

### Scenario 2: Demo on Multiple Machines
```
Evaluator A              Evaluator B              Evaluator C
│                        │                        │
├─ PC-1                  ├─ PC-2                  ├─ PC-3
│  Firefox              │  Chrome                │  IE
│  localhost:5000       │  192.168.x.x:5000     │  192.168.x.y:5000
│                        │                        │
└────┬────────┬──────────┼────────┬───────────────┼────────┬──────┘
     │        │          │        │               │        │
     └────────┴────────┬─┴────────┴───────────────┴────────┘
                       │
              MongoDB Atlas (Cloud)
                       │
Result: All 3 PCs access SAME database!
        Register on PC-1 → Login on PC-2, see same data ✅
```

### Scenario 3: Final Paper Submission
```
Project Demo:
─────────────
1. Show Flask app running
2. Register patient on PC-A
3. Make prediction
4. Open PC-B
5. Login with same credentials
6. See prediction from PC-A ✅
7. Show data in MongoDB Atlas UI ✅

Evaluator Notes:
───────────────
"Multi-machine database integration" ✅
"Cloud technology" ✅
"Professional architecture" ✅
"Secure authentication" ✅
```

---

## ✅ Verification Steps

### After Setup, Verify:

```
1. Test Connection
   python test_mongodb.py
   Expected: ✅ Passed: 8/8

2. Start Application
   python app.py
   Expected: ✓ MongoDB Atlas connection successful

3. Register User
   username: testuser
   password: testpass123
   Expected: Redirects to login

4. Login
   username: testuser
   password: testpass123
   Expected: Shows patient dashboard

5. Make Prediction
   Fill form → Submit
   Expected: Shows result with risk category

6. Verify in MongoDB
   Atlas UI → Collections → assessments
   Expected: Your prediction is there!

7. Multi-Machine Test
   Different PC → Login with testuser
   Expected: See same dashboard & predictions!
```

---

## 🎓 Academic Project Benefits

**What Professors See:**
- ✅ Cloud database setup (MongoDB Atlas)
- ✅ Multi-machine data synchronization
- ✅ Secure authentication (password hashing)
- ✅ Professional architecture
- ✅ Complete documentation
- ✅ Automated testing
- ✅ Error handling
- ✅ Scalable design

**Impressive for Demos:**
- Show registration on one PC
- Login from another PC
- See SAME data (cloud synchronization!)
- Show data in MongoDB Atlas UI
- Explain the architecture

---

## 🔍 Key Differences at a Glance

| Aspect | SQLite | MongoDB |
|--------|--------|---------|
| File Location | cad_system.db (local) | Cloud (128.x.x.x) |
| Access From PC-B | ❌ No access | ✅ Full access |
| Data Persistence | Per-machine | Global |
| Driver | sqlite3 (built-in) | pymongo (external) |
| Collections | Tables (sql_alchemy like) | BSON documents |
| Indexes | CREATE INDEX | create_index() |
| Queries | SQL WHERE clauses | MongoDB find() |
| Connection | Local file path | Connection string |

---

## 📞 Quick Reference

**To Resume MongoDB Development:**
1. `pip install -r requirements.txt` (one-time)
2. Create `.env` with MONGODB_URL
3. `cd backend`
4. `python app_mongodb.py`

**To Test:**
1. `cd backend`
2. `python test_mongodb.py`

**To Switch Back:**
1. `move app.py app_mongodb_backup.py`
2. `move app_sqlite_backup.py app.py`
3. `python app.py`

---

This visual guide helps you understand the architecture, data flow, and benefits of MongoDB Atlas for your CAD Prediction System!
