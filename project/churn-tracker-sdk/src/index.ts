export interface UserData {
    email: string;
    planType: 'free' | 'pro' | 'enterprise';
    status?: 'active' | 'inactive';
}

export class ChurnTracker {
    private userId: string | null;
    private apiUrl: string;
    private apiKey: string;

    constructor(config: { apiUrl?: string; apiKey: string }) {
        this.userId = null;
        this.apiUrl = config.apiUrl || 'https://flask-hello-world-i02qp96fs-anshulscodes-projects.vercel.app';
        this.apiKey = config.apiKey;
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
        return response.json();
    }

    async initUser(userData: UserData): Promise<string> {
        const response = await this.makeRequest('/track/user', userData);
        if (response.success) {
            this.userId = response.user_id;
            return response.user_id;
        }
        throw new Error(response.error || 'Failed to initialize user');
    }

    async trackFeatureUsage(featureName: string): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized! Call initUser first');
        }

        await this.makeRequest('/track/metrics', {
            user_id: this.userId,
            metrics: {
                feature_name: featureName,
                timestamp: new Date().toISOString()
            }
        });
    }

    async updateUserStatus(status: 'active' | 'inactive'): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized! Call initUser first');
        }

        await this.makeRequest('/track/user/status', {
            user_id: this.userId,
            status: status
        });
    }
}