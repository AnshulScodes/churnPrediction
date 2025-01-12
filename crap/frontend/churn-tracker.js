class ChurnTracker {
    constructor(apiUrl, options = {}) {
        this.apiUrl = apiUrl;
        this.sessionStartTime = Date.now();
        this.lastActiveTime = Date.now();
        this.options = {
            autoTrackSessions: true,
            autoTrackEngagement: true,
            ...options
        };
    }

    // Initialize user
    async initUser(email, planType = 'free') {
        try {
            const response = await fetch(`${this.apiUrl}/track/user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, plan_type: planType })
            });
            const data = await response.json();
            if (data.success) {
                this.userId = data.user_id;
                if (this.options.autoTrackSessions) {
                    this.startSessionTracking();
                }
                return data.user_id;
            }
            throw new Error(data.error);
        } catch (error) {
            console.error('Error initializing user:', error);
            throw error;
        }
    }

    // Track feature usage with proper structure
    async trackFeatureUsage(featureName) {
        if (!this.userId) throw new Error('User not initialized');
        console.log(`Tracking feature usage: ${featureName}`); // Debug log

        try {
            const response = await fetch(`${this.apiUrl}/track/metrics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    type: 'engagement',
                    metrics: {
                        feature_name: featureName
                    }
                })
            });
            const data = await response.json();
            console.log('Feature tracking response:', data); // Debug log
            return data;
        } catch (error) {
            console.error('Error tracking feature:', error);
            throw error;
        }
    }

    // Track page visits
    async trackPageVisit(pageName, timeSpent = 0) {
        if (!this.userId) throw new Error('User not initialized');
        console.log(`Tracking page visit: ${pageName}`); // Debug log

        try {
            const response = await fetch(`${this.apiUrl}/track/metrics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    type: 'behavioral',
                    metrics: {
                        page_visited: pageName,
                        time_spent: timeSpent
                    }
                })
            });
            const data = await response.json();
            console.log('Page tracking response:', data); // Debug log
            return data;
        } catch (error) {
            console.error('Error tracking page visit:', error);
            throw error;
        }
    }

    // Track subscription changes
    async trackSubscription(planType, billingStatus = 'active') {
        if (!this.userId) throw new Error('User not initialized');
        console.log(`Tracking subscription: ${planType}`); // Debug log

        try {
            const response = await fetch(`${this.apiUrl}/track/metrics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    type: 'subscription',
                    metrics: {
                        plan_type: planType,
                        billing_status: billingStatus
                    }
                })
            });
            const data = await response.json();
            console.log('Subscription tracking response:', data); // Debug log
            return data;
        } catch (error) {
            console.error('Error tracking subscription:', error);
            throw error;
        }
    }

    // Auto-tracking session
    startSessionTracking() {
        if (this.sessionInterval) return;

        // Track initial page load
        this.trackPageVisit('initial_load', 0);

        // Update session duration every minute
        this.sessionInterval = setInterval(() => {
            const timeSpent = Math.floor((Date.now() - this.lastActiveTime) / 1000);
            this.trackPageVisit('session_active', timeSpent);
            this.lastActiveTime = Date.now();
        }, 60000); // every minute

        // Track when user leaves
        window.addEventListener('beforeunload', () => {
            const timeSpent = Math.floor((Date.now() - this.sessionStartTime) / 1000);
            this.trackPageVisit('session_end', timeSpent);
            clearInterval(this.sessionInterval);
        });
    }
} 