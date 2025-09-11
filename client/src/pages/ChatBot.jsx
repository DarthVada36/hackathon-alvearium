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
  FiHelpCircle,
  FiChevronRight,
  FiRefreshCw,
  FiArrowRight,
  FiStar,
  FiUsers,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';

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
  const messagesEndRef = useRef(null);

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

      // Si no hay historial, mostrar mensaje de bienvenida
      if (formattedMessages.length === 0) {
        const welcomeMessage = {
          id: 'welcome',
          text: `¡Hola ${selectedFamily.name}! Soy el Ratoncito Pérez, vuestro guía personal por Madrid. ¿En qué puedo ayudaros hoy?`,
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        };
        setMessages([welcomeMessage]);
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

    setMessages(prev => [...prev, userMessage]);
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

        setMessages(prev => [...prev, botResponse]);

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
      setMessages(prev => [...prev, errorMessage]);
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

        setMessages(prev => [...prev, advanceMessage]);

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
          setMessages(prev => [...prev, completionMessage]);
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

  const quickQuestions = [
    "¿Dónde está la Casa del Ratoncito Pérez?",
    "Cuéntame sobre la Puerta del Sol",
    "¿Qué lugares puedo visitar cerca?",
    "Historia de Madrid",
    "¿Cómo llego a Plaza Mayor?",
    "Restaurantes típicos madrileños"
  ];

  // Si está cargando familias
  if (isLoadingFamilies) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
        <Header title="Ratoncito Pérez" showBackButton />
        <div className="container mx-auto px-4 py-4 flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto mb-4"></div>
            <p className="text-amber-600 font-medium">Cargando familias...</p>
          </div>
        </div>
        <Navigation />
      </div>
    );
  }

  // Si no hay familias
  if (families.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
        <Header title="Ratoncito Pérez" showBackButton />
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-amber-100">
            <div className="text-6xl mb-4">🐭</div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">No tienes familias creadas</h2>
            <p className="text-gray-600 mb-6">
              Para chatear conmigo, primero necesitas crear una familia desde tu perfil.
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
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
      <Header title="Ratoncito Pérez" showBackButton />
      
      <div className="container mx-auto px-4 py-4">
        {/* Selector de Familia */}
        {families.length > 1 && (
          <div className="bg-white rounded-2xl p-4 mb-4 shadow-sm border border-amber-100">
            <label className="block text-sm font-medium text-gray-700 mb-2">
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
                  {family.name} ({family.member_count} miembros)
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Información de la Familia y Progreso */}
        {selectedFamily && familyStatus && (
          <div className="bg-white rounded-2xl p-4 mb-4 shadow-sm border border-amber-100">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-bold text-gray-800">{selectedFamily.name}</h3>
                <p className="text-sm text-gray-600">
                  {familyStatus.visited_pois}/{familyStatus.total_pois} lugares visitados
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-1 text-amber-600">
                  <FiStar size={16} />
                  <span className="font-bold">{familyStatus.total_points}</span>
                </div>
                <button
                  onClick={loadFamilyStatus}
                  className="p-2 text-gray-400 hover:text-amber-600 transition-colors"
                >
                  <FiRefreshCw size={16} />
                </button>
              </div>
            </div>
            
            {/* Barra de progreso */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
              <div 
                className="bg-gradient-to-r from-amber-400 to-amber-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${familyStatus.progress_percentage}%` }}
              />
            </div>

            {/* Botón Siguiente POI */}
            <div className="flex justify-center">
              <button
                onClick={handleAdvanceToNextPOI}
                disabled={isAdvancing || familyStatus.progress_percentage >= 100}
                className="flex items-center space-x-2 bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-2 rounded-xl font-medium hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isAdvancing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Avanzando...</span>
                  </>
                ) : familyStatus.progress_percentage >= 100 ? (
                  <>
                    <FiCheckCircle size={16} />
                    <span>¡Ruta Completada!</span>
                  </>
                ) : (
                  <>
                    <FiArrowRight size={16} />
                    <span>Siguiente POI</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            <div className="flex items-center">
              <FiAlertCircle className="mr-2" size={16} />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

        {selectedFamily ? (
          <div className="h-[calc(100vh-340px)] flex flex-col">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4">
              {isLoadingHistory ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] ${
                      message.sender === 'user' 
                        ? 'bg-amber-600 text-white' 
                        : message.isError 
                        ? 'bg-red-50 border border-red-200 text-red-700'
                        : message.isAdvance
                        ? 'bg-green-50 border border-green-200 text-green-700'
                        : message.isCompletion
                        ? 'bg-purple-50 border border-purple-200 text-purple-700'
                        : 'bg-white border border-lime-200'
                    } rounded-2xl p-4 shadow-sm`}>
                      {message.sender === 'bot' && !message.isError && (
                        <div className="flex items-center space-x-2 mb-2">
                          <FiTarget className="text-amber-600" size={16} />
                          <span className="text-xs font-medium text-amber-600">Ratoncito Pérez</span>
                        </div>
                      )}
                      
                      <p className={`text-sm ${
                        message.sender === 'user' ? 'text-white' : 
                        message.isError ? 'text-red-700' :
                        message.isAdvance ? 'text-green-700' :
                        message.isCompletion ? 'text-purple-700' :
                        'text-gray-800'
                      }`}>
                        {message.text}
                      </p>
                      
                      {/* Información adicional para mensajes de avance */}
                      {message.advanceData && (
                        <div className="mt-3 p-3 bg-green-100 rounded-lg">
                          <div className="text-sm">
                            <div className="font-semibold">📍 {message.advanceData.poi?.name}</div>
                            <div className="flex items-center justify-between mt-2">
                              <span>Progreso: {message.advanceData.progress}</span>
                              <span className="font-bold">+{message.advanceData.points_earned} pts</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Puntos ganados */}
                      {message.points_earned > 0 && (
                        <div className="mt-2 flex items-center space-x-1">
                          <FiStar className="text-yellow-500" size={14} />
                          <span className="text-xs font-medium text-yellow-600">
                            +{message.points_earned} puntos
                          </span>
                        </div>
                      )}

                      <div className="flex items-center justify-end space-x-1 mt-2">
                        <FiClock size={12} className={
                          message.sender === 'user' ? 'text-white/70' : 
                          message.isError ? 'text-red-500' :
                          'text-gray-400'
                        } />
                        <span className={`text-xs ${
                          message.sender === 'user' ? 'text-white/70' : 
                          message.isError ? 'text-red-500' :
                          'text-gray-400'
                        }`}>
                          {message.timestamp}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white border border-lime-200 rounded-2xl p-4 shadow-sm">
                    <div className="flex items-center space-x-2 mb-2">
                      <FiTarget className="text-amber-600" size={16} />
                      <span className="text-xs font-medium text-amber-600">Ratoncito Pérez</span>
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Questions */}
            {messages.length <= 1 && !isLoadingHistory && (
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-3 flex items-center">
                  <FiHelpCircle className="mr-2" />
                  Preguntas frecuentes:
                </p>
                <div className="grid grid-cols-1 gap-2">
                  {quickQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setNewMessage(question)}
                      className="text-left p-3 bg-white/70 border border-lime-200 rounded-lg text-sm text-gray-700 hover:bg-lime-200/30 transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Message Input */}
            <div className="bg-white/80 backdrop-blur-sm rounded-xl border border-lime-200/30 p-3">
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <textarea
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Pregunta sobre Madrid, su historia, lugares que visitar..."
                    className="w-full resize-none border-0 focus:outline-none bg-transparent text-gray-800 placeholder-gray-500 text-sm max-h-20"
                    rows="1"
                    disabled={isSending}
                  />
                </div>
                <button
                  onClick={handleSendMessage}
                  disabled={!newMessage.trim() || isSending}
                  className="bg-amber-600 text-white p-3 rounded-xl hover:bg-amber-600/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSending ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <FiSend size={18} />
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-8 text-center shadow-sm border border-amber-100">
            <div className="text-4xl mb-4">🐭</div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">Selecciona una familia</h3>
            <p className="text-gray-600">Elige una familia para comenzar a chatear conmigo</p>
          </div>
        )}
      </div>

      <Navigation />
    </div>
  );
};

export default ChatBot;