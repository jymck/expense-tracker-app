# 💰 Expense Tracker App

A comprehensive web-based expense management application with secure user authentication, advanced password recovery, admin management, and detailed expense analytics.

## ✨ Features

### 🔐 Authentication & Security
- **User Registration** with security questions for enhanced security
- **Secure Login** with session management and password hashing
- **Two-Step Password Recovery** using security questions and answers (no email required)
- **Admin/User Role Management** with granular permissions
- **Session-based Authentication** with automatic expiration

### 💰 Expense Management
- **Add/Track Expenses** with comprehensive categories
- **Edit/Delete Expenses** with real-time updates
- **Date-wise Expense Tracking** with calendar navigation
- **Category-wise Breakdown** with visual indicators
- **Person-wise Expense Analysis** (Self, Mother, Father, Relatives, Son, Daughter, Spouse)

### 📊 Analytics & Reporting
- **Daily, Weekly, Monthly, Yearly** expense summaries
- **Real-time Statistics** with automatic updates
- **Category Breakdown** showing spending patterns
- **Person-wise Analysis** for family expense tracking

### 🎨 User Interface
- **Modern, Responsive Design** with smooth multi-color gradients
- **Intuitive Navigation** between features
- **Mobile-Friendly** layout for all devices
- **Smooth Animations** and transitions
- **Professional UI** with enhanced readability

### 💾 Data Management
- **Backup/Restore** functionality with JSON export
- **Local Data Storage** using SQLite database
- **Data Export** in structured JSON format
- **Secure Data Handling** with proper validation

### � Education & Activities Categories
- **Music class free** - For tracking free music lessons
- **Extra curricular activities free** - For tracking free activities

### 👨‍👩‍👧‍👦 Family Categories
- **Mother** - Track mother-related expenses
- **Father** - Track father-related expenses  
- **Relatives** - Track relative-related expenses
- **Self, Son, Daughter, Spouse** - Complete family expense tracking

## 🚀 Quick Start

### Requirements
- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jymck/expense-tracker-app.git
   cd expense-tracker-app
   ```

2. **Run the server:**
   ```bash
   python server.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5000
   ```

4. **First-time setup:**
   - Register a new account (first user becomes admin)
   - Set up security questions for password recovery
   - Start tracking expenses!

## � Usage Guide

### Registration & Login
1. **Register**: Click "Register here" and fill in details
2. **Security Questions**: Choose and answer security questions (required for password recovery)
3. **Login**: Use credentials to access the dashboard

### Adding Expenses
1. **Select Date**: Defaults to today's date
2. **Choose Category**: Select from comprehensive category list
3. **Enter Amount**: Input expense amount in rupees (₹)
4. **Add Description**: Optional details about the expense
5. **Click "Add Expense"**: Save to database

### Password Recovery
1. **Click "Forgot password?"** on login page
2. **Step 1**: Enter username and answer security questions
3. **Step 2**: Set new password after validation
4. **Login** with new password

### Admin Features
- **User Management**: View all registered users
- **Delete Users**: Remove user accounts (except self)
- **User Statistics**: Track user activity

### Data Backup & Restore
- **Backup**: Click "💾 Backup Data" to download JSON file
- **Restore**: Click "📂 Restore Data" to import from backup file

## 🏗️ Project Structure

```
expense-tracker-app/
├── server.py              # Main Flask server with authentication
├── expenses.db            # SQLite database (created automatically)
├── public/
│   ├── index.html         # Main application interface
│   ├── login.html         # Authentication page with security questions
│   ├── styles.css         # Modern styling with gradients
│   ├── script.js          # Main JavaScript logic
│   └── admin.js           # Admin functionality
└── README.md              # This documentation
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    security_question TEXT NOT NULL,
    security_answer TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Expenses Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🌐 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration with security questions
- `POST /api/logout` - User logout
- `POST /api/validate-security` - Validate security questions
- `POST /api/reset-password-with-security` - Reset password with security

### Expenses
- `GET /api/expenses/date/{date}` - Get expenses by date
- `GET /api/expenses/daily/{date}` - Get daily statistics
- `GET /api/expenses/weekly/{start}/{end}` - Get weekly statistics
- `GET /api/expenses/monthly/{year}/{month}` - Get monthly statistics
- `GET /api/expenses/yearly/{year}` - Get yearly statistics
- `POST /api/expenses` - Add new expense
- `DELETE /api/expenses/{id}` - Delete expense

### Data Management
- `GET /api/backup` - Export user data
- `POST /api/restore` - Import user data

### Admin
- `GET /api/users` - Get all users (admin only)
- `DELETE /api/users/{id}` - Delete user (admin only)

## 📋 Expense Categories

### 🛒 Groceries & Food
- Groceries
- Provisions

### ⚡ Utilities
- Water, Electricity, Mobile, Broadband

### ⛽ Fuel & Vehicle
- Petrol, Diesel, Vehicle Maintenance

### 🚌 Travel & Transport
- Train, Bus, Taxi, Auto Fare

### 🛡️ Insurance
- Life Insurance, Car Insurance, Bike Insurance

### 🏥 Healthcare
- Hospital, Medicines

### 🎓 Education & Activities
- College Fee, School Fee, Hostel Fee
- **Music class free** - For free music lessons
- **Extra curricular activities free** - For free activities

### 👨‍👩‍👧‍👦 Family & Personal
- Self Expenses
- **Mother** - Mother-related expenses
- **Father** - Father-related expenses
- **Relatives** - Relative-related expenses
- Son's Expenses, Daughter's Expenses, Spouse Expenses

### 📝 Other
- Others

## 🔒 Security Features

### Password Security
- **SHA-256 Hashing** with salt for password storage
- **Minimum Length**: 6 characters required
- **Security Questions**: Two-factor authentication for recovery

### Session Management
- **Secure Tokens**: Random session tokens
- **Expiration**: 7-day session validity
- **Automatic Cleanup**: Expired sessions removed automatically

### Data Protection
- **Local Storage**: All data stored locally in SQLite
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Prevention**: Using parameterized queries

## 🛠️ Technical Details

### Backend (Python Flask)
- **Server**: Built with Python standard library
- **Database**: SQLite for lightweight, serverless storage
- **Authentication**: Session-based with secure tokens
- **API**: RESTful design with proper error handling

### Frontend (Vanilla JavaScript)
- **No Framework Dependencies**: Pure HTML, CSS, JavaScript
- **Responsive Design**: Mobile-first approach
- **Modern UI**: CSS gradients and smooth animations
- **Real-time Updates**: Dynamic content loading

## 🔧 Troubleshooting

### Common Issues

#### Server Won't Start
- **Python Version**: Ensure Python 3.7+
- **Port Conflict**: Default port is 5000 (not 3000)
- **Permissions**: Ensure write access for database file

#### Database Issues
- **Corrupted Database**: Delete `expenses.db` and restart server
- **Migration Issues**: Server handles schema updates automatically

#### Login Problems
- **Forgot Password**: Use security question recovery
- **Account Issues**: Contact admin for account reset

#### Performance Issues
- **Large Dataset**: Use backup/restore to archive old data
- **Browser Cache**: Clear browser cache if UI seems slow

### Error Messages

#### "Connection error: Failed to fetch"
- **Server Status**: Ensure server is running on port 5000
- **Network Issues**: Check firewall settings
- **Browser Issues**: Try refreshing the page

#### "Invalid security question or answer"
- **Exact Match**: Ensure answers match exactly (case-sensitive)
- **Contact Admin**: If recovery fails, contact admin

## 🚀 Deployment

### Local Development
```bash
python server.py
# Access at http://localhost:5000
```

### Production Considerations
- **HTTPS**: Use HTTPS for production
- **Database Backups**: Regular database backups
- **Monitoring**: Monitor server logs and performance
- **Security**: Keep Python and dependencies updated

## 📝 Development

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m "Add feature"`
5. Push to branch: `git push origin feature-name`
6. Submit pull request

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use modern ES6+ features
- **CSS**: Use consistent naming conventions
- **HTML**: Semantic HTML5 structure

## 📄 License

This project is provided as-is for educational and personal use.

## 📞 Support

### Developer Information
- **Developer**: YCR
- **Version**: 1.0
- **Year**: 2026
- **Repository**: https://github.com/jymck/expense-tracker-app

### Disclaimer
This application is provided as-is for expense tracking purposes. The developer (YCR) is not responsible for any data loss, inaccuracies, or technical issues. Users are advised to maintain regular backups of their data.

### Contact & Issues
For bugs, issues, or feature requests, please use the GitHub repository issue tracker.

---

**Happy Expense Tracking! 🎉**
