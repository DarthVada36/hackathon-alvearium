import React from 'react';
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
  FiChevronRight
} from 'react-icons/fi';

const Dashboard = () => {
  const { user } = useAuth();

  const quickActions = [
    {
      title: "Chatear con Ratoncito",
      description: "Pregunta sobre Madrid",
      icon: <FiMessageCircle size={24} />,
      link: "/chat",
      color: "bg-blue-500"
    },
    {
      title: "Continuar Gymkana",
      description: "Sigue explorando",
      icon: <FiMap size={24} />,
      link: "/gymkana",
      color: "bg-green-500"
    }
  ];

  const recentPlaces = [
    { name: "Puerta del Sol", points: 25, date: "Hoy" },
    { name: "Plaza Mayor", points: 30, date: "Ayer" },
    { name: "Casa Ratoncito Pérez", points: 50, date: "2 días atrás" }
  ];

  const badges = [
    { name: "Primera Visita", icon: "🏆", unlocked: true },
    { name: "Explorador", icon: "🗺️", unlocked: true },
    { name: "Madrileño", icon: "🏛️", unlocked: false },
    { name: "Maestro", icon: "👑", unlocked: false }
  ];

  const getNextLevel = () => {
    if (user?.points < 51) return { level: "Explorador", needed: 51 - user.points };
    if (user?.points < 151) return { level: "Aventurero", needed: 151 - user.points };
    if (user?.points < 301) return { level: "Maestro Explorador", needed: 301 - user.points };
    return { level: "Máximo nivel", needed: 0 };
  };

  const nextLevel = getNextLevel();

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
      <Header title="Dashboard" />
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Saludo y Stats Principales */}
        <div className="card p-6">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 bg-amber-600 rounded-full flex items-center justify-center">
              <span className="text-2xl">🐭</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">
                ¡Hola, {user?.name}!
              </h2>
              <p className="text-gray-600">Nivel: {user?.level}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-600">{user?.points || 0}</div>
              <div className="text-sm text-gray-600">Puntos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-600">{user?.visitedPlaces?.length || 0}</div>
              <div className="text-sm text-gray-600">Lugares</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-600">{user?.badges?.length || 0}</div>
              <div className="text-sm text-gray-600">Insignias</div>
            </div>
          </div>
        </div>

        {/* Progreso al Siguiente Nivel */}
        {nextLevel.needed > 0 && (
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <FiTrendingUp className="mr-2 text-amber-600" />
              Progreso al Siguiente Nivel
            </h3>
            <div className="mb-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Próximo: {nextLevel.level}</span>
                <span>{nextLevel.needed} puntos restantes</span>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-amber-600 h-3 rounded-full transition-all duration-300"
                style={{ 
                  width: `${Math.max(10, ((user?.points || 0) / (user?.points + nextLevel.needed)) * 100)}%` 
                }}
              ></div>
            </div>
          </div>
        )}

        {/* Acciones Rápidas */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Acciones Rápidas</h3>
          <div className="grid grid-cols-1 gap-4">
            {quickActions.map((action, index) => (
              <Link key={index} to={action.link}>
                <div className="card p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center text-white`}>
                        {action.icon}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-800">{action.title}</h4>
                        <p className="text-sm text-gray-600">{action.description}</p>
                      </div>
                    </div>
                    <FiChevronRight className="text-gray-400" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Lugares Recientes */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <FiMapPin className="mr-2 text-amber-600" />
            Lugares Visitados Recientemente
          </h3>
          <div className="space-y-3">
            {recentPlaces.map((place, index) => (
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

        {/* Insignias */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <FiAward className="mr-2 text-amber-600" />
            Insignias
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {badges.map((badge, index) => (
              <div 
                key={index} 
                className={`card p-4 text-center ${!badge.unlocked ? 'opacity-50' : ''}`}
              >
                <div className="text-3xl mb-2">{badge.icon}</div>
                <h4 className="font-medium text-gray-800 text-sm">{badge.name}</h4>
                {!badge.unlocked && (
                  <p className="text-xs text-gray-500 mt-1">Bloqueada</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <Navigation />
    </div>
  );
};

export default Dashboard;
