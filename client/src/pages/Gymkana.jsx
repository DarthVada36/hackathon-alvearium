import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { 
  FiMapPin, 
  FiNavigation, 
  FiStar, 
  FiCheckCircle,
  FiClock,
  FiTarget,
  FiRefreshCw
} from 'react-icons/fi';

const Gymkana = () => {
  const { user, updateUserPoints } = useAuth();
  const [userLocation, setUserLocation] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);

  // Lugares oficiales de la ruta del Ratoncito Pérez con coordenadas reales
  const officialPlaces = [
    {
      id: 1,
      name: "Casa del Ratoncito Pérez",
      address: "Calle Arenal, 8",
      description: "El hogar oficial del Ratoncito Pérez en Madrid. Una pequeña tienda que recrea su casa.",
      points: 50,
      coordinates: { lat: 40.4165, lng: -3.7026 },
      visited: user?.visitedPlaces?.includes("Casa del Ratoncito Pérez") || false,
      difficulty: "Fácil",
      estimatedTime: "15 min",
      tips: "Busca la pequeña placa dorada en la fachada del edificio."
    },
    {
      id: 2,
      name: "Puerta del Sol",
      address: "Plaza de la Puerta del Sol",
      description: "El kilómetro 0 de España y corazón de Madrid. Aquí está el famoso oso y el madroño.",
      points: 25,
      coordinates: { lat: 40.4168, lng: -3.7038 },
      visited: user?.visitedPlaces?.includes("Puerta del Sol") || false,
      difficulty: "Fácil",
      estimatedTime: "20 min",
      tips: "Haz una foto con el oso y el madroño, símbolo de Madrid."
    },
    {
      id: 3,
      name: "Plaza Mayor",
      address: "Plaza Mayor",
      description: "Una de las plazas más hermosas de Europa, llena de historia y arquitectura impresionante.",
      points: 30,
      coordinates: { lat: 40.4155, lng: -3.7074 },
      visited: user?.visitedPlaces?.includes("Plaza Mayor") || false,
      difficulty: "Fácil",
      estimatedTime: "25 min",
      tips: "Observa los frescos de la Casa de la Panadería."
    },
    {
      id: 4,
      name: "Palacio Real",
      address: "Calle de Bailén",
      description: "El palacio real más grande de Europa Occidental con más de 3.000 habitaciones.",
      points: 40,
      coordinates: { lat: 40.4185, lng: -3.7138 },
      visited: user?.visitedPlaces?.includes("Palacio Real") || false,
      difficulty: "Medio",
      estimatedTime: "45 min",
      tips: "Los miércoles y sábados hay cambio de guardia a las 12:00."
    },
    {
      id: 5,
      name: "Teatro Real",
      address: "Plaza de Oriente",
      description: "El teatro de ópera más importante de España, frente al Palacio Real.",
      points: 35,
      coordinates: { lat: 40.4188, lng: -3.7119 },
      visited: user?.visitedPlaces?.includes("Teatro Real") || false,
      difficulty: "Medio",
      estimatedTime: "30 min",
      tips: "Construido sobre los cimientos del antiguo Teatro de los Caños del Peral."
    },
    {
      id: 6,
      name: "Plaza de Oriente",
      address: "Plaza de Oriente",
      description: "Hermosa plaza con jardines y estatuas de reyes españoles.",
      points: 20,
      coordinates: { lat: 40.4186, lng: -3.7134 },
      visited: user?.visitedPlaces?.includes("Plaza de Oriente") || false,
      difficulty: "Fácil",
      estimatedTime: "20 min",
      tips: "Cuenta las estatuas de los reyes godos y visigodos."
    }
  ];

  const getCurrentLocation = () => {
    setIsLoadingLocation(true);
    setLocationError(null);
    
    if (!navigator.geolocation) {
      setLocationError("Tu navegador no soporta geolocalización");
      setIsLoadingLocation(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
        setIsLoadingLocation(false);
      },
      (error) => {
        setLocationError("No se pudo obtener tu ubicación. Verifica los permisos.");
        setIsLoadingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  };

  const calculateDistance = (place) => {
    if (!userLocation) return null;
    
    const R = 6371; // Radio de la Tierra en km
    const dLat = (place.coordinates.lat - userLocation.lat) * Math.PI / 180;
    const dLng = (place.coordinates.lng - userLocation.lng) * Math.PI / 180;
    const a = 
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(userLocation.lat * Math.PI / 180) * Math.cos(place.coordinates.lat * Math.PI / 180) *
      Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    const distance = R * c * 1000; // Convertir a metros
    
    return Math.round(distance);
  };

  const isNearPlace = (place) => {
    const distance = calculateDistance(place);
    return distance && distance <= 100; // 100 metros de tolerancia
  };

  const visitPlace = (place) => {
    if (isNearPlace(place) && !place.visited) {
      updateUserPoints(place.points);
      // Aquí se actualizaría la lista de lugares visitados en el contexto
      alert(`¡Felicidades! Has visitado ${place.name} y ganado ${place.points} puntos.`);
    }
  };

  const openDirections = (place) => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${place.coordinates.lat},${place.coordinates.lng}`;
    window.open(url, '_blank');
  };

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const sortedPlaces = officialPlaces.sort((a, b) => {
    if (!userLocation) return 0;
    const distanceA = calculateDistance(a) || Infinity;
    const distanceB = calculateDistance(b) || Infinity;
    return distanceA - distanceB;
  });

  const completedPlaces = officialPlaces.filter(place => place.visited).length;
  const totalPoints = officialPlaces.reduce((sum, place) => place.visited ? sum + place.points : sum, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
      <Header title="Gymkana del Ratoncito" showBackButton />
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Progreso General */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-800">Tu Progreso</h2>
            <button 
              onClick={getCurrentLocation}
              disabled={isLoadingLocation}
              className="p-2 rounded-lg hover:bg-lime-200/50 transition-colors"
            >
              <FiRefreshCw className={`text-amber-600 ${isLoadingLocation ? 'animate-spin' : ''}`} />
            </button>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-600">{completedPlaces}</div>
              <div className="text-xs text-gray-600">Completados</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-600">{officialPlaces.length - completedPlaces}</div>
              <div className="text-xs text-gray-600">Restantes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-600">{totalPoints}</div>
              <div className="text-xs text-gray-600">Puntos</div>
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-amber-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${(completedPlaces / officialPlaces.length) * 100}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-2 text-center">
            {Math.round((completedPlaces / officialPlaces.length) * 100)}% completado
          </p>
        </div>

        {/* Estado de Ubicación */}
        {locationError && (
          <div className="card p-4 border-l-4 border-red-500">
            <p className="text-red-600 text-sm">{locationError}</p>
            <button 
              onClick={getCurrentLocation}
              className="btn-secondary text-sm mt-2"
            >
              Intentar de nuevo
            </button>
          </div>
        )}

        {userLocation && (
          <div className="card p-4 border-l-4 border-green-500">
            <p className="text-green-600 text-sm flex items-center">
              <FiTarget className="mr-2" />
              Ubicación detectada - Los lugares están ordenados por distancia
            </p>
          </div>
        )}

        {/* Lista de Lugares */}
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Lugares de la Ruta Oficial
          </h3>
          <div className="space-y-4">
            {sortedPlaces.map((place) => {
              const distance = calculateDistance(place);
              const isNear = isNearPlace(place);
              
              return (
                <div 
                  key={place.id} 
                  className={`card p-6 ${place.visited ? 'bg-green-50 border-green-200' : ''} ${isNear ? 'ring-2 ring-amber-600' : ''}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="font-semibold text-gray-800">{place.name}</h4>
                        {place.visited && <FiCheckCircle className="text-green-500" size={20} />}
                      </div>
                      <p className="text-sm text-gray-600 mb-1">{place.address}</p>
                      <p className="text-sm text-gray-700">{place.description}</p>
                    </div>
                    
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-amber-600">
                        <FiStar size={16} />
                        <span className="font-bold">{place.points}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <FiClock size={14} />
                        <span>{place.estimatedTime}</span>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${
                        place.difficulty === 'Fácil' ? 'bg-green-100 text-green-800' :
                        place.difficulty === 'Medio' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {place.difficulty}
                      </span>
                    </div>
                    
                    {distance && (
                      <div className="flex items-center space-x-1">
                        <FiMapPin size={14} />
                        <span>
                          {distance < 1000 ? `${distance}m` : `${(distance/1000).toFixed(1)}km`}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="bg-lime-200/20 p-3 rounded-lg mb-4">
                    <p className="text-sm text-gray-700">
                      <strong>Consejo:</strong> {place.tips}
                    </p>
                  </div>
                  
                  <div className="flex space-x-3">
                    <button
                      onClick={() => openDirections(place)}
                      className="btn-secondary text-sm flex items-center space-x-2 flex-1"
                    >
                      <FiNavigation size={16} />
                      <span>Cómo llegar</span>
                    </button>
                    
                    {isNear && !place.visited && (
                      <button
                        onClick={() => visitPlace(place)}
                        className="btn-primary text-sm flex items-center space-x-2 flex-1"
                      >
                        <FiCheckCircle size={16} />
                        <span>¡Marcar Visitado!</span>
                      </button>
                    )}
                    
                    {place.visited && (
                      <div className="flex-1 text-center py-2 text-green-600 font-medium text-sm">
                        ✓ Completado
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Información Adicional */}
        <div className="card p-6">
          <h3 className="font-semibold text-gray-800 mb-3">ℹ️ Información Importante</h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• Debes estar a menos de 100 metros del lugar para marcarlo como visitado</p>
            <p>• Solo los lugares oficiales de la ruta otorgan puntos</p>
            <p>• Puedes preguntar al Ratoncito sobre cualquier lugar de Madrid</p>
            <p>• La geolocalización debe estar activada para funcionar correctamente</p>
          </div>
        </div>
      </div>

      <Navigation />
    </div>
  );
};

export default Gymkana;
