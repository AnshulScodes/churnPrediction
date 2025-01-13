export interface UserData {
    email: string;
    planType: 'free' | 'pro' | 'enterprise';
    status?: 'active' | 'inactive';
}

export interface SessionData {
    duration: number;
    lastActivePage?: string;
}

export interface MetricsData {
    featureName: string;
    metadata?: Record<string, any>;
}

export class ChurnTracker {
    private userId: string | null;
    private apiUrl: string;
    private apiKey: string;
    private sessionStartTime: number | null;

    constructor(config: { apiUrl?: string; apiKey: string }) {
        this.userId = null;
        this.apiUrl = config.apiUrl || 'http://localhost:3000';
        this.apiKey = config.apiKey;
        this.sessionStartTime = null;
    }

    private async makeRequest(endpoint: string, data: any): Promise<any> {
        const response = await fetch(`${this.apiUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }

        return response.json();
    }

    async initUser(userData: UserData): Promise<string> {
        const response = await this.makeRequest('/track/user', userData);
        if (response.success) {
            this.userId = response.user_id;
            this.startSession();
            return response.user_id;
        }
        throw new Error('Failed to initialize user');
    }

    async trackFeatureUsage(featureName: string, metadata?: Record<string, any>): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized! Call initUser first');
        }

        await this.makeRequest('/track/feature', {
            user_id: this.userId,
            feature_name: featureName,
            metadata
        });
    }

    startSession(): void {
        this.sessionStartTime = Date.now();
    }

    async endSession(lastActivePage?: string): Promise<void> {
        if (!this.userId || !this.sessionStartTime) {
            return;
        }

        const duration = Math.floor((Date.now() - this.sessionStartTime) / 1000);
        await this.makeRequest('/track/session', {
            user_id: this.userId,
            duration,
            last_active_page: lastActivePage
        });

        this.sessionStartTime = null;
    }

    async updateUserStatus(status: 'active' | 'inactive'): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized! Call initUser first');
        }

        await this.makeRequest('/track/user', {
            user_id: this.userId,
            status
        });
    }

    // Helper method to track page visits
    async trackPageVisit(pageName: string): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized! Call initUser first');
        }

        await this.trackFeatureUsage(`page_visit_${pageName}`, {
            type: 'page_visit',
            page: pageName,
            timestamp: new Date().toISOString()
        });
    }
}