import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  User, 
  Users, 
  Plus, 
  Trash2, 
  Check, 
  Globe, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff,
  AlertCircle,
  Info
} from 'lucide-react';
import Header from '../components/Header';
import ApiService from '../services/ApiService';
import ratonSaco from '../assets/img/raton-saco.png';
import icon1 from '../assets/img/icon1png.png';
import icon2 from '../assets/img/icon2.png';
import icon3 from '../assets/img/icon3.png';
import icon4 from '../assets/img/icon4.png';
import icon5 from '../assets/img/icon5.png';
import icon6 from '../assets/img/icon6.png';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    preferred_language: 'es',
    avatar: 'icon1',
    members: [
      { name: '', age: '', member_type: 'adult' }
    ]
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const navigate = useNavigate();

  // Opciones de idioma - SIN EMOJIS Y MÁS COMPACTAS
  const languages = [
    { code: 'es', name: 'Español' },
    { code: 'en', name: 'English' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' }
  ];

  // Tipos de miembro
  const memberTypes = [
    { value: 'adult', label: 'Adulto', icon: User },
    { value: 'child', label: 'Niño/a', icon: Users }
  ];

  // Avatares disponibles con las rutas correctas
  const avatars = [
    { id: 'icon1', name: 'Avatar 1', src: icon1 },
    { id: 'icon2', name: 'Avatar 2', src: icon2 },
    { id: 'icon3', name: 'Avatar 3', src: icon3 },
    { id: 'icon4', name: 'Avatar 4', src: icon4 },
    { id: 'icon5', name: 'Avatar 5', src: icon5 },
    { id: 'icon6', name: 'Avatar 6', src: icon6 }
  ];

  // Contar miembros por tipo
  const adultCount = formData.members.filter(m => m.member_type === 'adult').length;
  const childCount = formData.members.filter(m => m.member_type === 'child').length;

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Limpiar errores cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleMemberChange = (index, field, value) => {
    const newMembers = [...formData.members];
    
    // Si cambia el tipo de miembro, validar edad
    if (field === 'member_type') {
      const currentAge = parseInt(newMembers[index].age) || 0;
      if (value === 'adult' && currentAge < 18) {
        newMembers[index].age = '18';
      } else if (value === 'child' && currentAge >= 18) {
        newMembers[index].age = '17';
      }
    }
    
    // Si cambia la edad, validar tipo
    if (field === 'age') {
      const age = parseInt(value) || 0;
      if (age >= 18 && newMembers[index].member_type === 'child') {
        newMembers[index].member_type = 'adult';
      } else if (age < 18 && newMembers[index].member_type === 'adult') {
        newMembers[index].member_type = 'child';
      }
    }
    
    newMembers[index][field] = value;
    
    setFormData(prev => ({
      ...prev,
      members: newMembers
    }));
    
    // Limpiar errores de miembros
    if (errors[`member_${index}_${field}`]) {
      setErrors(prev => ({
        ...prev,
        [`member_${index}_${field}`]: ''
      }));
    }
  };

  const addMember = () => {
    setFormData(prev => ({
      ...prev,
      members: [...prev.members, { name: '', age: '', member_type: 'child' }]
    }));
  };

  const removeMember = (index) => {
    if (formData.members.length > 1) {
      setFormData(prev => ({
        ...prev,
        members: prev.members.filter((_, i) => i !== index)
      }));
    }
  };

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password) => {
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const hasMinLength = password.length >= 8;
    
    return {
      isValid: hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar && hasMinLength,
      requirements: {
        minLength: hasMinLength,
        upperCase: hasUpperCase,
        lowerCase: hasLowerCase,
        numbers: hasNumbers,
        specialChar: hasSpecialChar
      }
    };
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Validar email
    if (!formData.email.trim()) {
      newErrors.email = 'El correo electrónico es obligatorio';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'El correo electrónico no es válido';
    }
    
    // Validar contraseña
    if (!formData.password) {
      newErrors.password = 'La contraseña es obligatoria';
    } else {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.isValid) {
        newErrors.password = 'La contraseña no cumple los requisitos de seguridad';
      }
    }
    
    // Validar confirmación de contraseña
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Confirma tu contraseña';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden';
    }
    
    // Validar nombre de familia
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre de la familia es obligatorio';
    }
    
    // Validar que hay exactamente un adulto
    if (adultCount !== 1) {
      newErrors.members = 'Debe haber exactamente un adulto en la familia';
    }
    
    // Validar miembros
    formData.members.forEach((member, index) => {
      if (!member.name.trim()) {
        newErrors[`member_${index}_name`] = 'El nombre es obligatorio';
      }
      
      const age = parseInt(member.age) || 0;
      if (!member.age || age < 0 || age > 120) {
        newErrors[`member_${index}_age`] = 'Edad válida requerida (0-120)';
      } else if (member.member_type === 'child' && age >= 18) {
        newErrors[`member_${index}_age`] = 'Los niños deben tener menos de 18 años';
      } else if (member.member_type === 'adult' && age < 18) {
        newErrors[`member_${index}_age`] = 'Los adultos deben tener 18 años o más';
      }
    });
    
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
    setErrors({});
    setSuccess('');

    try {
      // Preparar datos para enviar al backend
      const familyData = {
        name: formData.name,
        preferred_language: formData.preferred_language,
        members: formData.members.map(member => ({
          ...member,
          age: parseInt(member.age) || 0
        }))
      };

      const response = await ApiService.createFamily(familyData);
      
      setSuccess('¡Familia creada exitosamente! Redirigiendo al dashboard...');
      
      // Esperar un momento y redirigir
      setTimeout(() => {
        navigate('/dashboard', { 
          state: { 
            newFamily: response,
            message: 'Bienvenidos al mundo del Ratoncito Pérez Digital' 
          } 
        });
      }, 2000);
      
    } catch (error) {
      console.error('Error creating family:', error);
      setErrors({ 
        submit: error.message || 'Error al crear la familia. Por favor, intenta de nuevo.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  const passwordValidation = validatePassword(formData.password);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100">
      <Header title="Registro de Familia" showBackButton />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="card p-8">
            <div className="text-center mb-8">
              {/* RATÓN SIN ENVOLTORIO - COMO EN HOWITWORKS */}
              <div className="relative mx-auto mb-4 w-24 h-24">
                <img 
                  src={ratonSaco} 
                  alt="Ratoncito Pérez" 
                  className="w-24 h-24 object-contain filter drop-shadow-lg"
                />
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2 flex items-center justify-center">
                <User className="mr-2 text-amber-600" />
                Registro de Familia
              </h2>
              <p className="text-gray-600">Crea tu familia para comenzar la aventura con el Ratoncito Pérez en Madrid</p>
              
              {/* Aviso importante */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                <div className="flex items-start">
                  <Info className="text-blue-500 mr-2 mt-0.5 flex-shrink-0" size={16} />
                  <p className="text-blue-700 text-sm text-left">
                    <strong>Importante:</strong> Solo puedes registrar un adulto (responsable) y máximo 4 niños en tu familia.
                  </p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Email */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <Mail className="mr-2 text-amber-600" size={20} />
                  Correo Electrónico *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="tu-email@ejemplo.com"
                  className={`input-field text-lg ${errors.email ? 'border-red-500' : ''}`}
                />
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle size={16} className="mr-1" />
                    {errors.email}
                  </p>
                )}
              </div>

              {/* Contraseña */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <Lock className="mr-2 text-amber-600" size={20} />
                  Contraseña *
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    placeholder="Mínimo 8 caracteres"
                    className={`input-field text-lg pr-12 ${errors.password ? 'border-red-500' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
                
                {/* Requisitos de contraseña */}
                {formData.password && (
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-medium text-gray-700 mb-2">Requisitos de contraseña:</p>
                    <div className="space-y-1 text-xs">
                      <div className={`flex items-center ${passwordValidation.requirements.minLength ? 'text-green-600' : 'text-red-600'}`}>
                        <Check size={12} className="mr-1" />
                        Mínimo 8 caracteres
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.upperCase ? 'text-green-600' : 'text-red-600'}`}>
                        <Check size={12} className="mr-1" />
                        Una letra mayúscula
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.lowerCase ? 'text-green-600' : 'text-red-600'}`}>
                        <Check size={12} className="mr-1" />
                        Una letra minúscula
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.numbers ? 'text-green-600' : 'text-red-600'}`}>
                        <Check size={12} className="mr-1" />
                        Un número
                      </div>
                      <div className={`flex items-center ${passwordValidation.requirements.specialChar ? 'text-green-600' : 'text-red-600'}`}>
                        <Check size={12} className="mr-1" />
                        Un carácter especial (!@#$%^&*)
                      </div>
                    </div>
                  </div>
                )}
                
                {errors.password && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle size={16} className="mr-1" />
                    {errors.password}
                  </p>
                )}
              </div>

              {/* Confirmar contraseña */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <Lock className="mr-2 text-amber-600" size={20} />
                  Confirmar Contraseña *
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                    placeholder="Repite tu contraseña"
                    className={`input-field text-lg pr-12 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle size={16} className="mr-1" />
                    {errors.confirmPassword}
                  </p>
                )}
              </div>

              {/* Nombre de la familia */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <User className="mr-2 text-amber-600" size={20} />
                  Nombre de la Familia *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Ej: Familia García"
                  className={`input-field text-lg ${errors.name ? 'border-red-500' : ''}`}
                />
                {errors.name && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle size={16} className="mr-1" />
                    {errors.name}
                  </p>
                )}
              </div>

              {/* Avatar - CONTENEDORES REDONDOS - MEJORADO PARA MÓVIL */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <User className="mr-2 text-amber-600" size={20} />
                  Elige tu Avatar
                </label>
                <div className="grid grid-cols-3 md:grid-cols-6 gap-3 md:gap-4">
                  {avatars.map((avatar) => (
                    <div
                      key={avatar.id}
                      className="flex flex-col items-center"
                    >
                      <button
                        type="button"
                        onClick={() => handleInputChange('avatar', avatar.id)}
                        className={`relative group transition-all hover:scale-105 focus:outline-none ${
                          formData.avatar === avatar.id
                            ? 'ring-3 ring-amber-500'
                            : 'hover:ring-2 hover:ring-amber-300'
                        }`}
                      >
                        {/* Contenedor circular perfectamente centrado */}
                        <div className={`w-16 h-16 md:w-18 md:h-18 rounded-full overflow-hidden border-2 transition-all flex items-center justify-center ${
                          formData.avatar === avatar.id
                            ? 'border-amber-500 bg-amber-100 shadow-lg'
                            : 'border-gray-200 bg-white group-hover:border-amber-300'
                        }`}>
                          <img 
                            src={avatar.src} 
                            alt={avatar.name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.src = ratonSaco; // Fallback image
                            }}
                          />
                        </div>
                      </button>
                      {/* Nombre centrado debajo */}
                      <div className="text-xs font-medium text-center mt-2 px-1 leading-tight">
                        {avatar.name}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Idioma preferido - MÁS COMPACTO Y SIN EMOJIS */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <Globe className="mr-2 text-amber-600" size={20} />
                  Idioma Preferido
                </label>
                <div className="flex flex-wrap gap-2">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      onClick={() => handleInputChange('preferred_language', lang.code)}
                      className={`px-4 py-2 rounded-lg border-2 transition-all hover:scale-105 text-sm font-medium ${
                        formData.preferred_language === lang.code
                          ? 'border-amber-500 bg-amber-100 text-amber-700 shadow-md'
                          : 'border-gray-200 bg-white text-gray-700 hover:border-amber-300'
                      }`}
                    >
                      {lang.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Miembros de la familia - MEJORADO PARA MÓVIL */}
              <div>
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 gap-3 sm:gap-0">
                  <label className="text-lg font-medium text-gray-700">
                    Miembros de la Familia * 
                    <span className="text-sm text-gray-500 ml-2 block sm:inline">
                      ({adultCount} adulto, {childCount} niños)
                    </span>
                  </label>
                  <button
                    type="button"
                    onClick={addMember}
                    disabled={childCount >= 4}
                    className="btn-secondary flex items-center justify-center text-xs sm:text-sm px-3 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Plus className="mr-1" size={14} />
                    Agregar Miembro
                  </button>
                </div>

                {errors.members && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
                    <p className="flex items-center">
                      <AlertCircle size={16} className="mr-2" />
                      {errors.members}
                    </p>
                  </div>
                )}

                <div className="space-y-4">
                  {formData.members.map((member, index) => (
                    <div key={index} className="bg-amber-50 border border-amber-200 rounded-xl p-4 sm:p-6">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="font-semibold text-gray-700">
                          {member.member_type === 'adult' ? 'Adulto Responsable' : `Niño ${index}`}
                        </h4>
                        {member.member_type === 'child' && (
                          <button
                            type="button"
                            onClick={() => removeMember(index)}
                            className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Nombre */}
                        <div>
                          <label className="block text-sm font-medium text-gray-600 mb-2">
                            Nombre *
                          </label>
                          <input
                            type="text"
                            value={member.name}
                            onChange={(e) => handleMemberChange(index, 'name', e.target.value)}
                            placeholder="Nombre completo"
                            className={`input-field ${errors[`member_${index}_name`] ? 'border-red-500' : ''}`}
                          />
                          {errors[`member_${index}_name`] && (
                            <p className="text-red-500 text-xs mt-1 flex items-center">
                              <AlertCircle size={12} className="mr-1" />
                              {errors[`member_${index}_name`]}
                            </p>
                          )}
                        </div>

                        {/* Edad */}
                        <div>
                          <label className="block text-sm font-medium text-gray-600 mb-2">
                            Edad * {member.member_type === 'adult' ? '(18+ años)' : '(0-17 años)'}
                          </label>
                          <input
                            type="number"
                            min={member.member_type === 'adult' ? 18 : 0}
                            max={member.member_type === 'adult' ? 120 : 17}
                            value={member.age}
                            onChange={(e) => handleMemberChange(index, 'age', e.target.value)}
                            placeholder="Edad"
                            className={`input-field ${errors[`member_${index}_age`] ? 'border-red-500' : ''}`}
                          />
                          {errors[`member_${index}_age`] && (
                            <p className="text-red-500 text-xs mt-1 flex items-center">
                              <AlertCircle size={12} className="mr-1" />
                              {errors[`member_${index}_age`]}
                            </p>
                          )}
                        </div>

                        {/* Tipo de miembro */}
                        <div>
                          <label className="block text-sm font-medium text-gray-600 mb-2">
                            Tipo
                          </label>
                          <div className="space-y-2">
                            {memberTypes.map((type) => {
                              const isDisabled = type.value === 'adult' && adultCount >= 1 && member.member_type !== 'adult';
                              return (
                                <label 
                                  key={type.value} 
                                  className={`flex items-center cursor-pointer ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                  <input
                                    type="radio"
                                    name={`member_${index}_type`}
                                    value={type.value}
                                    checked={member.member_type === type.value}
                                    onChange={(e) => handleMemberChange(index, 'member_type', e.target.value)}
                                    disabled={isDisabled}
                                    className="mr-2 text-amber-600"
                                  />
                                  <span className="text-sm">{type.label}</span>
                                </label>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Mensajes de error y éxito */}
              {errors.submit && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl">
                  <p className="font-medium flex items-center">
                    <AlertCircle className="mr-2" size={20} />
                    {errors.submit}
                  </p>
                </div>
              )}

              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-6 py-4 rounded-xl">
                  <p className="font-medium flex items-center">
                    <Check className="mr-2" size={20} />
                    {success}
                  </p>
                </div>
              )}

              {/* Botones - MEJORADOS PARA MÓVIL */}
              <div className="pt-6 space-y-4">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary w-full py-3 sm:py-4 text-base sm:text-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creando Familia...
                    </span>
                  ) : (
                    <span className="flex items-center">
                      <Check className="mr-2" size={20} />
                      Crear Familia y Comenzar Aventura
                    </span>
                  )}
                </button>

                {/* Link de texto en lugar de botón */}
                <div className="text-center">
                  <p className="text-gray-600 text-sm">
                    ¿Ya tienes una familia?{' '}
                    <Link
                      to="/login"
                      className="text-amber-600 hover:text-amber-700 font-medium underline hover:no-underline transition-all"
                    >
                      Iniciar Sesión
                    </Link>
                  </p>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
