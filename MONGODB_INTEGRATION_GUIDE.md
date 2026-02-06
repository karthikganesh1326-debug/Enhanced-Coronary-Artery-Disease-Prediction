# MongoDB Integration Guide - CAD Prediction System

## 📋 Overview

Your CAD Prediction System has been enhanced with MongoDB Atlas support. This guide walks you through the activation and verification process.

## 🔄 How It Works

```
┌─ Original Version (SQLite) ──────┐
│  Backend: app.py                 │
│  Database: cad_system.db (local) │
│  Issue: Only works on one PC     │
└──────────────────────────────────┘
                ⬇️ Migration
┌─ New Version (MongoDB) ──────────────────┐
│  Backend: app_mongodb.py                 │
│  Database: MongoDB Atlas (cloud)         │
│  Benefit: Works across all PCs globally  │
└──────────────────────────────────────────┘
```

## 📁 Files Created/Modified

### New Files:
- **`backend/app_mongodb.py`** - MongoDB-based Flask application
- **`backend/test_mongodb.py`** - Automated testing script
- **`MONGODB_SETUP.md`** - Complete setup instructions
- **`QUICK_START_MONGODB.md`** - Quick reference guide
- **`MONGODB_TECHNICAL_DOCS.md`** - Technical documentation
- **`.env.example`** - Example configuration file

### Modified Files:
- **`requirements.txt`** - Added pymongo and python-dotenv

### Original Preserved:
- **`backend/app.py`** - Original SQLite version (unchanged)

---

## ⚡ Installation Steps

### Step 1: Install New Dependencies
```bash
pip install -r requirements.txt
```

This adds:
- `pymongo==4.6.0` - MongoDB driver
- `python-dotenv==1.0.0` - Environment variable loader

### Step 2: Setup MongoDB Atlas

Follow **QUICK_START_MONGODB.md** OR **MONGODB_SETUP.md** for:
1. Create free MongoDB Atlas account
2. Create cluster (M0 Sandbox - free)
3. Create database user
4. Get connection string

### Step 3: Create Configuration File

Create `.env` file in project root:

```
MONGODB_URL=mongodb+srv://cad_user:YourPassword@your-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
SECRET_KEY=your-secret-key-change-in-production
```

**Get your connection string from MongoDB Atlas:**
- Clusters → Connect → Drivers → Copy connection string
- Replace `<password>` with actual database user password

### Step 4: Test Configuration

Run the test suite:
```bash
cd backend
python test_mongodb.py
```

Expected output:
```
✅ Passed: 8/8
🎉 All tests passed! MongoDB is properly configured.
```

If tests fail, check:
- Internet connection
- MongoDB Atlas cluster is running
- Connection string is correct
- IP whitelist includes your IP

### Step 5: Activate MongoDB Version

Choose one approach:

**Option A: Replace app.py (Recommended)**
```bash
cd backend
# Backup original
ren app.py app_sqlite_backup.py

# Activate MongoDB version
ren app_mongodb.py app.py
```

**Option B: Keep Both (Advanced)**
```bash
# Don't rename, specify on run:
python -m flask run --app app_mongodb
```

### Step 6: Run Application

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

## ✅ Verification Checklist

- [ ] MongoDB Atlas account created
- [ ] Cluster deployed and running
- [ ] Database user created
- [ ] Network access configured (IP whitelist)
- [ ] Connection string copied
- [ ] `.env` file created with MONGODB_URL
- [ ] `test_mongodb.py` passes all tests
- [ ] App starts without errors
- [ ] Can register new patient
- [ ] Can login with credentials
- [ ] Can make prediction
- [ ] Data appears in MongoDB Atlas UI

## 🧪 Manual Testing

### Test User Registration

1. Start app: `python app.py`
2. Visit: http://127.0.0.1:5000/register_patient
3. Register: `testuser1` / `testpass123`
4. Should redirect to login page

### Test Login

1. Visit: http://127.0.0.1:5000/login
2. Login: `testuser1` / `testpass123`
3. Should show patient dashboard

### Test Prediction

1. Click "Make Prediction"
2. Fill medical features
3. Submit form
4. Should show result with risk category

### Verify Data in MongoDB

1. Open MongoDB Atlas: https://cloud.mongodb.com
2. Go to: Clusters → Collections
3. Select: `cad_prediction_db`
4. You should see:
   - `users` collection with your test user
   - `assessments` collection with your prediction

### Test Multi-Machine Access

1. On Machine A:
   - Register: `patient_a` / `password123`
   - Make prediction
   
2. On Machine B (different computer):
   - Login: `patient_a` / `password123`
   - Click dashboard
   - **Should see same prediction from Machine A! 🎉**

## 🔄 Switching Back to SQLite

If you need to revert:

```bash
cd backend

# Restore original
ren app.py app_mongodb.py
ren app_sqlite_backup.py app.py

# Run
python app.py
```

Your SQLite database (`cad_system.db`) is unchanged.

## 🛠️ Troubleshooting

### "Connection refused"
```
Error: ServerSelectionTimeoutError
```
**Fix:**
- Check internet connection
- Verify MongoDB Atlas cluster is deployed
- Wait a few minutes for cluster startup
- Check MongoDB URL has no typos

### "Authentication failed"
```
Error: authentication failed
```
**Fix:**
- Verify password in connection string
- Check username matches database user
- Ensure special characters are URL-encoded
- Test with simpler password (no special chars)

### "DuplicateKeyError"
```
E11000 duplicate key error collection
```
**Fix:**
- Username already exists
- Try different username in registration
- Or delete user from MongoDB Atlas UI

### Module not found
```
ModuleNotFoundError: No module named 'pymongo'
```
**Fix:**
```bash
pip install pymongo python-dotenv
pip install -r requirements.txt
```

### .env file not loading
```bash
# Verify .env exists in project root
ls -la .env

# Verify it's readable
head .env
```

## 📊 Monitoring

### Check Database Size
```bash
# In MongoDB Atlas UI
Clusters → Metrics → Storage
```

### Check Active Connections
```bash
# In MongoDB Atlas UI
Clusters → Metrics → Connections
```

### View Database Statistics
```python
# In Python terminal
from pymongo import MongoClient
client = MongoClient('your-connection-string')
db = client['cad_prediction_db']
db.command('dbStats')
```

## 🔐 Security Notes

### Development (Testing)
- Connection string with password in `.env` is acceptable
- Use simple credentials
- Only expose to localhost

### Production (Deployment)
- Never commit `.env` to version control
- Use strong passwords
- Restrict IP whitelist (not 0.0.0.0/0)
- Use VPC for database access
- Rotate credentials regularly
- Enable MFA on MongoDB Atlas account
- Use environment variables for secrets

## 📚 Documentation Files

- **QUICK_START_MONGODB.md** - 5-minute setup
- **MONGODB_SETUP.md** - Detailed setup guide
- **MONGODB_TECHNICAL_DOCS.md** - Architecture & queries
- **app_mongodb.py** - Inline code comments
- **test_mongodb.py** - Example database operations

## 🎯 What's Different from SQLite Version

| Feature | SQLite | MongoDB |
|---------|--------|---------|
| Database | Local file | Cloud hosted |
| Multi-PC | ❌ No | ✅ Yes |
| Sharing | Manual sync | Automatic |
| Scalability | Limited | High |
| Backup | Manual | Automatic |
| Uptime | Depends on PC | 99.5% SLA |
| Cost | Free | Free (M0) |

## 🚀 Next Steps

1. **Complete Basic Setup** (from docs)
2. **Run Tests** (`test_mongodb.py`)
3. **Test Locally** (register, login, predict)
4. **Test Multi-Machine** (access from 2 computers)
5. **Deploy** (share with team)
6. **Monitor** (check Atlas dashboard regularly)

## 💡 Tips

1. **Always store connection string in `.env`**, not in code
2. **Keep backup** of SQLite version in case of issues
3. **Test locally first** before deploying to production
4. **Check MongoDB Atlas metrics** monthly
5. **Rotate passwords** every 3 months
6. **Use version control** for code, NOT for credentials

## ❓ FAQ

**Q: Can I use MongoDB AND SQLite together?**
A: Yes, but app only supports one at a time. Choose MongoDB for multi-device.

**Q: Will my SQLite data be lost?**
A: No, `cad_system.db` remains unchanged. You can switch back anytime.

**Q: Is MongoDB M0 (free) sufficient?**
A: Yes, for academic projects and testing. Supports thousands of records.

**Q: Can I migrate existing data?**
A: Yes, use migration script (see MONGODB_TECHNICAL_DOCS.md).

**Q: What if MongoDB Atlas goes down?**
A: App won't function. Use try-except for graceful error handling.

**Q: How do I backup data?**
A: MongoDB Atlas provides automated daily backups. Export CSV via doctor dashboard.

## 📞 Support

For issues:
1. Check troubleshooting section above
2. Review relevant documentation
3. Check MongoDB Atlas dashboard
4. Review inline comments in app_mongodb.py
5. Run test_mongodb.py for diagnostics

---

## ✨ Summary

You now have:
- ✅ MongoDB Atlas cloud database
- ✅ Multi-machine user access
- ✅ Automatic data synchronization
- ✅ Complete documentation
- ✅ Testing tools
- ✅ Working Flask application

**Your CAD Prediction System is now ready for global deployment!** 🎉

---

Last updated: 2024
