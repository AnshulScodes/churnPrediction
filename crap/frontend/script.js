// PostHog will automatically track pageviews and clicks
// We just need to add any custom events or properties we want to track

// Function to get user stats from PostHog
async function getStats() {
    try {
        const distinctId = posthog.get_distinct_id();
        const response = await fetch(`/stats/${distinctId}`);
        const stats = await response.json();
        
        document.getElementById('stats').innerHTML = `
            <h3>User Activity:</h3>
            <pre>${JSON.stringify(stats, null, 2)}</pre>
        `;
    } catch (error) {
        console.error('Error getting stats:', error);
        document.getElementById('stats').innerHTML = 'Error loading stats';
    }
}

// Update stats every minute
setInterval(getStats, 60000);

// Initial load
document.addEventListener('DOMContentLoaded', getStats);

// Example of adding custom properties to automatic tracking
posthog.register({
    'app_version': '1.0.0',
    'user_type': 'beta'
});

// Example of tracking a custom event
function trackCustomEvent(eventName, properties = {}) {
    posthog.capture(eventName, properties);
}

// Generate session ID on page load
const SESSION_ID = 'session_' + Math.random().toString(36).substr(2, 9);

// Add headers to all fetch requests
const headers = {
    'Content-Type': 'application/json',
    'X-User-ID': USER_ID,
    'X-Session-ID': SESSION_ID
};

// Track page view
async function trackPageView(url) {
    try {
        const response = await fetch('/track/pageview', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                page_url: url,
                timestamp: new Date().toISOString()
            })
        });
    } catch (error) {
        console.error('Error tracking page view:', error);
    }
}

// Track button click
async function trackButtonClick(buttonId) {
    try {
        const response = await fetch('/track/button', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                button_id: buttonId,
                page_url: window.location.href,
                timestamp: new Date().toISOString()
            })
        });
    } catch (error) {
        console.error('Error tracking button click:', error);
    }
}

// Track feature usage
async function trackFeatureUsage(featureName, durationSeconds) {
    try {
        const response = await fetch('/track/feature', {
            method: 'POST',
            headers,
            body: JSON.stringify({
                feature_name: featureName,
                duration_seconds: durationSeconds,
                timestamp: new Date().toISOString()
            })
        });
    } catch (error) {
        console.error('Error tracking feature usage:', error);
    }
}

// Update user metadata
async function updateUserMetadata(metadata) {
    try {
        const response = await fetch('/user/metadata', {
            method: 'POST',
            headers,
            body: JSON.stringify(metadata)
        });
    } catch (error) {
        console.error('Error updating metadata:', error);
    }
}

// Track session start
window.addEventListener('load', () => {
    trackPageView(window.location.href);
});

// Track session end
window.addEventListener('beforeunload', () => {
    // Send final session data
    navigator.sendBeacon('/track/session/end', JSON.stringify({
        session_id: SESSION_ID,
        end_time: new Date().toISOString()
    }));
});