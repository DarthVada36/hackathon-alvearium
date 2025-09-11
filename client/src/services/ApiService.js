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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // ============ AUTH ENDPOINTS ============
  async register(userData) {
    const response = await this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    // Guardar token automáticamente
    if (response.access_token) {
      localStorage.setItem('raton_perez_token', response.access_token);
    }
    
    return response;
  }

  async login(email, password) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    // Guardar token automáticamente
    if (response.access_token) {
      localStorage.setItem('raton_perez_token', response.access_token);
    }
    
    return response;
  }

  async getCurrentUser() {
    return this.request('/api/auth/me');
  }

  async logout() {
    try {
      await this.request('/api/auth/logout', { method: 'POST' });
    } finally {
      localStorage.removeItem('raton_perez_token');
    }
  }

  // Health check
  async checkHealth() {
    return this.request('/health');
  }

  // Family endpoints
  async createFamily(familyData) {
    return this.request('/api/families/', {
      method: 'POST',
      body: JSON.stringify(familyData),
    });
  }

  async getFamilies() {
    return this.request('/api/families/');
  }

  // Chat endpoints
  async sendChatMessage(messageData) {
    return this.request('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  }

  // Routes endpoints
  async getRoutes() {
    return this.request('/api/routes/overview');
  }
}

export default new ApiService();