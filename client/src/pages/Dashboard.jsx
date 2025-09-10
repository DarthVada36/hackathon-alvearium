import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
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
  FiInfo
} from 'react-icons/fi';

const Dashboard = () => {
  const { user } = useAuth();
  const [showLevelUpAnimation, setShowLevelUpAnimation] = useState(false);
  const [rutaProgress, setRutaProgress] = useState(35); // Progreso de la ruta actual

  // Animación de entrada
  useEffect(() => {
    const timer = setTimeout(() => {
      if (user?.points === 100) {
        setShowLevelUpAnimation(true);
        setTimeout(() => setShowLevelUpAnimation(false), 3000);
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [user?.points]);

  const quickActions = [
    {
      title: "Continuar Ruta",
      description: "Siguiente parada • 15 min",
      icon: <FiMap size={24} />,
      link: "/gymkana",
      gradient: "from-amber-500 to-amber-600",
      monedas: "+5",
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

  // Paradas de la Ruta del Ratón Pérez
  const rutaStops = [
    { name: "Casa Museo Ratón Pérez", status: "completed", monedas: 10, icon: "🏠", address: "Arenal, 8" },
    { name: "Palacio Real", status: "completed", monedas: 15, icon: "👑", address: "Bailén, s/n" },
    { name: "Puerta del Sol", status: "current", monedas: 10, icon: "☀️", address: "Puerta del Sol" },
    { name: "Plaza Mayor", status: "locked", monedas: 15, icon: "🏛️", address: "Plaza Mayor" },
    { name: "Convento Descalzas", status: "locked", monedas: 20, icon: "⛪", address: "Plaza Descalzas" },
    { name: "Final: Casa Ratoncito", status: "locked", monedas: 50, icon: "🎁", address: "Arenal, 8" }
  ];

  const achievements = [
    { name: "Primera Visita", icon: "🦷", unlocked: true, description: "Visitaste la Casa Museo" },
    { name: "Coleccionista", icon: "💰", unlocked: true, description: "10 monedas doradas" },
    { name: "Explorador Real", icon: "👑", unlocked: false, description: "Visita el Palacio Real" },
    { name: "Madrileño Experto", icon: "🏛️", unlocked: false, description: "Completa toda la ruta" }
  ];

  const museoStats = {
    tiempoEstimado: "2 horas",
    paradasCompletadas: 2,
    paradasTotales: 6,
    distanciaTotal: "1.5 km",
    monedasGanadas: user?.points || 25,
    fotosTomadas: 3
  };

  const getNextLevel = () => {
    const levels = [
      { threshold: 0, name: "Ratoncito Novato", color: "from-gray-400 to-gray-500", icon: "🐭" },
      { threshold: 30, name: "Ayudante del Ratón", color: "from-amber-400 to-amber-500", icon: "🦷" },
      { threshold: 60, name: "Guardian de Dientes", color: "from-amber-500 to-amber-600", icon: "✨" },
      { threshold: 100, name: "Amigo de Ratoncito", color: "from-amber-600 to-yellow-500", icon: "⭐" },
      { threshold: 150, name: "Embajador Real", color: "from-purple-500 to-purple-600", icon: "👑" }
    ];
    
    const currentLevel = levels.filter(l => user?.points >= l.threshold).pop();
    const nextLevel = levels.find(l => l.threshold > user?.points);
    
    if (!nextLevel) {
      return { 
        current: currentLevel, 
        next: null, 
        progress: 100,
        needed: 0 
      };
    }
    
    const progress = ((user?.points - currentLevel.threshold) / (nextLevel.threshold - currentLevel.threshold)) * 100;
    
    return {
      current: currentLevel,
      next: nextLevel,
      progress: Math.min(progress, 100),
      needed: nextLevel.threshold - user?.points
    };
  };

  const levelInfo = getNextLevel();

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
      {/* Header Temático */}
      <div className="bg-white shadow-sm sticky top-0 z-40 border-b-2 border-amber-200">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-amber-400 to-amber-500 rounded-full flex items-center justify-center shadow-lg animate-bounce">
                <span className="text-2xl">🐭</span>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-800">¡Hola, {user?.name}!</h1>
                <p className="text-xs text-amber-600 font-medium">{levelInfo.current?.name}</p>
              </div>
            </div>
            
            {/* Monedas y Nivel */}
            <div className="flex items-center space-x-3">
              <div className="bg-amber-100 px-3 py-1 rounded-full flex items-center space-x-1">
                <span className="text-xl">🪙</span>
                <span className="font-bold text-amber-700">{user?.points || 25}</span>
              </div>
              <div className="bg-purple-100 px-3 py-1 rounded-full">
                <span className="text-lg">{levelInfo.current?.icon}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Animación de nivel */}
      {showLevelUpAnimation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-3xl p-8 animate-bounce shadow-2xl">
            <div className="text-6xl text-center mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-center text-amber-600">¡Nuevo Nivel!</h2>
            <p className="text-gray-600 text-center mt-2">Ahora eres {levelInfo.current?.name}</p>
            <div className="text-4xl text-center mt-4">{levelInfo.current?.icon}</div>
          </div>
        </div>
      )}
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Banner de Bienvenida */}
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-2xl p-5 text-white shadow-lg">
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
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-amber-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-gray-800">Tu Progreso en la Ruta</h3>
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
                style={{ width: `${(museoStats.paradasCompletadas / museoStats.paradasTotales) * 100}%` }}
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
          <div className="bg-amber-50 rounded-xl p-3 border border-amber-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">☀️</span>
                <div>
                  <p className="text-xs text-amber-600 font-medium">Siguiente parada</p>
                  <p className="font-bold text-gray-800">Puerta del Sol</p>
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
                <div className={`bg-white rounded-2xl p-4 shadow-sm border-2 ${
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
            <Link to="/map" className="text-sm text-amber-600 font-medium">Ver mapa</Link>
          </div>
          <div className="bg-white rounded-2xl shadow-sm border border-amber-100 overflow-hidden">
            {rutaStops.map((stop, index) => (
              <div 
                key={index} 
                className={`p-4 border-b last:border-b-0 ${
                  stop.status === 'current' ? 'bg-amber-50' : ''
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
                className={`bg-white rounded-2xl p-4 text-center border-2 transition-all ${
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
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-2xl p-5 text-white shadow-lg">
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
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-amber-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Tu Visita</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <FiCamera className="mx-auto text-amber-500 mb-2" size={24} />
              <div className="text-2xl font-bold text-gray-800">{museoStats.fotosTomadas}</div>
              <div className="text-xs text-gray-600">Fotos</div>
            </div>
            <div className="text-center">
              <FiClock className="mx-auto text-amber-500 mb-2" size={24} />
              <div className="text-2xl font-bold text-gray-800">45</div>
              <div className="text-xs text-gray-600">Minutos</div>
            </div>
            <div className="text-center">
              <span className="text-2xl">🪙</span>
              <div className="text-2xl font-bold text-gray-800 mt-2">{museoStats.monedasGanadas}</div>
              <div className="text-xs text-gray-600">Monedas</div>
            </div>
          </div>
        </div>
      </div>

      {/* Menú de Navegación Original */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg">
        <div className="container mx-auto px-4">
          <div className="flex justify-around items-center py-2">
            <Link to="/dashboard" className="flex flex-col items-center p-2">
              <div className="p-2 rounded-lg bg-amber-100">
                <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </div>
              <span className="text-xs mt-1 text-amber-600 font-medium">Inicio</span>
            </Link>
            
            <Link to="/gymkana" className="flex flex-col items-center p-2">
              <div className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                <FiMap className="w-6 h-6 text-gray-600" />
              </div>
              <span className="text-xs mt-1 text-gray-600">Ruta</span>
            </Link>
            
            <Link to="/chat" className="flex flex-col items-center p-2">
              <div className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                <FiMessageCircle className="w-6 h-6 text-gray-600" />
              </div>
              <span className="text-xs mt-1 text-gray-600">Chat</span>
            </Link>
            
            <Link to="/profile" className="flex flex-col items-center p-2">
              <div className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <span className="text-xs mt-1 text-gray-600">Perfil</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;