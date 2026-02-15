const http = require('http');
const path = require('path');
const fs = require('fs');
const url = require('url');
const sqlite3 = require('sqlite3').verbose();

const PORT = 3000;

// Database setup
const db = new sqlite3.Database('./expenses.db', (err) => {
  if (err) {
    console.error('Error opening database:', err);
  } else {
    console.log('Connected to SQLite database');
    initializeDatabase();
  }
});

// Initialize database tables
function initializeDatabase() {
  db.run(`
    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      category TEXT NOT NULL,
      amount REAL NOT NULL,
      description TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
}

// Helper function to parse JSON from request body
function getBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk.toString());
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(e);
      }
    });
  });
}

// Create HTTP server
const server = http.createServer(async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const query = parsedUrl.query;

  res.setHeader('Content-Type', 'application/json');

  try {
    // Serve static files
    if (pathname === '/' || pathname === '/index.html') {
      res.setHeader('Content-Type', 'text/html');
      const filePath = path.join(__dirname, 'public', 'index.html');
      res.end(fs.readFileSync(filePath, 'utf8'));
      return;
    }

    if (pathname.startsWith('/public/')) {
      const filePath = path.join(__dirname, pathname);
      let contentType = 'text/plain';
      if (filePath.endsWith('.css')) contentType = 'text/css';
      if (filePath.endsWith('.js')) contentType = 'application/javascript';
      
      res.setHeader('Content-Type', contentType);
      res.end(fs.readFileSync(filePath, 'utf8'));
      return;
    }

    // API Routes
    if (pathname === '/api/expenses' && req.method === 'GET') {
      db.all(`SELECT * FROM expenses ORDER BY date DESC`, [], (err, rows) => {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify(rows));
      });
      return;
    }

    if (pathname.match(/^\/api\/expenses\/date\//) && req.method === 'GET') {
      const date = pathname.split('/').pop();
      db.all(`SELECT * FROM expenses WHERE date = ? ORDER BY created_at DESC`, [date], (err, rows) => {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify(rows));
      });
      return;
    }

    if (pathname.match(/^\/api\/expenses\/daily\//) && req.method === 'GET') {
      const date = pathname.split('/').pop();
      db.get(`SELECT SUM(amount) as total FROM expenses WHERE date = ?`, [date], (err, row) => {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify({ total: row.total || 0 }));
      });
      return;
    }

    if (pathname.match(/^\/api\/expenses\/weekly\//) && req.method === 'GET') {
      const parts = pathname.split('/').slice(-2);
      const [startDate, endDate] = parts;
      db.get(`SELECT SUM(amount) as total FROM expenses WHERE date BETWEEN ? AND ?`, [startDate, endDate], (err, row) => {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify({ total: row.total || 0 }));
      });
      return;
    }

    if (pathname.match(/^\/api\/expenses\/monthly\//) && req.method === 'GET') {
      const parts = pathname.split('/').slice(-2);
      const [year, month] = parts;
      const monthPadded = month.padStart(2, '0');
      db.get(`SELECT SUM(amount) as total FROM expenses WHERE strftime('%Y-%m', date) = ?`, [`${year}-${monthPadded}`], (err, row) => {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify({ total: row.total || 0 }));
      });
      return;
    }

    if (pathname.match(/^\/api\/expenses\/yearly\//) && req.method === 'GET') {
      const year = pathname.split('/').pop();
      db.get(`SELECT SUM(amount) as total FROM expenses WHERE strftime('%Y', date) = ?`, [year], (err, row) => {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify({ total: row.total || 0 }));
      });
      return;
    }

    if (pathname === '/api/expenses' && req.method === 'POST') {
      const body = await getBody(req);
      const { date, category, amount, description } = body;

      if (!date || !category || !amount) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: 'Missing required fields' }));
        return;
      }

      db.run(`INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)`, 
        [date, category, amount, description || ''], function(err) {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify({ id: this.lastID, message: 'Expense added successfully' }));
      });
      return;
    }

    if (pathname.match(/^\/api\/expenses\/\d+$/) && req.method === 'DELETE') {
      const id = pathname.split('/').pop();
      db.run(`DELETE FROM expenses WHERE id = ?`, [id], function(err) {
        if (err) {
          res.writeHead(500);
          res.end(JSON.stringify({ error: err.message }));
          return;
        }
        res.end(JSON.stringify({ message: 'Expense deleted successfully' }));
      });
      return;
    }

    // 404
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not found' }));

  } catch (error) {
    console.error('Error:', error);
    res.writeHead(500);
    res.end(JSON.stringify({ error: error.message }));
  }
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`Open http://localhost:${PORT} in your browser`);
});

process.on('exit', () => {
  db.close();
});
