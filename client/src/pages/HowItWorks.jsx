import React from 'react';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { 
  FiMapPin, 
  FiStar, 
  FiTarget, 
  FiMessageCircle, 
  FiAward, 
  FiCamera,
  FiPlay,
  FiShare,
  FiGift,
  FiHelpCircle,
  FiNavigation,
  FiDollarSign,
  FiClock,
  FiUsers,
  FiSmartphone,
  FiBook,
  FiTruck,
  FiCoffee,
  FiBattery,
  FiSun
} from 'react-icons/fi';

// Importar imagen del ratón
import ratonSaco from '../assets/img/raton-saco.png';

const HowItWorks = () => {
  const guideSteps = [
    {
      icon: <FiMapPin className="text-amber-600" size={32} />,
      title: "Explora la Ruta Official",
      description: "Visita los 6 lugares oficiales del Ratoncito Pérez en Madrid y gana entre 10-50 puntos por ubicación.",
      points: "10-50 puntos"
    },
    {
      icon: <FiNavigation className="text-blue-600" size={32} />,
      title: "Encuentra Lugares Cercanos",
      description: "Usa la geolocalización para descubrir sitios históricos cerca de ti con recompensas especiales.",
      points: "5-25 puntos"
    },
    {
      icon: <FiMessageCircle className="text-green-600" size={32} />,
      title: "Usa el Chat Guía",
      description: "Pregunta al Ratoncito sobre historia, direcciones y curiosidades de Madrid.",
      points: "Gratis"
    },
    {
      icon: <FiCamera className="text-purple-600" size={32} />,
      title: "Toma Fotos en Ubicaciones",
      description: "Captura momentos especiales en cada lugar de la ruta y guárdalos en tu perfil.",
      points: "2-5 puntos extra"
    }
  ];

  const bonusActivities = [
    {
      icon: <FiShare className="text-pink-500" size={28} />,
      title: "Comparte en Instagram",
      description: "Sube una foto taggeando @ratonperez_madrid",
      reward: "+15 puntos",
      color: "border-pink-200 bg-pink-50"
    },
    {
      icon: <FiPlay className="text-indigo-500" size={28} />,
      title: "Minijuegos en Ubicaciones",
      description: "Encuentra códigos QR ocultos para juegos especiales",
      reward: "+20 puntos",
      color: "border-indigo-200 bg-indigo-50"
    },
    {
      icon: <FiGift className="text-red-500" size={28} />,
      title: "Visitas en Grupo",
      description: "Trae a 3+ amigos y obtén bonificación grupal",
      reward: "+30 puntos",
      color: "border-red-200 bg-red-50"
    },
    {
      icon: <FiStar className="text-yellow-500" size={28} />,
      title: "Completa Desafíos Diarios",
      description: "Pequeñas misiones que cambian cada día",
      reward: "+10 puntos",
      color: "border-yellow-200 bg-yellow-50"
    }
  ];

  const chatFeatures = [
    { icon: <FiNavigation className="text-blue-500" size={16} />, text: "Direcciones precisas a cualquier lugar de la ruta" },
    { icon: <FiBook className="text-green-500" size={16} />, text: "Historia y curiosidades de cada ubicación" }, 
    { icon: <FiClock className="text-purple-500" size={16} />, text: "Horarios de apertura y mejor momento para visitar" },
    { icon: <FiCoffee className="text-amber-500" size={16} />, text: "Recomendaciones de restaurantes cercanos" },
    { icon: <FiTruck className="text-gray-500" size={16} />, text: "Información del transporte público" },
    { icon: <FiStar className="text-yellow-500" size={16} />, text: "Consejos para maximizar tus puntos" }
  ];

  const levelSystem = [
    { level: "Ratoncito Novato", points: "0-29 puntos", perks: "Acceso básico a la ruta" },
    { level: "Ayudante del Ratón", points: "30-59 puntos", perks: "Descuentos en tiendas oficiales" },
    { level: "Guardian de Dientes", points: "60-99 puntos", perks: "Acceso a eventos especiales" },
    { level: "Amigo de Ratoncito", points: "100-149 puntos", perks: "Tours privados gratuitos" },
    { level: "Embajador Real", points: "150+ puntos", perks: "Acceso VIP y merchandise exclusivo" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
      <Header title="Guía de la App" showBackButton />
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Hero Section con imagen del ratón */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <div className="flex items-center space-x-6">
            <div className="flex-shrink-0">
              <img 
                src={ratonSaco} 
                alt="Ratoncito Pérez" 
                className="w-24 h-24 object-contain"
              />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                ¡Bienvenido a la Aventura!
              </h2>
              <p className="text-gray-600">
                Descubre Madrid siguiendo los pasos del famoso Ratoncito Pérez
              </p>
            </div>
          </div>
        </div>

        {/* Cómo Ganar Puntos */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FiDollarSign className="mr-2 text-amber-600" />
            Cómo Ganar Puntos
          </h3>
          <div className="space-y-4">
            {guideSteps.map((step, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-xl">
                <div className="flex-shrink-0">
                  {step.icon}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-800 mb-1">{step.title}</h4>
                  <p className="text-gray-600 text-sm mb-2">{step.description}</p>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                    {step.points}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actividades Bonus */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FiGift className="mr-2 text-amber-600" />
            Puntos Extra y Actividades Especiales
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bonusActivities.map((activity, index) => (
              <div key={index} className={`p-4 rounded-xl border-2 ${activity.color}`}>
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {activity.icon}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800 mb-1">{activity.title}</h4>
                    <p className="text-gray-600 text-sm mb-2">{activity.description}</p>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800">
                      {activity.reward}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Guía del Chat Bot */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FiMessageCircle className="mr-2 text-amber-600" />
            Tu Guía Turístico Virtual
          </h3>
          <p className="text-gray-600 mb-4">
            El Ratoncito Pérez está aquí para ayudarte. Puedes preguntarle sobre:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {chatFeatures.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-amber-50 rounded-lg">
                {feature.icon}
                <span className="text-sm text-gray-700">{feature.text}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <p className="text-blue-800 text-sm flex items-center">
              <FiHelpCircle className="mr-2 text-blue-600" size={16} />
              <strong>Consejo:</strong> Pregunta "¿Dónde estoy?" para obtener información específica de tu ubicación actual
            </p>
          </div>
        </div>

        {/* Sistema de Niveles */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FiAward className="mr-2 text-amber-600" />
            Sistema de Niveles y Recompensas
          </h3>
          <div className="space-y-3">
            {levelSystem.map((level, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl border border-amber-200">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-800">{level.level}</h4>
                  <p className="text-amber-600 text-sm font-medium">{level.points}</p>
                </div>
                <div className="text-right">
                  <p className="text-gray-600 text-sm">{level.perks}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Consejos Finales */}
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-2xl p-6 text-white">
          <h3 className="text-xl font-bold mb-4 flex items-center">
            <FiTarget className="mr-2" />
            ¡Consejos para Maximizar tu Aventura!
          </h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <FiBattery className="text-amber-200 mt-1" size={16} />
              <p className="text-sm">Mantén tu batería cargada para no perderte ninguna ubicación</p>
            </div>
            <div className="flex items-start space-x-3">
              <FiSun className="text-amber-200 mt-1" size={16} />
              <p className="text-sm">Los mejores momentos para visitar son por la mañana (menos multitudes)</p>
            </div>
            <div className="flex items-start space-x-3">
              <FiCamera className="text-amber-200 mt-1" size={16} />
              <p className="text-sm">No olvides tomar fotos en cada ubicación para puntos extra</p>
            </div>
            <div className="flex items-start space-x-3">
              <FiUsers className="text-amber-200 mt-1" size={16} />
              <p className="text-sm">Invita amigos para obtener bonificaciones grupales</p>
            </div>
          </div>
        </div>
      </div>

      <Navigation />
    </div>
  );
};

export default HowItWorks;
