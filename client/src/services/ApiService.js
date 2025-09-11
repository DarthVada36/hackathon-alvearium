// Default to port 8000 which is used by the backend during local verification.
// You can override by creating a `VITE_API_URL` in the client's .env (ex: VITE_API_URL=http://127.0.0.1:8000)
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    // ensure we don't duplicate slashes
    const base = this.baseURL.endsWith("/")
      ? this.baseURL.slice(0, -1)
      : this.baseURL;
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    const url = `${base}${path}`;
    const token = localStorage.getItem("raton_perez_token");

    const config = {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
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
      console.error("API request failed:", error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    return this.request("/health");
  }

  // Family endpoints
  async createFamily(familyData) {
    return this.request("/api/families/", {
      method: "POST",
      body: JSON.stringify(familyData),
    });
  }

  async getFamilies() {
    return this.request("/api/families/");
  }

  // Chat endpoints
  async sendChatMessage(message, context = {}) {
    return this.request("/api/chat/message", {
      method: "POST",
      body: JSON.stringify({ message, context }),
    });
  }

  // Routes endpoints
  async getRoutes() {
    return this.request("/api/routes/overview");
  }
}

export default new ApiService();
