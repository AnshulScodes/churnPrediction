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

    // Track engagement metrics
    async trackEngagement(metrics = {}) {
        if (!this.userId) throw new Error('User not initialized');
        
        const sessionDuration = (Date.now() - this.sessionStartTime) / 1000 / 60; // in minutes
        
        return this.trackMetrics('engagement', {
            last_active_date: new Date().toISOString(),
            average_session_duration: sessionDuration,
            ...metrics
        });
    }

    // Track subscription events
    async trackSubscription(status, cancellationAttempted = false) {
        return this.trackMetrics('subscription', {
            billing_status: status,
            cancellation_attempt: cancellationAttempted
        });
    }

    // Track support interactions
    async trackSupport(ticketOpened = false, ticketClosed = false, resolutionTime = null) {
        return this.trackMetrics('support', {
            open_tickets: ticketOpened ? 1 : (ticketClosed ? -1 : 0),
            average_ticket_resolution_time: resolutionTime
        });
    }

    // Track communication events
    async trackCommunication(emailOpened = false, notificationClicked = false) {
        return this.trackMetrics('communication', {
            email_open_rate: emailOpened ? 1 : 0,
            notification_click_rate: notificationClicked ? 1 : 0
        });
    }

    // Track behavioral patterns
    async trackBehavior(onboardingCompleted = false, usageDecline = null) {
        return this.trackMetrics('behavioral', {
            onboarding_completion: onboardingCompleted,
            usage_decline: usageDecline
        });
    }

    // Generic metric tracking
    async trackMetrics(type, metrics) {
        if (!this.userId) throw new Error('User not initialized');
        
        try {
            const response = await fetch(`${this.apiUrl}/track/metrics`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    type,
                    metrics
                })
            });
            return await response.json();
        } catch (error) {
            console.error(`Error tracking ${type} metrics:`, error);
            throw error;
        }
    }

    // Auto-tracking session
    startSessionTracking() {
        if (this.sessionInterval) return;

        // Update session duration every minute
        this.sessionInterval = setInterval(() => {
            this.trackEngagement({
                login_frequency: 1,
                feature_usage_frequency: 1
            });
        }, 60000); // every minute

        // Track when user leaves
        window.addEventListener('beforeunload', () => {
            this.trackEngagement();
            clearInterval(this.sessionInterval);
        });
    }

    // Feature usage tracking
    async trackFeatureUsage(featureName) {
        return this.trackEngagement({
            feature_usage_frequency: 1
        });
    }
} 