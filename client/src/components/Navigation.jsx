import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  FiMessageCircle, 
  FiMap
} from 'react-icons/fi';

const Navigation = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return null;

  const isActive = (path) => location.pathname === path;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-around items-center py-2">
          <Link to="/dashboard" className="flex flex-col items-center p-2">
            <div className={`p-2 rounded-lg ${isActive('/dashboard') ? 'bg-amber-100' : 'hover:bg-gray-100'} transition-colors`}>
              <svg className={`w-6 h-6 ${isActive('/dashboard') ? 'text-amber-600' : 'text-gray-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <span className={`text-xs mt-1 ${isActive('/dashboard') ? 'text-amber-600 font-medium' : 'text-gray-600'}`}>Inicio</span>
          </Link>
          
          <Link to="/gymkana" className="flex flex-col items-center p-2">
            <div className={`p-2 rounded-lg ${isActive('/gymkana') ? 'bg-amber-100' : 'hover:bg-gray-100'} transition-colors`}>
              <FiMap className={`w-6 h-6 ${isActive('/gymkana') ? 'text-amber-600' : 'text-gray-600'}`} />
            </div>
            <span className={`text-xs mt-1 ${isActive('/gymkana') ? 'text-amber-600 font-medium' : 'text-gray-600'}`}>Ruta</span>
          </Link>
          
          <Link to="/chat" className="flex flex-col items-center p-2">
            <div className={`p-2 rounded-lg ${isActive('/chat') ? 'bg-amber-100' : 'hover:bg-gray-100'} transition-colors`}>
              <FiMessageCircle className={`w-6 h-6 ${isActive('/chat') ? 'text-amber-600' : 'text-gray-600'}`} />
            </div>
            <span className={`text-xs mt-1 ${isActive('/chat') ? 'text-amber-600 font-medium' : 'text-gray-600'}`}>Chat</span>
          </Link>
          
          <Link to="/profile" className="flex flex-col items-center p-2">
            <div className={`p-2 rounded-lg ${isActive('/profile') ? 'bg-amber-100' : 'hover:bg-gray-100'} transition-colors`}>
              <svg className={`w-6 h-6 ${isActive('/profile') ? 'text-amber-600' : 'text-gray-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <span className={`text-xs mt-1 ${isActive('/profile') ? 'text-amber-600 font-medium' : 'text-gray-600'}`}>Perfil</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Navigation;
