# Password Recovery Setup Guide

## For Development/Testing (Current Setup)

The password recovery feature logs recovery tokens to make testing easy:

### How it Works:
1. User clicks "Forgot Password" on the login page
2. Enters their email address
3. The server generates a recovery token and logs it to:
   - **Console output** (visible in the terminal running the server)
   - **recovery_tokens.log** file (in the project folder)

### Testing Password Recovery:
1. **Request recovery**: Enter the email address registered in the app
2. **Check logs**: Look at the terminal output or open `recovery_tokens.log`
3. **Get the token**: Copy the recovery token from the logs
4. **Visit recovery page**: Go to `http://localhost:3000/recovery.html?token=YOUR_TOKEN`
5. **Reset password**: Enter and confirm your new password

### Example Log Entry:
```
[2026-02-12T16:22:29.123456] Password recovery requested
  Email: user@example.com
  Username: testuser
  Token: abc123def456ghi789
  Recovery URL: http://localhost:3000/recovery.html?token=abc123def456ghi789
```

---

## For Production (Email Configuration)

To enable real email sending, set these environment variables:

```powershell
# PowerShell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_USER = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-app-password"
$env:SMTP_PORT = "587"

# Then start the server
python server.py
```

### Supported Email Providers:

**Gmail:**
```
SMTP_SERVER: smtp.gmail.com
SMTP_PORT: 587
SMTP_USER: your-email@gmail.com
SMTP_PASSWORD: (generate app-specific password in Gmail settings)
```

**Outlook/Office365:**
```
SMTP_SERVER: smtp-mail.outlook.com
SMTP_PORT: 587
SMTP_USER: your-email@outlook.com
SMTP_PASSWORD: your-password
```

**Custom SMTP Server:**
```
SMTP_SERVER: mail.example.com
SMTP_PORT: 587
SMTP_USER: your-username
SMTP_PASSWORD: your-password
```

---

## Testing Email Configuration

```powershell
# Test if environment variables are set
Write-Host $env:SMTP_SERVER
Write-Host $env:SMTP_USER

# The server will show in console if email is configured
# Output: "Email sent to user@example.com" → Success
# Output: "[DEVELOPMENT] Email service not configured..." → Not configured
```

---

## Default Test Account

- **Username:** admin
- **Password:** admin123
- **Email:** admin@expensetracker.local

For testing, you can register a new account with your own email address on the login page.
