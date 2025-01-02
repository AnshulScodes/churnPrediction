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