"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChurnTracker = void 0;
class ChurnTracker {
    constructor(config) {
        this.userId = null;
        console.log('Initializing ChurnTracker...', { config });
        this.apiUrl = config.apiUrl || 'https://flask-hello-world-i02qp96fs-anshulscodes-projects.vercel.app';
        this.apiKey = config.apiKey || '';
    }
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
        };
    }
    async initUser(userData) {
        console.log('Initializing user...', { userData });
        try {
            const response = await fetch(`${this.apiUrl}/track/user`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(userData)
            });
            const data = await response.json();
            console.log('User initialization response:', data);
            if (!data.success)
                throw new Error(data.error);
            if (!data.user_id)
                throw new Error('No user ID returned from server');
            this.userId = data.user_id;
            return data.user_id;
        }
        catch (error) {
            console.error('Failed to initialize user:', error);
            throw error;
        }
    }
    async trackFeatureUsage(featureName) {
        console.log('Tracking feature usage...', { featureName, userId: this.userId });
        if (!this.userId)
            throw new Error('User not initialized');
        try {
            const response = await fetch(`${this.apiUrl}/track/metrics`, {
                method: 'POST',
                headers: this.getHeaders(),
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
            if (!data.success)
                throw new Error(data.error);
        }
        catch (error) {
            console.error('Failed to track feature usage:', error);
            throw error;
        }
    }
    async updateUserStatus(status) {
        if (!this.userId)
            throw new Error('User not initialized');
        try {
            const response = await fetch(`${this.apiUrl}/track/user/status`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({
                    user_id: this.userId,
                    status: status
                })
            });
            const data = await response.json();
            if (!data.success)
                throw new Error(data.error);
        }
        catch (error) {
            console.error('Failed to update user status:', error);
            throw error;
        }
    }
}
exports.ChurnTracker = ChurnTracker;
