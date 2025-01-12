// Initialize the tracker
const tracker = new ChurnTracker({
    apiKey: 'r0ATgJZptfqX5TGhUziMD9GsbsfNZBWNL1DvLKdoVmc',
    apiUrl: ''
});

let userId = null;

function log(message) {
    const results = document.getElementById('results');
    results.textContent += `\n${new Date().toISOString()}: ${message}`;
    results.scrollTop = results.scrollHeight;
}

// Initialize user
document.getElementById('initUser').addEventListener('click', async () => {
    try {
        userId = await tracker.initUser({
            email: `test${Date.now()}@example.com`,
            planType: 'free',
            status: 'active'
        });
        log(`User initialized: ${userId}`);
    } catch (error) {
        log(`Error initializing user: ${error.message}`);
    }
});

// Update user status
document.getElementById('updateUser').addEventListener('click', async () => {
    try {
        await tracker.updateUserStatus('inactive');
        log('User status updated to inactive');
    } catch (error) {
        log(`Error updating user: ${error.message}`);
    }
});

// Test features
['1', '2', '3'].forEach(num => {
    document.getElementById(`testFeature${num}`).addEventListener('click', async () => {
        try {
            await tracker.trackFeatureUsage(`feature_${num}`);
            log(`Feature ${num} usage tracked`);
        } catch (error) {
            log(`Error tracking feature ${num}: ${error.message}`);
        }
    });
});