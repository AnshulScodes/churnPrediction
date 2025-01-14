"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChurnTracker = void 0;
class ChurnTracker {
    constructor(config) {
        this.userId = null;
        this.userEmail = null;
        this.planType = null;
        this.sessionStart = null;
        this.apiUrl = config.apiUrl || 'http://localhost:3000';
        this.apiKey = config.apiKey;
    }
    log(message, data) {
        console.log(`[ChurnTracker SDK] ${message}`, data || '');
    }
    makeRequest(endpoint, data) {
        return __awaiter(this, void 0, void 0, function* () {
            this.log(`Making request to ${endpoint}`, data);
            try {
                const response = yield fetch(`${this.apiUrl}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.apiKey}`
                    },
                    body: JSON.stringify(data)
                });
                this.log(`Response status: ${response.status}`);
                const responseData = yield response.json();
                this.log(`Response data:`, responseData);
                if (!response.ok) {
                    throw new Error(responseData.error || 'Request failed');
                }
                return responseData;
            }
            catch (error) {
                this.log(`Request failed:`, error);
                throw error;
            }
        });
    }
    initUser(userData) {
        return __awaiter(this, void 0, void 0, function* () {
            this.log('Initializing user with data:', userData);
            try {
                const response = yield this.makeRequest('/track/user', {
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
            }
            catch (error) {
                this.log('Error initializing user:', error);
                throw error;
            }
        });
    }
    updateUserStatus(status) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId || !this.userEmail || !this.planType) {
                throw new Error('User not initialized');
            }
            yield this.makeRequest('/track/user', {
                email: this.userEmail,
                planType: this.planType,
                status: status,
                user_id: this.userId
            });
        });
    }
    trackFeature(featureName) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId) {
                throw new Error('User not initialized');
            }
            yield this.makeRequest('/track/feature', {
                user_id: this.userId,
                feature_name: featureName
            });
        });
    }
    trackSession(duration) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId) {
                throw new Error('User not initialized');
            }
            yield this.makeRequest('/track/session', {
                user_id: this.userId,
                duration: duration
            });
        });
    }
    startSession() {
        this.sessionStart = Date.now();
    }
    endSession() {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.sessionStart || !this.userId)
                return;
            const duration = Math.floor((Date.now() - this.sessionStart) / 1000);
            yield this.trackSession(duration);
            this.sessionStart = null;
        });
    }
    getUserId() {
        return this.userId;
    }
    isInitialized() {
        return Boolean(this.userId && this.userEmail && this.planType);
    }
}
exports.ChurnTracker = ChurnTracker;
exports.default = ChurnTracker;
