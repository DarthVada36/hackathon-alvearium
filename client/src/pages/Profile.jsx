import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import ApiService from '../services/ApiService';
import { 
  FiUser, 
  FiStar, 
  FiMapPin, 
  FiAward,
  FiEdit3,
  FiMail,
  FiCalendar,
  FiTrendingUp,
  FiCheck,
  FiRefreshCw,
  FiAlertCircle
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

  // ============ ESTADOS DINÁMICOS ============
  const [families, setFamilies] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Available avatars
  const avatars = [
    { id: 'icon1', src: icon1, name: 'Ratoncito Clásico' },
    { id: 'icon2', src: icon2, name: 'Ratoncito Aventurero' },
    { id: 'icon3', src: icon3, name: 'Ratoncito Explorador' },
    { id: 'icon4', src: icon4, name: 'Ratoncito Real' },
    { id: 'icon5', src: icon5, name: 'Ratoncito Mágico' },
    { id: 'icon6', src: icon6, name: 'Ratoncito Maestro' }
  ];

  // ============ FUNCIONES DE CARGA ============
  
  const loadUserData = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      // Cargar perfil del usuario
      const profile = await ApiService.getCurrentUser();
      setUserProfile(profile);
      
      // Cargar familias del usuario
      const familiesResponse = await ApiService.getFamilies();
      setFamilies(familiesResponse.families || []);
      
      // DEBUG: Ver qué datos llegan exactamente
      console.log('🔍 Familias del backend:', familiesResponse.families);
      if (familiesResponse.families?.[0]) {
        console.log('🔍 Primera familia:', familiesResponse.families[0]);
        console.log('🔍 Campos disponibles:', Object.keys(familiesResponse.families[0]));
        
        // Verificar si current_poi_index existe
        console.log('🔍 current_poi_index:', familiesResponse.families[0].current_poi_index);
        console.log('🔍 points_earned:', familiesResponse.families[0].points_earned);
      }
      
      // DEBUG: También cargar estado de familia para comparar
      if (familiesResponse.families?.[0]) {
        try {
          const firstFamilyStatus = await ApiService.getFamilyStatus(familiesResponse.families[0].id);
          console.log('🔍 Estado de primera familia:', firstFamilyStatus);
          console.log('🔍 current_poi_index en estado:', firstFamilyStatus.current_poi_index);
          console.log('🔍 progress_percentage:', firstFamilyStatus.progress_percentage);
        } catch (error) {
          console.error('❌ Error obteniendo estado de familia:', error);
        }
      }
      
    } catch (error) {
      console.error('Error loading user data:', error);
      setError('Error cargando datos del perfil');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshData = async () => {
    await loadUserData();
  };

  // ============ EFFECTS ============
  
  useEffect(() => {
    loadUserData();
  }, []);

  useEffect(() => {
    if (user) {
      setEditForm({
        name: user.name || '',
        email: user.email || '',
        avatar: user.avatar || 'icon1'
      });
    }
  }, [user]);

  // ============ DATOS DINÁMICOS CALCULADOS ============
  
  // Calcular estadísticas reales desde las familias
  const totalPoints = userProfile?.total_points || families.reduce((sum, family) => sum + (family.points_earned || 0), 0) || 0;
  const totalPlaces = families.reduce((sum, family) => sum + (family.visited_pois || 0), 0) || 0;
  const totalFamilies = families.length || 0;

  const stats = [
    {
      label: "Puntos Totales",
      value: totalPoints,
      icon: <FiStar className="text-amber-600" />,
      color: "text-amber-600"
    },
    {
      label: "Lugares Visitados",
      value: totalPlaces,
      icon: <FiMapPin className="text-blue-500" />,
      color: "text-blue-500"
    },
    {
      label: "Familias",
      value: totalFamilies,
      icon: <FiAward className="text-green-500" />,
      color: "text-green-500"
    }
  ];

  // Logros dinámicos basados en datos reales
  const achievements = [
    { 
      name: "Primera Visita", 
      icon: "🦷", 
      unlocked: totalPlaces > 0, 
      description: "Visitaste tu primer lugar",
      date: families[0]?.created_at ? new Date(families[0].created_at).toLocaleDateString('es-ES') : null
    },
    { 
      name: "Explorador", 
      icon: "💰", 
      unlocked: totalPlaces >= 3, 
      description: "Visitaste 3 lugares diferentes",
      date: totalPlaces >= 3 ? new Date().toLocaleDateString('es-ES') : null
    },
    { 
      name: "Coleccionista", 
      icon: "👑", 
      unlocked: totalPoints >= 100, 
      description: "Conseguiste 100 puntos",
      date: totalPoints >= 100 ? new Date().toLocaleDateString('es-ES') : null
    },
    { 
      name: "Madrileño Experto", 
      icon: "🏛️", 
      unlocked: totalPlaces >= 10, 
      description: "Completa toda la ruta",
      date: totalPlaces >= 10 ? new Date().toLocaleDateString('es-ES') : null
    }
  ];

  // Lugares visitados dinámicos (simplificado basado en familias)
  const visitedPlaces = families.flatMap((family, familyIndex) => {
    const currentIndex = family.current_poi_index || 0;
    // Si está en índice N, ha visitado N+1 lugares
    const placesVisited = currentIndex + 1;
    const pointsPerPlace = Math.floor((family.points_earned || 0) / Math.max(placesVisited, 1));
    
    // Generar lugares genéricos basados en el progreso
    const places = [];
    for (let i = 0; i < Math.min(placesVisited, 3); i++) {
      places.push({
        name: `Lugar ${i + 1} - ${family.name}`,
        points: pointsPerPlace || 25,
        date: new Date(family.created_at).toLocaleDateString('es-ES')
      });
    }
    return places;
  }).slice(0, 5); // Mostrar máximo 5

  const getCurrentAvatar = () => {
    const currentAvatar = avatars.find(avatar => avatar.id === (user?.avatar || 'icon1'));
    return currentAvatar ? currentAvatar.src : icon1;
  };

  const handleSave = async () => {
    try {
      setError('');
      
      // Actualizar perfil en el contexto de autenticación
      updateUserProfile({
        name: editForm.name,
        email: editForm.email,
        avatar: editForm.avatar
      });
      
      // Aquí podrías agregar una llamada al backend si hay endpoint para actualizar perfil
      // await ApiService.updateProfile(editForm);
      
      setIsEditing(false);
      setShowAvatarSelection(false);
    } catch (error) {
      setError('Error actualizando perfil');
    }
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

  const getLevelProgress = () => {
    const points = totalPoints;
    if (points < 51) return { current: "Principiante", next: "Explorador", progress: (points / 51) * 100 };
    if (points < 151) return { current: "Explorador", next: "Aventurero", progress: ((points - 50) / 101) * 100 };
    if (points < 301) return { current: "Aventurero", next: "Maestro Explorador", progress: ((points - 150) / 151) * 100 };
    return { current: "Maestro Explorador", next: null, progress: 100 };
  };

  const levelInfo = getLevelProgress();

  // ============ LOADING STATE ============
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
        <Header title="Mi Perfil" showBackButton />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto mb-4"></div>
            <p className="text-amber-600 font-medium">Cargando perfil...</p>
          </div>
        </div>
        <Navigation />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
      <Header 
        title="Mi Perfil" 
        showBackButton
      >
        <div className="flex items-center space-x-2">
          <button
            onClick={refreshData}
            className="p-2 rounded-lg hover:bg-amber-200 transition-colors"
          >
            <FiRefreshCw size={16} className="text-amber-600" />
          </button>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="p-2 rounded-lg hover:bg-amber-200 transition-colors"
          >
            <FiEdit3 size={20} className="text-amber-600" />
          </button>
        </div>
      </Header>
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <div className="flex items-center">
              <FiAlertCircle className="mr-2" size={16} />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

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
                  <h2 className="text-xl font-bold text-gray-800">{user?.email?.split('@')[0] || 'Usuario'}</h2>
                  <div className="flex items-center space-x-2 text-gray-600 mt-1">
                    <FiMail size={16} />
                    <span>{user?.email}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-600 mt-1">
                    <FiCalendar size={16} />
                    <span>Miembro desde {userProfile?.user?.created_at ? new Date(userProfile.user.created_at).toLocaleDateString('es-ES') : 'Recientemente'}</span>
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

        {/* Estadísticas - AHORA DINÁMICAS */}
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

        {/* Logros - AHORA DINÁMICOS */}
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
                  {achievement.unlocked && achievement.date && (
                    <div className="text-right">
                      <div className="text-xs text-gray-500">{achievement.date}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Familias Creadas */}
        {families.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <FiUser className="mr-2 text-amber-600" />
              Mis Familias
            </h3>
            <div className="space-y-3">
              {families.map((family, index) => (
                <div key={index} className="bg-white rounded-2xl p-4 shadow-sm border border-amber-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-800">{family.name}</h4>
                      <p className="text-sm text-gray-600">
                        {family.member_count || 0} miembros • Creada el {new Date(family.created_at).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <FiStar className="text-amber-600" size={16} />
                      <span className="font-bold text-amber-600">{family.points_earned || 0}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lugares Visitados - SIMPLIFICADO PERO DINÁMICO */}
        {visitedPlaces.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <FiMapPin className="mr-2 text-amber-600" />
              Actividad Reciente
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
        )}

        {/* No hay familias */}
        {families.length === 0 && (
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-amber-100">
            <div className="text-4xl mb-4">🐭</div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">Crea tu primera familia</h3>
            <p className="text-gray-600">Para comenzar tu aventura con el Ratoncito Pérez, necesitas crear una familia.</p>
          </div>
        )}
      </div>

      <Navigation />
    </div>
  );
};

export default Profile;