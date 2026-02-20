#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sqlite3
import os
import sys
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

PORT = 3000
DB_FILE = 'expenses.db'
RECOVERY_LOG_FILE = 'recovery_tokens.log'

# Database lock to prevent concurrent access issues
db_lock = threading.RLock()  # RLock allows the same thread to acquire the lock multiple times

# Configure SQLite for better concurrent access
def get_db_connection():
    """Get database connection with proper settings"""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)  # 10 second timeout
    conn.isolation_level = None  # Autocommit mode
    return conn

# Password hashing helper
def hash_password(password):
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def verify_password(password, pwd_hash):
    try:
        salt, hashed = pwd_hash.split('$')
        pwd_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwd_check.hex() == hashed
    except:
        return False

def generate_session_token():
    return secrets.token_urlsafe(32)

def generate_recovery_token():
    return secrets.token_urlsafe(16)

def send_recovery_email(email, token, username):
    """Send password recovery email to user"""
    try:
        # For development: Log token to console and file
        recovery_message = f"[{datetime.now().isoformat()}] Password recovery requested\n  Email: {email}\n  Username: {username}\n  Token: {token}\n  Recovery URL: http://localhost:3000/recovery.html?token={token}\n"
        print(recovery_message, file=sys.stderr)
        
        # Log to file for reference
        with open(RECOVERY_LOG_FILE, 'a') as f:
            f.write(recovery_message + "\n")
        
        # Try to send actual email if configured
        # For production, configure SMTP settings here
        smtp_server = os.getenv('SMTP_SERVER', '')
        if smtp_server:
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASSWORD')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            
            message = MIMEMultipart("alternative")
            message["Subject"] = "Expense Tracker - Password Recovery"
            message["From"] = smtp_user
            message["To"] = email
            
            html = f"""\
            <html>
              <body>
                <h2>Password Recovery Request</h2>
                <p>Hi {username},</p>
                <p>You requested a password recovery. Click the link below to reset your password:</p>
                <p><a href="http://localhost:3000/recovery.html?token={token}">Reset Password</a></p>
                <p>This link expires in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
              </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, email, message.as_string())
                print(f"Email sent to {email}", file=sys.stderr)
        else:
            print(f"[DEVELOPMENT] Email service not configured. Check recovery_tokens.log for recovery tokens.", file=sys.stderr)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}", file=sys.stderr)
        # Still consider it success for development - token is logged
        return True

# Database initialization
def init_db():
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Password recovery tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_recovery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Expenses table (modified with user_id)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create default admin user if not exists
        try:
            cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            if not cursor.fetchone():
                admin_password_hash = hash_password('admin123')
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, is_admin)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', 'admin@expensetracker.local', admin_password_hash, 1))
        except:
            pass
        
        conn.commit()
        conn.close()

def get_user_from_token(token):
    """Get user info from session token"""
    with db_lock:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.is_admin 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        ''', (token, datetime.now().isoformat()))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

class ExpenseHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_url = urlparse(self.path)
            pathname = parsed_url.path
            
            # Serve static files
            if pathname == '/' or pathname == '/login.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                with open('public/login.html', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
                return
            
            if pathname == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                with open('public/index.html', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
                return
            
            if pathname == '/recovery.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                with open('public/recovery.html', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
                return
            
            if pathname.endswith('.css'):
                self.send_response(200)
                self.send_header('Content-type', 'text/css; charset=utf-8')
                self.end_headers()
                with open('public' + pathname, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
                return
            
            if pathname.endswith('.js'):
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript; charset=utf-8')
                self.end_headers()
                with open('public' + pathname, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
                return
            
            # Session info endpoint
            if pathname == '/api/session':
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                if not token:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                user = get_user_from_token(token)
                if user:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'user': user}).encode())
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Session expired'}).encode())
                return
            
            # Expenses endpoints - require authentication
            elif pathname == '/api/expenses':
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC', (user['id'],))
                rows = cursor.fetchall()
                conn.close()
                response = json.dumps([dict(row) for row in rows])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname.startswith('/api/expenses/date/'):
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                date = pathname.split('/api/expenses/date/')[1]
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM expenses WHERE user_id = ? AND date = ? ORDER BY created_at DESC', (user['id'], date))
                rows = cursor.fetchall()
                conn.close()
                response = json.dumps([dict(row) for row in rows])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname.startswith('/api/expenses/daily/'):
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                date = pathname.split('/api/expenses/daily/')[1]
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND date = ?', (user['id'], date))
                row = cursor.fetchone()
                conn.close()
                response = json.dumps({'total': row[0] or 0})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname.startswith('/api/expenses/weekly/'):
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                parts = pathname.split('/api/expenses/weekly/')[1].split('/')
                start_date, end_date = parts[0], parts[1]
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ?', (user['id'], start_date, end_date))
                row = cursor.fetchone()
                conn.close()
                response = json.dumps({'total': row[0] or 0})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname.startswith('/api/expenses/monthly/'):
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                parts = pathname.split('/api/expenses/monthly/')[1].split('/')
                year, month = parts[0], parts[1]
                month = month.zfill(2)
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND strftime("%Y-%m", date) = ?', (user['id'], f'{year}-{month}'))
                row = cursor.fetchone()
                conn.close()
                response = json.dumps({'total': row[0] or 0})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname.startswith('/api/expenses/yearly/'):
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                year = pathname.split('/api/expenses/yearly/')[1]
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = ? AND strftime("%Y", date) = ?', (user['id'], year))
                row = cursor.fetchone()
                conn.close()
                response = json.dumps({'total': row[0] or 0})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname == '/api/backup':
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC', (user['id'],))
                rows = cursor.fetchall()
                conn.close()
                
                backup_data = {
                    'backup_date': datetime.now().isoformat(),
                    'expenses': [dict(row) for row in rows]
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Disposition', 'attachment; filename="expense_backup.json"')
                self.end_headers()
                self.wfile.write(json.dumps(backup_data, indent=2).encode())
                return
            
            # User management endpoints
            elif pathname == '/api/users':
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user or not user.get('is_admin'):
                    self.send_response(403)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Admin only'}).encode())
                    return
                
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, email, is_admin, created_at FROM users')
                rows = cursor.fetchall()
                conn.close()
                response = json.dumps([dict(row) for row in rows])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            elif pathname.startswith('/api/recovery/'):
                token = pathname.split('/api/recovery/')[1]
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT pr.user_id, u.username, u.email 
                    FROM password_recovery pr
                    JOIN users u ON pr.user_id = u.id
                    WHERE pr.token = ? AND pr.expires_at > ? AND pr.used = 0
                ''', (token, datetime.now().isoformat()))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'valid': True, 'username': result['username']}).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid or expired token'}).encode())
                return

            
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
                return
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_POST(self):
        
        try:
            pathname = urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            data = json.loads(body.decode()) if body else {}
            
            # Login endpoint
            if pathname == '/api/login':
                username = data.get('username')
                password = data.get('password')
                
                if not (username and password):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Username and password required'}).encode())
                    return
                
                with db_lock:
                    conn = get_db_connection()
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, username, email, is_admin, password_hash FROM users WHERE username = ?', (username,))
                    user = cursor.fetchone()
                    conn.close()
                
                if not user or not verify_password(password, user['password_hash']):
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
                    return
                
                # Create session
                token = generate_session_token()
                expires_at = (datetime.now() + timedelta(days=7)).isoformat()
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                                 (user['id'], token, expires_at))
                    conn.commit()
                    conn.close()
                
                response = json.dumps({
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'is_admin': user['is_admin']
                    }
                })
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            # Register endpoint
            elif pathname == '/api/register':
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                
                if not (username and email and password):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'All fields required'}).encode())
                    return
                
                if len(password) < 6:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Password must be at least 6 characters'}).encode())
                    return
                
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid email format'}).encode())
                    return
                
                pwd_hash = hash_password(password)
                
                with db_lock:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # Insert user
                        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                                     (username, email, pwd_hash))
                        user_id = cursor.lastrowid
                        
                        # Create session
                        token = generate_session_token()
                        expires_at = (datetime.now() + timedelta(days=7)).isoformat()
                        
                        cursor.execute('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                                     (user_id, token, expires_at))
                        
                        conn.commit()
                        conn.close()
                        
                        response = json.dumps({
                            'token': token,
                            'user': {
                                'id': user_id,
                                'username': username,
                                'email': email,
                                'is_admin': False
                            }
                        })
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(response.encode())
                    except sqlite3.IntegrityError:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Username or email already exists'}).encode())
                return
            
            # Forgot password endpoint
            elif pathname == '/api/forgot-password':
                email = data.get('email')
                
                if not email:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Email required'}).encode())
                    return
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, username FROM users WHERE email = ?', (email,))
                    user = cursor.fetchone()
                    
                    if not user:
                        # Don't reveal if email exists
                        conn.close()
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'message': 'If email exists, recovery token sent'}).encode())
                        return
                    
                    user_id, username = user[0], user[1]
                    token = generate_recovery_token()
                    expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
                    
                    cursor.execute('INSERT INTO password_recovery (user_id, token, expires_at) VALUES (?, ?, ?)',
                                 (user_id, token, expires_at))
                    conn.commit()
                    conn.close()
                
                # Send recovery email (logs token for development)
                send_recovery_email(email, token, username)
                
                response = json.dumps({
                    'message': 'Password recovery link sent',
                    'note': 'Check your email for the recovery link. For development, see recovery_tokens.log'
                })
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            # Reset password endpoint
            elif pathname == '/api/reset-password':
                token = data.get('token')
                new_password = data.get('password')
                
                if not (token and new_password):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Token and password required'}).encode())
                    return
                
                if len(new_password) < 6:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Password must be at least 6 characters'}).encode())
                    return
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT user_id FROM password_recovery 
                        WHERE token = ? AND expires_at > ? AND used = 0
                    ''', (token, datetime.now().isoformat()))
                    result = cursor.fetchone()
                    
                    if not result:
                        conn.close()
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Invalid or expired token'}).encode())
                        return
                    
                    pwd_hash = hash_password(new_password)
                    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (pwd_hash, result[0]))
                    cursor.execute('UPDATE password_recovery SET used = 1 WHERE token = ?', (token,))
                    conn.commit()
                    conn.close()
                
                response = json.dumps({'message': 'Password reset successfully'})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            # Logout endpoint
            elif pathname == '/api/logout':
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                if token:
                    with db_lock:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
                        conn.commit()
                        conn.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Logged out'}).encode())
                return
            
            # Delete user endpoint (admin only)
            elif pathname.startswith('/api/users/'):
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                admin = get_user_from_token(token)
                if not admin or not admin.get('is_admin'):
                    self.send_response(403)
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Admin only'}).encode())
                    return
                
                user_id = pathname.split('/api/users/')[1]
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Don't allow deleting self
                    if int(user_id) == admin['id']:
                        conn.close()
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Cannot delete your own account'}).encode())
                        return
                    
                    cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
                    cursor.execute('DELETE FROM password_recovery WHERE user_id = ?', (user_id,))
                    cursor.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))
                    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    conn.commit()
                    conn.close()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'User deleted'}).encode())
                return
            
            # Handle restore backup
            elif pathname == '/api/restore':
                token = self.headers.get('Authorization', '').replace('Bearer ', '')
                user = get_user_from_token(token)
                if not user:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                    return
                
                expenses = data.get('expenses', [])
                
                if not expenses:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'No expenses to restore'}).encode())
                    return
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    restored_count = 0
                    for expense in expenses:
                        try:
                            cursor.execute('INSERT INTO expenses (user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)',
                                         (user['id'], expense['date'], expense['category'], expense['amount'], expense.get('description', '')))
                            restored_count += 1
                        except Exception as e:
                            print(f"Error restoring expense: {e}", file=sys.stderr)
                            continue
                    
                    conn.commit()
                    conn.close()
                
                response = json.dumps({'message': f'{restored_count} expenses restored successfully'})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
                return
            
            # Handle add expense
            else:
                if pathname == '/api/expenses':
                    token = self.headers.get('Authorization', '').replace('Bearer ', '')
                    user = get_user_from_token(token)
                    if not user:
                        self.send_response(401)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                        return
                    
                    date = data.get('date')
                    category = data.get('category')
                    amount = data.get('amount')
                    description = data.get('description', '')
                    
                    if not (date and category and amount):
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                        return
                    
                    # Convert amount to float and back to string to ensure precise storage
                    try:
                        amount_float = float(amount)
                        amount_str = str(amount_float)
                    except (ValueError, TypeError):
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Invalid amount'}).encode())
                        return
                    
                    with db_lock:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute('INSERT INTO expenses (user_id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)',
                                     (user['id'], date, category, amount_str, description))
                        conn.commit()
                        expense_id = cursor.lastrowid
                        conn.close()
                    
                    response = json.dumps({'id': expense_id, 'message': 'Expense added successfully'})
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response.encode())
                    return
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_DELETE(self):
        try:
            pathname = urlparse(self.path).path
            token = self.headers.get('Authorization', '').replace('Bearer ', '')
            user = get_user_from_token(token)
            
            if not user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            
            if pathname.startswith('/api/expenses/'):
                expense_id = pathname.split('/api/expenses/')[1]
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Verify expense belongs to user
                    cursor.execute('SELECT id FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user['id']))
                    expense = cursor.fetchone()
                    
                    if not expense:
                        conn.close()
                        self.send_response(404)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Expense not found'}).encode())
                        return
                    
                    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
                    conn.commit()
                    conn.close()
                
                response = json.dumps({'message': 'Expense deleted successfully'})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_PUT(self):
        try:
            pathname = urlparse(self.path).path
            token = self.headers.get('Authorization', '').replace('Bearer ', '')
            user = get_user_from_token(token)
            
            if not user:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            
            if pathname.startswith('/api/expenses/'):
                expense_id = pathname.split('/api/expenses/')[1]
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else b''
                data = json.loads(body.decode()) if body else {}
                
                date = data.get('date')
                category = data.get('category')
                amount = data.get('amount')
                description = data.get('description', '')
                
                if not (date and category and amount):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                    return
                
                # Convert amount to float and back to string to ensure precise storage
                try:
                    amount_float = float(amount)
                    amount_str = str(amount_float)
                except (ValueError, TypeError):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid amount'}).encode())
                    return
                
                with db_lock:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Verify expense belongs to user
                    cursor.execute('SELECT id FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user['id']))
                    expense = cursor.fetchone()
                    
                    if not expense:
                        conn.close()
                        self.send_response(404)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': 'Expense not found'}).encode())
                        return
                    
                    cursor.execute('UPDATE expenses SET date = ?, category = ?, amount = ?, description = ? WHERE id = ?',
                                 (date, category, amount_str, description, expense_id))
                    conn.commit()
                    conn.close()
                
                response = json.dumps({'message': 'Expense updated successfully'})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('0.0.0.0', PORT), ExpenseHandler)
    print(f"Server running at http://localhost:{PORT}")
    print(f"Open http://localhost:{PORT} in your browser")
    server.serve_forever()
