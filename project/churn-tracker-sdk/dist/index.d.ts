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
export declare class ChurnTracker {
    private userId;
    private userEmail;
    private planType;
    private apiUrl;
    private apiKey;
    private sessionStart;
    constructor(config: {
        apiUrl?: string;
        apiKey: string;
    });
    private log;
    private makeRequest;
    initUser(userData: UserData): Promise<string>;
    updateUserStatus(status: 'active' | 'inactive'): Promise<void>;
    trackFeature(featureName: string): Promise<void>;
    trackSession(duration: number): Promise<void>;
    startSession(): void;
    endSession(): Promise<void>;
    getUserId(): string | null;
    isInitialized(): boolean;
}
export default ChurnTracker;
