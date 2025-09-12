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
  FiSun,
  FiArrowRight,
  FiCheckCircle
} from 'react-icons/fi';

// Importar imagen del ratón
import ratonSaco from '../assets/img/raton-saco.png';

const HowItWorks = () => {
  const guideSteps = [
    {
      icon: <FiMapPin className="text-white" size={24} />,
      title: "Explora la Ruta Oficial",
      description: "Visita los 6 lugares oficiales del Ratoncito Pérez en Madrid y gana entre 10-50 puntos por ubicación.",
      points: "10-50 puntos",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: <FiNavigation className="text-white" size={24} />,
      title: "Encuentra Lugares Cercanos",
      description: "Usa la geolocalización para descubrir sitios históricos cerca de ti con recompensas especiales.",
      points: "5-25 puntos",
      gradient: "from-emerald-500 to-teal-500"
    },
    {
      icon: <FiMessageCircle className="text-white" size={24} />,
      title: "Usa el Chat Guía",
      description: "Pregunta al Ratoncito sobre historia, direcciones y curiosidades de Madrid.",
      points: "Gratis",
      gradient: "from-violet-500 to-purple-500"
    },
    {
      icon: <FiCamera className="text-white" size={24} />,
      title: "Toma Fotos en Ubicaciones",
      description: "Captura momentos especiales en cada lugar de la ruta y guárdalos en tu perfil.",
      points: "2-5 puntos extra",
      gradient: "from-rose-500 to-pink-500"
    }
  ];

  const bonusActivities = [
    {
      icon: <FiShare size={20} />,
      title: "Comparte en Instagram",
      description: "Sube una foto taggeando @ratonperez_madrid",
      reward: "+15 puntos",
      metric: "15%"
    },
    {
      icon: <FiPlay size={20} />,
      title: "Minijuegos en Ubicaciones", 
      description: "Encuentra códigos QR ocultos para juegos especiales",
      reward: "+20 puntos",
      metric: "25%"
    },
    {
      icon: <FiGift size={20} />,
      title: "Visitas en Grupo",
      description: "Trae a 3+ amigos y obtén bonificación grupal",
      reward: "+30 puntos",
      metric: "40%"
    },
    {
      icon: <FiStar size={20} />,
      title: "Completa Desafíos Diarios",
      description: "Pequeñas misiones que cambian cada día",
      reward: "+10 puntos",
      metric: "Daily"
    }
  ];

  const chatFeatures = [
    "Direcciones precisas a cualquier lugar de la ruta",
    "Historia y curiosidades de cada ubicación", 
    "Horarios de apertura y mejor momento para visitar",
    "Recomendaciones de restaurantes cercanos",
    "Información del transporte público",
    "Consejos para maximizar tus puntos"
  ];

  const levelSystem = [
    { 
      level: "Ratoncito Novato", 
      points: "0-29 puntos", 
      perks: "Acceso básico a la ruta",
      users: "2.5k+",
      color: "text-slate-600"
    },
    { 
      level: "Ayudante del Ratón", 
      points: "30-59 puntos", 
      perks: "Descuentos en tiendas oficiales",
      users: "1.8k+",
      color: "text-blue-600"
    },
    { 
      level: "Guardián de Dientes", 
      points: "60-99 puntos", 
      perks: "Acceso a eventos especiales",
      users: "920+",
      color: "text-violet-600"
    },
    { 
      level: "Amigo de Ratoncito", 
      points: "100-149 puntos", 
      perks: "Tours privados gratuitos",
      users: "450+",
      color: "text-emerald-600"
    },
    { 
      level: "Embajador Real", 
      points: "150+ puntos", 
      perks: "Acceso VIP y merchandise exclusivo",
      users: "120+",
      color: "text-[#f8c73c]"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      <Header title="Guía de la App" showBackButton />
      
      <div className="max-w-7xl mx-auto px-4 py-12 space-y-16 pb-24">
        {/* Hero Section estilo Apollo */}
        <section className="text-center py-16">
          <div className="relative inline-block mb-8">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#f8c73c] to-amber-400 p-1 shadow-2xl">
              <div className="w-full h-full bg-white rounded-2xl p-2">
                <img 
                  src={ratonSaco} 
                  alt="Ratoncito Pérez" 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-emerald-500 rounded-full border-2 border-white"></div>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
            Tu guía completa para la
            <span className="block text-[#f8c73c]">Aventura del Ratoncito Pérez</span>
          </h1>
          
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
            Descubre Madrid de una forma única, gana puntos, desbloquea recompensas 
            y vive una experiencia inolvidable siguiendo los pasos del famoso Ratoncito Pérez.
          </p>
          
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <span>+5.8k exploradores activos</span>
            </div>
            <div className="flex items-center space-x-2">
              <FiStar className="text-[#f8c73c]" size={16} />
              <span>4.9/5 valoración</span>
            </div>
          </div>
        </section>

        {/* Cómo Ganar Puntos */}
        <section>
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Cómo ganar puntos</h2>
            <p className="text-xl text-gray-600">Múltiples formas de acumular puntos en tu aventura</p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {guideSteps.map((step, index) => (
              <div key={index} className="group relative bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-xl transition-all duration-300">
                <div className="flex items-start space-x-6">
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-r ${step.gradient} shadow-lg flex items-center justify-center flex-shrink-0`}>
                    {step.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">{step.title}</h3>
                    <p className="text-gray-600 mb-4 leading-relaxed">{step.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center px-4 py-2 bg-[#f8c73c] bg-opacity-10 text-[#f8c73c] rounded-lg font-semibold">
                        {step.points}
                      </span>
                      <FiArrowRight className="text-gray-400 group-hover:text-[#f8c73c] group-hover:translate-x-1 transition-all" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Actividades Bonus */}
        <section className="bg-gray-50 rounded-3xl p-12">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Actividades especiales</h2>
            <p className="text-xl text-gray-600">Maximiza tu experiencia con estas actividades extra</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {bonusActivities.map((activity, index) => (
              <div key={index} className="bg-white rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-all duration-300">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-gray-50 rounded-xl flex items-center justify-center text-gray-600">
                    {activity.icon}
                  </div>
                  <span className="text-2xl font-bold text-[#f8c73c]">{activity.metric}</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">{activity.title}</h4>
                <p className="text-gray-600 text-sm mb-4">{activity.description}</p>
                <span className="inline-flex items-center px-3 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium">
                  {activity.reward}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Chat Bot */}
        <section>
          <div className="bg-gray-900 rounded-3xl p-12 text-white">
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <div className="w-16 h-16 bg-[#f8c73c] rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <FiMessageCircle className="text-gray-900" size={24} />
                </div>
                <h2 className="text-3xl font-bold mb-4">Tu guía turístico virtual</h2>
                <p className="text-xl text-gray-300">El Ratoncito Pérez está aquí para ayudarte en cada paso de tu aventura</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {chatFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-4 p-4 bg-gray-800 rounded-xl">
                    <FiCheckCircle className="text-[#f8c73c] flex-shrink-0" size={20} />
                    <span className="text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
              
              <div className="mt-8 p-6 bg-gray-800 rounded-2xl border border-gray-700">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-[#f8c73c] bg-opacity-20 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FiHelpCircle className="text-[#f8c73c]" size={20} />
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">Consejo profesional</h4>
                    <p className="text-gray-300">Pregunta "¿Dónde estoy?" para obtener información específica de tu ubicación actual y recomendaciones personalizadas.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Sistema de Niveles */}
        <section>
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Sistema de progreso</h2>
            <p className="text-xl text-gray-600">Avanza por diferentes niveles y desbloquea recompensas exclusivas</p>
          </div>
          
          <div className="space-y-4">
            {levelSystem.map((level, index) => (
              <div key={index} className="flex items-center justify-between p-6 bg-white border border-gray-200 rounded-2xl hover:shadow-lg transition-all duration-300">
                <div className="flex items-center space-x-6">
                  <div className="text-4xl font-bold text-gray-200">{String(index + 1).padStart(2, '0')}</div>
                  <div>
                    <h4 className="text-xl font-semibold text-gray-900 mb-1">{level.level}</h4>
                    <p className={`font-medium ${level.color} mb-1`}>{level.points}</p>
                    <p className="text-gray-600">{level.perks}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500 mb-1">{level.users} usuarios</div>
                  <FiUsers className="text-gray-400" size={20} />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Consejos Finales */}
        <section className="bg-gradient-to-r from-[#f8c73c] to-amber-400 rounded-3xl p-12 text-gray-900">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-6">¿Listo para comenzar tu aventura?</h2>
            <p className="text-xl mb-8 opacity-80">Sigue estos consejos para maximizar tu experiencia</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl p-6 text-left">
                <FiBattery className="text-2xl mb-4" />
                <h4 className="font-semibold mb-2">Mantén la batería cargada</h4>
                <p className="opacity-80">Para no perderte ninguna ubicación ni oportunidad de ganar puntos.</p>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl p-6 text-left">
                <FiSun className="text-2xl mb-4" />
                <h4 className="font-semibold mb-2">Visita por las mañanas</h4>
                <p className="opacity-80">Menos multitudes y mejor luz para tus fotografías.</p>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl p-6 text-left">
                <FiCamera className="text-2xl mb-4" />
                <h4 className="font-semibold mb-2">Captura cada momento</h4>
                <p className="opacity-80">Las fotos no solo te dan puntos extra, sino recuerdos únicos.</p>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-2xl p-6 text-left">
                <FiUsers className="text-2xl mb-4" />
                <h4 className="font-semibold mb-2">Invita a tus amigos</h4>
                <p className="opacity-80">Multiplica la diversión y obtén bonificaciones grupales.</p>
              </div>
            </div>
          </div>
        </section>
      </div>

      <Navigation />
    </div>
  );
};

export default HowItWorks;