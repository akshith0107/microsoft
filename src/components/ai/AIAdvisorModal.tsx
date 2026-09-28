import React, { useState, useEffect, useRef } from 'react';
import { Send, X, ArrowRight } from 'lucide-react';
import { assistantAPI } from '../../api/services';

interface AIAdvisorModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  hindsightMemoryUsed?: string;
  timestamp: string;
}

export const AIAdvisorModal: React.FC<AIAdvisorModalProps> = ({
  isOpen,
  onClose,
  initialQuery,
}) => {
  const [inputQuery, setInputQuery] = useState('');
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: `DukaanPulse Intelligence Assistant active. Powered by Gemini reasoning & store history memory.`,
      hindsightMemoryUsed: 'Memory index: Live store transactions & database facts',
      timestamp: 'SYSTEM READY',
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "Sales comparison this week vs last week",
    "Which products should I reorder before Friday?",
    "Who owes overdue Khata money?",
    "Maggi stock velocity & lead time",
  ];

  useEffect(() => {
    if (initialQuery && isOpen) {
      handleSend(initialQuery);
    }
  }, [initialQuery, isOpen]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || inputQuery;
    if (!query.trim()) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputQuery('');
    setIsTyping(true);

    try {
      const res = await assistantAPI.chat(query, conversationId);
      if (res.conversation_id) {
        setConversationId(res.conversation_id);
      }
      const aiMsg: ChatMessage = {
        id: res.message_id || (Date.now() + 1).toString(),
        sender: 'ai',
        text: res.response,
        hindsightMemoryUsed: res.recommendation_id ? `Recommendation #${res.recommendation_id}` : 'Live PostgreSQL & Hindsight memory',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: `Error connecting to assistant: ${err.message || 'FastAPI backend unavailable.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-end sm:justify-center p-0 sm:p-4 bg-black/60 backdrop-blur-xs font-sans">
      <div className="w-full sm:max-w-[500px] h-[90vh] sm:h-[640px] bg-white rounded-t-[12px] sm:rounded-[10px] border-2 border-[#111111] shadow-[6px_6px_0_#111111] flex flex-col overflow-hidden">
        
        {/* Drawer Header */}
        <div className="p-3.5 bg-[#111111] text-white flex items-center justify-between border-b border-[#111111]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-[#F4C84A] rounded-[2px]" />
            <div>
              <h3 className="font-bold text-white text-xs font-mono uppercase tracking-wider">STORE ADVISOR</h3>
              <p className="text-[10px] text-[#888888] font-mono">Kirana Store Intelligence Layer</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white rounded hover:bg-white/10"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Body */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-[#F5F4EF]">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`
                  max-w-[88%] p-3 rounded-[6px] text-xs leading-relaxed space-y-1.5 border border-[#111111]
                  ${msg.sender === 'user'
                    ? 'bg-[#111111] text-white'
                    : 'bg-white text-[#111111]'
                  }
                `}
              >
                <p className="font-medium">{msg.text}</p>

                {msg.hindsightMemoryUsed && (
                  <div className="pt-1.5 border-t border-[#111111]/20 text-[9px] font-mono font-bold text-[#6B6B6B]">
                    MEMORY: {msg.hindsightMemoryUsed}
                  </div>
                )}
              </div>
              <span className="text-[9px] font-mono text-[#6B6B6B] mt-0.5 px-1">{msg.timestamp}</span>
            </div>
          ))}

          {isTyping && (
            <div className="p-2 bg-white rounded-[6px] border border-[#111111] text-xs font-mono text-[#6B6B6B] animate-pulse">
              Querying store history memory...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Quick Prompts */}
        <div className="p-2 bg-white border-t border-[#111111] space-y-1">
          <div className="text-[9px] font-mono font-bold text-[#6B6B6B] uppercase px-1">
            ANALYTICAL PRESETS
          </div>
          <div className="flex items-center gap-1 overflow-x-auto pb-1 no-scrollbar">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                className="px-2 py-1 bg-[#F5F4EF] hover:bg-[#111111] hover:text-white text-[#111111] border border-[#111111] rounded-[4px] text-[10px] font-mono font-bold whitespace-nowrap transition-colors shrink-0 cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="p-2.5 bg-white border-t border-[#111111] flex items-center gap-2">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Query store sales, stock, or Khata..."
            className="flex-1 px-3 py-2 bg-[#F5F4EF] rounded-[6px] text-xs font-mono text-[#111111] focus:outline-none border border-[#111111]"
          />
          <button
            onClick={() => handleSend()}
            disabled={!inputQuery.trim()}
            className="px-3 py-2 bg-[#111111] hover:bg-black disabled:opacity-40 text-white rounded-[6px] border border-[#111111] cursor-pointer"
          >
            <Send className="w-3.5 h-3.5 text-[#F4C84A]" />
          </button>
        </div>
      </div>
    </div>
  );
};

export const FloatingAIButton: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-40 flex items-center gap-2 px-4 py-2.5 bg-[#111111] text-white hover:bg-black rounded-[6px] border border-[#111111] shadow-[3px_3px_0_#111111] font-mono font-bold text-xs cursor-pointer hover:translate-x-[-1px] transition-all"
    >
      <span>ASK YOUR STORE</span>
      <ArrowRight className="w-3.5 h-3.5 text-[#F4C84A]" />
    </button>
  );
};
