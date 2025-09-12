import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import ApiService from '../services/ApiService';
import { 
  FiMapPin, 
  FiStar, 
  FiTrendingUp, 
  FiAward,
  FiMessageCircle,
  FiMap,
  FiChevronRight,
  FiClock,
  FiTarget,
  FiLock,
  FiCheck,
  FiGift,
  FiBookOpen,
  FiCamera,
  FiInfo,
  FiUsers,
  FiRefreshCw,
  FiAlertCircle
} from 'react-icons/fi';

// Importar imagen de fondo
import bgImage from '../assets/img/bg1.png'; // tu imagen de fondo

// Importar avatares
import icon1 from '../assets/img/icon1png.png';
import icon2 from '../assets/img/icon2.png';
import icon3 from '../assets/img/icon3.png';
import icon4 from '../assets/img/icon4.png';
import icon5 from '../assets/img/icon5.png';
import icon6 from '../assets/img/icon6.png';

// POIs oficiales con coordenadas (mismo que Gymkana)
const OFFICIAL_POIS_WITH_COORDINATES = [
  {
    id: "plaza_oriente",
    name: "Plaza de Oriente", 
    coordinates: { lat: 40.418407, lng: -3.712354 },
    address: "Plaza de Oriente, Madrid",
    description: "Plaza histórica frente al Palacio Real",
    points: 50,
    difficulty: "Fácil",
    estimatedTime: "15 min",
    tips: "Observa las estatuas de los reyes españoles en los jardines.",
    index: 0,
    icon: "👑"
  },
  {
    id: "plaza_ramales",
    name: "Plaza de Ramales",
    coordinates: { lat: 40.4175, lng: -3.7115 },
    address: "Plaza de Ramales, Madrid", 
    description: "Pequeña plaza con historia arqueológica",
    points: 30,
    difficulty: "Fácil",
    estimatedTime: "10 min",
    tips: "Busca las placas que mencionan los restos arqueológicos encontrados aquí.",
    index: 1,
    icon: "🏛️"
  },
  {
    id: "calle_vergara", 
    name: "Calle Vergara",
    coordinates: { lat: 40.4172, lng: -3.7095 },
    address: "Calle de Vergara, Madrid",
    description: "Calle histórica del centro de Madrid",
    points: 25,
    difficulty: "Fácil",
    estimatedTime: "8 min",
    tips: "Una calle tranquila perfecta para observar la arquitectura madrileña.",
    index: 2,
    icon: "🏘️"
  },
  {
    id: "plaza_isabel_ii",
    name: "Plaza de Isabel II", 
    coordinates: { lat: 40.4188, lng: -3.7119 },
    address: "Plaza de Isabel II, Madrid",
    description: "Plaza junto al Teatro Real",
    points: 40,
    difficulty: "Medio",
    estimatedTime: "12 min",
    tips: "Admira la fachada del Teatro Real, uno de los teatros de ópera más importantes de España.",
    index: 3,
    icon: "🎭"
  },
  {
    id: "calle_arenal_1",
    name: "Calle del Arenal (Teatro)",
    coordinates: { lat: 40.4185, lng: -3.7090 },
    address: "Calle del Arenal, Madrid",
    description: "Famosa calle comercial madrileña",
    points: 30,
    difficulty: "Fácil",
    estimatedTime: "10 min",
    tips: "Una de las calles más transitadas del centro histórico.",
    index: 4,
    icon: "🛍️"
  },
  {
    id: "calle_bordadores",
    name: "Calle de Bordadores",
    coordinates: { lat: 40.4178, lng: -3.7085 },
    address: "Calle de Bordadores, Madrid", 
    description: "Calle de artesanos tradicionales",
    points: 25,
    difficulty: "Fácil",
    estimatedTime: "8 min",
    tips: "Históricamente aquí trabajaban los bordadores de la corte real.",
    index: 5,
    icon: "🧵"
  },
  {
    id: "plazuela_san_gines",
    name: "Plazuela de San Ginés",
    coordinates: { lat: 40.4168, lng: -3.7088 },
    address: "Plazuela de San Ginés, Madrid",
    description: "Rincón histórico junto a la iglesia",
    points: 35,
    difficulty: "Medio",
    estimatedTime: "10 min",
    tips: "Visita la iglesia de San Ginés, una de las más antiguas de Madrid.",
    index: 6,
    icon: "⛪"
  },
  {
    id: "pasadizo_san_gines", 
    name: "Pasadizo de San Ginés",
    coordinates: { lat: 40.4166, lng: -3.7092 },
    address: "Pasadizo de San Ginés, Madrid",
    description: "Famoso por la chocolatería centenaria",
    points: 45,
    difficulty: "Medio",
    estimatedTime: "15 min",
    tips: "¡No te pierdas la chocolatería San Ginés, abierta desde 1894!",
    index: 7,
    icon: "🍫"
  },
  {
    id: "calle_arenal_2",
    name: "Calle del Arenal (Sol)",
    coordinates: { lat: 40.4167, lng: -3.7038 },
    address: "Calle del Arenal, Madrid", 
    description: "Tramo hacia Puerta del Sol",
    points: 30,
    difficulty: "Fácil",
    estimatedTime: "8 min",
    tips: "Estás muy cerca de la Puerta del Sol, corazón de Madrid.",
    index: 8,
    icon: "☀️"
  },
  {
    id: "museo_raton_perez",
    name: "Museo Ratoncito Pérez", 
    coordinates: { lat: 40.4165, lng: -3.7026 },
    address: "Calle del Arenal, 8, Madrid",
    description: "¡El hogar oficial del Ratoncito Pérez!",
    points: 100,
    difficulty: "Especial",
    estimatedTime: "20 min",
    tips: "¡El final de tu aventura! Busca la pequeña placa dorada en la fachada.",
    index: 9,
    icon: "🏠"
  }
];

const Dashboard = () => {
  const { user } = useAuth();
  
  // ============ ESTADOS DINÁMICOS ============
  const [families, setFamilies] = useState([]);
  const [selectedFamily, setSelectedFamily] = useState(null);
  const [familyStatus, setFamilyStatus] = useState(null);
  const [isLoadingFamilies, setIsLoadingFamilies] = useState(true);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [error, setError] = useState('');
  const [showLevelUpAnimation, setShowLevelUpAnimation] = useState(false);

  // Available avatars
  const avatars = [
    { id: 'icon1', src: icon1, name: 'Ratoncito Clásico' },
    { id: 'icon2', src: icon2, name: 'Ratoncito Aventurero' },
    { id: 'icon3', src: icon3, name: 'Ratoncito Explorador' },
    { id: 'icon4', src: icon4, name: 'Ratoncito Real' },
    { id: 'icon5', src: icon5, name: 'Ratoncito Mágico' },
    { id: 'icon6', src: icon6, name: 'Ratoncito Maestro' }
  ];

  // Get user's selected avatar
  const getUserAvatar = () => {
    const userAvatar = avatars.find(avatar => avatar.id === user?.avatar);
    return userAvatar ? userAvatar.src : icon1;
  };

  // ============ FUNCIONES DE CARGA DE DATOS ============
  
  const loadUserFamilies = async () => {
    try {
      setIsLoadingFamilies(true);
      setError('');
      const response = await ApiService.getFamilies();
      setFamilies(response.families || []);
      
      // Auto-seleccionar la primera familia si solo hay una
      if (response.families && response.families.length === 1) {
        setSelectedFamily(response.families[0]);
      }
    } catch (error) {
      console.error('Error loading families:', error);
      setError('Error cargando familias: ' + ApiService.formatError(error));
    } finally {
      setIsLoadingFamilies(false);
    }
  };

  const loadFamilyStatus = async () => {
    if (!selectedFamily) return;
    
    try {
      setIsLoadingStatus(true);
      const status = await ApiService.getFamilyStatus(selectedFamily.id);
      setFamilyStatus(status);
    } catch (error) {
      console.error('Error loading family status:', error);
      setError('Error cargando progreso de familia');
    } finally {
      setIsLoadingStatus(false);
    }
  };

  const refreshData = async () => {
    await Promise.all([
      loadUserFamilies(),
      selectedFamily ? loadFamilyStatus() : Promise.resolve()
    ]);
  };

  // ============ EFFECTS ============
  
  useEffect(() => {
    loadUserFamilies();
  }, []);

  useEffect(() => {
    if (selectedFamily) {
      loadFamilyStatus();
    }
  }, [selectedFamily]);

  // Animación de entrada
  useEffect(() => {
    const timer = setTimeout(() => {
      if (familyStatus?.total_points === 100) {
        setShowLevelUpAnimation(true);
        setTimeout(() => setShowLevelUpAnimation(false), 3000);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [familyStatus?.total_points]);

  // ============ DATOS DINÁMICOS CALCULADOS ============
  
  const museoStats = {
    tiempoEstimado: "2 horas",
    paradasCompletadas: familyStatus?.current_poi_index || 0,
    paradasTotales: OFFICIAL_POIS_WITH_COORDINATES.length,
    distanciaTotal: "1.5 km",
    monedasGanadas: familyStatus?.total_points || 0,
    fotosTomadas: 3
  };

  const rutaProgress = familyStatus?.progress_percentage || 0;

  // Generar rutaStops dinámicamente desde el backend
  const rutaStops = OFFICIAL_POIS_WITH_COORDINATES.map((poi) => {
    const currentIndex = familyStatus?.current_poi_index || 0;
    let status = 'locked';
    
    if (poi.index < currentIndex) {
      status = 'completed';
    } else if (poi.index === currentIndex) {
      status = 'current';
    }
    
    return {
      name: poi.name,
      status: status,
      monedas: poi.points,
      icon: poi.icon,
      address: poi.address
    };
  });

  // Obtener POI actual
  const getCurrentPoi = () => {
    const currentIndex = familyStatus?.current_poi_index || 0;
    return OFFICIAL_POIS_WITH_COORDINATES[currentIndex] || OFFICIAL_POIS_WITH_COORDINATES[0];
  };

  const currentPoi = getCurrentPoi();

  const quickActions = [
    {
      title: "Continuar Ruta",
      description: `Siguiente parada • ${currentPoi?.estimatedTime || '15 min'}`,
      icon: <FiMap size={24} />,
      link: "/gymkana",
      gradient: "from-amber-500 to-amber-600",
      monedas: `+${currentPoi?.points || 5}`,
      highlight: true
    },
    {
      title: "Hablar con Ratoncito",
      description: "Aprende curiosidades",
      icon: <FiMessageCircle size={24} />,
      link: "/chat",
      gradient: "from-blue-500 to-blue-600",
      monedas: "+2"
    },
    {
      title: "Museo Virtual",
      description: "Explora la casa museo",
      icon: <FiBookOpen size={24} />,
      link: "/museum",
      gradient: "from-purple-500 to-purple-600",
      monedas: "+3"
    }
  ];

  const achievements = [
    { name: "Primera Visita", icon: "🦷", unlocked: (familyStatus?.visited_pois || 0) > 0, description: "Visitaste la Casa Museo" },
    { name: "Coleccionista", icon: "💰", unlocked: (familyStatus?.total_points || 0) >= 30, description: "30 monedas doradas" },
    { name: "Explorador Real", icon: "👑", unlocked: (familyStatus?.visited_pois || 0) >= 5, description: "Visita 5 lugares" },
    { name: "Madrileño Experto", icon: "🏛️", unlocked: (familyStatus?.progress_percentage || 0) >= 100, description: "Completa toda la ruta" }
  ];

  const getNextLevel = () => {
    const points = familyStatus?.total_points || 0;
    const levels = [
      { threshold: 0, name: "Ratoncito Novato", color: "from-gray-400 to-gray-500", icon: "🐭" },
      { threshold: 30, name: "Ayudante del Ratón", color: "from-amber-400 to-amber-500", icon: "🦷" },
      { threshold: 60, name: "Guardian de Dientes", color: "from-amber-500 to-amber-600", icon: "✨" },
      { threshold: 100, name: "Amigo de Ratoncito", color: "from-amber-600 to-yellow-500", icon: "⭐" },
      { threshold: 150, name: "Embajador Real", color: "from-purple-500 to-purple-600", icon: "👑" }
    ];
    
    const currentLevel = levels.filter(l => points >= l.threshold).pop();
    const nextLevel = levels.find(l => l.threshold > points);
    
    if (!nextLevel) {
      return { 
        current: currentLevel, 
        next: null, 
        progress: 100,
        needed: 0 
      };
    }
    
    const progress = ((points - currentLevel.threshold) / (nextLevel.threshold - currentLevel.threshold)) * 100;
    
    return {
      current: currentLevel,
      next: nextLevel,
      progress: Math.min(progress, 100),
      needed: nextLevel.threshold - points
    };
  };

  const levelInfo = getNextLevel();

  // ============ LOADING STATES ============
  
  if (isLoadingFamilies) {
    return (
      <div 
        className="min-h-screen pb-20 relative"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-amber-50/80 via-yellow-50/80 to-amber-50/80 backdrop-blur-sm"></div>
        
        <div className="relative z-10">
          <div className="bg-white/95 backdrop-blur-sm shadow-sm sticky top-0 z-40 border-b-2 border-amber-200">
            <div className="container mx-auto px-4 py-3">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
                <span className="ml-3 text-amber-600 font-medium">Cargando dashboard...</span>
              </div>
            </div>
          </div>
          <Navigation />
        </div>
      </div>
    );
  }

  // ============ NO FAMILIES STATE ============
  
  if (families.length === 0) {
    return (
      <div 
        className="min-h-screen pb-20 relative"
        style={{
          backgroundImage: `url(${bgImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundAttachment: 'fixed'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-amber-50/80 via-yellow-50/80 to-amber-50/80"></div>
        
        <div className="relative z-10">
          <div className="bg-white/95 backdrop-blur-sm shadow-sm sticky top-0 z-40 border-b-2 border-amber-200">
            <div className="container mx-auto px-4 py-3">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-amber-400 to-amber-500 rounded-full flex items-center justify-center shadow-lg overflow-hidden border-2 border-amber-300">
                  <img 
                    src={getUserAvatar()} 
                    alt="Avatar del usuario" 
                    className="w-12 h-12 object-cover"
                  />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-800">¡Hola, {user?.email}!</h1>
                  <p className="text-xs text-amber-600 font-medium">Sin familias</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="container mx-auto px-4 py-8">
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 text-center shadow-sm border border-amber-100">
              <div className="text-6xl mb-4">🐭</div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">No tienes familias creadas</h2>
              <p className="text-gray-600 mb-6">
                Para comenzar tu aventura, necesitas crear una familia desde tu perfil.
              </p>
              <Link to="/profile">
                <button className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:from-amber-600 hover:to-amber-700 transition-colors">
                  Ir a Perfil
                </button>
              </Link>
            </div>
          </div>
          <Navigation />
        </div>
      </div>
    );
  }

  return (
    <div 
      className="min-h-screen pb-20 relative"
      style={{
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed'
      }}
    >
      {/* Overlay para mejorar legibilidad */}
      <div className="absolute inset-0 bg-gradient-to-b via-yellow-50/80 to-amber-50/80 backdrop-blur-sm"></div>
      
      {/* Todo el contenido existente va dentro de este div con z-index */}
      <div className="relative z-10">
        
        {/* Header Temático */}
        <div className="bg-white/95 backdrop-blur-sm shadow-sm sticky top-0 z-40 border-b-2 border-amber-200">
          <div className="container mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-amber-400 to-amber-500 rounded-full flex items-center justify-center shadow-lg overflow-hidden border-2 border-amber-300">
                  <img 
                    src={getUserAvatar()} 
                    alt="Avatar del usuario" 
                    className="w-12 h-12 object-cover"
                  />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-800">¡Hola, {user?.email?.split('@')[0] || 'Aventurero'}!</h1>
                  <p className="text-xs text-amber-600 font-medium">{levelInfo.current?.name}</p>
                </div>
              </div>
              
              {/* Monedas, Nivel y Refresh */}
              <div className="flex items-center space-x-3">
                <div className="bg-amber-100 px-3 py-1 rounded-full flex items-center space-x-1">
                  <span className="text-xl">🪙</span>
                  <span className="font-bold text-amber-700">{museoStats.monedasGanadas}</span>
                </div>
                <div className="bg-purple-100 px-3 py-1 rounded-full">
                  <span className="text-lg">{levelInfo.current?.icon}</span>
                </div>
                <button 
                  onClick={refreshData}
                  disabled={isLoadingStatus}
                  className="p-2 rounded-full bg-blue-100 hover:bg-blue-200 transition-colors"
                >
                  <FiRefreshCw className={`text-blue-600 ${isLoadingStatus ? 'animate-spin' : ''}`} size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Animación de nivel */}
        {showLevelUpAnimation && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="bg-white/95 backdrop-blur-sm rounded-3xl p-8 animate-bounce shadow-2xl">
              <div className="text-6xl text-center mb-4">🎉</div>
              <h2 className="text-2xl font-bold text-center text-amber-600">¡Nuevo Nivel!</h2>
              <p className="text-gray-600 text-center mt-2">Ahora eres {levelInfo.current?.name}</p>
              <div className="text-4xl text-center mt-4">{levelInfo.current?.icon}</div>
            </div>
          </div>
        )}
        
        <div className="container mx-auto px-4 py-6 space-y-6">
          {/* Selector de Familia */}
          {families.length > 1 && (
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-amber-100">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <FiUsers className="inline mr-2" />
                Selecciona tu familia:
              </label>
              <select
                value={selectedFamily?.id || ''}
                onChange={(e) => {
                  const family = families.find(f => f.id === parseInt(e.target.value));
                  setSelectedFamily(family);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
              >
                <option value="">Selecciona una familia...</option>
                {families.map((family) => (
                  <option key={family.id} value={family.id}>
                    {family.name} ({family.member_count || 0} miembros)
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50/95 backdrop-blur-sm border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              <div className="flex items-center">
                <FiAlertCircle className="mr-2" size={16} />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}

          {selectedFamily ? (
            <>
              {/* Banner de Bienvenida */}
              <div className="bg-gradient-to-r from-amber-500/95 to-amber-600/95 backdrop-blur-sm rounded-2xl p-5 text-white shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold mb-1">Ruta del Ratón Pérez</h2>
                    <p className="text-amber-100 text-sm">Descubre los lugares mágicos de Madrid</p>
                    <div className="flex items-center space-x-4 mt-3">
                      <div className="flex items-center space-x-1">
                        <FiClock size={16} />
                        <span className="text-sm">{museoStats.tiempoEstimado}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FiMapPin size={16} />
                        <span className="text-sm">{museoStats.distanciaTotal}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-6xl opacity-80">🦷</div>
                </div>
              </div>

              {/* Progreso de la Ruta */}
              <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-5 shadow-sm border border-amber-100">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">Progreso de {selectedFamily.name}</h3>
                    <p className="text-sm text-gray-600">
                      {museoStats.paradasCompletadas} de {museoStats.paradasTotales} paradas
                    </p>
                  </div>
                  <div className="bg-amber-100 p-3 rounded-full">
                    <FiMap className="text-amber-600" size={20} />
                  </div>
                </div>
                
                {/* Barra de progreso visual */}
                <div className="relative mb-6">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-amber-400 to-amber-500 h-3 rounded-full transition-all duration-700"
                      style={{ width: `${rutaProgress}%` }}
                    />
                  </div>
                  {/* Indicadores de paradas */}
                  <div className="absolute -top-1 w-full flex justify-between">
                    {rutaStops.map((stop, index) => (
                      <div 
                        key={index}
                        className={`w-5 h-5 rounded-full border-2 ${
                          stop.status === 'completed' 
                            ? 'bg-amber-500 border-amber-600' 
                            : stop.status === 'current'
                            ? 'bg-white border-amber-500 animate-pulse'
                            : 'bg-gray-300 border-gray-400'
                        }`}
                      />
                    ))}
                  </div>
                </div>

                {/* Próxima parada */}
                <div className="bg-amber-50/95 backdrop-blur-sm rounded-xl p-3 border border-amber-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{currentPoi?.icon || '📍'}</span>
                      <div>
                        <p className="text-xs text-amber-600 font-medium">Siguiente parada</p>
                        <p className="font-bold text-gray-800">{currentPoi?.name || 'Siguiente ubicación'}</p>
                      </div>
                    </div>
                    <Link to="/gymkana">
                      <button className="bg-amber-500 text-white px-4 py-2 rounded-full font-medium text-sm hover:bg-amber-600 transition">
                        Ir ahora
                      </button>
                    </Link>
                  </div>
                </div>
              </div>

              {/* Acciones Rápidas */}
              <div>
                <h3 className="text-lg font-bold text-gray-800 mb-4">Actividades</h3>
                <div className="space-y-3">
                  {quickActions.map((action, index) => (
                    <Link key={index} to={action.link}>
                      <div className={`bg-white/95 backdrop-blur-sm rounded-2xl p-4 shadow-sm border-2 ${
                        action.highlight ? 'border-amber-400' : 'border-transparent'
                      } hover:border-amber-400 transition-all transform hover:scale-[1.02] active:scale-[0.98]`}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className={`w-14 h-14 bg-gradient-to-r ${action.gradient} rounded-2xl flex items-center justify-center text-white shadow-lg`}>
                              {action.icon}
                            </div>
                            <div>
                              <h4 className="font-bold text-gray-800">{action.title}</h4>
                              <p className="text-sm text-gray-600">{action.description}</p>
                            </div>
                          </div>
                          <div className="flex flex-col items-end">
                            <div className="flex items-center space-x-1">
                              <span className="text-lg">🪙</span>
                              <span className="text-sm font-bold text-amber-600">{action.monedas}</span>
                            </div>
                            <FiChevronRight className="text-gray-400 mt-1" />
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>

              {/* Paradas de la Ruta */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-800">Paradas de la Ruta</h3>
                  <Link to="/gymkana" className="text-sm text-amber-600 font-medium">Ver mapa</Link>
                </div>
                <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-sm border border-amber-100 overflow-hidden">
                  {rutaStops.slice(0, 6).map((stop, index) => (
                    <div 
                      key={index} 
                      className={`p-4 border-b last:border-b-0 ${
                        stop.status === 'current' ? 'bg-amber-50/95 backdrop-blur-sm' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`text-2xl ${stop.status === 'locked' ? 'opacity-40' : ''}`}>
                            {stop.status === 'locked' ? '🔒' : stop.icon}
                          </div>
                          <div>
                            <h4 className={`font-semibold ${
                              stop.status === 'locked' ? 'text-gray-400' : 'text-gray-800'
                            }`}>{stop.name}</h4>
                            <p className="text-xs text-gray-500">{stop.address}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {stop.status === 'completed' ? (
                            <>
                              <FiCheck className="text-green-500" size={16} />
                              <div className="flex items-center space-x-1">
                                <span className="text-sm">🪙</span>
                                <span className="font-bold text-green-600">+{stop.monedas}</span>
                              </div>
                            </>
                          ) : stop.status === 'current' ? (
                            <span className="bg-amber-500 text-white text-xs px-2 py-1 rounded-full font-medium animate-pulse">
                              Actual
                            </span>
                          ) : (
                            <div className="flex items-center space-x-1 opacity-50">
                              <span className="text-sm">🪙</span>
                              <span className="text-gray-500">{stop.monedas}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {rutaStops.length > 6 && (
                    <div className="p-4 text-center">
                      <Link to="/gymkana" className="text-amber-600 hover:text-amber-700 font-medium text-sm">
                        Ver todas las paradas ({rutaStops.length - 6} más)
                      </Link>
                    </div>
                  )}
                </div>
              </div>

              {/* Logros */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-800">Tus Logros</h3>
                  <span className="text-sm text-gray-600">
                    {achievements.filter(a => a.unlocked).length}/{achievements.length}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {achievements.map((achievement, index) => (
                    <div 
                      key={index} 
                      className={`bg-white/95 backdrop-blur-sm rounded-2xl p-4 text-center border-2 transition-all ${
                        achievement.unlocked 
                          ? 'border-amber-400 shadow-md' 
                          : 'border-gray-200 opacity-60'
                      }`}
                    >
                      <div className={`text-4xl mb-2 ${achievement.unlocked ? '' : 'grayscale'}`}>
                        {achievement.icon}
                      </div>
                      <h4 className="font-bold text-gray-800 text-sm">{achievement.name}</h4>
                      <p className="text-xs text-gray-500 mt-1">{achievement.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Datos Curiosos */}
              <div className="bg-gradient-to-r from-purple-500/95 to-purple-600/95 backdrop-blur-sm rounded-2xl p-5 text-white shadow-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-bold flex items-center">
                      <FiInfo className="mr-2" />
                      ¿Sabías que...?
                    </h3>
                    <p className="text-sm opacity-90 mt-2">
                      El Ratón Pérez vive en una caja de galletas Prast en el sótano de la Casa Museo, 
                      en el número 8 de la calle Arenal de Madrid.
                    </p>
                  </div>
                  <div className="text-5xl opacity-50">🦷</div>
                </div>
                <Link to="/chat">
                  <button className="mt-4 bg-white text-purple-600 px-4 py-2 rounded-full text-sm font-bold hover:bg-purple-50 transition">
                    Descubre más curiosidades
                  </button>
                </Link>
              </div>

              {/* Estadísticas del Museo */}
              <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-5 shadow-sm border border-amber-100">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Tu Visita</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <FiCamera className="mx-auto text-amber-500 mb-2" size={24} />
                    <div className="text-2xl font-bold text-gray-800">{museoStats.fotosTomadas}</div>
                    <div className="text-xs text-gray-600">Fotos</div>
                  </div>
                  <div className="text-center">
                    <FiClock className="mx-auto text-amber-500 mb-2" size={24} />
                    <div className="text-2xl font-bold text-gray-800">{Math.round(rutaProgress * 0.45)}</div>
                    <div className="text-xs text-gray-600">Minutos</div>
                  </div>
                  <div className="text-center">
                    <span className="text-2xl">🪙</span>
                    <div className="text-2xl font-bold text-gray-800 mt-2">{museoStats.monedasGanadas}</div>
                    <div className="text-xs text-gray-600">Monedas</div>
                  </div>
                </div>
              </div>

              {/* Información de progreso real del backend */}
              {familyStatus && (
                <div className="bg-gradient-to-r from-blue-500/95 to-blue-600/95 backdrop-blur-sm rounded-2xl p-5 text-white shadow-lg">
                  <h3 className="font-bold text-lg mb-3 flex items-center">
                    <FiTarget className="mr-2" />
                    Estado de tu Aventura
                  </h3>
                  <div className="space-y-2 text-sm text-blue-100">
                    <p>• <strong>POI actual:</strong> {familyStatus.current_poi_index + 1}/{OFFICIAL_POIS_WITH_COORDINATES.length}</p>
                    <p>• <strong>Progreso:</strong> {familyStatus.progress_percentage}% completado</p>
                    <p>• <strong>Puntos totales:</strong> {familyStatus.total_points} monedas</p>
                    <p>• <strong>Lugares visitados:</strong> {familyStatus.visited_pois} de {OFFICIAL_POIS_WITH_COORDINATES.length}</p>
                    {familyStatus.progress_percentage < 100 && (
                      <p>• <strong>Siguiente:</strong> {currentPoi?.name}</p>
                    )}
                  </div>
                </div>
              )}
            </>
          ) : (
            /* Sin familia seleccionada */
            <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 text-center shadow-sm border border-amber-100">
              <div className="text-4xl mb-4">🐭</div>
              <h3 className="text-lg font-bold text-gray-800 mb-2">Selecciona una familia</h3>
              <p className="text-gray-600">Elige una familia para ver tu progreso en la aventura</p>
            </div>
          )}
        </div>

        <Navigation />
      </div>
    </div>
  );
};

export default Dashboard;