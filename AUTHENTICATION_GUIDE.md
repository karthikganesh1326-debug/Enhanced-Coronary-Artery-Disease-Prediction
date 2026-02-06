# CAD Prediction System - Authentication Guide

## Overview

The CAD Prediction System now includes a professional authentication layer with user registration, login, and session management. All prediction endpoints are protected and require users to be logged in.

## Features

✅ **User Registration** - New users can create accounts with username and password
✅ **Secure Login** - Password hashing using Werkzeug security
✅ **Session Management** - Flask session-based authentication (24-hour timeout)
✅ **Protected Routes** - Prediction endpoints require authentication
✅ **SQLite Database** - Secure user credential storage
✅ **Responsive UI** - Professional login/register pages with validation

## System Architecture

### Backend (Flask)
```
app.py
├── Authentication Routes
│   ├── /register (GET/POST) - User registration
│   ├── /login (GET/POST) - User login
│   └── /logout (GET) - User logout
├── Protected Routes
│   ├── / (GET) - Home page (requires login)
│   ├── /predict (POST) - Prediction form (requires login)
│   ├── /api/predict (POST) - JSON prediction API (requires login)
│   └── /api/predictions-log (GET) - Predictions log (public)
└── Database
    └── users.db (SQLite)
        └── users table
            ├── id (INTEGER PRIMARY KEY)
            ├── username (TEXT UNIQUE)
            ├── password_hash (TEXT)
            └── created_at (TIMESTAMP)
```

### Frontend (Templates)
```
Templates/
├── base.html - Navigation with auth links
├── login.html - Login form
├── register.html - Registration form
├── index.html - Home/prediction form (protected)
├── result.html - Prediction results
└── about.html - About page (public)
```

## User Flow

### Registration Flow
1. User clicks "Register" in navbar
2. Fills username (≥3 chars) and password (≥6 chars)
3. System validates inputs and checks for username uniqueness
4. Password is securely hashed using werkzeug.security
5. User record stored in SQLite database
6. Redirect to login page

### Login Flow
1. User enters username and password
2. System retrieves hashed password from database
3. Verifies password using werkzeug.security.check_password_hash
4. Creates session cookie if credentials valid
5. User can access protected routes
6. Session expires after 24 hours of inactivity

### Prediction Flow
1. User must be logged in
2. Access home page (/predict form)
3. Submit 12 medical parameters
4. System makes prediction with ML model
5. Results displayed with risk category
6. Prediction logged to CSV with timestamp

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Security Implementation

### Password Security
- **Hashing Algorithm**: Werkzeug PBKDF2 (industry standard)
- **Hash Method**: `werkzeug.security.generate_password_hash(password)`
- **Verification**: `werkzeug.security.check_password_hash(hash, password)`
- **Salt**: Automatically generated and included in hash

### Session Security
- **Type**: Flask secure cookie-based session
- **Lifetime**: 24 hours
- **HttpOnly**: True (prevents JavaScript access)
- **SameSite**: Strict (prevents CSRF attacks)
- **Secure**: Should be True in production with HTTPS

### Database Security
- **Storage**: SQLite (local file-based)
- **Location**: `backend/users.db`
- **Encryption**: Passwords never stored in plain text
- **Isolation**: Each user has unique username

## API Endpoints

### Authentication Routes

#### POST /register
Register new user
```json
Request:
{
    "username": "john_doe",
    "password": "secure_password_123",
    "confirm_password": "secure_password_123"
}

Response: Redirect to /login
```

#### POST /login
Authenticate user
```json
Request:
{
    "username": "john_doe",
    "password": "secure_password_123"
}

Response: Redirect to / (home) + Session created
```

#### GET /logout
Clear session and redirect to login
```
Response: Redirect to /login + Session cleared
```

### Protected Prediction Routes

#### POST /predict
Make prediction (form submission)
```
Headers: 
  - Cookie: session=...

Form Parameters:
  age: 50
  sex: 1 (0=Female, 1=Male)
  anaemia: 0
  creatinine_phosphokinase: 500
  diabetes: 1
  ejection_fraction: 40
  high_blood_pressure: 1
  platelets: 250000
  serum_creatinine: 1.2
  serum_sodium: 140
  smoking: 0
  time: 100

Response: HTML result page with prediction
```

#### POST /api/predict
Make prediction (JSON API)
```json
Headers:
  - Cookie: session=...
  - Content-Type: application/json

Request:
{
    "age": 50,
    "sex": 1,
    "anaemia": 0,
    "creatinine_phosphokinase": 500,
    "diabetes": 1,
    "ejection_fraction": 40,
    "high_blood_pressure": 1,
    "platelets": 250000,
    "serum_creatinine": 1.2,
    "serum_sodium": 140,
    "smoking": 0,
    "time": 100
}

Response:
{
    "success": true,
    "probability": 45.23,
    "risk_category": "MEDIUM",
    "risk_color": "#f39c12",
    "recommendation": {
        "text": "Schedule appointment with cardiologist...",
        "icon": "⚠"
    }
}
```

## Testing the System

### Test Case 1: User Registration
1. Navigate to http://127.0.0.1:5000
2. Click "Register" in navbar
3. Enter username: `testuser`
4. Enter password: `test123456`
5. Confirm password: `test123456`
6. Click "Create Account"
7. **Expected**: Redirect to login page

### Test Case 2: User Login
1. On login page
2. Enter username: `testuser`
3. Enter password: `test123456`
4. Click "Sign In"
5. **Expected**: Redirect to home page with form visible

### Test Case 3: Make Prediction
1. After login, on home page
2. Fill in all 12 parameters:
   - Age: 55
   - Sex: Male (1)
   - Anaemia: No (0)
   - CPK: 582
   - Diabetes: Yes (1)
   - Ejection Fraction: 40
   - High Blood Pressure: Yes (1)
   - Platelets: 265000
   - Serum Creatinine: 1.5
   - Serum Sodium: 138
   - Smoking: Yes (1)
   - Time: 110
3. Click "Get Prediction"
4. **Expected**: Result page with risk category and probability

### Test Case 4: Logout
1. While logged in
2. Click "Logout" button in navbar
3. **Expected**: Redirect to login page, session cleared

### Test Case 5: Protected Route Access
1. While logged out
2. Try to access http://127.0.0.1:5000/
3. **Expected**: Redirect to login page

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here  # Set in production
```

### Session Configuration (app.py)
```python
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set True for HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
```

## Troubleshooting

### Issue: "Invalid username or password"
- **Cause**: Incorrect login credentials
- **Solution**: Check username/password are correct, verify account exists

### Issue: "Username already exists"
- **Cause**: Trying to register with existing username
- **Solution**: Use different username or login with existing account

### Issue: "Passwords do not match"
- **Cause**: Password confirmation doesn't match password
- **Solution**: Re-enter both password fields to match exactly

### Issue: Redirected to login when accessing prediction
- **Cause**: Session expired or user not logged in
- **Solution**: Login again, or check browser cookies are enabled

### Issue: Database file not found
- **Cause**: users.db not created
- **Solution**: App auto-creates on first run, delete users.db and restart if corrupted

## Production Deployment

For production deployments:

1. **Set Secret Key**:
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

2. **Enable Secure Cookies**:
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True  # Requires HTTPS
   ```

3. **Use Production WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```

4. **Database Backup**:
   - Regular backup of `users.db`
   - Monitor database size

5. **Logging**:
   - Enable login attempt logging
   - Monitor failed login attempts
   - Keep audit trail of predictions

## Files Modified/Created

### New Files
- `frontend/templates/login.html` - Login page
- `frontend/templates/register.html` - Registration page
- `backend/users.db` - User credentials database (created on first run)

### Modified Files
- `backend/app.py` - Added authentication routes, decorators, database setup
- `frontend/templates/base.html` - Updated navbar with login/logout

### Unchanged Files
- `frontend/templates/index.html` - Prediction form (now protected)
- `frontend/templates/result.html` - Results display
- `frontend/templates/about.html` - About page
- `frontend/static/style.css` - Styling

## API Credentials Format

### For Testing JSON API with Authentication

```bash
# Using curl to test /api/predict with session
curl -X POST http://127.0.0.1:5000/register \
  -d "username=testuser&password=test123456&confirm_password=test123456"

curl -X POST http://127.0.0.1:5000/login \
  -c cookies.txt \
  -d "username=testuser&password=test123456"

curl -X POST http://127.0.0.1:5000/api/predict \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{
    "age": 50,
    "sex": 1,
    "anaemia": 0,
    "creatinine_phosphokinase": 500,
    "diabetes": 1,
    "ejection_fraction": 40,
    "high_blood_pressure": 1,
    "platelets": 250000,
    "serum_creatinine": 1.2,
    "serum_sodium": 140,
    "smoking": 0,
    "time": 100
  }'
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test cases
3. Check Flask debug output in terminal
4. Verify database permissions
5. Ensure all dependencies are installed

---

**Last Updated**: 2024
**Version**: 2.0 (Authentication Added)
**Status**: Production Ready
