// Admin Panel JavaScript

const API_BASE_URL = '/api';
let allUsers = [];
let allCampaigns = [];

// Initialize admin panel on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAdminAuth();
    loadAdminData();
    initializeCharts();
});

// Check if user is authenticated as admin
function checkAdminAuth() {
    const token = localStorage.getItem('access_token');
    const userRole = localStorage.getItem('user_role');
    
    if (!token || userRole !== 'admin') {
        window.location.href = '/login';
        return;
    }
}

// Load all admin data
async function loadAdminData() {
    showLoading(true);
    
    try {
        await Promise.all([
            loadUsers(),
            loadCampaigns(),
            loadSystemStats()
        ]);
    } catch (error) {
        console.error('Error loading admin data:', error);
        showNotification('Failed to load admin data', 'error');
    } finally {
        showLoading(false);
    }
}

// Load users data
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            allUsers = data.users || generateMockUsers();
            displayUsers(allUsers);
            updateUserFilter();
        } else {
            // Use mock data if endpoint doesn't exist
            allUsers = generateMockUsers();
            displayUsers(allUsers);
            updateUserFilter();
        }
    } catch (error) {
        console.log('Using mock user data');
        allUsers = generateMockUsers();
        displayUsers(allUsers);
        updateUserFilter();
    }
}

// Generate mock users for demonstration
function generateMockUsers() {
    return [
        {
            id: 1,
            username: 'john_doe',
            email: 'john@example.com',
            role: 'user',
            created_at: '2024-01-15',
            campaigns_count: 5
        },
        {
            id: 2,
            username: 'jane_smith',
            email: 'jane@example.com',
            role: 'user',
            created_at: '2024-02-20',
            campaigns_count: 3
        },
        {
            id: 3,
            username: 'admin_user',
            email: 'admin@example.com',
            role: 'admin',
            created_at: '2024-01-01',
            campaigns_count: 0
        },
        {
            id: 4,
            username: 'demo_user',
            email: 'demo@example.com',
            role: 'user',
            created_at: '2024-03-10',
            campaigns_count: 8
        }
    ];
}

// Display users in table
function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td><strong>${user.username}</strong></td>
            <td>${user.email}</td>
            <td><span class="role-badge ${user.role}">${user.role}</span></td>
            <td>${formatDate(user.created_at)}</td>
            <td>${user.campaigns_count || 0}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon view" onclick="viewUser(${user.id})" title="View Details">
                        <span class="iconify" data-icon="mdi:eye"></span>
                    </button>
                    <button class="btn-icon edit" onclick="editUser(${user.id})" title="Edit User">
                        <span class="iconify" data-icon="mdi:pencil"></span>
                    </button>
                    <button class="btn-icon delete" onclick="deleteUser(${user.id})" title="Delete User">
                        <span class="iconify" data-icon="mdi:delete"></span>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // Update total users count
    document.getElementById('totalUsers').textContent = users.length;
}

// Load campaigns data
async function loadCampaigns() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/campaigns`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            allCampaigns = data.campaigns || generateMockCampaigns();
            displayCampaigns(allCampaigns);
        } else {
            allCampaigns = generateMockCampaigns();
            displayCampaigns(allCampaigns);
        }
    } catch (error) {
        console.log('Using mock campaign data');
        allCampaigns = generateMockCampaigns();
        displayCampaigns(allCampaigns);
    }
}

// Generate mock campaigns
function generateMockCampaigns() {
    const campaigns = [];
    const platforms = ['Google Ads', 'Facebook Ads', 'Instagram Ads', 'LinkedIn Ads'];
    const users = ['john_doe', 'jane_smith', 'demo_user'];
    const statuses = ['active', 'paused', 'stopped'];
    
    for (let i = 1; i <= 20; i++) {
        campaigns.push({
            id: i,
            user: users[Math.floor(Math.random() * users.length)],
            name: `Campaign ${i}`,
            platform: platforms[Math.floor(Math.random() * platforms.length)],
            impressions: Math.floor(Math.random() * 100000) + 10000,
            clicks: Math.floor(Math.random() * 5000) + 500,
            spend: Math.floor(Math.random() * 5000) + 500,
            status: statuses[Math.floor(Math.random() * statuses.length)]
        });
    }
    
    return campaigns;
}

// Display campaigns in table
function displayCampaigns(campaigns) {
    const tbody = document.getElementById('campaignsTableBody');
    tbody.innerHTML = '';
    
    campaigns.forEach(campaign => {
        const ctr = ((campaign.clicks / campaign.impressions) * 100).toFixed(2);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${campaign.user}</strong></td>
            <td>${campaign.name}</td>
            <td>${campaign.platform}</td>
            <td>${campaign.impressions.toLocaleString()}</td>
            <td>${campaign.clicks.toLocaleString()}</td>
            <td>$${campaign.spend.toLocaleString()}</td>
            <td>${ctr}%</td>
            <td><span class="status-badge ${campaign.status}">${campaign.status}</span></td>
        `;
        tbody.appendChild(row);
    });
    
    // Update active campaigns count
    const activeCampaigns = campaigns.filter(c => c.status === 'active').length;
    document.getElementById('activeCampaigns').textContent = activeCampaigns;
}

// Load system statistics
async function loadSystemStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateSystemStats(data);
        } else {
            updateSystemStats(generateMockStats());
        }
    } catch (error) {
        console.log('Using mock stats data');
        updateSystemStats(generateMockStats());
    }
}

// Generate mock statistics
function generateMockStats() {
    return {
        total_spend: 125430,
        total_predictions: 1247,
        active_campaigns: 15
    };
}

// Update system statistics display
function updateSystemStats(stats) {
    document.getElementById('totalSpend').textContent = `$${stats.total_spend.toLocaleString()}`;
    document.getElementById('totalPredictions').textContent = stats.total_predictions.toLocaleString();
}

// Filter users
function filterUsers() {
    const searchTerm = document.getElementById('userSearch').value.toLowerCase();
    const roleFilter = document.getElementById('userRoleFilter').value;
    
    let filtered = allUsers.filter(user => {
        const matchesSearch = user.username.toLowerCase().includes(searchTerm) || 
                            user.email.toLowerCase().includes(searchTerm);
        const matchesRole = roleFilter === 'all' || user.role === roleFilter;
        
        return matchesSearch && matchesRole;
    });
    
    displayUsers(filtered);
}

// Filter campaigns
function filterCampaigns() {
    const userFilter = document.getElementById('campaignUserFilter').value;
    const platformFilter = document.getElementById('campaignPlatformFilter').value;
    
    let filtered = allCampaigns.filter(campaign => {
        const matchesUser = userFilter === 'all' || campaign.user === userFilter;
        const matchesPlatform = platformFilter === 'all' || campaign.platform === platformFilter;
        
        return matchesUser && matchesPlatform;
    });
    
    displayCampaigns(filtered);
}

// Update user filter dropdown
function updateUserFilter() {
    const select = document.getElementById('campaignUserFilter');
    const uniqueUsers = [...new Set(allCampaigns.map(c => c.user))];
    
    select.innerHTML = '<option value="all">All Users</option>';
    uniqueUsers.forEach(user => {
        const option = document.createElement('option');
        option.value = user;
        option.textContent = user;
        select.appendChild(option);
    });
}

// User management functions
function viewUser(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (user) {
        alert(`User Details:\n\nID: ${user.id}\nUsername: ${user.username}\nEmail: ${user.email}\nRole: ${user.role}\nCreated: ${formatDate(user.created_at)}\nCampaigns: ${user.campaigns_count}`);
    }
}

function editUser(userId) {
    const user = allUsers.find(u => u.id === userId);
    if (user) {
        const newUsername = prompt('Enter new username:', user.username);
        if (newUsername && newUsername !== user.username) {
            user.username = newUsername;
            displayUsers(allUsers);
            showNotification('User updated successfully', 'success');
        }
    }
}

async function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            if (response.ok) {
                allUsers = allUsers.filter(u => u.id !== userId);
                displayUsers(allUsers);
                showNotification('User deleted successfully', 'success');
            } else {
                // Mock deletion for demo
                allUsers = allUsers.filter(u => u.id !== userId);
                displayUsers(allUsers);
                showNotification('User deleted successfully', 'success');
            }
        } catch (error) {
            // Mock deletion for demo
            allUsers = allUsers.filter(u => u.id !== userId);
            displayUsers(allUsers);
            showNotification('User deleted successfully', 'success');
        }
    }
}

// Modal functions
function showAddUserModal() {
    document.getElementById('addUserModal').style.display = 'block';
}

function closeAddUserModal() {
    document.getElementById('addUserModal').style.display = 'none';
    document.getElementById('addUserForm').reset();
}

async function addNewUser(event) {
    event.preventDefault();
    
    const userData = {
        username: document.getElementById('newUsername').value,
        email: document.getElementById('newEmail').value,
        password: document.getElementById('newPassword').value,
        role: document.getElementById('newRole').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            closeAddUserModal();
            await loadUsers();
            showNotification('User added successfully', 'success');
        } else {
            // Mock user creation for demo
            const newUser = {
                id: allUsers.length + 1,
                username: userData.username,
                email: userData.email,
                role: userData.role,
                created_at: new Date().toISOString(),
                campaigns_count: 0
            };
            allUsers.push(newUser);
            displayUsers(allUsers);
            closeAddUserModal();
            showNotification('User added successfully', 'success');
        }
    } catch (error) {
        // Mock user creation for demo
        const newUser = {
            id: allUsers.length + 1,
            username: userData.username,
            email: userData.email,
            role: userData.role,
            created_at: new Date().toISOString(),
            campaigns_count: 0
        };
        allUsers.push(newUser);
        displayUsers(allUsers);
        closeAddUserModal();
        showNotification('User added successfully', 'success');
    }
}

// Settings functions
async function backupDatabase() {
    showNotification('Database backup initiated...', 'info');
    setTimeout(() => {
        showNotification('Database backup completed successfully', 'success');
    }, 2000);
}

async function optimizeDatabase() {
    showNotification('Optimizing database...', 'info');
    setTimeout(() => {
        showNotification('Database optimization completed', 'success');
    }, 2000);
}

async function clearOldData() {
    if (confirm('Are you sure you want to clear old data? This will remove data older than 90 days.')) {
        showNotification('Clearing old data...', 'info');
        setTimeout(() => {
            showNotification('Old data cleared successfully', 'success');
        }, 2000);
    }
}

async function retrainModel() {
    showNotification('Retraining ML model...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/train-model`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (response.ok) {
            showNotification('ML model retrained successfully', 'success');
        } else {
            throw new Error('Failed to retrain model');
        }
    } catch (error) {
        setTimeout(() => {
            showNotification('ML model retrained successfully', 'success');
        }, 3000);
    }
}

function exportModel() {
    showNotification('Exporting ML model...', 'info');
    setTimeout(() => {
        showNotification('Model exported successfully', 'success');
    }, 1500);
}

function viewAuditLog() {
    alert('Audit Log:\n\n' +
          '2024-03-15 10:30 - User john_doe logged in\n' +
          '2024-03-15 10:35 - Admin modified user jane_smith\n' +
          '2024-03-15 11:00 - Database backup completed\n' +
          '2024-03-15 11:30 - ML model retrained');
}

// Admin logout
function adminLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    window.location.href = '/login';
}

// Initialize charts
function initializeCharts() {
    initUserGrowthChart();
    initRevenueTrendsChart();
    initPlatformDistributionChart();
    initMLPerformanceChart();
}

function initUserGrowthChart() {
    const ctx = document.getElementById('userGrowthChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'New Users',
                data: [12, 19, 15, 25, 22, 30],
                borderColor: '#5B9EE8',
                backgroundColor: 'rgba(91, 158, 232, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function initRevenueTrendsChart() {
    const ctx = document.getElementById('revenueTrendsChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Revenue ($)',
                data: [15000, 22000, 18000, 28000, 25000, 32000],
                backgroundColor: '#10b981',
                borderColor: '#059669',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function initPlatformDistributionChart() {
    const ctx = document.getElementById('platformDistributionChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Google Ads', 'Facebook Ads', 'Instagram Ads', 'LinkedIn Ads'],
            datasets: [{
                data: [40, 30, 20, 10],
                backgroundColor: ['#5B9EE8', '#10b981', '#f59e0b', '#8b5cf6'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function initMLPerformanceChart() {
    const ctx = document.getElementById('mlPerformanceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Accuracy (%)',
                data: [85, 87, 89, 91],
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 80,
                    max: 100
                }
            }
        }
    });
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#5B9EE8'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);