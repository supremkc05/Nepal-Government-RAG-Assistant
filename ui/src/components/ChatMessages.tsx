import { Message } from '../App';
import { Bot, User } from 'lucide-react';
import { useEffect, useRef } from 'react';

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 md:p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex gap-3">
            <div className="bg-blue-100 p-2 rounded-lg size-fit">
              <Bot className="size-5 text-blue-900" />
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200 max-w-3xl">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`${isUser ? 'bg-blue-600' : 'bg-blue-100'} p-2 rounded-lg size-fit h-fit`}>
        {isUser ? (
          <User className={`size-5 ${isUser ? 'text-white' : 'text-blue-900'}`} />
        ) : (
          <Bot className="size-5 text-blue-900" />
        )}
      </div>
      
      <div
        className={`rounded-lg p-4 max-w-3xl shadow-sm ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white border border-gray-200'
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <FormattedContent content={message.content} />
        )}
        <p className={`text-xs mt-3 ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
          {message.timestamp.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}

function FormattedContent({ content }: { content: string }) {
  // Split content into lines for better processing
  const lines = content.split('\n');
  const elements: JSX.Element[] = [];
  let currentList: string[] = [];
  let listType: 'bullet' | 'number' | null = null;
  
  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="space-y-2.5 my-3 ml-2">
          {currentList.map((item, idx) => (
            <li key={idx} className="flex gap-3 items-start">
              <span className="text-blue-600 font-bold mt-0.5 flex-shrink-0">•</span>
              <span className="flex-1 leading-relaxed text-gray-800">
                {formatInlineText(item)}
              </span>
            </li>
          ))}
        </ul>
      );
      currentList = [];
      listType = null;
    }
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    
    // Skip empty lines
    if (!trimmed) {
      flushList();
      return;
    }
    
    // Check for numbered list items (1., 2., etc.)
    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
    if (numberedMatch) {
      if (listType !== 'number') {
        flushList();
        listType = 'number';
      }
      currentList.push(numberedMatch[2]);
      return;
    }
    
    // Check for bullet points (•, *, -, etc.)
    const bulletMatch = trimmed.match(/^[•\-*]\s+(.+)$/);
    if (bulletMatch) {
      if (listType !== 'bullet') {
        flushList();
        listType = 'bullet';
      }
      currentList.push(bulletMatch[1]);
      return;
    }
    
    // Not a list item, flush any pending list
    flushList();
    
    // Check if it's a heading (ends with : or is short and bold)
    const isHeading = trimmed.endsWith(':') && trimmed.length < 100;
    
    if (isHeading) {
      elements.push(
        <h3 key={`heading-${idx}`} className="font-bold text-blue-900 text-base mt-4 mb-2">
          {trimmed}
        </h3>
      );
    } else {
      // Regular paragraph text
      elements.push(
        <p key={`p-${idx}`} className="leading-relaxed text-gray-800 my-2">
          {formatInlineText(trimmed)}
        </p>
      );
    }
  });
  
  // Flush any remaining list
  flushList();
  
  return <div className="space-y-1">{elements}</div>;
}

function formatInlineText(text: string) {
  // Bold text between ** or __
  let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
  formatted = formatted.replace(/__(.*?)__/g, '<strong class="font-semibold">$1</strong>');
  
  // Italic text between * or _
  formatted = formatted.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');
  formatted = formatted.replace(/_(.*?)_/g, '<em class="italic">$1</em>');
  
  // Code/inline code between `
  formatted = formatted.replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>');
  
  // Links
  formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">$1</a>');
  
  return <span dangerouslySetInnerHTML={{ __html: formatted }} />;
}
