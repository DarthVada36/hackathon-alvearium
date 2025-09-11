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

  // ============ FAMILY ENDPOINTS ============
  async createFamily(familyData) {
    return this.request('/api/families/', {
      method: 'POST',
      body: JSON.stringify(familyData),
    });
  }

  async getFamilies() {
    return this.request('/api/families/');
  }

  async getFamily(familyId) {
    return this.request(`/api/families/${familyId}`);
  }

  async deleteFamily(familyId) {
    return this.request(`/api/families/${familyId}`, {
      method: 'DELETE',
    });
  }

  // ============ CHAT ENDPOINTS ============
  async sendChatMessage(familyId, message, location = null, speakerName = null) {
    const messageData = {
      family_id: familyId,
      message: message,
      ...(location && { location }),
      ...(speakerName && { speaker_name: speakerName })
    };

    return this.request('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  }

  async getFamilyStatus(familyId) {
    return this.request(`/api/chat/family/${familyId}/status`);
  }

  async getChatHistory(familyId, limit = 20) {
    return this.request(`/api/chat/family/${familyId}/history?limit=${limit}`);
  }

  async clearChatHistory(familyId) {
    return this.request(`/api/chat/family/${familyId}/history`, {
      method: 'DELETE',
    });
  }

  async getChatFamilies() {
    return this.request('/api/chat/families');
  }

  // ============ ROUTES ENDPOINTS ============
  async getRouteOverview() {
    return this.request('/api/routes/overview');
  }

  async getNextDestination(familyId) {
    return this.request(`/api/routes/family/${familyId}/next`);
  }

  async advanceToNextPOI(familyId) {
    return this.request(`/api/routes/family/${familyId}/advance`, {
      method: 'POST',
    });
  }

  async updateLocation(familyId, latitude, longitude) {
    const locationData = {
      family_id: familyId,
      latitude: latitude,
      longitude: longitude
    };

    return this.request('/api/routes/location/update', {
      method: 'POST',
      body: JSON.stringify(locationData),
    });
  }

  // ============ HEALTH CHECK ============
  async checkHealth() {
    return this.request('/health');
  }

  // ============ DEBUG ENDPOINTS (opcional) ============
  async debugPing() {
    return this.request('/debug/ping');
  }

  async debugPinecone() {
    return this.request('/debug/pinecone');
  }

  // ============ UTILITY METHODS ============
  
  /**
   * Verifica si hay un token válido almacenado
   */
  hasValidToken() {
    const token = localStorage.getItem('raton_perez_token');
    return !!token;
  }

  /**
   * Obtiene el token actual
   */
  getToken() {
    return localStorage.getItem('raton_perez_token');
  }

  /**
   * Limpia todos los datos de autenticación
   */
  clearAuth() {
    localStorage.removeItem('raton_perez_token');
    localStorage.removeItem('raton_perez_user');
  }

  /**
   * Manejo genérico de errores para mostrar al usuario
   */
  formatError(error) {
    if (error.message.includes('401')) {
      return 'Sesión expirada. Por favor, inicia sesión de nuevo.';
    }
    if (error.message.includes('403')) {
      return 'No tienes permisos para realizar esta acción.';
    }
    if (error.message.includes('404')) {
      return 'El recurso solicitado no fue encontrado.';
    }
    if (error.message.includes('500')) {
      return 'Error del servidor. Por favor, intenta de nuevo.';
    }
    return error.message || 'Ha ocurrido un error inesperado.';
  }
}

export default new ApiService();