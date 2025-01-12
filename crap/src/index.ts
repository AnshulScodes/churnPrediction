import { ChurnPredictionConfig, UserData, PredictionResult, UserInitData } from './types';

export class ChurnTracker {
  private config: ChurnPredictionConfig;
  private apiUrl: string;

  constructor(config: ChurnPredictionConfig) {
    this.config = config;
    this.apiUrl = config.apiUrl || 'http://localhost:5000';
  }

  async initUser(userData: UserInitData): Promise<string> {
    try {
      const response = await fetch(`${this.apiUrl}/init-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.userId;
    } catch (error) {
      if (this.config.debug) {
        console.error('User initialization failed:', error);
      }
      throw error;
    }
  }

  async trackFeatureUsage(featureName: string): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/track-feature`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({ feature: featureName })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      if (this.config.debug) {
        console.error('Feature tracking failed:', error);
      }
      throw error;
    }
  }

  async predictChurn(userData: UserData): Promise<PredictionResult> {
    try {
      const response = await fetch(`${this.apiUrl}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (this.config.debug) {
        console.error('Churn prediction failed:', error);
      }
      throw error;
    }
  }
}

export * from './types';