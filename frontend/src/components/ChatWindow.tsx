import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { MessageSquare, Send, Plus, Trash2, BookOpen, AlertTriangle, FileText, ChevronDown, ChevronUp } from 'lucide-react';

interface Source {
  score: number;
  content: string;
  filename: string;
  chunk_index: number;
}

interface Message {
  id: number;
  sender: 'user' | 'bot';
  content: string;
  sources?: string; // JSON encoded string list of Source
  timestamp: string;
}

interface Conversation {
  id: number;
  title: string;
  created_at: string;
}

interface ChatWindowProps {
  onRefreshStats: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ onRefreshStats }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [expandedSources, setExpandedSources] = useState<Record<number, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const fetchConversations = async () => {
    try {
      const data = await api.get<Conversation[]>('/chat/conversations');
      setConversations(data);
      if (data.length > 0 && activeConvId === null) {
        setActiveConvId(data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadMessages = async (id: number) => {
    try {
      const data = await api.get<{ messages: Message[] }>(`/chat/conversations/${id}`);
      setMessages(data.messages);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateChat = async () => {
    try {
      const chat = await api.post<Conversation>('/chat/conversations', { title: "Nouvelle discussion" });
      setConversations(prev => [chat, ...prev]);
      setActiveConvId(chat.id);
      onRefreshStats();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteChat = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Voulez-vous supprimer cette discussion ?')) return;
    try {
      await api.delete(`/chat/conversations/${id}`);
      setConversations(prev => prev.filter(c => c.id !== id));
      if (activeConvId === id) {
        setActiveConvId(null);
      }
      onRefreshStats();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || activeConvId === null || loading) return;

    const userText = inputText;
    setInputText('');
    setLoading(true);
    
    // Optimistic user update
    const tempUserMsg: Message = {
      id: Date.now(),
      sender: 'user',
      content: userText,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const botMsg = await api.post<Message>(`/chat/conversations/${activeConvId}/messages`, { content: userText });
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id).concat(tempUserMsg, botMsg));
      // Refresh list to update title
      fetchConversations();
    } catch (err: any) {
      console.error(err.message || 'Échec d\'envoi.');
    } finally {
      setLoading(false);
    }
  };

  const toggleSources = (msgId: number) => {
    setExpandedSources(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex overflow-hidden border border-slate-100 dark:border-slate-700/50 rounded-2xl bg-white dark:bg-slate-800 shadow-sm animate-fade-in">
      
      {/* Chats Sidebar */}
      <div className="w-64 border-r border-slate-100 dark:border-slate-700 flex flex-col bg-slate-50/50 dark:bg-slate-900/10 shrink-0">
        <div className="p-4 border-b border-slate-100 dark:border-slate-700">
          <button
            onClick={handleCreateChat}
            className="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium text-sm flex items-center justify-center space-x-2 transition"
          >
            <Plus className="h-4 w-4" />
            <span>Nouveau chat</span>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map(conv => (
            <div
              key={conv.id}
              onClick={() => setActiveConvId(conv.id)}
              className={`p-3 rounded-lg cursor-pointer flex items-center justify-between group transition ${
                activeConvId === conv.id
                  ? 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-medium'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/30'
              }`}
            >
              <div className="flex items-center space-x-2.5 truncate">
                <MessageSquare className="h-4.5 w-4.5 shrink-0" />
                <span className="truncate text-sm">{conv.title}</span>
              </div>
              <button
                onClick={(e) => handleDeleteChat(conv.id, e)}
                className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-opacity p-0.5"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Main Conversation Pane */}
      <div className="flex-1 flex flex-col bg-white dark:bg-slate-800">
        {activeConvId === null ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500 dark:text-slate-400">
            <MessageSquare className="h-16 w-16 text-slate-200 dark:text-slate-700 mb-3" />
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">Assistant Réglementaire</h3>
            <p className="max-w-xs text-sm mt-1 text-slate-400">
              Créez une discussion dans la barre latérale pour interroger l'IA sur la conformité textile.
            </p>
          </div>
        ) : (
          <>
            {/* Conversation Headers */}
            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center">
              <h3 className="font-bold text-slate-900 dark:text-white truncate">
                {conversations.find(c => c.id === activeConvId)?.title || 'Discussion'}
              </h3>
            </div>

            {/* Messages Lists */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map(msg => {
                const isBot = msg.sender === 'bot';
                // Try parsing sources
                let sourcesList: Source[] = [];
                if (isBot && msg.sources) {
                  try {
                    sourcesList = JSON.parse(msg.sources);
                  } catch (_) {}
                }
                const isOutOfScope = isBot && msg.content.includes("Je suis un assistant spécialisé uniquement");

                return (
                  <div key={msg.id} className={`flex ${isBot ? 'justify-start' : 'justify-end'}`}>
                    <div className={`max-w-2xl rounded-2xl p-4 text-sm shadow-sm space-y-2 ${
                      isBot
                        ? isOutOfScope
                          ? 'bg-amber-500/10 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300'
                          : 'bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200'
                        : 'bg-indigo-600 text-white'
                    }`}>
                      <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>

                      {/* Out of scope warning */}
                      {isOutOfScope && (
                        <div className="flex items-center space-x-1.5 text-xs text-amber-600 dark:text-amber-400 font-medium pt-1">
                          <AlertTriangle className="h-4 w-4" />
                          <span>Filtre de domaine actif</span>
                        </div>
                      )}

                      {/* Source citing panel */}
                      {sourcesList.length > 0 && (
                        <div className="border-t border-slate-200 dark:border-slate-800 mt-3 pt-2">
                          <button
                            onClick={() => toggleSources(msg.id)}
                            className="flex items-center space-x-1 text-xs text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
                          >
                            <BookOpen className="h-3.5 w-3.5" />
                            <span>Sources utilisées ({sourcesList.length})</span>
                            {expandedSources[msg.id] ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                          </button>

                          {expandedSources[msg.id] && (
                            <div className="mt-2 space-y-2 max-h-48 overflow-y-auto pr-1 animate-scale-up">
                              {sourcesList.map((src, i) => (
                                <div key={i} className="p-2.5 bg-white dark:bg-slate-800 border border-slate-200/50 dark:border-slate-700/50 rounded-lg text-xs space-y-1">
                                  <div className="flex items-center justify-between text-slate-400 font-medium">
                                    <span className="flex items-center space-x-1">
                                      <FileText className="h-3.5 w-3.5" />
                                      <span className="truncate max-w-xs">{src.filename} (Chunk {src.chunk_index})</span>
                                    </span>
                                    <span>Confiance: {(src.score * 100).toFixed(0)}%</span>
                                  </div>
                                  <p className="text-slate-500 dark:text-slate-400 italic">"{src.content}"</p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form Box */}
            <div className="p-4 border-t border-slate-100 dark:border-slate-700">
              <form onSubmit={handleSendMessage} className="flex items-center space-x-3">
                <input
                  type="text" required
                  disabled={loading}
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  placeholder="Posez votre question réglementaire textile..."
                  className="flex-1 px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm disabled:opacity-60"
                />
                <button
                  type="submit" disabled={loading || !inputText.trim()}
                  className="p-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition disabled:opacity-40 shrink-0"
                >
                  <Send className="h-5 w-5" />
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
