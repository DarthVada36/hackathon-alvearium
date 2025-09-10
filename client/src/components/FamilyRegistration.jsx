import React, { useState } from 'react';
import ApiService from '../services/ApiService';

const FamilyRegistration = ({ onFamilyCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    preferred_language: 'es',
    members: [
      { name: '', age: '', member_type: 'adult' }
    ]
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMemberChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.map((member, i) => 
        i === index ? { ...member, [field]: value } : member
      )
    }));
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      // Convertir ages a números
      const familyData = {
        ...formData,
        members: formData.members.map(member => ({
          ...member,
          age: parseInt(member.age) || 0
        }))
      };

      const response = await ApiService.createFamily(familyData);
      setSuccess('¡Familia creada exitosamente! 🎉');
      
      // Reset form
      setFormData({
        name: '',
        preferred_language: 'es',
        members: [{ name: '', age: '', member_type: 'adult' }]
      });

      if (onFamilyCreated) {
        onFamilyCreated(response);
      }
    } catch (error) {
      setError(`Error al crear la familia: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold text-amber-600 mb-2">
          🐭 Registro de Familia del Ratoncito Pérez
        </h2>
        <p className="text-gray-600">
          Crea tu familia para comenzar la aventura en Madrid
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Nombre de la familia */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nombre de la Familia *
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            placeholder="Ej: Familia García"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            required
          />
        </div>

        {/* Idioma preferido */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Idioma Preferido
          </label>
          <select
            value={formData.preferred_language}
            onChange={(e) => handleInputChange('preferred_language', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
          >
            <option value="es">Español</option>
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="de">Deutsch</option>
          </select>
        </div>

        {/* Miembros de la familia */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <label className="block text-sm font-medium text-gray-700">
              Miembros de la Familia *
            </label>
            <button
              type="button"
              onClick={addMember}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm"
            >
              + Agregar Miembro
            </button>
          </div>

          {formData.members.map((member, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-medium text-gray-700">
                  Miembro {index + 1}
                </h4>
                {formData.members.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeMember(index)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Eliminar
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Nombre */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Nombre *
                  </label>
                  <input
                    type="text"
                    value={member.name}
                    onChange={(e) => handleMemberChange(index, 'name', e.target.value)}
                    placeholder="Nombre completo"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent text-sm"
                    required
                  />
                </div>

                {/* Edad */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Edad *
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="120"
                    value={member.age}
                    onChange={(e) => handleMemberChange(index, 'age', e.target.value)}
                    placeholder="Edad"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent text-sm"
                    required
                  />
                </div>

                {/* Tipo de miembro */}
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Tipo
                  </label>
                  <select
                    value={member.member_type}
                    onChange={(e) => handleMemberChange(index, 'member_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent text-sm"
                  >
                    <option value="adult">Adulto</option>
                    <option value="child">Niño</option>
                    <option value="baby">Bebé</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Mensajes de error y éxito */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Botón de envío */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold rounded-lg hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creando Familia...
            </span>
          ) : (
            '🐭 Crear Familia y Comenzar Aventura'
          )}
        </button>
      </form>
    </div>
  );
};

export default FamilyRegistration;
