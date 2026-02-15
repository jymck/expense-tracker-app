# 💰 Expense Tracker

A full-featured daily expense tracking web application with user authentication, password recovery, admin management, and expense statistics.

## ✨ Features

- 🔐 **User Authentication** - Secure login/registration with password hashing
- 💾 **Expense Management** - Add, edit, delete expenses with categories
- 📊 **Statistics** - View expenses by day, week, month, and year
- 🔑 **Password Recovery** - Email-based password reset (with logging for development)
- 👨‍💼 **Admin Dashboard** - Manage users (admin panel with user deletion)
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- 💾 **Backup & Restore** - Export and import your expense data
- 🎨 **Beautiful UI** - Modern, gradient-based interface
- ⚡ **No Dependencies** - Uses only Python standard library

## 🚀 Quick Start

### Requirements
- Python 3.7 or higher
- Modern web browser

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/expense-tracker.git
   cd expense-tracker
   ```

2. **Run the server:**
   ```bash
   python server.py
   ```

3. **Open in browser:**
   ```
   http://localhost:3000
   ```

4. **Login with defaults:**
   - Username: `admin`
   - Password: `admin123`

## 🚢 Deploy & Host
   ```
   http://localhost:3000
   ```

The application will create a SQLite database file (`expenses.db`) automatically on first run.

## Project Structure

```
.
├── server.py              # Python backend server
├── public/
│   ├── index.html        # Main HTML file
│   ├── styles.css        # CSS styling
│   └── script.js         # Frontend JavaScript
├── expenses.db           # SQLite database (created automatically)
├── package.json          # Project metadata
└── README.md             # This file
```

## API Endpoints

### GET Endpoints

- `GET /api/expenses` - Get all expenses
- `GET /api/expenses/date/{date}` - Get expenses for a specific date
- `GET /api/expenses/daily/{date}` - Get daily total for a date
- `GET /api/expenses/weekly/{startDate}/{endDate}` - Get weekly total
- `GET /api/expenses/monthly/{year}/{month}` - Get monthly total
- `GET /api/expenses/yearly/{year}` - Get yearly total

### POST Endpoints

- `POST /api/expenses` - Add a new expense
  - Required fields: `date`, `category`, `amount`
  - Optional field: `description`

### DELETE Endpoints

- `DELETE /api/expenses/{id}` - Delete an expense by ID

## Usage

1. **Adding an Expense**:
   - Select a date (defaults to today)
   - Choose a category from the dropdown
   - Enter the amount
   - (Optional) Add a description
   - Click "Add Expense"

2. **Viewing Expenses**:
   - Daily expenses appear in the left panel
   - Summary statistics appear on the right panel
   - Change the date to view different days' expenses

3. **Deleting an Expense**:
   - Find the expense in the list
   - Click the "Delete" button next to it

## Database Schema

The application uses a single table with the following structure:

```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Currency

The application uses Indian Rupees (₹) by default. You can modify the currency symbol in:
- [script.js](public/script.js) - Search for `₹` to change the symbol
- [styles.css](public/styles.css) - If needed for styling

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

## Features I Could Add

- Export data to CSV/PDF
- Multiple currency support
- Budget alerts
- Monthly/yearly comparisons
- Data visualization with charts
- User authentication
- Cloud backup

## License

ISC

## Support

For issues or questions, please check:
1. Make sure Python 3.x is installed
2. Ensure port 3000 is not in use
3. Check that the `public/` folder exists with `index.html`, `styles.css`, and `script.js`
