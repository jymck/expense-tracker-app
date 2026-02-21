// Authentication & Session Management
let currentToken = '';
let currentUser = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');

  if (!token || !user) {
    // Redirect to login if not authenticated
    window.location.href = '/login.html';
    return;
  }

  currentToken = token;
  currentUser = JSON.parse(user);

  // Update user display
  if (currentUser) {
    document.getElementById('userDisplay').innerHTML = `${currentUser.username} (${currentUser.is_admin ? 'Admin' : 'User'})`;
    
    // Show admin button if user is admin
    if (currentUser.is_admin) {
      document.getElementById('adminButton').style.display = 'inline-block';
    }
  }

  // Initialize app
  document.getElementById('expenseDate').valueAsDate = new Date();
  loadTodayExpenses();
  updateAllStats();
});

// Logout function
async function logout() {
  const token = localStorage.getItem('token');
  
  try {
    await fetch('/api/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  } catch (error) {
    console.error('Logout error:', error);
  }

  // Clear localStorage
  localStorage.removeItem('token');
  localStorage.removeItem('user');

  // Redirect to login
  window.location.href = '/login.html';
}

// Update stats whenever the date changes
document.getElementById('expenseDate').addEventListener('change', () => {
  loadTodayExpenses();
  updateDailyStats();
});

// Add expense function
async function addExpense() {
  const date = document.getElementById('expenseDate').value;
  const category = document.getElementById('expenseCategory').value;
  const amount = parseFloat(document.getElementById('expenseAmount').value);
  const description = document.getElementById('expenseDescription').value;

  if (!date || !category || !amount || amount <= 0) {
    alert('Please fill in all required fields (Amount must be greater than 0)');
    return;
  }

  try {
    const response = await fetch('/api/expenses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
      },
      body: JSON.stringify({
        date,
        category,
        amount,
        description
      })
    });

    if (response.ok) {
      alert('Expense added successfully!');
      // Clear form
      document.getElementById('expenseAmount').value = '';
      document.getElementById('expenseCategory').value = '';
      document.getElementById('expenseDescription').value = '';
      document.getElementById('expenseDate').valueAsDate = new Date();

      // Reload data
      loadTodayExpenses();
      updateAllStats();
    } else {
      alert('Error adding expense');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error adding expense');
  }
}

// Load today's expenses
async function loadTodayExpenses() {
  const dateInput = document.getElementById('expenseDate').value;
  const date = dateInput || new Date().toISOString().split('T')[0];

  try {
    const response = await fetch(`/api/expenses/date/${date}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const expenses = await response.json();

    const listContainer = document.getElementById('todayExpensesList');
    
    if (expenses.length === 0) {
      listContainer.innerHTML = '<p class="empty-message">No expenses for today</p>';
      return;
    }

    listContainer.innerHTML = expenses
      .map(expense => `
        <div class="expense-item">
          <div class="expense-info">
            <div class="expense-category">${expense.category}</div>
            ${expense.description ? `<div class="expense-description">${expense.description}</div>` : ''}
          </div>
          <div class="expense-amount">₹ ${parseFloat(expense.amount).toFixed(2)}</div>
          <button class="btn-edit" onclick="openEditModal(${expense.id}, '${expense.date}', '${expense.category}', ${expense.amount}, '${(expense.description || '').replace(/'/g, "\\'")}')">Edit</button>
          <button class="btn-delete" onclick="deleteExpense(${expense.id})">Delete</button>
        </div>
      `)
      .join('');
  } catch (error) {
    console.error('Error loading expenses:', error);
  }
}

// Delete expense
async function deleteExpense(id) {
  if (!confirm('Are you sure you want to delete this expense?')) return;

  try {
    const response = await fetch(`/api/expenses/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });

    if (response.ok) {
      loadTodayExpenses();
      updateAllStats();
    } else {
      alert('Error deleting expense');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error deleting expense');
  }
}

// Modal Functions
let currentEditId = null;

function openEditModal(id, date, category, amount, description) {
  currentEditId = id;
  document.getElementById('editExpenseDate').value = date;
  document.getElementById('editExpenseCategory').value = category;
  document.getElementById('editExpenseAmount').value = amount;
  document.getElementById('editExpenseDescription').value = description;
  document.getElementById('editModal').style.display = 'block';
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
  currentEditId = null;
}

async function saveExpense() {
  const date = document.getElementById('editExpenseDate').value;
  const category = document.getElementById('editExpenseCategory').value;
  const amount = parseFloat(document.getElementById('editExpenseAmount').value);
  const description = document.getElementById('editExpenseDescription').value;

  if (!date || !category || !amount || amount <= 0) {
    alert('Please fill in all required fields (Amount must be greater than 0)');
    return;
  }

  try {
    const response = await fetch(`/api/expenses/${currentEditId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
      },
      body: JSON.stringify({
        date,
        category,
        amount,
        description
      })
    });

    if (response.ok) {
      alert('Expense updated successfully!');
      closeEditModal();
      loadTodayExpenses();
      updateAllStats();
    } else {
      alert('Error updating expense');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error updating expense');
  }
}

// Close modal when clicking outside of it
window.onclick = function(event) {
  const modal = document.getElementById('editModal');
  if (event.target == modal) {
    closeEditModal();
  }
}

// Backup functionality
async function backupExpenses() {
  try {
    const response = await fetch('/api/backup', {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const filename = `expense_backup_${new Date().toISOString().split('T')[0]}.json`;
      
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      alert('Backup downloaded successfully!');
    } else {
      alert('Error creating backup');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error creating backup');
  }
}

// Restore functionality
async function restoreExpenses(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function(e) {
    try {
      const backupData = JSON.parse(e.target.result);
      
      if (!backupData.expenses || !Array.isArray(backupData.expenses)) {
        alert('Invalid backup file format');
        return;
      }

      const response = await fetch('/api/restore', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${currentToken}`
        },
        body: JSON.stringify(backupData)
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        loadTodayExpenses();
        updateAllStats();
        document.getElementById('restoreFile').value = ''; // Clear file input
      } else {
        alert('Error restoring backup');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error reading backup file');
    }
  };
  reader.readAsText(file);
}

// Update all statistics
async function updateAllStats() {
  updateDailyStats();
  updateWeeklyStats();
  updateMonthlyStats();
  updateYearlyStats();
  updatePersonBreakdown();
  updateCategoryBreakdown();
}

// Update daily stats
async function updateDailyStats() {
  const dateInput = document.getElementById('expenseDate').value;
  const date = dateInput || new Date().toISOString().split('T')[0];

  try {
    const response = await fetch(`/api/expenses/daily/${date}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const data = await response.json();
    
    document.getElementById('dailyTotal').textContent = `₹ ${parseFloat(data.total).toFixed(2)}`;
    
    const dateObj = new Date(date);
    const formattedDate = dateObj.toLocaleDateString('en-IN', { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
    document.getElementById('dailyDate').textContent = formattedDate;
  } catch (error) {
    console.error('Error updating daily stats:', error);
  }
}

// Update weekly stats
async function updateWeeklyStats() {
  const today = new Date();
  const endDate = today.toISOString().split('T')[0];
  
  const startDate = new Date(today);
  startDate.setDate(startDate.getDate() - 6);
  const startDateStr = startDate.toISOString().split('T')[0];

  try {
    const response = await fetch(`/api/expenses/weekly/${startDateStr}/${endDate}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const data = await response.json();
    document.getElementById('weeklyTotal').textContent = `₹ ${parseFloat(data.total).toFixed(2)}`;
  } catch (error) {
    console.error('Error updating weekly stats:', error);
  }
}

// Update monthly stats
async function updateMonthlyStats() {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + 1;

  try {
    const response = await fetch(`/api/expenses/monthly/${year}/${month}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const data = await response.json();
    
    document.getElementById('monthlyTotal').textContent = `₹ ${parseFloat(data.total).toFixed(2)}`;
    
    const monthName = today.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
    document.getElementById('monthlyDate').textContent = monthName;
  } catch (error) {
    console.error('Error updating monthly stats:', error);
  }
}

// Update yearly stats
async function updateYearlyStats() {
  const today = new Date();
  const year = today.getFullYear();

  try {
    const response = await fetch(`/api/expenses/yearly/${year}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const data = await response.json();
    
    document.getElementById('yearlyTotal').textContent = `₹ ${parseFloat(data.total).toFixed(2)}`;
    document.getElementById('yearlyDate').textContent = year.toString();
  } catch (error) {
    console.error('Error updating yearly stats:', error);
  }
}

// Update category breakdown for today
async function updateCategoryBreakdown() {
  const dateInput = document.getElementById('expenseDate').value;
  const date = dateInput || new Date().toISOString().split('T')[0];

  try {
    const response = await fetch(`/api/expenses/date/${date}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const expenses = await response.json();

    const categoryTotals = {};
    expenses.forEach(expense => {
      if (!categoryTotals[expense.category]) {
        categoryTotals[expense.category] = 0;
      }
      categoryTotals[expense.category] += parseFloat(expense.amount);
    });

    const breakdownContainer = document.getElementById('categoryBreakdown');
    
    if (Object.keys(categoryTotals).length === 0) {
      breakdownContainer.innerHTML = '<p class="empty-message">No data available</p>';
      return;
    }

    breakdownContainer.innerHTML = Object.entries(categoryTotals)
      .map(([category, total]) => `
        <div class="category-item">
          <span class="category-name">${category}</span>
          <span class="category-amount">₹ ${parseFloat(total).toFixed(2)}</span>
        </div>
      `)
      .join('');
  } catch (error) {
    console.error('Error updating category breakdown:', error);
  }
}

// Update person-wise breakdown for today
async function updatePersonBreakdown() {
  const dateInput = document.getElementById('expenseDate').value;
  const date = dateInput || new Date().toISOString().split('T')[0];

  try {
    const response = await fetch(`/api/expenses/date/${date}`, {
      headers: { 'Authorization': `Bearer ${currentToken}` }
    });
    const expenses = await response.json();

    const personTotals = {};
    const personMap = {
      "Self Expenses": "Self",
      "Mother": "Mother",
      "Father": "Father",
      "Relatives": "Relatives",
      "Son's Expenses": "Son",
      "Daughter's Expenses": "Daughter",
      "Spouse Expenses": "Spouse"
    };

    expenses.forEach(expense => {
      const personKey = personMap[expense.category];
      if (personKey) {
        if (!personTotals[personKey]) {
          personTotals[personKey] = 0;
        }
        personTotals[personKey] += parseFloat(expense.amount);
      }
    });

    const breakdownContainer = document.getElementById('personBreakdown');
    
    if (Object.keys(personTotals).length === 0) {
      breakdownContainer.innerHTML = '<p class="empty-message">No data available</p>';
      return;
    }

    breakdownContainer.innerHTML = Object.entries(personTotals)
      .map(([person, total]) => `
        <div class="category-item">
          <span class="category-name">${person}</span>
          <span class="category-amount">₹ ${parseFloat(total).toFixed(2)}</span>
        </div>
      `)
      .join('');
  } catch (error) {
    console.error('Error updating person breakdown:', error);
  }
}
