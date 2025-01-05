// Initialize the tracker
const tracker = new ChurnTracker('http://localhost:5000', {
    autoTrackSessions: true,
    autoTrackEngagement: true
});

let currentUser = null;

// User Authentication
async function loginUser() {
    const email = document.getElementById('email').value;
    const planType = document.getElementById('plan-type').value;

    try {
        // Initialize user in tracking system
        const userId = await tracker.initUser(email, planType);
        
        // Store user info
        currentUser = {
            email,
            planType,
            userId
        };

        // Update UI
        document.getElementById('user-email').textContent = email;
        document.getElementById('user-plan').textContent = planType;
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('user-info').style.display = 'block';
        
        // Show other sections
        document.getElementById('features-section').style.display = 'block';
        document.getElementById('support-section').style.display = 'block';
        document.getElementById('communication-section').style.display = 'block';
        document.getElementById('stats-section').style.display = 'block';

        // Load initial stats
        refreshStats();

    } catch (error) {
        console.error('Login failed:', error);
        alert('Login failed. Please try again.');
    }
}

function logoutUser() {
    currentUser = null;
    
    // Reset UI
    document.getElementById('login-form').style.display = 'flex';
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('features-section').style.display = 'none';
    document.getElementById('support-section').style.display = 'none';
    document.getElementById('communication-section').style.display = 'none';
    document.getElementById('stats-section').style.display = 'none';
}

// Feature Usage
async function useFeature(featureName) {
    if (!currentUser) return;

    try {
        console.log(`Using feature: ${featureName}`); // Debug log
        await tracker.trackFeatureUsage(featureName);
        console.log(`Feature ${featureName} tracked successfully`);
        refreshStats();
    } catch (error) {
        console.error(`Error using feature ${featureName}:`, error);
    }
}

// Support Tickets
async function openSupportTicket() {
    if (!currentUser) return;

    try {
        console.log('Opening support ticket'); // Debug log
        await tracker.trackFeatureUsage('support_ticket_open');
        console.log('Support ticket tracked');
        refreshStats();
    } catch (error) {
        console.error('Error opening support ticket:', error);
    }
}

async function closeSupportTicket() {
    if (!currentUser) return;

    try {
        await tracker.trackSupport(false, true, 24); // Assuming 24 hours resolution time
        console.log('Support ticket closed');
        refreshStats();
    } catch (error) {
        console.error('Error closing support ticket:', error);
    }
}

// Communication Tracking
async function handleNotificationClick() {
    if (!currentUser) return;

    try {
        console.log('Clicking notification'); // Debug log
        await tracker.trackFeatureUsage('notification_click');
        console.log('Notification click tracked');
        refreshStats();
    } catch (error) {
        console.error('Error tracking notification click:', error);
    }
}

async function handleEmailOpen() {
    if (!currentUser) return;

    try {
        console.log('Opening email'); // Debug log
        await tracker.trackFeatureUsage('email_open');
        console.log('Email open tracked');
        refreshStats();
    } catch (error) {
        console.error('Error tracking email open:', error);
    }
}

// Stats Refresh
async function refreshStats() {
    if (!currentUser) return;

    try {
        const response = await fetch(`http://localhost:5000/get/metrics/${currentUser.userId}`);
        const data = await response.json();
        
        if (data.success) {
            const statsContent = document.getElementById('stats-content');
            statsContent.innerHTML = formatStats(data.metrics);
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Helper function to format stats
function formatStats(metrics) {
    let html = '';
    
    for (const [table, data] of Object.entries(metrics)) {
        if (data) {
            html += `<h3>${table.replace(/_/g, ' ').toUpperCase()}</h3>`;
            html += '<ul>';
            for (const [key, value] of Object.entries(data)) {
                if (key !== 'user_id' && key !== 'id') {
                    html += `<li>${key.replace(/_/g, ' ')}: ${value}</li>`;
                }
            }
            html += '</ul>';
        }
    }
    
    return html;
} 