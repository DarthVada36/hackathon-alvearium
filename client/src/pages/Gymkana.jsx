import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import SnapMapView from '../components/InteractiveMap';
import ApiService from '../services/ApiService';
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
  FiCheck,
  FiAlertCircle,
  FiUsers
} from 'react-icons/fi';

const Gymkana = () => {
  const { user } = useAuth();
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
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [mapViewMode, setMapViewMode] = useState('list'); // 'list' or 'map'

  // ============ ESTADO DINÁMICO DEL BACKEND ============
  const [families, setFamilies] = useState([]);
  const [selectedFamily, setSelectedFamily] = useState(null);
  const [officialPlaces, setOfficialPlaces] = useState([]);
  const [familyStatus, setFamilyStatus] = useState(null);
  const [isLoadingFamilies, setIsLoadingFamilies] = useState(true);
  const [isLoadingRoute, setIsLoadingRoute] = useState(true);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [error, setError] = useState('');

  // ============ POIs OFICIALES CON COORDENADAS EXACTAS ============
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
      index: 0
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
      index: 1
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
      index: 2
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
      index: 3
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
      index: 4
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
      index: 5
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
      index: 6
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
      index: 7
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
      index: 8
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
      index: 9
    }
  ];

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

  const loadRouteData = async () => {
    try {
      setIsLoadingRoute(true);
      // Cargar ruta oficial del backend
      const routeResponse = await ApiService.getRouteOverview();
      
      // Combinar datos del backend con coordenadas locales
      const backendRoute = routeResponse.route || [];
      const enrichedPlaces = OFFICIAL_POIS_WITH_COORDINATES.map(localPoi => {
        const backendPoi = backendRoute.find(bp => bp.id === localPoi.id);
        return {
          ...localPoi,
          // Mantener datos del backend si existen
          ...(backendPoi && {
            description: backendPoi.description || localPoi.description,
            visit_duration: backendPoi.visit_duration || localPoi.estimatedTime
          })
        };
      });
      
      setOfficialPlaces(enrichedPlaces);
    } catch (error) {
      console.error('Error loading route:', error);
      // Fallback: usar datos locales si falla el backend
      setOfficialPlaces(OFFICIAL_POIS_WITH_COORDINATES);
      setError('Usando datos offline de la ruta');
    } finally {
      setIsLoadingRoute(false);
    }
  };

  const loadFamilyStatus = async () => {
    if (!selectedFamily) return;
    
    try {
      setIsLoadingStatus(true);
      const status = await ApiService.getFamilyStatus(selectedFamily.id);
      setFamilyStatus(status);
      
      // Actualizar estado de POIs visitados
      updatePlacesWithStatus(status);
    } catch (error) {
      console.error('Error loading family status:', error);
      setError('Error cargando progreso de familia');
    } finally {
      setIsLoadingStatus(false);
    }
  };

  const updatePlacesWithStatus = (status) => {
    if (!status || !status.visited_pois) return;
    
    setOfficialPlaces(prevPlaces => 
      prevPlaces.map(place => ({
        ...place,
        visited: status.current_poi_index > place.index,
        isCurrent: status.current_poi_index === place.index
      }))
    );
  };

  // ============ EFFECTS ============
  
  useEffect(() => {
    loadUserFamilies();
    loadRouteData();
  }, []);

  useEffect(() => {
    if (selectedFamily) {
      loadFamilyStatus();
    }
  }, [selectedFamily]);

  useEffect(() => {
    const getUserLocation = () => {
      setIsLoadingLocation(true);
      
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setUserLocation({
              lat: position.coords.latitude,
              lng: position.coords.longitude
            });
            setIsLoadingLocation(false);
          },
          (error) => {
            console.log('Geolocation error:', error);
            // ✅ FALLBACK: Usar ubicación mock en Madrid
            setUserLocation({
              lat: 40.4168, // Puerta del Sol (centro de Madrid)
              lng: -3.7038
            });
            setLocationError('Usando ubicación de ejemplo en Madrid');
            setIsLoadingLocation(false);
          }
        );
      } else {
        // ✅ FALLBACK: Usar ubicación mock si no hay soporte
        setUserLocation({
          lat: 40.4168,
          lng: -3.7038
        });
        setLocationError('Geolocalización no disponible - usando ubicación de ejemplo');
        setIsLoadingLocation(false);
      }
    };

    getUserLocation();
  }, []);

  // ============ FUNCIONES DE INTERACCIÓN ============
  
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

  const refreshData = async () => {
    await Promise.all([
      loadUserFamilies(),
      loadRouteData(),
      selectedFamily ? loadFamilyStatus() : Promise.resolve()
    ]);
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

  const visitPlace = async (place) => {
    if (!selectedFamily) {
      setError('Selecciona una familia primero');
      return;
    }

    if (isNearPlace(place) && !place.visited) {
      try {
        // Enviar mensaje al chat para registrar la visita
        await ApiService.sendChatMessage(
          selectedFamily.id,
          `¡Hemos llegado a ${place.name}!`,
          userLocation,
          null
        );
        
        // Recargar estado de la familia
        await loadFamilyStatus();
        
        alert(`¡Felicidades! Has visitado ${place.name} y ganado ${place.points} puntos.`);
      } catch (error) {
        setError('Error registrando visita: ' + ApiService.formatError(error));
      }
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
      // Award points for photo (could integrate with backend)
      setActivePlace(null);
    }
  };

  const discardPhoto = () => {
    setCapturedPhoto(null);
    setShowPhotoModal(false);
    setActivePlace(null);
  };

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
  const totalPoints = familyStatus?.total_points || 0;

  // ============ LOADING STATES ============
  
  if (isLoadingFamilies || isLoadingRoute) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
        <Header title="Ruta del Ratoncito Pérez" showBackButton />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto mb-4"></div>
            <p className="text-amber-600 font-medium">Cargando datos de la ruta...</p>
          </div>
        </div>
        <Navigation />
      </div>
    );
  }

  // ============ NO FAMILIES STATE ============
  
  if (families.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
        <Header title="Ruta del Ratoncito Pérez" showBackButton />
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-amber-100">
            <div className="text-6xl mb-4">🐭</div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">No tienes familias creadas</h2>
            <p className="text-gray-600 mb-6">
              Para explorar la ruta, primero necesitas crear una familia desde tu perfil.
            </p>
            <button 
              onClick={() => window.history.back()}
              className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-6 py-3 rounded-xl font-medium hover:from-amber-600 hover:to-amber-700 transition-colors"
            >
              Volver al Dashboard
            </button>
          </div>
        </div>
        <Navigation />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-yellow-50 to-amber-50 pb-20">
      <Header title="Ruta del Ratoncito Pérez" showBackButton />
      
      <div className="container mx-auto px-4 py-6 space-y-6">
        {/* Selector de Familia */}
        {families.length > 1 && (
          <div className="bg-white rounded-2xl p-4 shadow-sm border border-amber-100">
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
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <FiAlertCircle className="mr-2" size={16} />
                <span className="text-sm">{error}</span>
              </div>
              <button
                onClick={() => setError('')}
                className="text-red-500 hover:text-red-700"
              >
                <FiX size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Progreso General */}
        {selectedFamily && (
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-amber-100">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-gray-800">Progreso de {selectedFamily.name}</h2>
                <p className="text-sm text-gray-600">Descubre los lugares mágicos de Madrid</p>
              </div>
              <div className="flex items-center space-x-3">
                <button 
                  onClick={getCurrentLocation}
                  disabled={isLoadingLocation}
                  className="p-3 rounded-full bg-amber-100 hover:bg-amber-200 transition-colors"
                >
                  <FiRefreshCw className={`text-amber-600 ${isLoadingLocation ? 'animate-spin' : ''}`} />
                </button>
                <button 
                  onClick={refreshData}
                  disabled={isLoadingStatus}
                  className="p-3 rounded-full bg-blue-100 hover:bg-blue-200 transition-colors"
                >
                  <FiTarget className={`text-blue-600 ${isLoadingStatus ? 'animate-spin' : ''}`} />
                </button>
              </div>
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

            {familyStatus && (
              <div className="text-sm text-gray-600">
                POI actual: {familyStatus.current_poi_index + 1}/{officialPlaces.length} | 
                Progreso: {familyStatus.progress_percentage}%
              </div>
            )}
          </div>
        )}

        {/* Map/List Toggle */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-amber-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">Explorar Madrid</h3>
            <div className="flex bg-gray-100 rounded-xl p-1">
              <button
                onClick={() => setMapViewMode('list')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  mapViewMode === 'list' 
                    ? 'bg-white text-amber-600 shadow-sm' 
                    : 'text-gray-600 hover:text-amber-600'
                }`}
              >
                Lista
              </button>
              <button
                onClick={() => setMapViewMode('map')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  mapViewMode === 'map' 
                    ? 'bg-white text-amber-600 shadow-sm' 
                    : 'text-gray-600 hover:text-amber-600'
                }`}
              >
                Mapa
              </button>
            </div>
          </div>

          {/* Interactive Map View */}
          {mapViewMode === 'map' && (
            <div className="h-[500px] rounded-2xl overflow-hidden border-2 border-amber-200">
              <SnapMapView
                places={displayedPlaces}
                userLocation={userLocation}
                selectedDestination={selectedDestination}
                onDestinationSelect={setSelectedDestination}
              />
            </div>
          )}

          {/* Route selector for list view */}
          {mapViewMode === 'list' && (
            <>
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
            </>
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
        {mapViewMode === 'list' && selectedFamily && (
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
                      place.isCurrent ? 'border-amber-400 bg-amber-50' :
                      isNear ? 'border-blue-400 bg-blue-50' : 
                      'border-gray-200 hover:border-amber-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-bold text-gray-800 text-lg">{place.name}</h4>
                          {place.visited && <FiCheckCircle className="text-green-500" size={20} />}
                          {place.isCurrent && (
                            <div className="bg-amber-100 px-2 py-1 rounded-full">
                              <span className="text-xs font-medium text-amber-700">Actual</span>
                            </div>
                          )}
                          {hasPhoto && (
                            <div className="bg-purple-100 p-1 rounded-full">
                              <FiImage className="text-purple-600" size={16} />
                            </div>
                          )}
                          {isNear && !place.visited && (
                            <div className="bg-blue-100 px-2 py-1 rounded-full">
                              <span className="text-xs font-medium text-blue-700">Cerca</span>
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
                          place.difficulty === 'Especial' ? 'bg-purple-100 text-purple-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {place.difficulty}
                        </span>
                        <span className="text-xs text-gray-500">#{place.index + 1}</span>
                      </div>
                    </div>
                    
                    {/* Recommendation */}
                    <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4">
                      <p className="text-sm text-gray-700">
                        <strong className="text-amber-700">Consejo:</strong> {place.tips}
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
                              <span>Registrar Visita</span>
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
        )}

        {/* No Family Selected for List View */}
        {mapViewMode === 'list' && !selectedFamily && (
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-amber-100">
            <div className="text-4xl mb-4">🐭</div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">Selecciona una familia</h3>
            <p className="text-gray-600">Elige una familia para ver tu progreso en la ruta</p>
          </div>
        )}

        {/* Información Adicional */}
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 rounded-2xl p-5 text-white shadow-lg">
          <h3 className="font-bold text-lg mb-3 flex items-center">
            <FiInfo className="mr-2" />
            Información de la Ruta Real
          </h3>
          <div className="space-y-2 text-sm text-amber-100">
            <p>• <strong>10 puntos oficiales</strong> del Ratoncito Pérez en Madrid</p>
            <p>• Debes estar a menos de 100 metros para registrar visitas</p>
            <p>• El progreso se sincroniza con el chat y dashboard</p>
            <p>• Usa el botón "Siguiente POI" en el chat para avanzar</p>
            {familyStatus && (
              <p>• <strong>Progreso actual:</strong> {familyStatus.progress_percentage}% completado</p>
            )}
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
                  <span>Guardar</span>
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