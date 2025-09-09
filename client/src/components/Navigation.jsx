import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  FiHome, 
  FiUser, 
  FiMessageCircle, 
  FiMap, 
  FiLogOut,
  FiMenu
} from 'react-icons/fi';

const Navigation = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-sm border-t border-lime-200/30 z-50">
      <div className="flex justify-around items-center py-2 px-4">
        <Link 
          to="/dashboard" 
          className="flex flex-col items-center p-2 text-amber-600 hover:text-lime-300 transition-colors"
        >
          <FiHome size={24} />
          <span className="text-xs mt-1">Inicio</span>
        </Link>
        
        <Link 
          to="/chat" 
          className="flex flex-col items-center p-2 text-amber-600 hover:text-lime-300 transition-colors"
        >
          <FiMessageCircle size={24} />
          <span className="text-xs mt-1">Ratoncito</span>
        </Link>
        
        <Link 
          to="/gymkana" 
          className="flex flex-col items-center p-2 text-amber-600 hover:text-lime-300 transition-colors"
        >
          <FiMap size={24} />
          <span className="text-xs mt-1">Gymkana</span>
        </Link>
        
        <Link 
          to="/profile" 
          className="flex flex-col items-center p-2 text-amber-600 hover:text-lime-300 transition-colors"
        >
          <FiUser size={24} />
          <span className="text-xs mt-1">Perfil</span>
        </Link>
        
        <button 
          onClick={handleLogout}
          className="flex flex-col items-center p-2 text-red-500 hover:text-red-600 transition-colors"
        >
          <FiLogOut size={24} />
          <span className="text-xs mt-1">Salir</span>
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
