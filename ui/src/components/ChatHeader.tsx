import { Bot, Languages } from 'lucide-react';

interface ChatHeaderProps {
  language: 'en' | 'ne';
  onLanguageToggle: () => void;
}

export function ChatHeader({ language, onLanguageToggle }: ChatHeaderProps) {
  return (
    <div className="bg-gradient-to-r from-blue-900 to-blue-800 text-white p-6 shadow-lg">
      <div className="max-w-4xl mx-auto flex items-center gap-4">
        <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
          <Bot className="size-8" />
        </div>
        <div className="flex-1">
          <h1>{language === 'en' ? 'Nepal Government Information Service' : 'नेपाल सरकार सूचना सेवा'}</h1>
          <p className="text-blue-100 text-sm">
            {language === 'en' 
              ? 'Ask questions about government services, policies, and procedures'
              : 'सरकारी सेवाहरू, नीतिहरू र प्रक्रियाहरूको बारेमा सोध्नुहोस्'}
          </p>
        </div>
        <button
          onClick={onLanguageToggle}
          className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors backdrop-blur-sm"
        >
          <Languages className="size-5" />
          <span>{language === 'en' ? 'नेपाली' : 'English'}</span>
        </button>
      </div>
    </div>
  );
}