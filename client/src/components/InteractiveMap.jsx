import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';
import 'leaflet-routing-machine';
import { 
  FiPlay, 
  FiPause, 
  FiSquare, 
  FiNavigation, 
  FiMapPin,
  FiTarget,
  FiNavigation2  // Cambio FiRoute por FiNavigation2 que sí existe
} from 'react-icons/fi';

// Fix for default markers in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons using HTML divs
const createCustomIcon = (color, emoji, isUser = false) => {
  const size = isUser ? 45 : 35;
  return L.divIcon({
    html: `
      <div style="
        background: ${color};
        border: 3px solid white;
        border-radius: 50%;
        width: ${size}px;
        height: ${size}px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${isUser ? '20px' : '16px'};
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        ${isUser ? 'animation: pulse 2s infinite;' : ''}
      ">
        ${emoji}
      </div>
      ${isUser ? `
        <style>
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
          }
        </style>
      ` : ''}
    `,
    className: 'custom-marker',
    iconSize: [size, size],
    iconAnchor: [size/2, size/2]
  });
};

// Icons for different states
const userIcon = createCustomIcon('#f59e0b', '🐭', true);
const placeIcon = createCustomIcon('#3b82f6', '📍');
const visitedIcon = createCustomIcon('#10b981', '✅');
const selectedIcon = createCustomIcon('#f59e0b', '🎯');

// Routing component
const RoutingControl = ({ start, end, onRouteFound, isActive }) => {
  const map = useMap();
  const routingControlRef = useRef(null);

  useEffect(() => {
    if (!start || !end || !isActive) {
      // Remove existing route if not active
      if (routingControlRef.current) {
        map.removeControl(routingControlRef.current);
        routingControlRef.current = null;
      }
      return;
    }

    // Remove existing route before creating new one
    if (routingControlRef.current) {
      map.removeControl(routingControlRef.current);
    }

    routingControlRef.current = L.Routing.control({
      waypoints: [
        L.latLng(start.lat, start.lng),
        L.latLng(end.lat, end.lng)
      ],
      routeWhileDragging: false,
      addWaypoints: false,
      createMarker: () => null, // Don't create default markers
      lineOptions: {
        styles: [{ 
          color: '#f59e0b', 
          weight: 5, 
          opacity: 0.8,
          className: 'route-active'
        }]
      },
      show: false, // Hide the instructions panel
      collapsible: false,
      draggableWaypoints: false,
      fitSelectedRoutes: true
    }).addTo(map);

    routingControlRef.current.on('routesfound', (e) => {
      const routes = e.routes;
      const summary = routes[0].summary;
      onRouteFound({
        distance: (summary.totalDistance / 1000).toFixed(1), // km
        time: Math.round(summary.totalTime / 60) // minutes
      });
    });

    return () => {
      if (routingControlRef.current) {
        map.removeControl(routingControlRef.current);
      }
    };
  }, [start, end, map, onRouteFound, isActive]);

  return null;
};

// Center map on user location
const CenterMapOnUser = ({ userLocation, shouldCenter }) => {
  const map = useMap();
  
  useEffect(() => {
    if (userLocation && shouldCenter) {
      map.setView([userLocation.lat, userLocation.lng], 16, {
        animate: true,
        duration: 1
      });
    }
  }, [map, userLocation, shouldCenter]);

  return null;
};

const InteractiveMap = ({ places, userLocation, selectedDestination, onDestinationSelect }) => {
  const [routeInfo, setRouteInfo] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  const [routeStarted, setRouteStarted] = useState(false);
  const [shouldCenterOnUser, setShouldCenterOnUser] = useState(false);

  // ✅ Siempre usar una ubicación por defecto si no hay userLocation
  const effectiveUserLocation = userLocation || {
    lat: 40.4168, // Puerta del Sol
    lng: -3.7038
  };

  const startRoute = () => {
    if (selectedDestination) { // ✅ Solo requerir destino, no userLocation
      setRouteStarted(true);
      setIsTracking(true);
    }
  };

  const pauseRoute = () => {
    setIsTracking(false);
  };

  const resumeRoute = () => {
    setIsTracking(true);
  };

  const stopRoute = () => {
    setRouteStarted(false);
    setIsTracking(false);
    setRouteInfo(null);
    onDestinationSelect(null);
  };

  const centerOnUser = () => {
    setShouldCenterOnUser(true);
    setTimeout(() => setShouldCenterOnUser(false), 100);
  };

  // Default center (Madrid center)
  const defaultCenter = [40.4165, -3.7026];
  const mapCenter = userLocation ? [userLocation.lat, userLocation.lng] : defaultCenter;

  return (
    <div className="relative w-full h-full">
      {/* Map Container */}
      <MapContainer
        center={[effectiveUserLocation.lat, effectiveUserLocation.lng]} // ✅ Usar ubicación efectiva
        zoom={15}
        className="w-full h-full rounded-2xl"
        style={{ minHeight: '400px' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {/* Center map component */}
        <CenterMapOnUser 
          userLocation={userLocation} 
          shouldCenter={shouldCenterOnUser}
        />
        
        {/* User Location - siempre mostrar */}
        <Marker 
          position={[effectiveUserLocation.lat, effectiveUserLocation.lng]} 
          icon={userIcon}
        >
          <Popup>
            <div className="text-center">
              <div className="font-bold text-amber-600">
                {userLocation ? 'Tu ubicación' : 'Ubicación de ejemplo'}
              </div>
              <div className="text-sm text-gray-600">Ratoncito Pérez</div>
              {!userLocation && (
                <div className="text-xs text-orange-500 mt-1">
                  (Ubicación simulada en Madrid)
                </div>
              )}
            </div>
          </Popup>
        </Marker>

        {/* Places */}
        {places.map((place) => (
          <Marker
            key={place.id}
            position={[place.coordinates.lat, place.coordinates.lng]}
            icon={place.visited ? visitedIcon : placeIcon}
            eventHandlers={{
              click: () => onDestinationSelect(place)
            }}
          >
            <Popup>
              <div className="text-center min-w-[200px]">
                <div className="font-bold text-gray-800">{place.name}</div>
                <div className="text-sm text-gray-600 mb-2">{place.address}</div>
                <div className="text-xs text-amber-600 font-medium">
                  {place.points} puntos
                </div>
                {place.visited && (
                  <div className="text-xs text-green-600 mt-1">✅ Visitado</div>
                )}
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Routing - usar ubicación efectiva */}
        {selectedDestination && (
          <RoutingControl
            start={effectiveUserLocation} // ✅ Usar ubicación efectiva
            end={selectedDestination.coordinates}
            onRouteFound={setRouteInfo}
            isActive={routeStarted}
          />
        )}
      </MapContainer>

      {/* Control Panel - SIEMPRE VISIBLE cuando hay destino */}
      {selectedDestination && (
        <div className="absolute top-4 left-4 right-4 z-[1000]">
          <div className="bg-white rounded-2xl p-4 shadow-xl border-2 border-amber-300">
            {/* Route Info */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold text-gray-900 text-base">{selectedDestination.name}</h3>
                <span className="text-sm text-amber-600 font-bold bg-amber-100 px-2 py-1 rounded-lg">
                  {selectedDestination.points} pts
                </span>
              </div>
              {routeInfo && (
                <div className="flex items-center space-x-4 text-sm text-gray-700 bg-gray-50 p-2 rounded-lg">
                  <span className="flex items-center font-medium">
                    <FiMapPin size={14} className="mr-1 text-blue-500" /> 
                    {routeInfo.distance} km
                  </span>
                  <span className="flex items-center font-medium">
                    <FiNavigation2 size={14} className="mr-1 text-green-500" /> 
                    {routeInfo.time} min
                  </span>
                </div>
              )}
              {!userLocation && (
                <div className="text-sm text-orange-600 mt-2 bg-orange-50 p-2 rounded-lg border border-orange-200">
                  ⚠️ Usando ubicación simulada - Activa GPS para precisión real
                </div>
              )}
            </div>

            {/* Control Buttons - MAS GRANDES Y VISIBLES */}
            <div className="flex items-center space-x-3">
              {!routeStarted ? (
                <>
                  <button
                    onClick={startRoute}
                    className="flex-1 py-3 px-4 rounded-xl font-bold text-base transition-all duration-200 flex items-center justify-center space-x-2 bg-gradient-to-r from-amber-500 to-amber-600 text-white hover:from-amber-600 hover:to-amber-700 shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    <FiPlay size={18} />
                    <span>INICIAR RUTA</span>
                  </button>
                  <button
                    onClick={centerOnUser}
                    className="p-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                    title="Centrar en mi ubicación"
                  >
                    <FiTarget size={18} />
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={isTracking ? pauseRoute : resumeRoute}
                    className="flex-1 py-3 px-4 rounded-xl font-bold text-base transition-all duration-200 flex items-center justify-center space-x-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    {isTracking ? <FiPause size={18} /> : <FiPlay size={18} />}
                    <span>{isTracking ? 'PAUSAR' : 'CONTINUAR'}</span>
                  </button>
                  <button
                    onClick={stopRoute}
                    className="p-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                    title="Parar ruta"
                  >
                    <FiSquare size={18} />
                  </button>
                  <button
                    onClick={centerOnUser}
                    className="p-3 bg-gray-500 text-white rounded-xl hover:bg-gray-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                    title="Centrar en mi ubicación"
                  >
                    <FiNavigation size={18} />
                  </button>
                </>
              )}
            </div>

            {/* Status - MAS VISIBLE */}
            {routeStarted && (
              <div className="mt-3 text-center">
                <div className={`text-sm font-bold py-2 px-4 rounded-lg ${
                  isTracking 
                    ? 'text-green-700 bg-green-100 border border-green-300' 
                    : 'text-orange-700 bg-orange-100 border border-orange-300'
                }`}>
                  {isTracking ? '🟢 NAVEGANDO ACTIVAMENTE...' : '⏸️ RUTA PAUSADA'}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* DEBUG: Botón para probar controles - TEMPORAL */}
      {!selectedDestination && (
        <div className="absolute top-4 right-4 z-[1000]">
          <button
            onClick={() => {
              // Seleccionar el primer lugar para prueba
              const firstPlace = places[0];
              if (firstPlace) {
                onDestinationSelect(firstPlace);
              }
            }}
            className="bg-green-500 text-white px-4 py-2 rounded-lg font-bold shadow-lg hover:bg-green-600 transition-all duration-200"
          >
            🧪 PROBAR CONTROLES
          </button>
        </div>
      )}

      {/* Destination Selection Hint - MAS VISIBLE */}
      {!selectedDestination && (
        <div className="absolute bottom-6 left-4 right-4 z-[1000]">
          <div className="bg-gradient-to-r from-amber-500 to-amber-600 text-white p-4 rounded-xl text-center shadow-xl border-2 border-amber-300">
            <div className="flex items-center justify-center space-x-2 text-base font-bold">
              <FiMapPin size={20} />
              <span>¡Toca un marcador para empezar tu aventura!</span>
            </div>
            <div className="text-sm mt-1 opacity-90">
              Selecciona un destino en el mapa para ver los controles de navegación
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveMap;