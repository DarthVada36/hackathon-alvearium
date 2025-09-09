import React from 'react';
import { FiArrowLeft } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';

const Header = ({ title, showBackButton = false, children }) => {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 bg-amber-50/95 backdrop-blur-sm border-b border-lime-200/30">
      <div className="flex items-center justify-between px-4 py-4">
        <div className="flex items-center space-x-3">
          {showBackButton && (
            <button 
              onClick={() => navigate(-1)}
              className="p-2 rounded-lg hover:bg-lime-200/50 transition-colors"
            >
              <FiArrowLeft size={20} className="text-amber-600" />
            </button>
          )}
          <h1 className="text-xl font-bold text-gray-800">{title}</h1>
        </div>
        <div className="flex items-center">
          {children}
        </div>
      </div>
    </header>
  );
};

export default Header;
