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
export declare class ChurnTracker {
    private userId;
    private apiUrl;
    private apiKey;
    private sessionStartTime;
    constructor(config: {
        apiUrl?: string;
        apiKey: string;
    });
    private makeRequest;
    initUser(userData: UserData): Promise<string>;
    trackFeatureUsage(featureName: string, metadata?: Record<string, any>): Promise<void>;
    startSession(): void;
    endSession(lastActivePage?: string): Promise<void>;
    updateUserStatus(status: 'active' | 'inactive'): Promise<void>;
    trackPageVisit(pageName: string): Promise<void>;
}
