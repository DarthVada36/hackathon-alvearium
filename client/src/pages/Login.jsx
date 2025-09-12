import React, { useState } from 'react';
import { FiMail, FiLock, FiEye, FiEyeOff } from 'react-icons/fi';
import logo from '../assets/img/logo-black.png'; 
import bg from '../assets/img/bg.png'; 
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // 👈 Importa tu AuthContext

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const { login } = useAuth(); // 👈 Obtenemos login de AuthContext

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Llamar a login de AuthContext
      const result = await login(formData.email, formData.password);

      if (result.success) {
        // 👇 Redirigir a Dashboard si login fue exitoso
        navigate('/dashboard', { 
          state: { message: '¡Bienvenido al mundo del Ratón Pérez 🐭✨!' }
        });
      } else {
        setError(result.error || 'Credenciales incorrectas. Intenta de nuevo.');
      }
    } catch (error) {
      setError('Error de conexión. Intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-cover bg-center" 
      style={{ backgroundImage: `url(${bg})` }}
    >
      {/* Elementos decorativos */}
      <div className="absolute inset-0 pointer-events-none opacity-30">
        <div className="absolute top-20 left-10 text-2xl text-yellow-300 animate-pulse">✨</div>
        <div className="absolute top-32 right-16 text-xl text-pink-300 animate-bounce" style={{animationDelay: '1s'}}>⭐</div>
        <div className="absolute bottom-40 left-20 text-lg text-blue-300 animate-pulse" style={{animationDelay: '2s'}}>🌟</div>
        <div className="absolute bottom-60 right-1/4 text-xl text-purple-300 animate-bounce" style={{animationDelay: '0.5s'}}>✨</div>
      </div>
      
      <div className="w-full max-w-sm relative z-10">
        {/* Logo */}
        <div className="text-center mb-12">
          <div className="mb-8">
            <img 
              src={logo} 
              alt="Logo Ratón Pérez" 
              className="w-45 h-24 mx-auto object-contain" 
            />
          </div>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Campo Email */}
          <div className="relative">
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-6 py-4 bg-white/70 backdrop-blur-sm rounded-[15px] border-0 text-gray-600 
                         placeholder-gray-400 text-lg font-medium focus:outline-none focus:ring-2 
                         focus:ring-pink-300 focus:bg-white/90 transition-all duration-300 shadow-sm"
              placeholder="Correo electrónico"
            />
            <FiMail className="absolute right-6 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>

          {/* Campo Contraseña */}
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-6 py-4 bg-white/70 backdrop-blur-sm rounded-[15px] border-0 text-gray-600 
                         placeholder-gray-400 text-lg font-medium focus:outline-none focus:ring-2 
                         focus:ring-pink-300 focus:bg-white/90 transition-all duration-300 shadow-sm"
              placeholder="Contraseña"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-6 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showPassword ? <FiEyeOff /> : <FiEye />}
            </button>
          </div>

          {/* Mensaje de error */}
          {error && (
            <div className="text-center text-red-500 text-sm font-medium bg-red-50 py-2 px-4 rounded-full">
              {error}
            </div>
          )}

          {/* Botón de login */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 px-8 rounded-[15px] font-bold text-white text-lg transition-all duration-300 
                       transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 
                       disabled:cursor-not-allowed shadow-lg hover:shadow-xl mt-6"
            style={{
              background: isLoading 
                ? 'linear-gradient(135deg, #D1D5DB 0%, #9CA3AF 100%)'
                : 'linear-gradient(135deg, #E7B923 0%, #F59E0B 100%)',
              boxShadow: isLoading ? '' : '0 8px 25px rgba(231, 185, 35, 0.3)'
            }}
          >
            <div className="flex items-center justify-center">
              {isLoading ? (
                <>
                  <div className="animate-spin mr-3 h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                  Iniciando sesión...
                </>
              ) : (
                'Iniciar Sesión'
              )}
            </div>
          </button>

          {/* Link de contraseña olvidada */}
          <div className="text-center mt-6">
            <button className="text-gray-500 text-base hover:text-gray-700 transition-colors">
              ¿Olvidaste tu contraseña?
            </button>
          </div>

          {/* Credenciales de prueba */}
          <div className="mt-8 p-4 bg-white/50 backdrop-blur-sm rounded-2xl border border-white/30">
            <div className="text-center text-sm text-gray-600">
              <p className="font-semibold mb-2 flex items-center justify-center">
                <span className="mr-2">💡</span>
                Credenciales de prueba:
              </p>
              <p className="font-medium">test@test.com</p>
              <p className="font-medium">password</p>
            </div>
          </div>

          {/* Link de registro */}
          <div className="text-center mt-6">
            <p className="text-gray-500 text-base">
              ¿No tienes cuenta?{' '}
              <Link 
                to="/register" 
                className="font-semibold transition-colors"
                style={{color: '#E7B923'}}
              >
                Regístrate aquí
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;
