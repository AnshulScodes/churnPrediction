import { TrackerConfig, UserData } from './types';
export declare class ChurnTracker {
    private userId;
    private apiUrl;
    private apiKey;
    constructor(config: TrackerConfig);
    private getHeaders;
    initUser(userData: UserData): Promise<string>;
    trackFeatureUsage(featureName: string): Promise<void>;
    updateUserStatus(status: 'active' | 'inactive'): Promise<void>;
}
