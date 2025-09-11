import React, { createContext, useContext, useState, useEffect } from 'react';
import ApiService from '../services/ApiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // ✅ Cargar usuario desde localStorage y verificar con backend al iniciar
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('raton_perez_token');
        
        if (storedToken) {
          // Verificar token con backend
          const userData = await ApiService.getCurrentUser();
          setUser(userData.user);
        }
      } catch (error) {
        console.error('Error loading user from backend:', error);
        // Token inválido, limpiar datos
        localStorage.removeItem('raton_perez_user');
        localStorage.removeItem('raton_perez_token');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // ✅ Guardar usuario en localStorage cuando cambie
  useEffect(() => {
    if (user) {
      localStorage.setItem('raton_perez_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('raton_perez_user');
      localStorage.removeItem('raton_perez_token');
    }
  }, [user]);

  const login = async (email, password) => {
    try {
      setIsLoading(true);
      
      const response = await ApiService.login(email, password);
      
      if (response.access_token && response.user) {
        setUser(response.user);
        return { success: true };
      } else {
        return { success: false, error: 'Respuesta inválida del servidor' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message || 'Error al iniciar sesión' };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setIsLoading(true);
      
      const response = await ApiService.register(userData);
      
      if (response.access_token && response.user) {
        setUser(response.user);
        return { success: true };
      } else {
        return { success: false, error: 'Error en el registro' };
      }
    } catch (error) {
      console.error('Register error:', error);
      return { success: false, error: error.message || 'Error en el registro' };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await ApiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const updateUserPoints = (points) => {
    if (user) {
      const updatedUser = {
        ...user,
        points: (user.points || 0) + points,
      };
      setUser(updatedUser);
    }
  };

  const updateUserProfile = (profileData) => {
    if (user) {
      const updatedUser = { ...user, ...profileData };
      setUser(updatedUser);
    }
  };

  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem('raton_perez_token');
  };

  const getAuthToken = () => {
    return localStorage.getItem('raton_perez_token');
  };

  const value = {
    user,
    isLoading,
    login,
    register,
    logout,
    updateUserPoints,
    updateUserProfile,
    isAuthenticated,
    getAuthToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};