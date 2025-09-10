import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import ApiService from '../services/ApiService';
import { FiUser, FiUsers, FiPlus, FiTrash2, FiCheck, FiGlobe } from 'react-icons/fi';
import ratonSaco from '../assets/img/raton-saco.png';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    preferred_language: 'es',
    members: [
      { name: '', age: '', member_type: 'adult' }
    ]
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();

  // Opciones de idioma
  const languages = [
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
  ];

  // Tipos de miembro
  const memberTypes = [
    { value: 'adult', label: 'Adulto', icon: '👨' },
    { value: 'child', label: 'Niño/a', icon: '🧒' },
    { value: 'baby', label: 'Bebé', icon: '👶' }
  ];

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
    setFormData(prev => ({
      ...prev,
      members: prev.members.map((member, i) => 
        i === index ? { ...member, [field]: value } : member
      )
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
      members: [...prev.members, { name: '', age: '', member_type: 'adult' }]
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

  const validateForm = () => {
    const newErrors = {};
    
    // Validar nombre de familia
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre de la familia es obligatorio';
    }
    
    // Validar miembros
    formData.members.forEach((member, index) => {
      if (!member.name.trim()) {
        newErrors[`member_${index}_name`] = 'El nombre es obligatorio';
      }
      if (!member.age || member.age < 0 || member.age > 120) {
        newErrors[`member_${index}_age`] = 'Edad válida requerida (0-120)';
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
        ...formData,
        members: formData.members.map(member => ({
          ...member,
          age: parseInt(member.age) || 0
        }))
      };

      const response = await ApiService.createFamily(familyData);
      
      setSuccess('¡Familia creada exitosamente! 🎉 Redirigiendo al dashboard...');
      
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100">
      <Header title="Registro de Familia" showBackButton />
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="card p-8">
            <div className="text-center mb-8">
              <div className="w-24 h-24 bg-gradient-to-br from-amber-100 to-amber-200 rounded-full overflow-hidden flex items-center justify-center mx-auto mb-4 border-4 border-amber-300 shadow-lg">
                <img 
                  src={ratonSaco} 
                  alt="Ratoncito Pérez" 
                  className="w-20 h-20 object-contain"
                />
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">🐭 Registro de Familia</h2>
              <p className="text-gray-600">Crea tu familia para comenzar la aventura con el Ratoncito Pérez en Madrid</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Nombre de la familia */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <FiUser className="mr-2 text-amber-600" />
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
                  <p className="text-red-500 text-sm mt-1">{errors.name}</p>
                )}
              </div>

              {/* Idioma preferido */}
              <div>
                <label className="flex items-center text-lg font-medium text-gray-700 mb-3">
                  <FiGlobe className="mr-2 text-amber-600" />
                  Idioma Preferido
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      onClick={() => handleInputChange('preferred_language', lang.code)}
                      className={`p-3 rounded-xl border-2 transition-all hover:scale-105 ${
                        formData.preferred_language === lang.code
                          ? 'border-amber-500 bg-amber-100 shadow-md'
                          : 'border-gray-200 bg-white hover:border-amber-300'
                      }`}
                    >
                      <div className="text-2xl mb-1">{lang.flag}</div>
                      <div className="text-sm font-medium">{lang.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Miembros de la familia */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <label className="flex items-center text-lg font-medium text-gray-700">
                    <FiUsers className="mr-2 text-amber-600" />
                    Miembros de la Familia *
                  </label>
                  <button
                    type="button"
                    onClick={addMember}
                    className="btn-secondary flex items-center text-sm"
                  >
                    <FiPlus className="mr-2" />
                    Agregar Miembro
                  </button>
                </div>

                <div className="space-y-4">
                  {formData.members.map((member, index) => (
                    <div key={index} className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="font-semibold text-gray-700 flex items-center">
                          <span className="text-amber-600 mr-2">👤</span>
                          Miembro {index + 1}
                        </h4>
                        {formData.members.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeMember(index)}
                            className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50"
                          >
                            <FiTrash2 />
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
                            <p className="text-red-500 text-xs mt-1">{errors[`member_${index}_name`]}</p>
                          )}
                        </div>

                        {/* Edad */}
                        <div>
                          <label className="block text-sm font-medium text-gray-600 mb-2">
                            Edad *
                          </label>
                          <input
                            type="number"
                            min="0"
                            max="120"
                            value={member.age}
                            onChange={(e) => handleMemberChange(index, 'age', e.target.value)}
                            placeholder="Edad"
                            className={`input-field ${errors[`member_${index}_age`] ? 'border-red-500' : ''}`}
                          />
                          {errors[`member_${index}_age`] && (
                            <p className="text-red-500 text-xs mt-1">{errors[`member_${index}_age`]}</p>
                          )}
                        </div>

                        {/* Tipo de miembro */}
                        <div>
                          <label className="block text-sm font-medium text-gray-600 mb-2">
                            Tipo
                          </label>
                          <div className="space-y-2">
                            {memberTypes.map((type) => (
                              <label key={type.value} className="flex items-center cursor-pointer">
                                <input
                                  type="radio"
                                  name={`member_${index}_type`}
                                  value={type.value}
                                  checked={member.member_type === type.value}
                                  onChange={(e) => handleMemberChange(index, 'member_type', e.target.value)}
                                  className="mr-2 text-amber-600"
                                />
                                <span className="text-lg mr-2">{type.icon}</span>
                                <span className="text-sm">{type.label}</span>
                              </label>
                            ))}
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
                  <p className="font-medium">❌ {errors.submit}</p>
                </div>
              )}

              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-6 py-4 rounded-xl">
                  <p className="font-medium">✅ {success}</p>
                </div>
              )}

              {/* Botones */}
              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="btn-primary flex-1 py-4 text-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
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
                      <FiCheck className="mr-2" />
                      🐭 Crear Familia y Comenzar Aventura
                    </span>
                  )}
                </button>

                <Link
                  to="/login"
                  className="btn-secondary flex-1 py-4 text-lg text-center"
                >
                  ¿Ya tienes una familia? Iniciar Sesión
                </Link>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
