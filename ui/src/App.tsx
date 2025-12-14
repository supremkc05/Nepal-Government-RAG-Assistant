import { ChatHeader } from './components/ChatHeader';
import { ChatMessages } from './components/ChatMessages';
import { ChatInput } from './components/ChatInput';
import { QuickActions } from './components/QuickActions';
import { ServiceSidebar } from './components/ServiceSidebar';
import { useState, useEffect } from 'react';
import { queryRAG, getOrCreateSessionId } from './services/api';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Namaste! I am the Nepal Government Information Assistant. I can help you with information about government services, policies, citizenship, passports, and more. How can I assist you today?',
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState<'en' | 'ne'>('en');
  const [sessionId] = useState(() => getOrCreateSessionId());

  const handleLanguageToggle = () => {
    const newLanguage = language === 'en' ? 'ne' : 'en';
    setLanguage(newLanguage);
    
    // Update welcome message
    setMessages([{
      id: '1',
      content: newLanguage === 'en' 
        ? 'Namaste! I am the Nepal Government Information Assistant. I can help you with information about government services, policies, citizenship, passports, and more. How can I assist you today?'
        : 'नमस्ते! म नेपाल सरकार सूचना सहायक हुँ। म तपाईंलाई सरकारी सेवाहरू, नीतिहरू, नागरिकता, राहदानी र थप बारे जानकारी दिन सक्छु। आज म तपाईंलाई कसरी सहयोग गर्न सक्छु?',
      role: 'assistant',
      timestamp: new Date(),
    }]);
  };

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call actual backend API
      const response = await queryRAG({
        query: content,
        session_id: sessionId,
        top_k: 5,
        use_hybrid: true,
        use_reranker: false,
      });
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        role: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error querying RAG:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again later.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCategory = (category: string) => {
    handleSendMessage(`Tell me about ${category} services`);
  };

  return (
    <div className="size-full flex flex-col bg-gray-50">
      <ChatHeader language={language} onLanguageToggle={handleLanguageToggle} />
      <div className="flex-1 flex overflow-hidden">
        <ServiceSidebar onSelectCategory={handleSelectCategory} />
        <div className="flex-1 flex flex-col">
          <ChatMessages messages={messages} isLoading={isLoading} />
          <QuickActions onSelectQuery={handleSendMessage} isLoading={isLoading} />
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}