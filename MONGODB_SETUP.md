# MongoDB Atlas Setup Guide - CAD Prediction System

This guide explains how to convert your Flask CAD Prediction System from SQLite to MongoDB Atlas for centralized cloud database support.

---

## 📋 Overview

**Benefits:**
- ✅ Multi-user access from different machines
- ✅ Global data persistence
- ✅ No local database synchronization issues
- ✅ Secure cloud-hosted database
- ✅ Scalable for production use

**Collections Structure:**
- `users`: User accounts (patients & doctors)
- `assessments`: CAD prediction results
- `patient_profiles`: Patient-specific data
- `doctor_profiles`: Doctor-specific data

---

## 🔧 Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pymongo==4.6.0` - MongoDB Python driver
- `python-dotenv==1.0.0` - Environment variable management

---

## 🌐 Step 2: Create MongoDB Atlas Account

1. **Go to MongoDB Atlas**: https://www.mongodb.com/cloud/atlas
2. **Sign Up**: Create a free account
3. **Create Organization** (or use default)
4. **Create Project**:
   - Click "Create Project"
   - Name: `CAD_Prediction` (or your choice)
   - Click "Create Project"

---

## 🔑 Step 3: Create a Cluster

1. **Build a Cluster**:
   - Select "M0 Sandbox" (FREE - perfect for academic projects)
   - Cloud Provider: AWS
   - Region: Choose closest to you
   - Cluster Name: `cad-cluster`
   - Click "Create Deployment"

2. **Wait for Cluster Creation** (2-5 minutes)

---

## 👤 Step 4: Create Database User

1. **Navigate to**: Database Access (left sidebar)
2. **Add New Database User**:
   - Authentication Method: **Password**
   - Username: `cad_user` (or your choice)
   - Password: `Generate Secure Password` (copy it!)
   - Built-in Role: **Atlas Admin** (for development)
   - Click "Add User"

**Save your credentials securely!**

---

## 🔓 Step 5: Configure Network Access

1. **Navigate to**: Network Access (left sidebar)
2. **Add IP Address**:
   - Click "Add IP Address"
   - Select "Allow Access from Anywhere"
   - CIDR: `0.0.0.0/0`
   - Click "Confirm"

⚠️ **Note**: For production, use specific IP addresses.

---

## 📝 Step 6: Get Connection String

1. **Go to Clusters** → Click "Connect"
2. **Choose Connection Method**: "Drivers"
3. **Select Driver**: Python 3.6+
4. **Copy Connection String**:
   ```
   mongodb+srv://cad_user:<password>@cad-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

**Replace:**
- `<password>` with your database user password
- Keep everything else as-is

---

## 🛠️ Step 7: Configuration

### Option A: Using Environment Variables (Recommended)

Create a `.env` file in the project root:

```bash
# .env file
MONGODB_URL=mongodb+srv://cad_user:your_password@cad-cluster.xxxxx.mongodb.net/cad_prediction_db?retryWrites=true&w=majority
SECRET_KEY=your-secret-key-change-in-production
```

### Option B: Direct Configuration

Edit `app_mongodb.py` line ~78:

```python
MONGODB_URL = 'mongodb+srv://cad_user:your_password@cad-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority'
```

---

## ✅ Step 8: Activate MongoDB Version

### Replace Old SQLite Version:

```bash
# Option 1: Rename old file
cd backend
mv app.py app_sqlite.py
mv app_mongodb.py app.py

# Option 2: Edit Flask run command
# Use: python -m flask run --app app_mongodb
```

---

## 🚀 Step 9: Run Application

```bash
cd backend
python app.py
```

You should see:
```
✓ MongoDB Atlas connection successful
✓ Connected to database: cad_prediction_db
Running on: http://127.0.0.1:5000
```

---

## 📊 Database Structure

### Users Collection
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  password_hash: String,
  role: "patient" | "doctor",
  created_at: DateTime,
  updated_at: DateTime
}
```

### Assessments Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,  // Reference to users
  age: Number,
  anaemia: Number,
  creatinine_phosphokinase: Number,
  diabetes: Number,
  ejection_fraction: Number,
  high_blood_pressure: Number,
  platelets: Number,
  serum_creatinine: Number,
  serum_sodium: Number,
  sex: Number,
  smoking: Number,
  time: Number,
  probability: Number,
  risk_category: String,
  created_at: DateTime
}
```

### Patient Profiles Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  age: Number,
  gender: String,
  medical_history: Array,
  created_at: DateTime
}
```

### Doctor Profiles Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  license_number: String,
  specialization: String,
  hospital: String,
  created_at: DateTime
}
```

---

## 🧪 Testing

### 1. Test Connection
```bash
python
>>> from pymongo import MongoClient
>>> client = MongoClient('your-connection-string')
>>> client.admin.command('ping')
{'ok': 1.0}  # Success!
```

### 2. Test Registration
1. Visit: `http://127.0.0.1:5000/register_patient`
2. Register test patient: `testpatient / testpass123`
3. Check MongoDB Atlas UI → Collections

### 3. Test Login
1. Visit: `http://127.0.0.1:5000/login`
2. Login with credentials above
3. Make a prediction
4. Verify data in MongoDB

### 4. Test Multi-User
- Open app in different browsers/machines
- Register different users
- Verify all users see shared global data

---

## 🔒 Security Best Practices

### For Development:
```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=dev-key-only-for-development
```

### For Production:
```python
# Use environment variables, never hardcode
MONGODB_URL = os.environ.get('MONGODB_URL')
if not MONGODB_URL:
    raise ValueError("MONGODB_URL not set in environment")

# Use specific IP whitelist instead of 0.0.0.0/0
# Rotate passwords regularly
# Enable MFA on MongoDB Atlas account
# Use VPC peering for additional security
```

---

## 🆘 Troubleshooting

### Connection Refused
```
Error: [Errno 111] Connection refused
```
**Solution:**
- Check internet connection
- Verify MONGODB_URL is correct
- Ensure IP whitelist includes your address
- Wait longer for Atlas cluster startup

### Authentication Failed
```
Error: authentication failed
```
**Solution:**
- Verify password has no special characters (use URL encoding)
- Example: password `p@ss!` → URL encode as `p%40ss%21`
- Check username in connection string

### Database Not Found
```
Error: namespace does not exist
```
**Solution:**
- First insert will auto-create collection
- Collections created on first write, not on app start

### Duplicate Key Error
```
DuplicateKeyError: E11000
```
**Solution:**
- Each username must be unique
- If testing, delete old test users from MongoDB Atlas UI

---

## 📊 Monitoring

### Check Data in MongoDB Atlas UI:

1. **Go to**: Clusters → Browse Collections
2. **Select**:
   - Database: `cad_prediction_db`
   - Collection: `users` or `assessments`
3. **View Documents**: Click to expand and inspect

### Real-time Metrics:
- Go to: Clusters → Metrics
- Watch: Connections, Operations, Storage

---

## 🔄 Migration from SQLite

If you have existing SQLite data:

```python
# Script to migrate SQLite → MongoDB (optional)
import sqlite3
from pymongo import MongoClient

# Read from SQLite
conn = sqlite3.connect('cad_system.db')
cursor = conn.cursor()

# Connect to MongoDB
mongo_client = MongoClient('mongodb+srv://...')
db = mongo_client['cad_prediction_db']

# Migrate users
cursor.execute('SELECT * FROM users')
for row in cursor.fetchall():
    db['users'].insert_one({
        'username': row[1],
        'email': row[2],
        'password_hash': row[3],
        'role': row[4],
        'created_at': row[5]
    })

print("Migration complete!")
```

---

## 📱 Deployment Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster deployed (M0 or higher)
- [ ] Database user created
- [ ] Network access configured
- [ ] Connection string copied
- [ ] `.env` file created with MONGODB_URL
- [ ] `requirements.txt` updated
- [ ] Old app.py renamed to app_sqlite.py
- [ ] `app_mongodb.py` renamed to `app.py`
- [ ] App runs without connection errors
- [ ] Can register and login
- [ ] Can make predictions
- [ ] Data visible in MongoDB Atlas UI

---

## 📚 Additional Resources

- **MongoDB Atlas**: https://docs.atlas.mongodb.com/
- **PyMongo Guide**: https://pymongo.readthedocs.io/
- **Connection String Format**: https://docs.mongodb.com/manual/reference/connection-string/
- **MongoDB Query Language**: https://docs.mongodb.com/manual/crud/

---

## ❓ FAQ

**Q: Is M0 (Free) tier sufficient?**
A: Yes! For academic projects and testing. Includes 512MB storage, sufficient for thousands of assessments.

**Q: Can I migrate from SQLite to MongoDB later?**
A: Yes, use the migration script example in this guide.

**Q: What happens if MongoDB Atlas is down?**
A: App will fail to connect. Use try-except in init_mongodb() for graceful error handling.

**Q: Can multiple instances of the app share the same database?**
A: Yes! That's the entire benefit. Deploy on multiple machines pointing to same MongoDB.

**Q: How do I backup data?**
A: MongoDB Atlas provides automated daily backups in free tier. Export CSV via doctor dashboard.

---

## 🎯 Next Steps

1. Complete setup steps above
2. Test with multiple users
3. Verify data persistence
4. Deploy on multiple machines
5. Monitor metrics in Atlas dashboard

---

**Questions?** Check the troubleshooting section or Mongolia Atlas documentation.
