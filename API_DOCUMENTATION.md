# API Documentation

## Overview
The Expense Tracker App provides a RESTful API for managing expenses, user authentication, and administrative functions. All API endpoints return JSON responses and use standard HTTP status codes.

## Base URL
```
http://localhost:5000
```

## Authentication
Most endpoints require authentication using a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

## HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Authentication Endpoints

### POST /api/login
Authenticate a user and receive a session token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "is_admin": false
  }
}
```

### POST /api/register
Register a new user with security questions.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "securityQuestion": "string",
  "securityAnswer": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "is_admin": false
  }
}
```

### POST /api/logout
Logout a user by invalidating their session token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Logged out"
}
```

### POST /api/validate-security
Validate security questions for password recovery.

**Request Body:**
```json
{
  "username": "string",
  "securityQuestion": "string",
  "securityAnswer": "string"
}
```

**Response:**
```json
{
  "message": "Security validation successful"
}
```

### POST /api/reset-password-with-security
Reset password after security validation.

**Request Body:**
```json
{
  "username": "string",
  "newPassword": "string"
}
```

**Response:**
```json
{
  "message": "Password reset successful"
}
```

## Expense Endpoints

### GET /api/expenses/date/{date}
Get all expenses for a specific date.

**Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "date": "2026-02-21",
    "category": "Groceries",
    "amount": 150.50,
    "description": "Weekly groceries",
    "created_at": "2026-02-21T10:30:00"
  }
]
```

### GET /api/expenses/daily/{date}
Get daily total for a specific date.

**Parameters:**
- `date` (string) - Date in YYYY-MM-DD format

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total": 150.50
}
```

### GET /api/expenses/weekly/{startDate}/{endDate}
Get weekly total for a date range.

**Parameters:**
- `startDate` (string) - Start date in YYYY-MM-DD format
- `endDate` (string) - End date in YYYY-MM-DD format

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total": 1050.75
}
```

### GET /api/expenses/monthly/{year}/{month}
Get monthly total for a specific month.

**Parameters:**
- `year` (string) - Year (e.g., "2026")
- `month` (string) - Month (e.g., "2" for February)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total": 3200.00
}
```

### GET /api/expenses/yearly/{year}
Get yearly total for a specific year.

**Parameters:**
- `year` (string) - Year (e.g., "2026")

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total": 38400.00
}
```

### POST /api/expenses
Add a new expense.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "date": "2026-02-21",
  "category": "Groceries",
  "amount": 150.50,
  "description": "Weekly groceries"
}
```

**Response:**
```json
{
  "message": "Expense added successfully",
  "id": 1
}
```

### DELETE /api/expenses/{id}
Delete an expense by ID.

**Parameters:**
- `id` (integer) - Expense ID

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Expense deleted successfully"
}
```

## Data Management Endpoints

### GET /api/backup
Export all user data as JSON.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "backup_date": "2026-02-21T15:30:00",
  "expenses": [
    {
      "id": 1,
      "date": "2026-02-21",
      "category": "Groceries",
      "amount": 150.50,
      "description": "Weekly groceries",
      "created_at": "2026-02-21T10:30:00"
    }
  ]
}
```

### POST /api/restore
Import expense data from JSON backup.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "expenses": [
    {
      "date": "2026-02-21",
      "category": "Groceries",
      "amount": 150.50,
      "description": "Weekly groceries"
    }
  ]
}
```

**Response:**
```json
{
  "message": "5 expenses restored successfully"
}
```

## Admin Endpoints
*Requires admin privileges*

### GET /api/users
Get all registered users.

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true,
    "created_at": "2026-02-21T09:00:00"
  },
  {
    "id": 2,
    "username": "user1",
    "email": "user1@example.com",
    "is_admin": false,
    "created_at": "2026-02-21T10:00:00"
  }
]
```

### DELETE /api/users/{id}
Delete a user account.

**Parameters:**
- `id` (integer) - User ID

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

## Expense Categories

### Available Categories
The following categories are supported:

#### 🛒 Groceries & Food
- `Groceries`
- `Provisions`

#### ⚡ Utilities
- `Water`
- `Electricity`
- `Mobile`
- `Broadband`

#### ⛽ Fuel & Vehicle
- `Petrol`
- `Diesel`
- `Vehicle Maintenance`

#### 🚌 Travel & Transport
- `Train`
- `Bus`
- `Taxi`
- `Auto Fare`

#### 🛡️ Insurance
- `Life Insurance`
- `Car Insurance`
- `Bike Insurance`

#### 🏥 Healthcare
- `Hospital`
- `Medicines`

#### 🎓 Education & Activities
- `College Fee`
- `School Fee`
- `Hostel Fee`
- `Music class free`
- `Extra curricular activities free`

#### 👨‍👩‍👧‍👦 Family & Personal
- `Self Expenses`
- `Mother`
- `Father`
- `Relatives`
- `Son's Expenses`
- `Daughter's Expenses`
- `Spouse Expenses`

#### 📝 Other
- `Others`

## Error Responses

### Validation Errors
```json
{
  "error": "Username and password required"
}
```

### Authentication Errors
```json
{
  "error": "Invalid credentials"
}
```

### Authorization Errors
```json
{
  "error": "Admin only"
}
```

### Not Found Errors
```json
{
  "error": "Not found"
}
```

### Server Errors
```json
{
  "error": "Internal server error"
}
```

## Usage Examples

### JavaScript (Fetch API)
```javascript
// Login
const loginResponse = await fetch('/api/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
});

const loginData = await loginResponse.json();
const token = loginData.token;

// Add expense
const expenseResponse = await fetch('/api/expenses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    date: '2026-02-21',
    category: 'Groceries',
    amount: 150.50,
    description: 'Weekly groceries'
  })
});
```

### Python (Requests)
```python
import requests

# Login
login_data = {
    'username': 'testuser',
    'password': 'password123'
}

response = requests.post('http://localhost:5000/api/login', json=login_data)
token = response.json()['token']

# Add expense
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

expense_data = {
    'date': '2026-02-21',
    'category': 'Groceries',
    'amount': 150.50,
    'description': 'Weekly groceries'
}

response = requests.post('http://localhost:5000/api/expenses', 
                        json=expense_data, headers=headers)
```

### cURL
```bash
# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Add expense (replace TOKEN with actual token)
curl -X POST http://localhost:5000/api/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"date":"2026-02-21","category":"Groceries","amount":150.50,"description":"Weekly groceries"}'
```

## Rate Limiting
Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Security Considerations
- Always use HTTPS in production
- Validate all input data
- Implement proper session management
- Regular security audits recommended
- Keep dependencies updated

## Testing
The API can be tested using:
- Postman
- curl commands
- Browser DevTools
- Automated testing frameworks

## Version Information
- **API Version**: 1.0
- **Base URL**: http://localhost:5000
- **Authentication**: Bearer Token
- **Data Format**: JSON
