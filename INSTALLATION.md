# Installation Guide

## System Requirements

### Minimum Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Browser**: Modern web browser (Chrome 70+, Firefox 65+, Safari 12+, Edge 79+)
- **RAM**: 512MB minimum
- **Storage**: 50MB free space

### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 1GB or more
- **Storage**: 100MB free space
- **Browser**: Latest version of Chrome, Firefox, Safari, or Edge

## Installation Steps

### Step 1: Check Python Installation

#### Windows
1. Open Command Prompt or PowerShell
2. Run: `python --version`
3. If Python is not installed, download from https://www.python.org/downloads/

#### macOS
1. Open Terminal
2. Run: `python3 --version`
3. If Python is not installed, install via Homebrew: `brew install python3`

#### Linux
1. Open Terminal
2. Run: `python3 --version`
3. If Python is not installed, install via package manager:
   - Ubuntu/Debian: `sudo apt-get install python3`
   - CentOS/RHEL: `sudo yum install python3`

### Step 2: Clone the Repository

#### Option A: Using Git (Recommended)
```bash
git clone https://github.com/jymck/expense-tracker-app.git
cd expense-tracker-app
```

#### Option B: Download ZIP
1. Visit https://github.com/jymck/expense-tracker-app
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Navigate to the extracted folder

### Step 3: Verify Project Structure

Ensure you have the following files and folders:
```
expense-tracker-app/
├── server.py              # Main application server
├── README.md              # Project documentation
├── API_DOCUMENTATION.md   # API reference
├── INSTALLATION.md        # This file
├── public/
│   ├── index.html         # Main application interface
│   ├── login.html         # Login/registration page
│   ├── styles.css         # Application styling
│   ├── script.js          # Frontend JavaScript
│   └── admin.js           # Admin functionality
└── expenses.db            # Database (created automatically)
```

### Step 4: Run the Application

#### Windows
```bash
# Using Command Prompt
python server.py

# Or using PowerShell
python server.py
```

#### macOS/Linux
```bash
python3 server.py
```

### Step 5: Access the Application

1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. You should see the login page

## First-Time Setup

### Step 1: Register an Admin Account

1. Click "Register here" on the login page
2. Fill in the registration form:
   - **Username**: Choose a unique username
   - **Email**: Enter your email address
   - **Password**: Minimum 6 characters
   - **Security Question**: Select from dropdown
   - **Security Answer**: Enter answer (case-sensitive)
3. Click "Create Account"
4. The first registered user automatically becomes an admin

### Step 2: Login and Explore

1. Login with your new credentials
2. Explore the dashboard features
3. Try adding a test expense

## Configuration Options

### Port Configuration
The default port is 5000. To change it:

1. Open `server.py` in a text editor
2. Find the line: `PORT = 5000`
3. Change the port number
4. Save the file and restart the server

### Database Configuration
The application uses SQLite database (`expenses.db`) which is created automatically. No additional configuration needed.

## Troubleshooting

### Common Issues and Solutions

#### Issue: "python: command not found"
**Solution:**
- **Windows**: Ensure Python is installed and added to PATH
- **macOS/Linux**: Use `python3` instead of `python`

#### Issue: "Port already in use"
**Solution:**
1. Change the port in `server.py` (see Port Configuration above)
2. Or kill the process using the port:
   - **Windows**: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`
   - **macOS/Linux**: `lsof -ti:5000 | xargs kill -9`

#### Issue: "Connection refused" in browser
**Solution:**
1. Ensure the server is running (check terminal for "Server running at...")
2. Verify the URL: `http://localhost:5000`
3. Check firewall settings

#### Issue: Database errors
**Solution:**
1. Delete `expenses.db` file
2. Restart the server
3. Database will be recreated automatically

#### Issue: Security question recovery not working
**Solution:**
1. Ensure answers match exactly (case-sensitive)
2. Check that security questions were set during registration
3. Contact admin to reset account if needed

### Performance Issues

#### Slow Loading
- Clear browser cache
- Check available RAM
- Close other applications

#### Large Database Size
- Use backup feature to archive old data
- Delete old expenses manually
- Consider database cleanup

## Advanced Installation

### Running as a Service (Linux)

#### Using systemd
1. Create service file: `/etc/systemd/system/expense-tracker.service`
2. Add content:
```ini
[Unit]
Description=Expense Tracker App
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/expense-tracker-app
ExecStart=/usr/bin/python3 /path/to/expense-tracker-app/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable expense-tracker
sudo systemctl start expense-tracker
```

### Docker Installation (Optional)

1. Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
EXPOSE 5000
CMD ["python", "server.py"]
```

2. Build and run:
```bash
docker build -t expense-tracker .
docker run -p 5000:5000 expense-tracker
```

## Security Considerations

### Production Deployment
- Use HTTPS (SSL/TLS)
- Set up firewall rules
- Regular database backups
- Monitor access logs
- Keep Python updated

### Data Protection
- Regular backups of `expenses.db`
- Secure password policies
- Limit admin access
- Monitor user activity

## Network Configuration

### Local Network Access
To access from other devices on your network:

1. Find your local IP address:
   - **Windows**: `ipconfig`
   - **macOS/Linux**: `ifconfig` or `ip addr`

2. Modify `server.py` to bind to all interfaces:
   - Change `server.serve_forever()` to include host
   - Or use: `python -m http.server 5000 --bind 0.0.0.0`

3. Access via: `http://YOUR_IP:5000`

### Firewall Configuration
Allow port 5000 through firewall:

#### Windows
```powershell
New-NetFirewallRule -DisplayName "Expense Tracker" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow
```

#### Linux (ufw)
```bash
sudo ufw allow 5000/tcp
```

## Maintenance

### Regular Tasks
- **Weekly**: Backup database
- **Monthly**: Review user accounts
- **Quarterly**: Update Python dependencies
- **Annually**: Security audit

### Backup Procedures
1. Stop the server
2. Copy `expenses.db` to backup location
3. Restart the server
4. Test backup integrity

### Updates
1. Check for updates: `git pull origin main`
2. Backup current version
3. Update files
4. Restart server
5. Test functionality

## Support Resources

### Documentation
- **README.md**: General overview and features
- **API_DOCUMENTATION.md**: API reference for developers
- **INSTALLATION.md**: This detailed installation guide

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Wiki**: Additional documentation and tutorials

### Developer Resources
- **Source Code**: Available on GitHub
- **API Reference**: See API_DOCUMENTATION.md
- **Database Schema**: See README.md

## System Compatibility

### Tested Configurations
- **Windows 10/11** with Python 3.9+
- **macOS 11+** with Python 3.9+
- **Ubuntu 20.04+** with Python 3.8+
- **CentOS 8+** with Python 3.6+

### Browser Compatibility
- **Chrome**: 70+ (recommended)
- **Firefox**: 65+
- **Safari**: 12+
- **Edge**: 79+

### Mobile Support
- **iOS Safari**: 12+
- **Chrome Mobile**: 70+
- **Samsung Internet**: 8+

## Uninstallation

### Complete Removal
1. Stop the server (Ctrl+C)
2. Delete the application folder
3. Remove database file (`expenses.db`)
4. Clear browser data if needed

### Preserving Data
1. Backup `expenses.db` before deletion
2. Export data using the backup feature
3. Save backup files to secure location

---

**Need Help?** Check the [GitHub repository](https://github.com/jymck/expense-tracker-app) for additional support and resources.
