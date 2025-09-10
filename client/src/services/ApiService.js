const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('raton_perez_token');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Auth endpoints
  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async refreshToken() {
    return this.request('/api/auth/refresh', {
      method: 'POST',
    });
  }

  // User endpoints
  async getUserProfile() {
    return this.request('/api/user/profile');
  }

  async updateUserProfile(profileData) {
    return this.request('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  // Routes endpoints
  async getUserRoutes() {
    return this.request('/api/routes/user');
  }

  async visitPlace(placeId, location) {
    return this.request('/api/routes/visit', {
      method: 'POST',
      body: JSON.stringify({ place_id: placeId, location }),
    });
  }

  // Chat endpoints
  async sendChatMessage(message, context = {}) {
    return this.request('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, context }),
    });
  }

  // Family endpoints (si necesitas múltiples usuarios)
  async createFamily(familyData) {
    return this.request('/api/family/create', {
      method: 'POST',
      body: JSON.stringify(familyData),
    });
  }
}

export default new ApiService();
