#!/usr/bin/env python3
"""Test script to identify the 500 error"""
import json
import sys
import traceback

# Add the working directory to path
sys.path.insert(0, '.')

try:
    print("Step 1: Import modules...", flush=True)
    from server import init_db, hash_password, generate_session_token
    from datetime import datetime, timedelta
    import sqlite3
    
    print("Step 2: Initialize database...", flush=True)
    init_db()
    
    print("Step 3: Test registration logic manually...", flush=True)
    
    # Simulate what the API does during registration
    username = "testuser456"
    email = "test456@example.com"
    password = "password123"
    
    # Check if user exists
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ? OR email = ?', (username, email))
    if cursor.fetchone():
        print("ERROR: User or email already exists!")
        conn.close()
        sys.exit(1)
    
    # Hash password
    pwd_hash = hash_password(password)
    print(f"  - Password hashed successfully (length: {len(pwd_hash)})", flush=True)
    
    # Insert user
    cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                 (username, email, pwd_hash))
    print(f"  - User inserted, rowid: {cursor.lastrowid}", flush=True)
    
    # Create session
    token = generate_session_token()
    print(f"  - Session token generated: {token[:20]}...", flush=True)
    
    expires_at = (datetime.now() + timedelta(days=7)).isoformat()
    user_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                 (user_id, token, expires_at))
    print(f"  - Session inserted", flush=True)
    
    conn.commit()
    conn.close()
    
    print("\nStep 4: SUCCESS - All operations completed!", flush=True)
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
