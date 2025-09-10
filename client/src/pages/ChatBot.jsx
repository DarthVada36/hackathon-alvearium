import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { FiSend, FiTarget, FiMapPin, FiClock, FiHelpCircle } from 'react-icons/fi';

const ChatBot = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: `¡Hola ${user?.name}! Soy el Ratoncito Pérez, tu guía personal por Madrid. ¿En qué puedo ayudarte hoy?`,
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickQuestions = [
    "¿Dónde está la Casa del Ratoncito Pérez?",
    "Cuéntame sobre la Puerta del Sol",
    "¿Qué lugares puedo visitar cerca?",
    "Historia de Madrid",
    "¿Cómo llego a Plaza Mayor?",
    "Restaurantes típicos madrileños"
  ];

  const generateBotResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('casa') && lowerMessage.includes('ratoncito')) {
      return "¡Ah, mi hogar! 🏠 La Casa del Ratoncito Pérez está en la Calle Arenal, 8, muy cerca de la Puerta del Sol. Es una pequeña tienda que recrea mi casa, ¡y es donde comienza nuestra aventura! ¿Te gustaría que te guíe hasta allí?";
    }
    
    if (lowerMessage.includes('puerta del sol')) {
      return "¡La Puerta del Sol es el corazón de Madrid! ❤️ Es el kilómetro 0 de todas las carreteras españolas. Aquí encontrarás el famoso oso y el madroño, símbolo de la ciudad. Durante las campanadas de Año Nuevo, miles de personas se reúnen aquí. ¡Un lugar lleno de historia y energía!";
    }
    
    if (lowerMessage.includes('plaza mayor')) {
      return "¡La Plaza Mayor es espectacular! 🏛️ Construida en el siglo XVII, es una de las plazas más bonitas de Europa. Fíjate en la Casa de la Panadería con sus hermosos frescos. ¿Sabías que aquí se celebraban corridas de toros, mercados y hasta la Inquisición? ¡Ahora es perfecta para tapas!";
    }
    
    if (lowerMessage.includes('cerca') || lowerMessage.includes('ubicación')) {
      return "Para ayudarte mejor con lugares cercanos, necesito que actives tu geolocalización en la sección de Ruta 📍. Desde allí podré guiarte a los sitios más interesantes según donde estés. ¡Te esperan muchas sorpresas!";
    }
    
    if (lowerMessage.includes('historia') && lowerMessage.includes('madrid')) {
      return "¡Madrid tiene una historia fascinante! 📚 Fundada por el emir Muhammad I en el siglo IX como 'Mayrit', se convirtió en capital de España en 1561 bajo Felipe II. Desde entonces ha sido testigo de momentos increíbles: el Siglo de Oro, la Guerra Civil, la Movida Madrileña... ¡Cada calle tiene una historia que contar!";
    }
    
    if (lowerMessage.includes('comer') || lowerMessage.includes('restaurante') || lowerMessage.includes('tapas')) {
      return "¡Me encanta la comida madrileña! 🍴 Te recomiendo probar el cocido madrileño en Casa Carola, los callos en Casa Ricardo, o unas bravas en La Dolores. Para algo más moderno, el Mercado de San Miguel es perfecto. ¡Y no olvides los churros con chocolate de San Ginés!";
    }
    
    if (lowerMessage.includes('hola') || lowerMessage.includes('buenos días') || lowerMessage.includes('buenas tardes')) {
      return `¡Hola de nuevo, ${user?.name}! 👋 ¿Listo para seguir explorando Madrid? Pregúntame lo que quieras sobre la ciudad, sus monumentos, su historia o su gastronomía. ¡Estoy aquí para ayudarte!`;
    }
    
    if (lowerMessage.includes('gracias')) {
      return "¡De nada! 😊 Es un placer ser tu guía por Madrid. Recuerda que puedes preguntarme cualquier cosa sobre la ciudad. ¡Que disfrutes tu aventura madrileña!";
    }
    
    if (lowerMessage.includes('puntos') || lowerMessage.includes('ruta')) {
      return `¡Genial que preguntes sobre los puntos! ⭐ Actualmente tienes ${user?.points || 0} puntos. Para ganar más, visita los lugares oficiales de mi ruta en la sección Ruta. ¡Cada lugar te dará entre 10 y 50 puntos dependiendo de su importancia histórica!`;
    }
    
    // Respuesta por defecto
    return "¡Qué pregunta tan interesante! 🤔 Soy experto en Madrid, su historia, monumentos, gastronomía y cultura. Puedes preguntarme sobre lugares específicos, cómo llegar a sitios, recomendaciones de restaurantes, o cualquier curiosidad sobre la capital. ¿Hay algo específico que te gustaría saber?";
  };

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: newMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);

    // Simular tiempo de respuesta del bot
    setTimeout(() => {
      const botResponse = {
        id: messages.length + 2,
        text: generateBotResponse(newMessage),
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1500 + Math.random() * 1000);
  };

  const handleQuickQuestion = (question) => {
    setNewMessage(question);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-amber-100 pb-20">
      <Header title="Ratoncito Pérez" showBackButton />
      
      <div className="container mx-auto px-4 py-4 h-[calc(100vh-140px)] flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] ${
                message.sender === 'user' 
                  ? 'bg-amber-600 text-white' 
                  : 'bg-white border border-lime-200'
              } rounded-2xl p-4 shadow-sm`}>
                {message.sender === 'bot' && (
                  <div className="flex items-center space-x-2 mb-2">
                    <FiTarget className="text-golden-amber" size={16} />
                    <span className="text-xs font-medium text-amber-600">Ratoncito Pérez</span>
                  </div>
                )}
                <p className={`text-sm ${message.sender === 'user' ? 'text-white' : 'text-gray-800'}`}>
                  {message.text}
                </p>
                <div className="flex items-center justify-end space-x-1 mt-2">
                  <FiClock size={12} className={message.sender === 'user' ? 'text-white/70' : 'text-gray-400'} />
                  <span className={`text-xs ${message.sender === 'user' ? 'text-white/70' : 'text-gray-400'}`}>
                    {message.timestamp}
                  </span>
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white border border-lime-200 rounded-2xl p-4 shadow-sm">
                <div className="flex items-center space-x-2 mb-2">
                  <FiTarget className="text-golden-amber" size={16} />
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
        {messages.length === 1 && (
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-3 flex items-center">
              <FiHelpCircle className="mr-2" />
              Preguntas frecuentes:
            </p>
            <div className="grid grid-cols-1 gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
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
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!newMessage.trim() || isTyping}
              className="bg-amber-600 text-white p-3 rounded-xl hover:bg-amber-600/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FiSend size={18} />
            </button>
          </div>
        </div>
      </div>

      <Navigation />
    </div>
  );
};

export default ChatBot;
