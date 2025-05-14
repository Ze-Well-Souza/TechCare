import axios from 'axios';

const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api';

class AuthService {
  async login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/login`, { username, password });
      
      if (response.data.access_token) {
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      
      return response.data;
    } catch (error) {
      console.error('Erro no login:', error);
      throw error;
    }
  }

  logout() {
    localStorage.removeItem('user');
  }

  async register(username, email, password, role) {
    try {
      const response = await axios.post(`${API_URL}/register`, {
        username,
        email,
        password,
        role
      });
      
      return response.data;
    } catch (error) {
      console.error('Erro no registro:', error);
      throw error;
    }
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  }

  isAuthenticated() {
    const user = this.getCurrentUser();
    return !!user && !!user.access_token;
  }

  getUserRole() {
    const user = this.getCurrentUser();
    return user ? user.user_role : null;
  }

  async refreshToken() {
    try {
      const user = this.getCurrentUser();
      const response = await axios.post(`${API_URL}/refresh`, {}, {
        headers: { Authorization: `Bearer ${user.access_token}` }
      });

      user.access_token = response.data.access_token;
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data.access_token;
    } catch (error) {
      this.logout();
      throw error;
    }
  }
}

export default new AuthService();
