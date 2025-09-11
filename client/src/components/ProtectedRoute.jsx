import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ApiService from '../services/ApiService';

const ProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  const [isValidating, setIsValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);

  useEffect(() => {
    const validateToken = async () => {
      try {
        const token = localStorage.getItem('raton_perez_token');
        
        if (!token) {
          setTokenValid(false);
          return;
        }

        // Validar token con backend
        await ApiService.getCurrentUser();
        setTokenValid(true);
      } catch (error) {
        console.error('Token validation failed:', error);
        setTokenValid(false);
        // Limpiar token inválido
        localStorage.removeItem('raton_perez_token');
        localStorage.removeItem('raton_perez_user');
      } finally {
        setIsValidating(false);
      }
    };

    if (!isLoading) {
      validateToken();
    }
  }, [isLoading]);

  if (isLoading || isValidating) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto mb-4"></div>
          <p className="text-amber-600 font-medium">Verificando acceso...</p>
        </div>
      </div>
    );
  }

  if (!user || !tokenValid) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;