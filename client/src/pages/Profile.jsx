import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { 
  FiUser, 
  FiStar, 
  FiMapPin, 
  FiAward,
  FiEdit3,
  FiMail,
  FiCalendar,
  FiTrendingUp
} from 'react-icons/fi';

const Profile = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });

  const handleSave = () => {
    // Aquí iría la lógica para actualizar el perfil
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditForm({
      name: user?.name || '',
      email: user?.email || ''
    });
    setIsEditing(false);
  };

  const stats = [
    {
      label: "Puntos Totales",
      value: user?.points || 0,
      icon: <FiStar className="text-amber-600" />,
      color: "text-amber-600"
    },
    {
      label: "Lugares Visitados",
      value: user?.visitedPlaces?.length || 0,
      icon: <FiMapPin className="text-blue-500" />,
      color: "text-blue-500"
    },
    {
      label: "Insignias",
      value: user?.badges?.length || 0,
      icon: <FiAward className="text-green-500" />,
      color: "text-green-500"
    }
  ];

  const achievements = [
    { name: "Primera Visita", description: "Visitaste tu primer lugar", unlocked: true, date: "15 Nov 2024" },
    { name: "Explorador", description: "Visitaste 3 lugares diferentes", unlocked: true, date: "16 Nov 2024" },
    { name: "Madrileño", description: "Completaste 5 lugares emblemáticos", unlocked: false, date: null },
    { name: "Maestro", description: "Completaste toda la ruta oficial", unlocked: false, date: null }
  ];

  const visitedPlaces = [
    { name: "Casa del Ratoncito Pérez", points: 50, date: "16 Nov 2024" },
    { name: "Puerta del Sol", points: 25, date: "16 Nov 2024" },
    { name: "Plaza Mayor", points: 30, date: "15 Nov 2024" }
  ];

  const getLevelProgress = () => {
    const points = user?.points || 0;
    if (points < 51) return { current: "Principiante", next: "Explorador", progress: (points / 51) * 100 };
    if (points < 151) return { current: "Explorador", next: "Aventurero", progress: ((points - 50) / 101) * 100 };
    if (points < 301) return { current: "Aventurero", next: "Maestro Explorador", progress: ((points - 150) / 151) * 100 };
    return { current: "Maestro Explorador", next: null, progress: 100 };
  };

  const levelInfo = getLevelProgress();

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
      <Header 
        title="Mi Perfil" 
        showBackButton
      >
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="p-2 rounded-lg hover:bg-lime-200/50 transition-colors"
        >
          <FiEdit3 size={20} className="text-amber-600" />
        </button>
      </Header>
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Información Personal */}
        <div className="card p-6">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-20 h-20 bg-amber-600 rounded-full flex items-center justify-center">
              <span className="text-3xl">🐭</span>
            </div>
            <div className="flex-1">
              {isEditing ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                    className="input-field"
                    placeholder="Nombre"
                  />
                  <input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({...editForm, email: e.target.value})}
                    className="input-field"
                    placeholder="Email"
                  />
                  <div className="flex space-x-2">
                    <button onClick={handleSave} className="btn-primary text-sm px-4 py-2">
                      Guardar
                    </button>
                    <button onClick={handleCancel} className="btn-secondary text-sm px-4 py-2">
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <h2 className="text-xl font-bold text-gray-800">{user?.name}</h2>
                  <div className="flex items-center space-x-2 text-gray-600 mt-1">
                    <FiMail size={16} />
                    <span>{user?.email}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-600 mt-1">
                    <FiCalendar size={16} />
                    <span>Miembro desde Nov 2024</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Nivel Actual y Progreso */}
          <div className="border-t border-lime-200/30 pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-800">Nivel: {levelInfo.current}</span>
              {levelInfo.next && (
                <span className="text-sm text-gray-600">Próximo: {levelInfo.next}</span>
              )}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-amber-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${levelInfo.progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Estadísticas */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <FiTrendingUp className="mr-2 text-amber-600" />
            Estadísticas
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {stats.map((stat, index) => (
              <div key={index} className="card p-4 text-center">
                <div className="flex justify-center mb-2">
                  {stat.icon}
                </div>
                <div className={`text-2xl font-bold ${stat.color}`}>
                  {stat.value}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Logros */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <FiAward className="mr-2 text-amber-600" />
            Logros Desbloqueados
          </h3>
          <div className="space-y-3">
            {achievements.map((achievement, index) => (
              <div 
                key={index} 
                className={`card p-4 ${!achievement.unlocked ? 'opacity-50' : ''}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      achievement.unlocked ? 'bg-amber-600' : 'bg-gray-300'
                    }`}>
                      <FiAward className="text-white" size={20} />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">{achievement.name}</h4>
                      <p className="text-sm text-gray-600">{achievement.description}</p>
                    </div>
                  </div>
                  {achievement.unlocked && (
                    <div className="text-right">
                      <div className="text-xs text-gray-500">{achievement.date}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lugares Visitados */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <FiMapPin className="mr-2 text-amber-600" />
            Lugares Visitados
          </h3>
          <div className="space-y-3">
            {visitedPlaces.map((place, index) => (
              <div key={index} className="card p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-800">{place.name}</h4>
                    <p className="text-sm text-gray-600">{place.date}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <FiStar className="text-amber-600" size={16} />
                    <span className="font-bold text-amber-600">+{place.points}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <Navigation />
    </div>
  );
};

export default Profile;
