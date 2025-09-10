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
  FiRefreshCw,
  FiCamera,
  FiImage,
  FiEye,
  FiX,
  FiHeart,
  FiShare,
  FiMap,
  FiInfo,
  FiCheck
} from 'react-icons/fi';

const Gymkana = () => {
  const { user, updateUserPoints } = useAuth();
  const [userLocation, setUserLocation] = useState(null);
  const [selectedPlace, setSelectedPlace] = useState(null);
  const [locationError, setLocationError] = useState(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [viewMode, setViewMode] = useState('map'); // 'map' or 'list'
  const [showCamera, setShowCamera] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [savedPhotos, setSavedPhotos] = useState({});
  const [activePlace, setActivePlace] = useState(null);
  const [routeMode, setRouteMode] = useState('official'); // 'official' or 'nearest'
  const [showMapEmbed, setShowMapEmbed] = useState(false);

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

  // Simulate camera functionality
  const takePhoto = (place) => {
    setActivePlace(place);
    setShowCamera(true);
    // Simulate photo capture after a delay
    setTimeout(() => {
      const photoData = `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==`;
      setCapturedPhoto(photoData);
      setShowCamera(false);
      setShowPhotoModal(true);
    }, 2000);
  };

  const savePhoto = () => {
    if (capturedPhoto && activePlace) {
      setSavedPhotos(prev => ({
        ...prev,
        [activePlace.id]: capturedPhoto
      }));
      setShowPhotoModal(false);
      setCapturedPhoto(null);
      updateUserPoints(20); // Award points for photo
      setActivePlace(null);
    }
  };

  const discardPhoto = () => {
    setCapturedPhoto(null);
    setShowPhotoModal(false);
    setActivePlace(null);
  };

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getDisplayedPlaces = () => {
    if (routeMode === 'nearest') {
      return officialPlaces.sort((a, b) => {
        if (!userLocation) return 0;
        const distanceA = calculateDistance(a) || Infinity;
        const distanceB = calculateDistance(b) || Infinity;
        return distanceA - distanceB;
      });
    }
    return officialPlaces; // Orden oficial de la ruta
  };

  const displayedPlaces = getDisplayedPlaces();
  const completedPlaces = officialPlaces.filter(place => place.visited).length;
  const totalPoints = officialPlaces.reduce((sum, place) => place.visited ? sum + place.points : sum, 0);

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
      <Header title="Ruta del Ratoncito Pérez" showBackButton />
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Progreso General */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-gray-800">Tu Progreso</h2>
              <p className="text-sm text-gray-600">Descubre los lugares mágicos de Madrid</p>
            </div>
            <button 
              onClick={getCurrentLocation}
              disabled={isLoadingLocation}
              className="p-3 rounded-full bg-amber-100 hover:bg-amber-200 transition-colors"
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
          
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div 
              className="bg-gradient-to-r from-amber-400 to-amber-500 h-3 rounded-full transition-all duration-300"
              style={{ width: `${(completedPlaces / officialPlaces.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Selector de Ruta y Mapa */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-amber-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">Explorar Madrid</h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowMapEmbed(!showMapEmbed)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  showMapEmbed 
                    ? 'bg-amber-500 text-white' 
                    : 'bg-amber-100 text-amber-600 hover:bg-amber-200'
                }`}
              >
                <FiMap className="inline mr-1" size={14} />
                Mapa
              </button>
            </div>
          </div>

          {/* Selector de Tipo de Ruta */}
          <div className="flex bg-gray-100 rounded-xl p-1 mb-4">
            <button
              onClick={() => setRouteMode('official')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-all ${
                routeMode === 'official'
                  ? 'bg-white text-amber-600 shadow-sm'
                  : 'text-gray-600 hover:text-amber-600'
              }`}
            >
              Ruta Oficial
            </button>
            <button
              onClick={() => setRouteMode('nearest')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium text-sm transition-all ${
                routeMode === 'nearest'
                  ? 'bg-white text-amber-600 shadow-sm'
                  : 'text-gray-600 hover:text-amber-600'
              }`}
            >
              Más Cercanos
            </button>
          </div>

          {/* Embed de Google Maps */}
          {showMapEmbed && (
            <div className="mb-4 rounded-xl overflow-hidden border-2 border-amber-200">
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3037.6104486936345!2d-3.7067149247649657!3d40.41654497144158!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xd42289637e3e23f%3A0x81bb596d04aab02a!2sCalle+del+Arenal%2C+8%2C+28013+Madrid!5e0!3m2!1sen!2ses!4v1234567890123"
                width="100%"
                height="300"
                style={{ border: 0 }}
                allowFullScreen=""
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Mapa de Madrid - Ruta del Ratoncito Pérez"
              />
              <div className="bg-amber-50 p-3 text-center">
                <p className="text-sm text-amber-700">
                  <FiMapPin className="inline mr-1" size={14} />
                  Toca en cualquier ubicación para obtener direcciones
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Estado de Ubicación */}
        {locationError && (
          <div className="bg-white rounded-2xl p-4 border-l-4 border-red-500 shadow-sm">
            <p className="text-red-600 text-sm flex items-center">
              <FiX className="mr-2" />
              {locationError}
            </p>
            <button 
              onClick={getCurrentLocation}
              className="mt-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
            >
              Intentar de nuevo
            </button>
          </div>
        )}

        {userLocation && (
          <div className="bg-white rounded-2xl p-4 border-l-4 border-green-500 shadow-sm">
            <p className="text-green-600 text-sm flex items-center">
              <FiTarget className="mr-2" />
              Ubicación detectada - {routeMode === 'nearest' ? 'Ordenados por distancia' : 'Ruta oficial del Ratoncito'}
            </p>
          </div>
        )}

        {/* Lista de Lugares */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">
              {routeMode === 'official' ? 'Ruta Oficial del Ratoncito' : 'Lugares más Cercanos'}
            </h3>
            <span className="text-sm text-gray-500">
              {displayedPlaces.length} lugares
            </span>
          </div>
          
          <div className="space-y-4">
            {displayedPlaces.map((place) => {
              const distance = calculateDistance(place);
              const isNear = isNearPlace(place);
              const hasPhoto = savedPhotos[place.id];
              
              return (
                <div 
                  key={place.id} 
                  className={`bg-white rounded-2xl p-6 shadow-sm border-2 transition-all ${
                    place.visited ? 'border-green-200 bg-green-50' : 
                    isNear ? 'border-amber-400 bg-amber-50' : 
                    'border-gray-200 hover:border-amber-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-bold text-gray-800 text-lg">{place.name}</h4>
                        {place.visited && <FiCheckCircle className="text-green-500" size={20} />}
                        {hasPhoto && (
                          <div className="bg-purple-100 p-1 rounded-full">
                            <FiImage className="text-purple-600" size={16} />
                          </div>
                        )}
                        {isNear && (
                          <div className="bg-amber-100 px-2 py-1 rounded-full">
                            <span className="text-xs font-medium text-amber-700">Cerca</span>
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{place.address}</p>
                      <p className="text-sm text-gray-700 mb-3">{place.description}</p>
                    </div>
                    
                    {/* Distance and Points */}
                    <div className="text-right ml-4">
                      {distance !== null && (
                        <div className="bg-gray-100 px-3 py-1 rounded-full mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            {distance < 1000 ? `${distance}m` : `${(distance/1000).toFixed(1)}km`}
                          </span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1 text-amber-600">
                        <FiStar size={16} />
                        <span className="font-bold">{place.points}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Details */}
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <FiClock size={14} />
                        <span>{place.estimatedTime}</span>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        place.difficulty === 'Fácil' ? 'bg-green-100 text-green-700' :
                        place.difficulty === 'Medio' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {place.difficulty}
                      </span>
                    </div>
                  </div>
                  
                  {/* Recommendation */}
                  <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4">
                    <p className="text-sm text-gray-700">
                      <strong className="text-amber-700">Recomendación:</strong> {place.tips}
                    </p>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex space-x-3">
                    <button
                      onClick={() => openDirections(place)}
                      className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-3 px-4 rounded-xl font-medium text-sm transition-colors flex items-center justify-center space-x-2"
                    >
                      <FiNavigation size={16} />
                      <span>Cómo llegar</span>
                    </button>
                    
                    {isNear && (
                      <>
                        <button
                          onClick={() => takePhoto(place)}
                          className="bg-purple-100 hover:bg-purple-200 text-purple-700 py-3 px-4 rounded-xl font-medium text-sm transition-colors flex items-center space-x-2"
                        >
                          <FiCamera size={16} />
                          <span>Foto</span>
                        </button>
                        
                        {!place.visited && (
                          <button
                            onClick={() => visitPlace(place)}
                            className="bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-white py-3 px-4 rounded-xl font-medium text-sm transition-colors flex items-center space-x-2"
                          >
                            <FiCheckCircle size={16} />
                            <span>Marcar Visitado</span>
                          </button>
                        )}
                      </>
                    )}
                    
                    {place.visited && (
                      <div className="bg-green-100 text-green-700 py-3 px-4 rounded-xl font-medium text-sm flex items-center space-x-2">
                        <FiCheck size={16} />
                        <span>Completado</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Información Adicional */}
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-2xl p-5 text-white shadow-lg">
          <h3 className="font-bold text-lg mb-3 flex items-center">
            <FiInfo className="mr-2" />
            Información Importante
          </h3>
          <div className="space-y-2 text-sm text-amber-100">
            <p>• Debes estar a menos de 100 metros del lugar para marcarlo como visitado</p>
            <p>• Solo los lugares oficiales de la ruta otorgan puntos</p>
            <p>• Puedes preguntar al Ratoncito sobre cualquier lugar de Madrid</p>
            <p>• La geolocalización debe estar activada para funcionar correctamente</p>
          </div>
        </div>
      </div>

      {/* Camera Modal */}
      {showCamera && (
        <div className="fixed inset-0 z-50 bg-black flex items-center justify-center">
          <div className="text-center text-white">
            <div className="w-32 h-32 border-4 border-white rounded-full animate-pulse mb-4 mx-auto flex items-center justify-center">
              <FiCamera size={48} />
            </div>
            <p className="text-lg font-medium">Tomando foto...</p>
            <p className="text-sm opacity-75 mt-2">Capturando {activePlace?.name}</p>
          </div>
        </div>
      )}

      {/* Photo Preview Modal */}
      {showPhotoModal && capturedPhoto && (
        <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl overflow-hidden max-w-sm w-full">
            <div className="bg-gradient-to-r from-amber-500 to-amber-600 p-4 text-white">
              <h3 className="font-bold text-lg">{activePlace?.name}</h3>
              <p className="text-sm opacity-90">¡Excelente foto! ¿Guardarla en tu colección?</p>
            </div>
            
            <div className="p-4">
              <div className="bg-gray-100 rounded-xl h-48 mb-4 flex items-center justify-center">
                <FiImage size={48} className="text-gray-400" />
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={discardPhoto}
                  className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors"
                >
                  Descartar
                </button>
                <button
                  onClick={savePhoto}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-xl font-medium hover:from-amber-600 hover:to-amber-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <FiHeart size={16} />
                  <span>Guardar (+20pts)</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <Navigation />
    </div>
  );
};

export default Gymkana;
