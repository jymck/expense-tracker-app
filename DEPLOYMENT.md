# Deployment & Hosting Guide

## Option 1: Deploy to Railway.app (Recommended - Free Tier Available)

### Step 1: Prepare GitHub Repository

```bash
cd /path/to/Expenses\ tracking\ project

# Initialize git if not already done
git init

# Create .gitignore file
```

### Step 2: Push to GitHub

1. Create a new repository on GitHub (https://github.com/new)
   - Name: `expense-tracker`
   - Description: `Daily expense tracking app with authentication`
   - Make it Public

2. Push your code:
```bash
git add .
git commit -m "Initial commit: Expense Tracker with Authentication"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/expense-tracker.git
git push -u origin main
```

### Step 3: Deploy to Railway

1. Go to https://railway.app
2. Sign up with GitHub account
3. Click "New Project" → "GitHub Repo"
4. Select your `expense-tracker` repository
5. Railway automatically detects Python and creates a Procfile
6. Set environment variables (Railway Dashboard → Variables):
   - Only needed if you want email: `SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_PORT`
7. Deploy!

Your app will be available at: `https://your-project-name.up.railway.app`

---

## Option 2: Deploy to PythonAnywhere (Good for Python Apps)

1. Go to https://www.pythonanywhere.com
2. Create a free account
3. Click "Web" → "Add a new web app"
4. Choose "Python 3.x" and "Manual configuration"
5. Clone your GitHub repo in the bash console:
   ```bash
   git clone https://github.com/YOUR_USERNAME/expense-tracker.git
   ```
6. Configure the app (point to your server.py)
7. Reload the app → Live at `yourname.pythonanywhere.com`

---

## Option 3: Deploy to Render (Easy & Free)

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Set Build Command: `pip install -r requirements.txt`
6. Set Start Command: `python server.py`
7. Publish → Live at `your-app-name.onrender.com`

---

## Option 4: Use Docker + Docker Hub (For Any Cloud)

### Create Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 3000

CMD ["python", "server.py"]
```

### Create docker-compose.yml:

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - ./expenses.db:/app/expenses.db
```

Run locally with Docker:
```bash
docker build -t expense-tracker .
docker run -p 3000:3000 expense-tracker
```

Push to Docker Hub and deploy anywhere that supports Docker.

---

## Step-by-Step: Complete GitHub Setup

### 1. Create .gitignore

```
__pycache__/
*.pyc
*.pyo
*.egg-info/
.DS_Store
*.log
recovery_tokens.log
expenses.db
.env
venv/
node_modules/
```

### 2. Create requirements.txt

```bash
# Run in project folder:
pip freeze > requirements.txt

# Or manually create with:
# No external packages needed - uses only Python stdlib!
```

### 3. Create README.md for GitHub

```markdown
# Expense Tracker

A full-featured daily expense tracking application with user authentication and password recovery.

## Features

- 🔐 User authentication (login/register)
- 💰 Track expenses by category
- 📊 View expense statistics (daily, weekly, monthly, yearly)
- 🔑 Password recovery via email
- 👨‍💼 Admin user management
- 💾 Backup & restore expenses
- 🎨 Beautiful responsive UI

## Quick Start

### Requirements
- Python 3.7+
- No additional dependencies (uses Python stdlib only)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/expense-tracker.git
cd expense-tracker
```

2. Run the server:
```bash
python server.py
```

3. Open browser:
```
http://localhost:3000
```

## Default Credentials

- **Username:** admin
- **Password:** admin123

## Configuration

### Enable Email (Optional)

Set environment variables before running:

```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export SMTP_PORT=587
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for hosting on Railway, PythonAnywhere, Render, Docker, etc.

## License

MIT License
```

### 4. Create .env.example

```
# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_PORT=587
```

### 5. Create Procfile (for Heroku-compatible platforms)

```
web: python server.py
```

---

## GitHub Repository Structure

```
expense-tracker/
├── server.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── .gitignore
├── README.md
├── DEPLOYMENT.md
├── PASSWORD_RECOVERY.md
├── public/
│   ├── index.html
│   ├── login.html
│   ├── recovery.html
│   ├── script.js
│   ├── admin.js
│   └── styles.css
├── expenses.db (auto-created)
└── recovery_tokens.log (auto-created)
```

---

## After Deployment

### Share with Users

1. **GitHub:** Point them to your GitHub repo
2. **Website:** Post the live link: `https://your-app.on-platform.com`
3. **Documentation:** Include setup instructions in README

### Monitor & Maintain

- Check logs on the hosting platform
- Set up automated backups for the database
- Monitor for errors and performance

### Update the App

```bash
# Make changes locally
git add .
git commit -m "Feature: Add category filters"
git push

# The hosting platform automatically redeploys!
```

---

## Cost Breakdown

| Platform | Free Tier | Best For |
|----------|----------|----------|
| Railway | $5/month credits | Easy, Python-friendly |
| PythonAnywhere | Limited free | Good for demos |
| Render | Free tier exists | Simple deployments |
| Heroku | Free tier removed | Professional projects |
| Docker Hub | Free public images | Any platform |
| DigitalOcean | $5/month VPS | More control |

---

## Security Checklist Before Sharing

- [ ] Change default admin password
- [ ] Set up HTTPS (handled by platforms automatically)
- [ ] Configure environment variables (not in code)
- [ ] Database backups enabled
- [ ] SMTP configured if using email
- [ ] IP restrictions (if needed)

