export interface TrackerConfig {
    apiKey: string;
    apiUrl?: string;
}
export interface UserData {
    email: string;
    planType: 'free' | 'pro' | 'enterprise';
}
export interface FeatureData {
    name: string;
    metadata?: Record<string, any>;
}
