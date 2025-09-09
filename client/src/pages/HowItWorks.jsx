import React from 'react';
import Header from '../components/Header';
import { FiMapPin, FiStar, FiTarget, FiSmartphone, FiAward, FiMessageCircle } from 'react-icons/fi';

const HowItWorks = () => {
  const steps = [
    {
      icon: <FiSmartphone size={40} />,
      title: "Descarga y Regístrate",
      description: "Crea tu cuenta en la app del Ratoncito Pérez y prepárate para explorar Madrid."
    },
    {
      icon: <FiMapPin size={40} />,
      title: "Activa la Geolocalización",
      description: "Permite que la app conozca tu ubicación para guiarte por los lugares más emblemáticos."
    },
    {
      icon: <FiTarget size={40} />,
      title: "Sigue al Ratoncito",
      description: "Nuestro guía virtual te llevará por la ruta oficial del Ratoncito Pérez en Madrid."
    },
    {
      icon: <FiStar size={40} />,
      title: "Gana Puntos",
      description: "Visita los lugares oficiales de la ruta y acumula puntos por cada sitio descubierto."
    },
    {
      icon: <FiMessageCircle size={40} />,
      title: "Conversa y Aprende",
      description: "Haz preguntas al Ratoncito sobre Madrid, su historia y cultura madrileña."
    },
    {
      icon: <FiAward size={40} />,
      title: "Desbloquea Logros",
      description: "Consigue insignias y sube de nivel mientras completas tu aventura por Madrid."
    }
  ];

  const officialPlaces = [
    "Casa del Ratoncito Pérez (Calle Arenal, 8)",
    "Puerta del Sol",
    "Plaza Mayor",
    "Palacio Real",
    "Teatro Real",
    "Mercado de San Miguel",
    "Plaza de Oriente",
    "Catedral de la Almudena",
    "Plaza de la Villa",
    "Casa de la Panadería"
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
      <Header title="¿Cómo Funciona?" showBackButton />
      
      <div className="container mx-auto px-4 py-6">
        {/* Introducción */}
        <div className="card p-6 mb-8">
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-amber-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🐭</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Descubre Madrid con el Ratoncito Pérez
            </h2>
            <p className="text-gray-600">
              Una experiencia única que combina historia, cultura y tecnología para explorar los rincones más emblemáticos de Madrid.
            </p>
          </div>
        </div>

        {/* Pasos */}
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-800 mb-6 text-center">
            Cómo Funciona la Aventura
          </h3>
          <div className="space-y-6">
            {steps.map((step, index) => (
              <div key={index} className="card p-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-amber-600 rounded-full flex items-center justify-center text-white font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="text-amber-600">
                        {step.icon}
                      </div>
                      <h4 className="text-lg font-semibold text-gray-800">
                        {step.title}
                      </h4>
                    </div>
                    <p className="text-gray-600">
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lugares Oficiales */}
        <div className="card p-6 mb-8">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FiMapPin className="text-amber-600 mr-2" />
            Lugares de la Ruta Oficial
          </h3>
          <p className="text-gray-600 mb-4">
            Estos son los sitios emblemáticos que forman parte de la ruta oficial del Ratoncito Pérez. 
            Solo visitando estos lugares ganarás puntos:
          </p>
          <div className="space-y-2">
            {officialPlaces.map((place, index) => (
              <div key={index} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-lime-200/20">
                <div className="w-6 h-6 bg-amber-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  {index + 1}
                </div>
                <span className="text-gray-700">{place}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Sistema de Puntos */}
        <div className="card p-6 mb-8">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <FiStar className="text-amber-600 mr-2" />
            Sistema de Puntos y Niveles
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-lime-200/20 rounded-lg">
              <span className="font-medium">Principiante</span>
              <span className="text-amber-600 font-bold">0 - 50 puntos</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-lime-200/20 rounded-lg">
              <span className="font-medium">Explorador</span>
              <span className="text-amber-600 font-bold">51 - 150 puntos</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-lime-200/20 rounded-lg">
              <span className="font-medium">Aventurero</span>
              <span className="text-amber-600 font-bold">151 - 300 puntos</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-lime-200/20 rounded-lg">
              <span className="font-medium">Maestro Explorador</span>
              <span className="text-amber-600 font-bold">300+ puntos</span>
            </div>
          </div>
          <p className="text-sm text-gray-600 mt-4">
            * Cada lugar oficial visitado otorga entre 10-30 puntos dependiendo de su importancia histórica.
          </p>
        </div>

        {/* Consejos */}
        <div className="card p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            Consejos para tu Aventura
          </h3>
          <div className="space-y-3 text-gray-600">
            <div className="flex items-start space-x-2">
              <span className="text-amber-600">•</span>
              <span>Lleva tu móvil con batería suficiente para toda la ruta</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-amber-600">•</span>
              <span>Usa calzado cómodo, caminarás bastante por el centro de Madrid</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-amber-600">•</span>
              <span>No olvides hacer preguntas al Ratoncito sobre lo que vas viendo</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-amber-600">•</span>
              <span>Puedes pausar la ruta en cualquier momento y continuarla después</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorks;
