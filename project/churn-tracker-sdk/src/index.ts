export interface UserData {
    email: string;
    planType: 'free' | 'pro' | 'enterprise';
    status?: 'active' | 'inactive';
}

export interface FeatureData {
    feature_name: string;
    user_id: string;
}

export interface SessionData {
    user_id: string;
    duration: number;
    last_active_page?: string;
}

export class ChurnTracker {
    private userId: string | null = null;
    private userEmail: string | null = null;
    private planType: string | null = null;
    private apiUrl: string;
    private apiKey: string;
    private sessionStart: number | null = null;

    constructor(config: { apiUrl?: string; apiKey: string }) {
        this.apiUrl = config.apiUrl || 'https://churn-prediction-nine.vercel.app/';
        this.apiKey = config.apiKey;
    }

    private log(message: string, data?: any) {
        console.log(`[ChurnTracker SDK] ${message}`, data || '');
    }

    private async makeRequest(endpoint: string, data: any): Promise<any> {
        this.log(`Making request to ${endpoint}`, data);
        
        try {
            const response = await fetch(`${this.apiUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(data)
            });

            this.log(`Response status: ${response.status}`);
            const responseData = await response.json();
            this.log(`Response data:`, responseData);

            if (!response.ok) {
                throw new Error(responseData.error || 'Request failed');
            }

            return responseData;
        } catch (error) {
            this.log(`Request failed:`, error);
            throw error;
        }
    }

    async initUser(userData: UserData): Promise<string> {
        this.log('Initializing user with data:', userData);
        
        try {
            const response = await this.makeRequest('/track/user', {
                email: userData.email,
                planType: userData.planType,
                status: userData.status || 'active'
            });

            this.log('User initialization response:', response);

            if (response.success && response.user_id) {
                this.userId = response.user_id;
                this.userEmail = userData.email;
                this.planType = userData.planType;
                this.log('User successfully initialized', {
                    userId: this.userId,
                    email: this.userEmail,
                    planType: this.planType
                });
                return response.user_id;
            }
            throw new Error('Failed to initialize user');
        } catch (error) {
            this.log('Error initializing user:', error);
            throw error;
        }
    }

    async updateUserStatus(status: 'active' | 'inactive'): Promise<void> {
        if (!this.userId || !this.userEmail || !this.planType) {
            throw new Error('User not initialized');
        }

        await this.makeRequest('/track/user', {
            email: this.userEmail,
            planType: this.planType,
            status: status,
            user_id: this.userId
        });
    }

    async trackFeature(featureName: string): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized');
        }

        await this.makeRequest('/track/feature', {
            user_id: this.userId,
            feature_name: featureName
        });
    }

    async trackSession(duration: number): Promise<void> {
        if (!this.userId) {
            throw new Error('User not initialized');
        }

        await this.makeRequest('/track/session', {
            user_id: this.userId,
            duration: duration
        });
    }

    startSession(): void {
        this.sessionStart = Date.now();
    }

    async endSession(): Promise<void> {
        if (!this.sessionStart || !this.userId) return;
        
        const duration = Math.floor((Date.now() - this.sessionStart) / 1000);
        await this.trackSession(duration);
        this.sessionStart = null;
    }

    getUserId(): string | null {
        return this.userId;
    }

    isInitialized(): boolean {
        return Boolean(this.userId && this.userEmail && this.planType);
    }
}

export default ChurnTracker;