# MongoDB Atlas Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create MongoDB Atlas Account
- Visit: https://www.mongodb.com/cloud/atlas
- Sign up (free)
- Create cluster (select "M0 Sandbox" - it's free)

### 3. Create Database User
- In Atlas: Database Access → Add User
- Username: `cad_user`
- Password: (generate secure one)
- Role: Atlas Admin

### 4. Get Connection String
- In Atlas: Clusters → Connect
- Choose: Drivers → Python
- Copy the connection string
- Replace `<password>` with your actual password

### 5. Create `.env` File
In project root (`c:\finalyear project\CAD_Prediction_System\.env`):
```
MONGODB_URL=mongodb+srv://cad_user:your_password@your-cluster.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=your-secret-key
```

### 6. Activate MongoDB Version
```bash
cd backend

# Backup old SQLite version
move app.py app_sqlite_backup.py

# Use MongoDB version
move app_mongodb.py app.py
```

### 7. Run Application
```bash
python app.py
```

**You should see:**
```
✓ MongoDB Atlas connection successful
✓ Connected to database: cad_prediction_db
Running on: http://127.0.0.1:5000
```

### 8. Test It
- Visit: http://127.0.0.1:5000
- Register a patient
- Login
- Make a prediction
- Data is now in MongoDB! 🎉

---

## ✅ Verification

Open MongoDB Atlas in browser:
- Clusters → Collections
- Database: `cad_prediction_db`
- See: `users` and `assessments` collections
- Click to view your test data

---

## 🆘 Common Issues

| Problem | Solution |
|---------|----------|
| Connection refused | Check internet, verify connection string is correct |
| Authentication failed | Ensure `<password>` in URL matches your database user password |
| DuplicateKeyError | Username already exists, use different one |
| Module not found | Run `pip install pymongo python-dotenv` |

---

## 📝 Collection Details

### users
- Stores patient & doctor accounts
- Auto-indexed on username (unique) and email (unique)
- Contains hashed passwords (NEVER plain text)

### assessments
- Stores all CAD predictions for all users
- Links to users via `user_id`
- Auto-indexed on creation date for fast queries

### patient_profiles
- Additional patient data (extendable)

### doctor_profiles  
- Additional doctor data (extendable)

---

## 🔒 Security Tips

**For Development:**
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
SECRET_KEY=dev-key-only
```

**For Production:**
- Use environment variables only (never hardcode)
- Restrict IP addresses in Network Access (not 0.0.0.0/0)
- Use strong passwords
- Rotate credentials regularly

---

## 🔄 Switching Back to SQLite (if needed)

```bash
cd backend
move app.py app_mongodb.py
move app_sqlite_backup.py app.py
```

---

That's it! Your system is now cloud-connected. 🚀
