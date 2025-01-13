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
        this.apiUrl = config.apiUrl || 'http://localhost:3000';
        this.apiKey = config.apiKey;
        this.sessionStartTime = null;
    }
    makeRequest(endpoint, data) {
        return __awaiter(this, void 0, void 0, function* () {
            const response = yield fetch(`${this.apiUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const error = yield response.json();
                throw new Error(error.error || 'Request failed');
            }
            return response.json();
        });
    }
    initUser(userData) {
        return __awaiter(this, void 0, void 0, function* () {
            const response = yield this.makeRequest('/track/user', userData);
            if (response.success) {
                this.userId = response.user_id;
                this.startSession();
                return response.user_id;
            }
            throw new Error('Failed to initialize user');
        });
    }
    trackFeatureUsage(featureName, metadata) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId) {
                throw new Error('User not initialized! Call initUser first');
            }
            yield this.makeRequest('/track/feature', {
                user_id: this.userId,
                feature_name: featureName,
                metadata
            });
        });
    }
    startSession() {
        this.sessionStartTime = Date.now();
    }
    endSession(lastActivePage) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId || !this.sessionStartTime) {
                return;
            }
            const duration = Math.floor((Date.now() - this.sessionStartTime) / 1000);
            yield this.makeRequest('/track/session', {
                user_id: this.userId,
                duration,
                last_active_page: lastActivePage
            });
            this.sessionStartTime = null;
        });
    }
    updateUserStatus(status) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId) {
                throw new Error('User not initialized! Call initUser first');
            }
            yield this.makeRequest('/track/user', {
                user_id: this.userId,
                status
            });
        });
    }
    // Helper method to track page visits
    trackPageVisit(pageName) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.userId) {
                throw new Error('User not initialized! Call initUser first');
            }
            yield this.trackFeatureUsage(`page_visit_${pageName}`, {
                type: 'page_visit',
                page: pageName,
                timestamp: new Date().toISOString()
            });
        });
    }
}
exports.ChurnTracker = ChurnTracker;
