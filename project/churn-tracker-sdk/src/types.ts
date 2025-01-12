export interface TrackerConfig {
    apiUrl?: string;
    apiKey: string;
}

export interface UserData {
    email: string;
    planType: 'free' | 'pro' | 'enterprise';
    status?: 'active' | 'inactive';
}

export interface MetricsData {
    feature_name: string;
    timestamp: string;
}