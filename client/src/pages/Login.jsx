import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiMail, FiLock, FiEye, FiEyeOff, FiArrowRight, FiStar } from 'react-icons/fi';

// 👇 Importa tu imagen de fondo
import BgLogin from '../assets/bg-login-2.png';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [showWelcomeAnimation, setShowWelcomeAnimation] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  // Animación ratón siguiendo el cursor
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setShowWelcomeAnimation(true);

    setTimeout(() => {
      const userData = {
        id: 1,
        name: formData.email.split('@')[0],
        email: formData.email,
        points: 0,
        level: 'Ratoncito Novato',
        visitedPlaces: [],
        badges: []
      };

      login(userData);
      setIsLoading(false);
      navigate('/dashboard');
    }, 2000);
  };

  // Datos curiosos
  const funFacts = [
    "El Ratón Pérez vive en el número 8 de la calle Arenal",
    "La tradición del Ratón Pérez existe desde 1894",
    "El Ratón Pérez tiene un museo en Madrid desde 2003",
    "Miles de niños visitan la casa del Ratón Pérez cada año"
  ];

  const [currentFact, setCurrentFact] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFact((prev) => (prev + 1) % funFacts.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="min-h-screen relative overflow-hidden"
      style={{
        backgroundImage: `url(${BgLogin})`,
        backgroundSize: "fill",
        backgroundPosition: "center",
      }}
    >
      {/* Overlay degradado */}
      <div className="absolute inset-0 bg-gradient-to-br from-amber-50/80 via-yellow-50/70 to-amber-100/80"></div>

      {/* Elementos decorativos */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-20 left-10 text-6xl opacity-10 animate-bounce">🦷</div>
        <div className="absolute top-40 right-20 text-5xl opacity-10 animate-pulse">⭐</div>
        <div className="absolute bottom-20 left-1/3 text-6xl opacity-10 animate-bounce" style={{ animationDelay: '1s' }}>🪙</div>
        <div className="absolute bottom-40 right-10 text-5xl opacity-10 animate-pulse" style={{ animationDelay: '0.5s' }}>✨</div>

        {/* Ratón siguiendo cursor */}
        <div 
          className="hidden lg:block absolute text-2xl transition-all duration-300 ease-out opacity-30"
          style={{ 
            left: `${mousePosition.x * 0.05}px`, 
            top: `${mousePosition.y * 0.05}px`,
            transform: 'translate(-50%, -50%)'
          }}
        >
          🐭
        </div>
      </div>

      {/* Animación bienvenida */}
      {showWelcomeAnimation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-amber-500/20 backdrop-blur-sm">
          <div className="bg-white rounded-3xl p-8 animate-bounce shadow-2xl">
            <div className="text-6xl text-center mb-4">🐭</div>
            <h2 className="text-2xl font-bold text-center text-amber-600">¡Bienvenido!</h2>
            <p className="text-gray-600 text-center mt-2">Preparando tu aventura...</p>
            <div className="flex justify-center mt-4">
              <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse mx-1"></div>
              <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse mx-1" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse mx-1" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        </div>
      )}
      
      {/* Contenido */}
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="max-w-md mx-auto">
          {/* Logo */}
          <div className="text-center mb-6">
            <Link to="/" className="inline-block">
              <div className="w-24 h-24 bg-gradient-to-r from-amber-400 to-amber-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-xl transform hover:scale-110 transition-transform cursor-pointer">
                <span className="text-5xl animate-bounce">🐭</span>
              </div>
            </Link>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Casa Museo</h1>
            <p className="text-xl text-amber-600 font-semibold">Ratón Pérez</p>
          </div>

          {/* Tarjeta login */}
          <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border-2 border-amber-200/50">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">¡Bienvenido de vuelta!</h2>
              <p className="text-gray-600 mt-2">Continúa tu aventura mágica por Madrid</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email */}
              <div className="space-y-2">
                <label className="block text-sm font-bold text-gray-700">
                  Correo electrónico
                </label>
                <div className="relative group">
                  <FiMail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-amber-500 group-focus-within:text-amber-600 transition-colors" size={18} />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-12 pr-4 py-3 border-2 border-amber-200 rounded-2xl focus:border-amber-400 focus:outline-none focus:ring-4 focus:ring-amber-100 transition-all bg-amber-50/30"
                    placeholder="tu@email.com"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-2">
                <label className="block text-sm font-bold text-gray-700">
                  Contraseña
                </label>
                <div className="relative group">
                  <FiLock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-amber-500 group-focus-within:text-amber-600 transition-colors" size={18} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full pl-12 pr-12 py-3 border-2 border-amber-200 rounded-2xl focus:border-amber-400 focus:outline-none focus:ring-4 focus:ring-amber-100 transition-all bg-amber-50/30"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-amber-500 hover:text-amber-600 transition-colors"
                  >
                    {showPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                  </button>
                </div>
              </div>

              {/* Botón */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold py-4 rounded-2xl hover:from-amber-600 hover:to-amber-700 transform hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg flex items-center justify-center group"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Entrando al museo...
                  </>
                ) : (
                  <>
                    Iniciar Aventura
                    <FiArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" size={20} />
                  </>
                )}
              </button>
            </form>

            {/* Dato curioso */}
            <div className="mt-6 bg-white/80 backdrop-blur-sm rounded-2xl p-4 border border-amber-200/50">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">💡</div>
                <div>
                  <p className="text-sm font-semibold text-amber-700 mb-1">¿Sabías que...?</p>
                  <p className="text-xs text-gray-600 leading-relaxed">{funFacts[currentFact]}</p>
                </div>
              </div>
            </div>

            {/* Badges */}
            <div className="mt-6 flex justify-center space-x-6 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <FiStar className="text-amber-500" />
                <span>4.9/5 valoración</span>
              </div>
              <div className="flex items-center space-x-1">
                <span>🦷</span>
                <span>+10,000 visitantes</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
