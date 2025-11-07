// ==================== GLOBAL CONFIGURATION ====================
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// ==================== API HELPER FUNCTIONS ====================

/**
 * Generic API call function with JWT support
 */
async function apiCall(endpoint, method = 'GET', data = null, requiresAuth = true) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    // Add JWT token if required
    if (requiresAuth) {
        const token = localStorage.getItem('access_token');
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        } else {
            // Redirect to login if no token found
            window.location.href = '/login';
            throw new Error('No authentication token found');
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        // Handle unauthorized (token expired)
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            localStorage.removeItem('user_name');
            localStorage.removeItem('user_email');
            window.location.href = '/login';
            throw new Error('Authentication failed');
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Login user
 */
async function loginUser(email, password) {
    return await apiCall('/login', 'POST', { email, password }, false);
}

/**
 * Signup new user
 */
async function signupUser(name, email, password) {
    return await apiCall('/register', 'POST', { username: name, email, password }, false);
}

/**
 * Get user metrics
 */
async function getMetrics() {
    return await apiCall('/get_metrics', 'GET');
}

/**
 * Get ML predictions
 */
async function getPredictions(data) {
    return await apiCall('/predict', 'POST', data);
}

/**
 * Get recommendations
 */
async function getRecommendations() {
    return await apiCall('/recommendations', 'GET');
}

/**
 * Train ML models
 */
async function trainModels() {
    return await apiCall('/train-model', 'POST');
}

/**
 * Apply optimization
 */
async function applyOptimization(data) {
    return await apiCall('/optimize', 'POST', data);
}

// ==================== AUTHENTICATION HELPERS ====================

/**
 * Check if user is logged in
 */
function checkLogin() {
    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id');

    if (!token || !userId) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

function goHome() {
    localStorage.removeItem('access_token');   // optional: start fresh
    localStorage.removeItem('user_id');
    window.location.replace('/');              // instant, no flicker
}

/**
 * Logout user
 */
async function logout() {
    try {
        await apiCall('/logout', 'POST');
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');

    window.location.href = '/'; // Redirect to index page after logout
}

/**
 * Get current user ID
 */
function getUserId() {
    return localStorage.getItem('user_id');
}

// ==================== UI HELPER FUNCTIONS ====================

/**
 * Show/hide loading spinner
 */
function toggleLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}

/**
 * Show error message
 */
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

/**
 * Show success message
 */
function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Format currency
 */
function formatCurrency(num) {
    return '$' + formatNumber(num.toFixed(2));
}

/**
 * Format percentage
 */
function formatPercentage(num) {
    return (num * 100).toFixed(2) + '%';
}

// ==================== LOGIN PAGE ====================

function initLoginPage() {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                toggleLoading('loading', true);
                
                // Call the API directly with proper parameters
                const response = await apiCall('/login', 'POST', { email, password }, false);

                if (response.status === 'success') {
                    // Store user data and token
                    localStorage.setItem('access_token', response.access_token);
                    localStorage.setItem('user_id', response.user_id);
                    localStorage.setItem('user_name', response.username || 'User');
                    localStorage.setItem('user_email', email);

                    console.log("✅ Login successful, redirecting to dashboard...");
                    window.location.href = '/dashboard';
                } else {
                    showError('errorMessage', response.message || 'Invalid email or password');
                }
            } catch (error) {
                console.error("Login error:", error);
                showError('errorMessage', 'Login failed. Please check if the server is running.');
            } finally {
                toggleLoading('loading', false);
            }
        });
    }
}

// ==================== SIGNUP PAGE ====================

function initSignupPage() {
    const signupForm = document.getElementById('signupForm');

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // Validate passwords match
            if (password !== confirmPassword) {
                showError('errorMessage', 'Passwords do not match');
                return;
            }

            // Validate password length
            if (password.length < 6) {
                showError('errorMessage', 'Password must be at least 6 characters long');
                return;
            }

            try {
                toggleLoading('loading', true);
                const response = await signupUser(name, email, password);

                if (response.status === 'success') {
                    showSuccess('successMessage', 'Account created successfully! Redirecting to login...');
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 2000);
                } else {
                    showError('errorMessage', response.message || 'Signup failed');
                }
            } catch (error) {
                showError('errorMessage', 'Signup failed. Please check if the server is running.');
            } finally {
                toggleLoading('loading', false);
            }
        });
    }
}

// ==================== DASHBOARD PAGE ====================

function initDashboard() {
    if (!checkLogin()) return;

    loadDashboardMetrics();

    // Sync button
    const syncButton = document.getElementById('syncData');
    if (syncButton) {
        syncButton.addEventListener('click', loadDashboardMetrics);
    }

    // Time range filter
    const timeRangeSelect = document.getElementById('timeRange');
    if (timeRangeSelect) {
        timeRangeSelect.addEventListener('change', loadDashboardMetrics);
    }
}

async function loadDashboardMetrics() {
    try {
        toggleLoading('loading', true);
        const response = await getMetrics();

        if (response.status === 'success' && response.data) {
            displayMetrics(response.data);
        } else {
            // Display sample data if no data available
            displaySampleMetrics();
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
        displaySampleMetrics();
    } finally {
        toggleLoading('loading', false);
    }
}

function displayMetrics(data) {
    if (data.ctr !== undefined) {
        document.getElementById('ctrValue').textContent = formatPercentage(data.ctr);
    }
    if (data.cpc !== undefined) {
        document.getElementById('cpcValue').textContent = formatCurrency(data.cpc);
    }
    if (data.conversions !== undefined) {
        document.getElementById('conversionsValue').textContent = formatNumber(data.conversions);
    }
    if (data.roas !== undefined) {
        document.getElementById('roasValue').textContent = data.roas.toFixed(2) + 'x';
    }
    if (data.spend !== undefined) {
        document.getElementById('spendValue').textContent = formatCurrency(data.spend);
    }
    if (data.engagement !== undefined) {
        document.getElementById('engagementValue').textContent = formatPercentage(data.engagement);
    }
}

function displaySampleMetrics() {
    const sampleData = {
        ctr: 0.0342,
        cpc: 18.50,
        conversions: 1247,
        roas: 4.2,
        spend: 12450,
        engagement: 0.0567
    };
    displayMetrics(sampleData);
}

// ==================== ML INSIGHTS PAGE ====================

function initMLInsights() {
    if (!checkLogin()) return;

    const predictButton = document.getElementById('getPredictions');
    if (predictButton) {
        predictButton.addEventListener('click', runPredictions);
    }

    // Load any existing predictions
    loadExistingPredictions();
}

async function runPredictions() {
    const impressions = parseFloat(document.getElementById('impressions').value) || 10000;
    const spend = parseFloat(document.getElementById('spend').value) || 1200;
    const ctr = parseFloat(document.getElementById('ctr').value) || 3.0; // Keep as percentage
    const cpc = parseFloat(document.getElementById('cpc').value) || 15.2;

    const data = {
        impressions: impressions,
        spend: spend,
        current_CTR: ctr / 100, // Convert to decimal for backend
        current_CPC: cpc,
        engagement_rate: 0.05
    };

    try {
        toggleLoading('predictionLoading', true);
        const response = await getPredictions(data);

        if (response.status === 'success') {
            displayPredictions(response);
            showSuccess('predictionSuccess', 'Predictions generated successfully!');
        } else {
            showError('predictionError', response.message || 'Failed to get predictions');
        }
    } catch (error) {
        console.error('Prediction error:', error);
        showError('predictionError', 'Failed to get predictions. Please check if the server is running.');
    } finally {
        toggleLoading('predictionLoading', false);
    }
}

function displayPredictions(data) {
    const tableBody = document.getElementById('predictionTableBody');

    if (tableBody) {
        const row = `
            <tr>
                <td>Current Campaign</td>
                <td>${formatPercentage(data.predicted_CTR || 0.035)}</td>
                <td>${formatCurrency(data.predicted_CPC || 16.8)}</td>
                <td><span class="recommendation-badge badge-${(data.label || 'High').toLowerCase()}">${data.label || 'High'}</span></td>
                <td>${data.recommendation || 'Performance is within expected range. Continue monitoring.'}</td>
            </tr>
        `;
        tableBody.innerHTML = row;
    }

    displayMLRecommendations(data);
}

function displayMLRecommendations(data) {
    const recommendationsDiv = document.getElementById('mlRecommendations');

    if (recommendationsDiv) {
        const ctrImprovement = data.predicted_CTR - (parseFloat(document.getElementById('ctr').value) / 100);
        
        const recommendations = [
            {
                title: 'Budget Optimization',
                description: data.recommendation || `Consider ${ctrImprovement > 0 ? 'increasing' : 'adjusting'} budget based on predicted performance`,
                badge: data.label || 'High'
            },
            {
                title: 'Channel Strategy',
                description: `Predicted performance level: ${data.label || 'High'} with strong potential`,
                badge: 'Recommended'
            },
            {
                title: 'Performance Insights',
                description: `CTR improvement: ${(ctrImprovement * 100).toFixed(2)}% predicted`,
                badge: 'Insight'
            }
        ];

        let html = '<h3>AI Recommendations</h3><div class="recommendations-grid">';
        recommendations.forEach(rec => {
            html += `
                <div class="recommendation-card">
                    <h4>${rec.title}</h4>
                    <p>${rec.description}</p>
                    <span class="recommendation-badge badge-${rec.badge.toLowerCase().includes('high') ? 'high' : rec.badge.toLowerCase().includes('medium') ? 'medium' : 'low'}">${rec.badge}</span>
                </div>
            `;
        });
        html += '</div>';
        
        recommendationsDiv.innerHTML = html;
    }
}

async function loadExistingPredictions() {
    try {
        // Load any previously saved predictions
        const response = await apiCall('/recommendations', 'GET');
        if (response.status === 'success' && response.recommendations) {
            // You can display historical predictions here if needed
        }
    } catch (error) {
        console.error('Error loading existing predictions:', error);
    }
}

// ==================== OPTIMIZATION PAGE ====================

function initOptimization() {
    if (!checkLogin()) return;

    const optimizeButton = document.getElementById('runOptimization');
    if (optimizeButton) {
        optimizeButton.addEventListener('click', runOptimization);
    }

    const budgetSlider = document.getElementById('budgetRange');
    const confidenceSlider = document.getElementById('confidence');

    if (budgetSlider) {
        budgetSlider.addEventListener('input', function () {
            document.getElementById('budgetValue').textContent = formatCurrency(parseFloat(this.value));
        });
        // Set initial value
        document.getElementById('budgetValue').textContent = formatCurrency(parseFloat(budgetSlider.value));
    }

    if (confidenceSlider) {
        confidenceSlider.addEventListener('input', function () {
            document.getElementById('confidenceValue').textContent = this.value + '%';
        });
        // Set initial value
        document.getElementById('confidenceValue').textContent = confidenceSlider.value + '%';
    }

    loadRecommendations();
}

async function runOptimization() {
    const budgetRange = parseFloat(document.getElementById('budgetRange').value) || 5000;
    const confidence = parseFloat(document.getElementById('confidence').value) || 75;
    const frequency = document.getElementById('frequency').value || 'daily';
    const autoBudget = document.getElementById('autoBudget').checked;
    const autoABTest = document.getElementById('autoABTest').checked;

    const data = {
        budget_range: budgetRange,
        confidence_threshold: confidence / 100, // Convert percentage to decimal
        frequency: frequency,
        auto_budget: autoBudget,
        auto_ab_test: autoABTest
    };

    try {
        toggleLoading('optimizationLoading', true);
        const response = await applyOptimization(data);

        if (response.status === 'success') {
            displayOptimizationResults(response.optimization_results);
            showSuccess('optimizationSuccess', 'Optimization completed successfully!');
        } else {
            showError('optimizationError', response.message || 'Optimization failed');
        }
    } catch (error) {
        console.error('Optimization error:', error);
        showError('optimizationError', 'Failed to run optimization. Please check if the server is running.');
    } finally {
        toggleLoading('optimizationLoading', false);
    }
}

function displayOptimizationResults(results) {
    const tableBody = document.getElementById('optimizationTableBody');

    if (tableBody) {
        let html = '';

        if (results && results.length > 0) {
            results.forEach(result => {
                const confidenceClass = result.confidence > 0.8 ? 'high' : result.confidence > 0.6 ? 'medium' : 'low';

                html += `
                    <tr>
                        <td>${result.campaign || 'Unnamed Campaign'}</td>
                        <td>${result.action || 'No action required'}</td>
                        <td>${Math.round(result.confidence * 100)}%</td>
                        <td><span class="recommendation-badge badge-${confidenceClass}">${confidenceClass.toUpperCase()}</span></td>
                    </tr>
                `;
            });
        } else {
            const sampleResults = [
                { campaign: 'Google Ads Q4', action: 'Increase budget by 15%', confidence: 0.85 },
                { campaign: 'Facebook Prospecting', action: 'Decrease budget by 20%', confidence: 0.72 },
                { campaign: 'Instagram Story Ads', action: 'Maintain current budget', confidence: 0.63 }
            ];

            sampleResults.forEach(result => {
                const confidenceClass = result.confidence > 0.8 ? 'high' : result.confidence > 0.6 ? 'medium' : 'low';

                html += `
                    <tr>
                        <td>${result.campaign}</td>
                        <td>${result.action}</td>
                        <td>${Math.round(result.confidence * 100)}%</td>
                        <td><span class="recommendation-badge badge-${confidenceClass}">${confidenceClass.toUpperCase()}</span></td>
                    </tr>
                `;
            });
        }

        tableBody.innerHTML = html;
    }
}

async function loadRecommendations() {
    try {
        const response = await getRecommendations();

        if (response.status === 'success' && response.recommendations) {
            displayRecommendations(response.recommendations);
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');

    if (container) {
        let html = '';

        recommendations.forEach(rec => {
            html += `
                <div class="recommendation-item">
                    <h4>${rec.campaign}</h4>
                    <p><strong>Predicted CTR:</strong> ${formatPercentage(rec.predicted_ctr)}</p>
                    <p><strong>Best Channel:</strong> ${rec.best_channel}</p>
                    <p><strong>Budget Change:</strong> ${rec.recommended_budget_pct > 0 ? '+' : ''}${rec.recommended_budget_pct}%</p>
                </div>
            `;
        });

        container.innerHTML = html;
    }
}

// ==================== NAVIGATION AND INITIALIZATION ====================
   /**
 * Initialize navigation and user info
 */
function initNavigation() {
    const userName = localStorage.getItem('user_name');
    if (userName) {
        const userElements = document.querySelectorAll('.user-name');
        userElements.forEach(el => {
            el.textContent = userName;
        });
    }

    const logoutButtons = document.querySelectorAll('.btn-logout');
    logoutButtons.forEach(button => {
        button.addEventListener('click', logout);
    });
    
    // Fix home navigation - remove the problematic prevention logic
}

/**
 * Initialize page based on current page
 */
function initPage() {
    initNavigation();

    const currentPath = window.location.pathname;

    // Handle Flask routes
    if (currentPath === '/login' || currentPath.endsWith('/login')) {
        initLoginPage();
    } else if (currentPath === '/signup' || currentPath.endsWith('/signup')) {
        initSignupPage();
    } else if (currentPath === '/dashboard' || currentPath.endsWith('/dashboard')) {
        initDashboard();
    } else if (currentPath === '/ml_insights' || currentPath.endsWith('/ml_insights')) {
        initMLInsights();
    } else if (currentPath === '/optimization' || currentPath.endsWith('/optimization')) {
        initOptimization();
    } else if (currentPath === '/' || currentPath.endsWith('index.html')) {
        // Home page - redirect to dashboard if already logged in
        const token = localStorage.getItem('access_token');
        if (token) {
            window.location.href = '/';
        }
    }
}

// Make logout function globally available
window.logout = logout;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initPage);
