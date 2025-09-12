import React from 'react';
import { Link } from 'react-router-dom';
import { 
  MapPin, 
  Star, 
  Users, 
  Trophy, 
  Compass, 
  Gift,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import ratonSaco from '../assets/img/raton-saco.png';
import saludoRaton from '../assets/img/saludo-raton.png';

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100">
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          {/* Ratón de bienvenida */}
          <div className="relative mx-auto mb-6 w-32 h-32">
            <img 
              src={saludoRaton} 
              alt="Ratoncito Pérez saludando" 
              className="w-32 h-32 object-contain"
            />
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            ¡Hola! Soy el Ratoncito Pérez
          </h1>
          <h2 className="text-xl md:text-2xl text-amber-600 mb-6 font-semibold">
            Tu Guía Digital por Madrid
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto leading-relaxed text-lg">
            ¿Estás listo para una aventura mágica? Te llevaré por los lugares más especiales de Madrid 
            donde he recolectado dientes durante siglos. ¡Gana monedas de oro y descubre mi mundo!
          </p>
        </div>

        {/* Moneda de oro 3D giratoria */}
        <div className="flex justify-center mb-12">
          <div className="coin-3d">
            <div className="coin-inner">
              <div className="coin-front">
                <Star className="text-yellow-400" size={42} />
              </div>
              <div className="coin-back">
                <Trophy className="text-yellow-400" size={42} />
              </div>
            </div>
          </div>
        </div>

        {/* Features Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {/* Explora Madrid */}
          <div className="card p-6 text-center hover:scale-105 transition-transform">
            <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-300">
              <MapPin className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-800">Explora Madrid</h3>
            <p className="text-gray-600 text-sm">
              Descubre lugares mágicos donde he dejado mis huellas a lo largo de la historia
            </p>
          </div>
          
          {/* Gana Monedas */}
          <div className="card p-6 text-center hover:scale-105 transition-transform">
            <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-300">
              <Star className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-800">Gana Monedas</h3>
            <p className="text-gray-600 text-sm">
              Colecciona monedas de oro visitando mis lugares favoritos en la capital
            </p>
          </div>
          
          {/* Aventura Familiar */}
          <div className="card p-6 text-center hover:scale-105 transition-transform">
            <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-300">
              <Users className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-800">Aventura Familiar</h3>
            <p className="text-gray-600 text-sm">
              Perfecto para niños y adultos. ¡Toda la familia puede disfrutar juntos!
            </p>
          </div>
          
          {/* Gymkana Interactiva */}
          <div className="card p-6 text-center hover:scale-105 transition-transform">
            <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-300">
              <Compass className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-800">Gymkana Interactiva</h3>
            <p className="text-gray-600 text-sm">
              Resuelve pistas y completa desafíos en cada ubicación histórica
            </p>
          </div>
          
          {/* Premios Especiales */}
          <div className="card p-6 text-center hover:scale-105 transition-transform">
            <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-300">
              <Gift className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-800">Premios Especiales</h3>
            <p className="text-gray-600 text-sm">
              Desbloquea recompensas únicas y sorpresas en tu recorrido
            </p>
          </div>
          
          {/* Historia de Madrid */}
          <div className="card p-6 text-center hover:scale-105 transition-transform">
            <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-amber-300">
              <Sparkles className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-800">Historia Mágica</h3>
            <p className="text-gray-600 text-sm">
              Aprende la verdadera historia de Madrid a través de mis ojos
            </p>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center space-y-6">
          <div className="bg-white rounded-2xl p-8 shadow-lg border-2 border-amber-200">
            <div className="flex justify-center mb-4">
              <img 
                src={ratonSaco} 
                alt="Ratoncito Pérez" 
                className="w-16 h-16 object-contain"
              />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              ¿Estás listo para la aventura?
            </h3>
            <p className="text-gray-600 mb-6">
              Crea tu familia y comienza a explorar Madrid conmigo. ¡Será divertido!
            </p>
            
            <div className="space-y-6 max-w-sm mx-auto">
              <Link 
                to="/register" 
                className="btn-primary w-full flex items-center justify-center"
              >
                <Users className="mr-2" size={20} />
                Comenzar Aventura
                <ArrowRight className="ml-2" size={20} />
              </Link>
              
              {/* Link de texto en lugar de botón */}
              <div className="text-center">
                <p className="text-gray-600 text-sm">
                  ¿Ya tienes tu familia?{' '}
                  <Link
                    to="/login"
                    className="text-amber-600 hover:text-amber-700 font-medium underline hover:no-underline transition-all"
                  >
                    Inicia sesión
                  </Link>
                </p>
              </div>
            </div>
          </div>
          
          <Link 
            to="/how-it-works" 
            className="text-amber-600 hover:text-amber-700 transition-colors font-medium inline-flex items-center"
          >
            <Compass className="mr-2" size={20} />
            ¿Cómo funciona la aventura?
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
