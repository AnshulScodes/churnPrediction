export interface ChurnPredictionConfig {
  apiKey: string;
  apiUrl?: string;
  debug?: boolean;
}

export interface UserData {
  userId: string;
  features: {
    [key: string]: number | string | boolean;
  };
}

export interface PredictionResult {
  userId: string;
  churnProbability: number;
  timestamp: string;
}

export interface UserInitData {
  email: string;
  planType: string;
}