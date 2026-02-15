// Admin user management functionality

async function loadUsers() {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  if (!user.is_admin) {
    showAdminAlert('Only admins can manage users');
    return;
  }

  try {
    const response = await fetch('/api/users', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) {
      showAdminAlert('Failed to load users');
      return;
    }

    const users = await response.json();
    displayUsersList(users);
  } catch (error) {
    showAdminAlert('Error loading users: ' + error.message);
  }
}

function displayUsersList(users) {
  const container = document.getElementById('usersList');
  
  if (!users || users.length === 0) {
    container.innerHTML = '<p class="empty-message">No users found</p>';
    return;
  }

  const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
  
  let html = '<table class="users-table">';
  html += '<thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Created</th><th>Actions</th></tr></thead>';
  html += '<tbody>';

  users.forEach(user => {
    const isCurrentUser = user.id === currentUser.id;
    const createdDate = new Date(user.created_at).toLocaleDateString();
    const role = user.is_admin ? 'Admin' : 'User';

    html += `
      <tr class="${isCurrentUser ? 'current-user' : ''}">
        <td><strong>${user.username}</strong>${isCurrentUser ? ' (You)' : ''}</td>
        <td>${user.email}</td>
        <td><span class="role-badge ${user.is_admin ? 'admin' : 'user'}">${role}</span></td>
        <td>${createdDate}</td>
        <td>
          ${!isCurrentUser ? `<button class="btn-small btn-delete" onclick="deleteUser(${user.id}, '${user.username}')">Delete</button>` : '-'}
        </td>
      </tr>
    `;
  });

  html += '</tbody></table>';
  container.innerHTML = html;
}

async function deleteUser(userId, username) {
  if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
    return;
  }

  const token = localStorage.getItem('token');

  try {
    const response = await fetch(`/api/users/${userId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const data = await response.json();

    if (!response.ok) {
      showAdminAlert('Failed to delete user: ' + (data.error || 'Unknown error'));
      return;
    }

    showAdminAlert('User deleted successfully');
    loadUsers(); // Reload list
  } catch (error) {
    showAdminAlert('Error deleting user: ' + error.message);
  }
}

function showAdminAlert(message) {
  const alertEl = document.getElementById('adminAlert');
  if (alertEl) {
    alertEl.textContent = message;
    alertEl.style.display = 'block';
    setTimeout(() => {
      alertEl.style.display = 'none';
    }, 4000);
  }
}

function openUserManagement() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  if (!user.is_admin) {
    showAdminAlert('Only administrators can access user management');
    return;
  }

  const modal = document.getElementById('userManagementModal');
  if (modal) {
    modal.style.display = 'flex';
    loadUsers();
  }
}

function closeUserManagement() {
  const modal = document.getElementById('userManagementModal');
  if (modal) {
    modal.style.display = 'none';
  }
}
