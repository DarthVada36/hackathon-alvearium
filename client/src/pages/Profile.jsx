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
  FiTrendingUp,
  FiCheck
} from 'react-icons/fi';

// Import avatar images
import icon1 from '../assets/img/icon1png.png';
import icon2 from '../assets/img/icon2.png';
import icon3 from '../assets/img/icon3.png';
import icon4 from '../assets/img/icon4.png';
import icon5 from '../assets/img/icon5.png';
import icon6 from '../assets/img/icon6.png';

const Profile = () => {
  const { user, updateUserProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [showAvatarSelection, setShowAvatarSelection] = useState(false);
  const [editForm, setEditForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    avatar: user?.avatar || 'icon1'
  });

  // Available avatars
  const avatars = [
    { id: 'icon1', src: icon1, name: 'Ratoncito Clásico' },
    { id: 'icon2', src: icon2, name: 'Ratoncito Aventurero' },
    { id: 'icon3', src: icon3, name: 'Ratoncito Explorador' },
    { id: 'icon4', src: icon4, name: 'Ratoncito Real' },
    { id: 'icon5', src: icon5, name: 'Ratoncito Mágico' },
    { id: 'icon6', src: icon6, name: 'Ratoncito Maestro' }
  ];

  const getCurrentAvatar = () => {
    const currentAvatar = avatars.find(avatar => avatar.id === (user?.avatar || 'icon1'));
    return currentAvatar ? currentAvatar.src : icon1;
  };

  const handleSave = () => {
    updateUserProfile({
      name: editForm.name,
      email: editForm.email,
      avatar: editForm.avatar
    });
    setIsEditing(false);
    setShowAvatarSelection(false);
  };

  const handleCancel = () => {
    setEditForm({
      name: user?.name || '',
      email: user?.email || '',
      avatar: user?.avatar || 'icon1'
    });
    setIsEditing(false);
    setShowAvatarSelection(false);
  };

  const handleAvatarSelect = (avatarId) => {
    setEditForm({...editForm, avatar: avatarId});
    setShowAvatarSelection(false);
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
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
      <Header 
        title="Mi Perfil" 
        showBackButton
      >
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="p-2 rounded-lg hover:bg-amber-200 transition-colors"
        >
          <FiEdit3 size={20} className="text-amber-600" />
        </button>
      </Header>
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Información Personal */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <div className="flex items-center space-x-4 mb-6">
            <div className="relative">
              <div className="w-20 h-20 bg-amber-100 rounded-full overflow-hidden flex items-center justify-center border-2 border-amber-200">
                <img 
                  src={isEditing ? avatars.find(a => a.id === editForm.avatar)?.src : getCurrentAvatar()} 
                  alt="Avatar" 
                  className="w-20 h-20 object-cover"
                />
              </div>
              {isEditing && (
                <button
                  onClick={() => setShowAvatarSelection(!showAvatarSelection)}
                  className="absolute -bottom-1 -right-1 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center text-white text-xs hover:bg-amber-600 transition-colors"
                >
                  <FiEdit3 size={12} />
                </button>
              )}
            </div>
            <div className="flex-1">
              {isEditing ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    placeholder="Nombre"
                  />
                  <input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({...editForm, email: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    placeholder="Email"
                  />
                  <div className="flex space-x-2">
                    <button onClick={handleSave} className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-4 py-2 rounded-lg font-medium hover:from-amber-600 hover:to-amber-700 transition-colors">
                      Guardar
                    </button>
                    <button onClick={handleCancel} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors">
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

          {/* Avatar Selection Modal */}
          {showAvatarSelection && (
            <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <h4 className="font-semibold text-gray-800 mb-3">Elige tu avatar:</h4>
              <div className="grid grid-cols-3 gap-3">
                {avatars.map((avatar) => (
                  <button
                    key={avatar.id}
                    onClick={() => handleAvatarSelect(avatar.id)}
                    className={`relative p-3 rounded-xl border-2 transition-all hover:scale-105 ${
                      editForm.avatar === avatar.id 
                        ? 'border-amber-500 bg-amber-100' 
                        : 'border-gray-200 bg-white hover:border-amber-300'
                    }`}
                  >
                    <img 
                      src={avatar.src} 
                      alt={avatar.name} 
                      className="w-12 h-12 object-cover mx-auto mb-1 rounded-lg"
                    />
                    <p className="text-xs text-gray-600 text-center">{avatar.name}</p>
                    {editForm.avatar === avatar.id && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center">
                        <FiCheck className="text-white" size={12} />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Nivel Actual y Progreso */}
          <div className="border-t border-amber-200 pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-800">Nivel: {levelInfo.current}</span>
              {levelInfo.next && (
                <span className="text-sm text-gray-600">Próximo: {levelInfo.next}</span>
              )}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-amber-400 to-amber-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${levelInfo.progress}%` }}
              />
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
              <div key={index} className="bg-white rounded-2xl p-4 text-center shadow-sm border border-amber-100">
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
                className={`bg-white rounded-2xl p-4 shadow-sm border border-amber-100 ${!achievement.unlocked ? 'opacity-50' : ''}`}
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
              <div key={index} className="bg-white rounded-2xl p-4 shadow-sm border border-amber-100">
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
