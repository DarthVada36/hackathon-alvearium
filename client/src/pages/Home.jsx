import React from 'react';
import { Link } from 'react-router-dom';
import { FiTarget, FiMapPin, FiStar, FiUsers } from 'react-icons/fi';

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-golden-cream to-golden-warm">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="mb-6">
            <FiTarget size={80} className="text-golden-amber mx-auto mb-4" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Ratoncito Pérez
          </h1>
          <h2 className="text-xl md:text-2xl text-gray-600 mb-6">
            Tu Guía Turístico por Madrid
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Descubre los lugares más emblemáticos de Madrid siguiendo la ruta del famoso Ratoncito Pérez. 
            Gana puntos visitando sitios históricos y aprende sobre la rica cultura madrileña.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="card p-6 text-center">
            <FiMapPin size={40} className="text-golden-amber mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Geolocalización</h3>
            <p className="text-gray-600 text-sm">
              Descubre lugares emblemáticos usando tu ubicación actual
            </p>
          </div>
          
          <div className="card p-6 text-center">
            <FiStar size={40} className="text-golden-amber mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Sistema de Puntos</h3>
            <p className="text-gray-600 text-sm">
              Gana puntos visitando los sitios de la ruta oficial
            </p>
          </div>
          
          <div className="card p-6 text-center">
            <FiUsers size={40} className="text-golden-amber mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Guía Personal</h3>
            <p className="text-gray-600 text-sm">
              El Ratoncito Pérez te guiará por toda la ciudad
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="text-center space-y-4">
          <div className="space-y-3">
            <Link 
              to="/register" 
              className="btn-primary w-full max-w-sm mx-auto block"
            >
              Comenzar Aventura
            </Link>
            
            <Link 
              to="/login" 
              className="btn-secondary w-full max-w-sm mx-auto block"
            >
              Ya tengo cuenta
            </Link>
            
            <Link 
              to="/how-it-works" 
              className="text-golden-amber hover:text-golden-medium transition-colors font-medium block"
            >
              ¿Cómo funciona?
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
