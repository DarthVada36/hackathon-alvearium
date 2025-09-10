import React, { createContext, useContext, useState, useEffect } from 'react';

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

  // ✅ Cargar usuario desde localStorage al iniciar
  useEffect(() => {
    const loadUserFromStorage = () => {
      try {
        const storedUser = localStorage.getItem('raton_perez_user');
        const storedToken = localStorage.getItem('raton_perez_token');
        
        if (storedUser && storedToken) {
          const userData = JSON.parse(storedUser);
          setUser(userData);
        }
      } catch (error) {
        console.error('Error loading user from storage:', error);
        // Limpiar datos corruptos
        localStorage.removeItem('raton_perez_user');
        localStorage.removeItem('raton_perez_token');
      } finally {
        setIsLoading(false);
      }
    };

    loadUserFromStorage();
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
      
      // TODO: Conectar con backend real - ApiService.login(email, password)
      const mockResponse = await new Promise(resolve => {
        setTimeout(() => {
          if (email === 'test@test.com' && password === 'password') {
            resolve({
              success: true,
              user: {
                id: 1,
                name: 'Usuario de Prueba',
                email: email,
                avatar: 'icon1',
                points: 0,
                level: 1,
                visitedPlaces: [],
                createdAt: new Date().toISOString()
              },
              token: 'mock_jwt_token_' + Date.now()
            });
          } else {
            resolve({ success: false, error: 'Credenciales inválidas' });
          }
        }, 1000);
      });

      if (mockResponse.success) {
        setUser(mockResponse.user);
        localStorage.setItem('raton_perez_token', mockResponse.token);
        return { success: true };
      } else {
        return { success: false, error: mockResponse.error };
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión' };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setIsLoading(true);
      
      // TODO: Conectar con backend real - ApiService.register(userData)
      const mockResponse = await new Promise(resolve => {
        setTimeout(() => {
          resolve({
            success: true,
            user: {
              id: Date.now(),
              name: userData.name,
              email: userData.email,
              avatar: userData.avatar || 'icon1',
              points: 0,
              level: 1,
              visitedPlaces: [],
              createdAt: new Date().toISOString()
            },
            token: 'mock_jwt_token_' + Date.now()
          });
        }, 1000);
      });

      if (mockResponse.success) {
        setUser(mockResponse.user);
        localStorage.setItem('raton_perez_token', mockResponse.token);
        return { success: true };
      } else {
        return { success: false, error: 'Error en el registro' };
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión' };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('raton_perez_user');
    localStorage.removeItem('raton_perez_token');
  };

  const updateUserPoints = (points) => {
    if (user) {
      const updatedUser = {
        ...user,
        points: user.points + points,
        level: Math.floor((user.points + points) / 100) + 1
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
