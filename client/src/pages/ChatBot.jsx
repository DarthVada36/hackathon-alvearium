import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import ApiService from '../services/ApiService';
import { 
  FiSend, 
  FiTarget, 
  FiMapPin, 
  FiClock, 
  FiRefreshCw,
  FiStar,
  FiUsers,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';
import bg from '../assets/img/bg.png';

const ChatBot = () => {
  const { user } = useAuth();
  const [selectedFamily, setSelectedFamily] = useState(null);
  const [families, setFamilies] = useState([]);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [familyStatus, setFamilyStatus] = useState(null);
  const [isLoadingFamilies, setIsLoadingFamilies] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState('');
  const [isAdvancing, setIsAdvancing] = useState(false);
  const [isGeneratingGreeting, setIsGeneratingGreeting] = useState(false);
  const messagesEndRef = useRef(null);

  // Lista de POIs para referencia
  const POIS_LIST = [
    { id: "plaza_oriente", name: "Plaza de Oriente", index: 0 },
    { id: "plaza_ramales", name: "Plaza de Ramales", index: 1 },
    { id: "calle_vergara", name: "Calle de Vergara", index: 2 },
    { id: "plaza_isabel_ii", name: "Plaza de Isabel II", index: 3 },
    { id: "calle_arenal_1", name: "Calle del Arenal (Teatro)", index: 4 },
    { id: "calle_bordadores", name: "Calle de Bordadores", index: 5 },
    { id: "plazuela_san_gines", name: "Plazuela de San Ginés", index: 6 },
    { id: "pasadizo_san_gines", name: "Pasadizo de San Ginés", index: 7 },
    { id: "calle_arenal_2", name: "Calle del Arenal (Sol)", index: 8 },
    { id: "museo_raton_perez", name: "Museo Ratoncito Pérez", index: 9 }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cargar familias del usuario al montar el componente
  useEffect(() => {
    loadUserFamilies();
  }, []);

  // Cargar historial cuando se selecciona una familia
  useEffect(() => {
    if (selectedFamily) {
      loadChatHistory();
      loadFamilyStatus();
    }
  }, [selectedFamily]);

  const loadUserFamilies = async () => {
    try {
      setIsLoadingFamilies(true);
      const response = await ApiService.getChatFamilies();
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

  const generateWelcomeMessage = async (family, status) => {
    try {
      setIsGeneratingGreeting(true);
      
      // Determinar POI actual basado en el estado de la familia
      const currentPoiIndex = status?.current_poi_index || 0;
      const currentPoi = POIS_LIST[currentPoiIndex] || POIS_LIST[0];
      
      // Determinar el tipo de saludo basado en el progreso
      let greetingType = 'inicial';
      if (status?.visited_pois > 0) {
        greetingType = 'regreso';
      }
      
      // Crear mensaje de contexto para el saludo
      const greetingContext = {
        family_name: family.name,
        current_poi: currentPoi,
        progress: {
          current_index: currentPoiIndex,
          total_pois: POIS_LIST.length,
          points: status?.total_points || 0,
          visited_count: status?.visited_pois || 0
        },
        greeting_type: greetingType
      };
      
      // Mensaje específico según el contexto
      let contextMessage = '';
      if (greetingType === 'inicial') {
        contextMessage = `¡Hola ${family.name}! Soy el Ratoncito Pérez y estoy muy emocionado de acompañaros en esta aventura por Madrid. Comenzamos nuestra ruta en ${currentPoi.name}, un lugar muy especial que me encanta. ¿Estáis listos para descubrir los secretos mágicos de Madrid conmigo?`;
      } else {
        contextMessage = `¡Bienvenidos de vuelta, ${family.name}! Me alegra veros otra vez. Veo que ya habéis visitado ${status.visited_pois} lugares en nuestra ruta y habéis conseguido ${status.total_points} puntos mágicos. Ahora estamos en ${currentPoi.name}. ¿Qué aventura os apetece vivir hoy?`;
      }
      
      // Enviar mensaje al backend para generar respuesta contextual
      const response = await ApiService.sendChatMessage(
        family.id,
        contextMessage,
        null,
        'Sistema'
      );
      
      if (response.success) {
        // Crear mensaje del sistema primero (contexto)
        const systemMessage = {
          id: `welcome_system_${Date.now()}`,
          text: contextMessage,
          sender: 'system',
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          isHidden: true // Para que no se muestre visualmente
        };
        
        // Crear respuesta del Ratoncito Pérez
        const welcomeMessage = {
          id: `welcome_${Date.now()}`,
          text: response.response,
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          points_earned: response.points_earned,
          situation: response.situation,
          achievements: response.achievements,
          isWelcome: true,
          currentPoi: currentPoi
        };
        
        // Agregar ambos mensajes (el sistema oculto y la respuesta visible)
        setMessages([systemMessage, welcomeMessage]);
        
        // Actualizar estado si hay cambios de puntos
        if (response.points_earned > 0) {
          await loadFamilyStatus();
        }
      } else {
        throw new Error(response.error || 'Error generando saludo');
      }
    } catch (error) {
      console.error('Error generating welcome message:', error);
      
      // Mensaje de bienvenida fallback
      const currentPoiIndex = status?.current_poi_index || 0;
      const currentPoi = POIS_LIST[currentPoiIndex] || POIS_LIST[0];
      
      const fallbackMessage = {
        id: `welcome_fallback_${Date.now()}`,
        text: `¡Hola ${family.name}! 🐭✨ Soy el Ratoncito Pérez y estoy aquí para acompañaros en vuestra aventura por Madrid. Actualmente nos encontramos en ${currentPoi.name}. ¡Preguntadme lo que queráis saber sobre este lugar mágico!`,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
        isWelcome: true,
        currentPoi: currentPoi
      };
      
      setMessages([fallbackMessage]);
    } finally {
      setIsGeneratingGreeting(false);
    }
  };

  const loadChatHistory = async () => {
    if (!selectedFamily) return;
    
    try {
      setIsLoadingHistory(true);
      const response = await ApiService.getChatHistory(selectedFamily.id);
      
      // Convertir historial del backend al formato del frontend
      const formattedMessages = response.messages.map((msg, index) => [
        {
          id: `${index}_user`,
          text: msg.user_message,
          sender: 'user',
          timestamp: new Date(msg.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          speaker: msg.speaker
        },
        {
          id: `${index}_bot`,
          text: msg.agent_response,
          sender: 'bot',
          timestamp: new Date(msg.timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        }
      ]).flat();

      setMessages(formattedMessages);

      // Si no hay historial, generar mensaje de bienvenida contextual
      if (formattedMessages.length === 0) {
        // Esperar a que se cargue el estado de la familia antes de generar el saludo
        const status = await ApiService.getFamilyStatus(selectedFamily.id);
        await generateWelcomeMessage(selectedFamily, status);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      setError('Error cargando historial: ' + ApiService.formatError(error));
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const loadFamilyStatus = async () => {
    if (!selectedFamily) return;
    
    try {
      const status = await ApiService.getFamilyStatus(selectedFamily.id);
      setFamilyStatus(status);
    } catch (error) {
      console.error('Error loading family status:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedFamily || isSending) return;

    const userMessage = {
      id: Date.now(),
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev.filter(msg => !msg.isHidden), userMessage]); // Filtrar mensajes ocultos
    const messageToSend = newMessage;
    setNewMessage('');
    setIsSending(true);
    setIsTyping(true);
    setError('');

    try {
      // Enviar mensaje al backend
      const response = await ApiService.sendChatMessage(
        selectedFamily.id,
        messageToSend,
        null, // location - por ahora null
        null  // speaker_name - por ahora null
      );

      if (response.success) {
        const botResponse = {
          id: Date.now() + 1,
          text: response.response,
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          points_earned: response.points_earned,
          situation: response.situation,
          achievements: response.achievements
        };

        setMessages(prev => [...prev.filter(msg => !msg.isHidden), botResponse]); // Filtrar mensajes ocultos

        // Actualizar estado de la familia si hay cambios
        if (response.points_earned > 0) {
          await loadFamilyStatus();
        }
      } else {
        throw new Error(response.error || 'Error en la respuesta del servidor');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Error enviando mensaje: ' + ApiService.formatError(error));
      
      // Mensaje de error del bot
      const errorMessage = {
        id: Date.now() + 1,
        text: "¡Ups! He tenido un problemita técnico. ¿Puedes intentarlo de nuevo? 🐭",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
        isError: true
      };
      setMessages(prev => [...prev.filter(msg => !msg.isHidden), errorMessage]); // Filtrar mensajes ocultos
    } finally {
      setIsSending(false);
      setIsTyping(false);
    }
  };

  const handleAdvanceToNextPOI = async () => {
    if (!selectedFamily || isAdvancing) return;

    setIsAdvancing(true);
    setError('');

    try {
      const response = await ApiService.advanceToNextPOI(selectedFamily.id);

      if (response.success) {
        // Mensaje del sistema sobre el avance
        const advanceMessage = {
          id: Date.now(),
          text: response.message || `¡Habéis avanzado al siguiente punto de interés!`,
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
          isAdvance: true,
          advanceData: {
            poi: response.poi,
            points_earned: response.points_earned,
            total_points: response.total_points,
            progress: response.progress
          }
        };

        setMessages(prev => [...prev.filter(msg => !msg.isHidden), advanceMessage]); // Filtrar mensajes ocultos

        // Actualizar estado de familia
        await loadFamilyStatus();

        if (response.completed) {
          // Mensaje de finalización
          const completionMessage = {
            id: Date.now() + 1,
            text: "🎉 ¡Felicidades! ¡Habéis completado toda la ruta del Ratoncito Pérez! Ha sido una aventura increíble. 🐭✨",
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }),
            isCompletion: true
          };
          setMessages(prev => [...prev.filter(msg => !msg.isHidden), completionMessage]); // Filtrar mensajes ocultos
        }
      } else {
        throw new Error(response.message || 'Error avanzando al siguiente POI');
      }
    } catch (error) {
      console.error('Error advancing POI:', error);
      setError('Error avanzando: ' + ApiService.formatError(error));
    } finally {
      setIsAdvancing(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Si está cargando familias
  if (isLoadingFamilies) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50">
        <Header title="Ratoncito Pérez" showBackButton />
        <div className="container mx-auto px-4 py-8 flex items-center justify-center h-64">
          <div className="text-center bg-white/70 backdrop-blur-sm rounded-3xl p-8 shadow-lg border border-yellow-200/50">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-yellow-200 border-t-yellow-500 mx-auto mb-4"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl">🐭</span>
              </div>
            </div>
            <p className="text-yellow-700 font-medium text-lg">Preparando la aventura...</p>
            <p className="text-yellow-600 text-sm mt-2">Cargando familias</p>
          </div>
        </div>
        <Navigation />
      </div>
    );
  }

  // Si no hay familias
  if (families.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 pb-20">
        <Header title="Ratoncito Pérez" showBackButton />
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-12 text-center shadow-xl border border-yellow-200/50 max-w-md mx-auto">
            <div className="relative mb-6">
              <div className="text-8xl mb-4 animate-bounce">🐭</div>
              <div className="absolute -top-2 -right-2 text-3xl animate-pulse">✨</div>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4 bg-gradient-to-r from-yellow-600 to-amber-600 bg-clip-text text-transparent">
              ¡Hola pequeño explorador!
            </h2>
            <p className="text-gray-600 mb-8 leading-relaxed">
              Para comenzar nuestra aventura mágica por Madrid, primero necesitas crear una familia desde tu perfil.
            </p>
            <button 
              onClick={() => window.history.back()}
              className="bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500 text-white px-8 py-4 rounded-2xl font-bold hover:from-yellow-600 hover:via-amber-600 hover:to-orange-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              Crear Mi Familia
            </button>
          </div>
        </div>
        <Navigation />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-amber-50 to-orange-50 pb-20">
      <Header title="Ratoncito Pérez" showBackButton />
      
      <div className="container mx-auto max-w-4xl">
        {/* Selector de Familia */}
        {families.length > 1 && (
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-6 mb-6 shadow-lg border border-yellow-200/50">
            <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center">
              <FiUsers className="mr-2 text-yellow-600" />
              Selecciona tu familia:
            </label>
            <select
              value={selectedFamily?.id || ''}
              onChange={(e) => {
                const family = families.find(f => f.id === parseInt(e.target.value));
                setSelectedFamily(family);
              }}
              className="w-full px-6 py-4 border-2 border-yellow-200 rounded-2xl focus:ring-4 focus:ring-yellow-300/50 focus:border-yellow-400 bg-white/80 backdrop-blur-sm transition-all duration-300 font-medium"
            >
              <option value="">✨ Selecciona una familia...</option>
              {families.map((family) => (
                <option key={family.id} value={family.id}>
                  👨‍👩‍👧‍👦 {family.name} ({family.member_count} miembros)
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Información de la Familia y Progreso */}
        {selectedFamily && familyStatus && (
          <div className="bg-gradient-to-r from-white/95 to-yellow-50/95 backdrop-blur-sm rounded-3xl p-6 mb-6 shadow-lg border border-yellow-200/50">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  👑
                </div>
                <div>
                  <h3 className="font-bold text-xl text-gray-800">{selectedFamily.name}</h3>
                  <p className="text-sm text-gray-600 flex items-center">
                    <FiMapPin className="mr-1" size={14} />
                    {Math.min(familyStatus.current_poi_index + 1, POIS_LIST.length)}/{POIS_LIST.length} lugares mágicos visitados
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 bg-gradient-to-r from-yellow-100 to-amber-100 px-4 py-2 rounded-2xl border border-yellow-300/50">
                  <FiStar className="text-yellow-600" size={18} />
                  <span className="font-bold text-xl text-yellow-700">{familyStatus.total_points}</span>
                  <span className="text-xs text-yellow-600 font-medium">pts</span>
                </div>
                <button
                  onClick={loadFamilyStatus}
                  className="p-3 text-gray-400 hover:text-yellow-600 transition-all duration-300 hover:bg-yellow-100 rounded-xl"
                >
                  <FiRefreshCw size={18} />
                </button>
              </div>
            </div>
            
            {/* Barra de progreso mejorada */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-600">Progreso de la aventura</span>
                <span className="text-sm font-bold text-yellow-600">
                  {Math.round(familyStatus.current_poi_index >= POIS_LIST.length ? 100 : ((familyStatus.current_poi_index + 1) / POIS_LIST.length) * 100)}%
                </span>
              </div>
              <div className="w-full bg-gradient-to-r from-gray-200 to-gray-300 rounded-full h-3 shadow-inner">
                <div 
                  className="bg-gradient-to-r from-yellow-400 via-amber-500 to-orange-500 h-3 rounded-full transition-all duration-700 shadow-lg relative overflow-hidden"
                  style={{ width: `${familyStatus.current_poi_index >= POIS_LIST.length ? 100 : ((familyStatus.current_poi_index + 1) / POIS_LIST.length) * 100}%` }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Botón Próximo Destino mejorado */}
            <div className="flex justify-center">
              <button
                onClick={handleAdvanceToNextPOI}
                disabled={isAdvancing || familyStatus.current_poi_index >= POIS_LIST.length}
                className={`group relative flex items-center space-x-3 px-8 py-4 rounded-2xl font-bold transition-all duration-300 transform ${
                  familyStatus.current_poi_index >= POIS_LIST.length
                    ? 'bg-gradient-to-r from-gray-400 to-gray-500 text-white cursor-not-allowed shadow-lg'
                    : familyStatus.current_poi_index === POIS_LIST.length - 1
                    ? 'bg-gradient-to-r from-purple-500 via-purple-600 to-pink-600 text-white hover:from-purple-600 hover:via-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl hover:-translate-y-1'
                    : 'bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 text-white hover:from-green-600 hover:via-emerald-600 hover:to-teal-600 shadow-lg hover:shadow-xl hover:-translate-y-1'
                } disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none`}
              >
                {isAdvancing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                    <span>Avanzando...</span>
                  </>
                ) : familyStatus.current_poi_index >= POIS_LIST.length ? (
                  <>
                    <FiCheckCircle size={20} />
                    <span>¡Aventura Completada!</span>
                    <div className="absolute -top-1 -right-1 text-lg animate-bounce">🎉</div>
                  </>
                ) : familyStatus.current_poi_index === POIS_LIST.length - 1 ? (
                  <>
                    <FiTarget size={20} />
                    <span>¡Finalizar Aventura!</span>
                    <div className="absolute -top-1 -right-1 text-lg animate-pulse">🏁</div>
                  </>
                ) : (
                  <>
                    <FiMapPin size={20} />
                    <span>Siguiente: {POIS_LIST[familyStatus.current_poi_index + 1]?.name}</span>
                    <div className="absolute -top-1 -right-1 text-lg animate-bounce">✨</div>
                  </>
                )}
                {!isAdvancing && familyStatus.current_poi_index < POIS_LIST.length && (
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Error Display mejorado */}
        {error && (
          <div className="bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-2xl mb-6 shadow-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mr-3">
                <FiAlertCircle size={20} className="text-red-600" />
              </div>
              <div>
                <h4 className="font-bold text-red-800">¡Ups! Algo salió mal</h4>
                <span className="text-sm">{error}</span>
              </div>
            </div>
          </div>
        )}

        {selectedFamily ? (
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-xl border border-yellow-200/50 overflow-hidden">
            {/* Chat Messages */}
            <div className="h-[calc(100vh-420px)] overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-transparent to-yellow-50/20">
              {isLoadingHistory || isGeneratingGreeting ? (
                <div className="flex justify-center py-12">
                  <div className="text-center bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-lg border border-yellow-200/50">
                    <div className="relative mb-4">
                      <div className="animate-spin rounded-full h-12 w-12 border-3 border-yellow-200 border-t-yellow-500 mx-auto"></div>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-xl">🐭</span>
                      </div>
                    </div>
                    <p className="text-yellow-700 font-bold text-lg">
                      {isGeneratingGreeting ? '✨ Preparando un saludo especial...' : '📚 Cargando vuestra historia...'}
                    </p>
                    <p className="text-yellow-600 text-sm mt-2">Un momento, por favor</p>
                  </div>
                </div>
              ) : (
                messages.filter(msg => !msg.isHidden).map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[85%] relative group ${
                      message.sender === 'user' 
                        ? 'bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500 text-white shadow-lg' 
                        : message.isError 
                        ? 'bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-200 text-red-700 shadow-lg'
                        : message.isAdvance
                        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 text-green-700 shadow-lg'
                        : message.isCompletion
                        ? 'bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 text-purple-700 shadow-lg'
                        : message.isWelcome
                        ? 'bg-gradient-to-r from-yellow-50 via-amber-50 to-orange-50 border-2 border-yellow-300 text-gray-800 shadow-lg'
                        : 'bg-white/95 backdrop-blur-sm border-2 border-yellow-200 text-gray-800 shadow-lg'
                    } rounded-3xl p-6 transition-all duration-300 hover:shadow-xl`}>
                      
                      {/* Avatar y header del bot */}
                      {message.sender === 'bot' && !message.isError && (
                        <div className="flex items-center space-x-3 mb-4">
                          <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full flex items-center justify-center text-white font-bold shadow-lg">
                            🐭
                          </div>
                          <div>
                            <span className="text-sm font-bold text-yellow-600 flex items-center">
                              <FiTarget className="mr-1" size={14} />
                              Ratoncito Pérez
                              {message.isWelcome && message.currentPoi && (
                                <span className="ml-3 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium border border-blue-200">
                                  📍 {message.currentPoi.name}
                                </span>
                              )}
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {/* Avatar del usuario */}
                      {message.sender === 'user' && (
                        <div className="flex items-center justify-end space-x-2 mb-3">
                          <span className="text-xs font-medium text-white/80">Tú</span>
                          <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center">
                            👤
                          </div>
                        </div>
                      )}
                      
                      {/* Contenido del mensaje */}
                      <div className={`text-sm leading-relaxed ${
                        message.sender === 'user' ? 'text-white' : 
                        message.isError ? 'text-red-700' :
                        message.isAdvance ? 'text-green-700' :
                        message.isCompletion ? 'text-purple-700' :
                        'text-gray-800'
                      }`}>
                        {message.text}
                      </div>
                      
                      {/* Información adicional para mensajes de avance */}
                      {message.advanceData && (
                        <div className="mt-4 p-4 bg-gradient-to-r from-green-100 to-emerald-100 rounded-2xl border border-green-200 shadow-inner">
                          <div className="text-sm">
                            <div className="font-bold text-green-800 text-base mb-2 flex items-center">
                              <FiMapPin className="mr-2" size={16} />
                              📍 {message.advanceData.poi?.name}
                            </div>
                            <div className="flex items-center justify-between bg-white/50 rounded-xl p-3">
                              <span className="text-green-700 font-medium">Progreso: {message.advanceData.progress}</span>
                              <div className="flex items-center space-x-1 bg-gradient-to-r from-yellow-400 to-amber-500 text-white px-3 py-1 rounded-full font-bold shadow-lg">
                                <FiStar size={14} />
                                <span>+{message.advanceData.points_earned}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Puntos ganados */}
                      {message.points_earned > 0 && (
                        <div className="mt-3 flex justify-end">
                          <div className="flex items-center space-x-2 bg-gradient-to-r from-yellow-400 to-amber-500 text-white px-4 py-2 rounded-full font-bold shadow-lg text-sm">
                            <FiStar size={14} />
                            <span>+{message.points_earned} puntos mágicos</span>
                          </div>
                        </div>
                      )}

                      {/* Timestamp */}
                      <div className="flex items-center justify-end space-x-2 mt-4 pt-2 border-t border-gray-200/50">
                        <FiClock size={12} className={
                          message.sender === 'user' ? 'text-white/60' : 
                          message.isError ? 'text-red-400' :
                          'text-gray-400'
                        } />
                        <span className={`text-xs ${
                          message.sender === 'user' ? 'text-white/60' : 
                          message.isError ? 'text-red-400' :
                          'text-gray-400'
                        }`}>
                          {message.timestamp}
                        </span>
                      </div>

                      {/* Efectos especiales para mensajes especiales */}
                      {message.isWelcome && (
                        <div className="absolute -top-2 -right-2 text-2xl animate-bounce">✨</div>
                      )}
                      {message.isCompletion && (
                        <div className="absolute -top-2 -right-2 text-2xl animate-pulse">🎉</div>
                      )}
                      {message.isAdvance && (
                        <div className="absolute -top-2 -right-2 text-2xl animate-bounce">🗺️</div>
                      )}
                    </div>
                  </div>
                ))
              )}
              
              {/* Indicador de escritura mejorado */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white/95 backdrop-blur-sm border-2 border-yellow-200 rounded-3xl p-6 shadow-lg max-w-[80%]">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full flex items-center justify-center text-white font-bold shadow-lg animate-pulse">
                        🐭
                      </div>
                      <span className="text-sm font-bold text-yellow-600">Ratoncito Pérez está escribiendo...</span>
                    </div>
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full animate-bounce shadow-lg"></div>
                      <div className="w-3 h-3 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full animate-bounce shadow-lg" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-3 h-3 bg-gradient-to-r from-yellow-400 to-amber-500 rounded-full animate-bounce shadow-lg" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input mejorado */}
            <div className="border-t-2 border-yellow-200/50 bg-gradient-to-r from-white/95 to-yellow-50/95 backdrop-blur-sm p-6">
              <div className="flex items-end space-x-4 bg-white/80 backdrop-blur-sm rounded-2xl border-2 border-yellow-200/50 p-4 shadow-lg">
                <div className="flex-1 relative">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="¿Qué quieres saber sobre Madrid? Pregúntame sobre historia, lugares secretos, leyendas..."
                    className="w-full resize-none border-0 focus:outline-none bg-transparent text-gray-800 placeholder-gray-500 text-sm max-h-32 leading-relaxed font-medium"
                    rows="1"
                    disabled={isSending || isGeneratingGreeting}
                  />
                  {!newMessage.trim() && !isSending && (
                    <div className="absolute top-8 left-0 text-xs text-gray-400 flex items-center space-x-1">
                      <span>💡</span>
                      <span>Pulsa Enter para enviar</span>
                    </div>
                  )}
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim() || isSending || isGeneratingGreeting}
                  className="group bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500 text-white p-4 rounded-2xl hover:from-yellow-600 hover:via-amber-600 hover:to-orange-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-1 disabled:transform-none"
                >
                  {isSending ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  ) : (
                    <FiSend size={20} className="group-hover:translate-x-1 transition-transform duration-200" />
                  )}
                </button>
              </div>
              <div className="flex justify-center mt-3">
                <p className="text-xs text-gray-500 flex items-center space-x-1">
                  <span>🔒</span>
                  <span>Conversación segura con el Ratoncito Pérez</span>
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-12 text-center shadow-xl border border-yellow-200/50 max-w-md mx-auto">
            <div className="relative mb-8">
              <div className="text-6xl mb-4 animate-bounce">🐭</div>
              <div className="absolute -top-2 -right-2 text-2xl animate-pulse">💭</div>
              <div className="absolute -bottom-2 -left-2 text-xl animate-bounce delay-200">✨</div>
            </div>
            <h3 className="text-xl font-bold text-gray-800 mb-3 bg-gradient-to-r from-yellow-600 to-amber-600 bg-clip-text text-transparent">
              ¡Elige tu familia aventurera!
            </h3>
            <p className="text-gray-600 leading-relaxed">
              Selecciona una familia de la lista de arriba para comenzar nuestra mágica conversación por Madrid
            </p>
          </div>
        )}
      </div>

      <Navigation />
    </div>
  );
}


export default ChatBot;