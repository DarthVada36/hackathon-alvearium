import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import { FiMail, FiLock, FiUser, FiEye, FiEyeOff, FiCheck } from 'react-icons/fi';

// Import avatar images
import icon1 from '../assets/img/icon1png.png';
import icon2 from '../assets/img/icon2.png';
import icon3 from '../assets/img/icon3.png';
import icon4 from '../assets/img/icon4.png';
import icon5 from '../assets/img/icon5.png';
import icon6 from '../assets/img/icon6.png';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    avatar: 'icon1'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Available avatars
  const avatars = [
    { id: 'icon1', src: icon1, name: 'Ratoncito Clásico' },
    { id: 'icon2', src: icon2, name: 'Ratoncito Aventurero' },
    { id: 'icon3', src: icon3, name: 'Ratoncito Explorador' },
    { id: 'icon4', src: icon4, name: 'Ratoncito Real' },
    { id: 'icon5', src: icon5, name: 'Ratoncito Mágico' },
    { id: 'icon6', src: icon6, name: 'Ratoncito Maestro' }
  ];
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es obligatorio';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'El email es obligatorio';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El email no es válido';
    }
    
    if (!formData.password) {
      newErrors.password = 'La contraseña es obligatoria';
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }
    
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formErrors = validateForm();
    if (Object.keys(formErrors).length > 0) {
      setErrors(formErrors);
      return;
    }
    
    setIsLoading(true);
    
    try {
      const result = await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        avatar: formData.avatar
      });
      
      if (result.success) {
        navigate('/dashboard');
      } else {
        setErrors({ submit: result.error || 'Error al crear la cuenta' });
      }
    } catch (error) {
      setErrors({ submit: 'Error de conexión. Intenta de nuevo.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100">
      <Header title="Crear Cuenta" showBackButton />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          <div className="card p-8">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-amber-100 rounded-full overflow-hidden flex items-center justify-center mx-auto mb-4 border-2 border-amber-200">
                <img 
                  src={avatars.find(a => a.id === formData.avatar)?.src} 
                  alt="Avatar seleccionado" 
                  className="w-20 h-20 object-cover"
                />
              </div>
              <h2 className="text-2xl font-bold text-gray-800">¡Únete a la aventura!</h2>
              <p className="text-gray-600 mt-2">Crea tu cuenta y comienza a explorar Madrid</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Avatar Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Elige tu avatar
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {avatars.map((avatar) => (
                    <button
                      key={avatar.id}
                      type="button"
                      onClick={() => setFormData({...formData, avatar: avatar.id})}
                      className={`relative p-3 rounded-xl border-2 transition-all hover:scale-105 ${
                        formData.avatar === avatar.id 
                          ? 'border-amber-500 bg-amber-100' 
                          : 'border-gray-200 bg-white hover:border-amber-300'
                      }`}
                    >
                      <img 
                        src={avatar.src} 
                        alt={avatar.name} 
                        className="w-10 h-10 object-cover mx-auto mb-1 rounded-lg"
                      />
                      <p className="text-xs text-gray-600 text-center">{avatar.name}</p>
                      {formData.avatar === avatar.id && (
                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center">
                          <FiCheck className="text-white" size={12} />
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre completo
                </label>
                <div className="relative">
                  <FiUser className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`input-field pl-10 ${errors.name ? 'border-red-500' : ''}`}
                    placeholder="Tu nombre"
                    required
                  />
                </div>
                {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Correo electrónico
                </label>
                <div className="relative">
                  <FiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={`input-field pl-10 ${errors.email ? 'border-red-500' : ''}`}
                    placeholder="tu@email.com"
                    required
                  />
                </div>
                {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contraseña
                </label>
                <div className="relative">
                  <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className={`input-field pl-10 pr-10 ${errors.password ? 'border-red-500' : ''}`}
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
                {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirmar contraseña
                </label>
                <div className="relative">
                  <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={`input-field pl-10 pr-10 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                  </button>
                </div>
                {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
              </div>

              {/* Mensaje de error general */}
              {errors.submit && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                  {errors.submit}
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Creando cuenta...' : 'Crear Cuenta'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-600">
                ¿Ya tienes cuenta?{' '}
                <Link to="/login" className="text-amber-600 hover:text-lime-300 font-medium">
                  Inicia sesión aquí
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
