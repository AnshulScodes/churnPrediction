const { ChurnTracker } = require('../churn-tracker-sdk/dist');

async function testSDK() {
    try {
        // Initialize tracker
        const tracker = new ChurnTracker({
            apiKey: '',  // Add your API key here
            apiUrl: 'http://localhost:5000'
        });

        console.log('Testing SDK...');

        // Initialize user
        const userId = await tracker.initUser({
            email: 'brrr@skibidi.com',
            planType: 'free'
        });
        console.log('User initialized:', userId);

        // Track feature
        await tracker.trackFeatureUsage('search');
        console.log('Feature tracked successfully');

    } catch (error) {
        console.error('Test failed:', error);
    }
}

testSDK();