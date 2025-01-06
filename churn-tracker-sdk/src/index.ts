import { UserData, TrackerConfig } from './types';

class ChurnTracker {
    private apiKey: string;
    private apiUrl: string;
    private userId: string | null = null;

    constructor(config: TrackerConfig) {
        console.log('Initializing ChurnTracker...', { config });
        if (!config.apiKey) throw new Error('API key is required');
        this.apiKey = config.apiKey;
        this.apiUrl = config.apiUrl || 'http://localhost:5000';
    }

    async initUser(userData: UserData): Promise<string> {
        console.log('Initializing user...', { userData });
        try {
            const response = await fetch(`${this.apiUrl}/track/user`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            console.log('User initialization response:', data);

            if (!data.success) throw new Error(data.error);
            if (!data.user_id) throw new Error('No user ID returned from server');
            
            this.userId = data.user_id;
            return data.user_id;
        } catch (error) {
            console.error('Failed to initialize user:', error);
            throw error;
        }
    }

    async trackFeatureUsage(featureName: string): Promise<void> {
        console.log('Tracking feature usage...', { featureName, userId: this.userId });
        if (!this.userId) throw new Error('User not initialized');

        try {
            const response = await fetch(`${this.apiUrl}/track/metrics`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    type: 'engagement',
                    metrics: {
                        feature_name: featureName
                    }
                })
            });

            const data = await response.json();
            console.log('Feature tracking response:', data);

            if (!data.success) throw new Error(data.error);
        } catch (error) {
            console.error('Failed to track feature usage:', error);
            throw error;
        }
    }
}

module.exports = { ChurnTracker };
