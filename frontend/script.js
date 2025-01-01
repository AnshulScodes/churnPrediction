const USER_ID = 'test_user_' + Math.random().toString(36).substr(2, 9);
const API_URL = 'http://localhost:5000';

async function trackEvent(eventType, eventData = {}) {
    try {
        const response = await fetch(`${API_URL}/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: USER_ID,
                event_type: eventType,
                event_data: eventData
            })
        });
        console.log(`Tracked ${eventType} event`);
    } catch (error) {
        console.error('Error tracking event:', error);
    }
}

async function makeApiCall() {
    await trackEvent('api_call', { endpoint: '/example' });
    document.getElementById('stats').innerHTML = 'API call tracked!';
}

async function changePreference() {
    await trackEvent('preference_change', { theme: 'dark' });
    document.getElementById('stats').innerHTML = 'Preference change tracked!';
}

async function getStats() {
    try {
        const response = await fetch(`${API_URL}/stats/${USER_ID}`);
        const stats = await response.json();
        document.getElementById('stats').innerHTML = `
            <h3>User Stats:</h3>
            <p>API Calls: ${stats.api_calls}</p>
            <p>Button Clicks: ${stats.button_clicks}</p>
            <p>Preference Changes: ${stats.preference_changes}</p>
        `;
    } catch (error) {
        console.error('Error getting stats:', error);
    }
}

// Track page load
trackEvent('page_view'); 