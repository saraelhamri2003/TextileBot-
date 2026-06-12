import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { 
  LayoutDashboard, MessageSquare, FileText, CheckSquare, 
  LogOut, Sun, Moon, Sparkles 
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const menuItems = [
    { id: 'dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
    { id: 'chat', label: 'Assistant Chat RAG', icon: MessageSquare },
    { id: 'documents', label: 'Réglementations', icon: FileText },
    { id: 'compliance', label: 'Vérification Produit', icon: CheckSquare },
  ];

  return (
    <div className="w-64 bg-slate-900 text-slate-400 flex flex-col h-full shrink-0 border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 space-x-3">
        <div className="p-2 bg-indigo-600 rounded-lg text-white">
          <Sparkles className="h-5 w-5" />
        </div>
        <span className="font-bold text-white text-lg tracking-wide">TextilBot</span>
      </div>

      {/* Main Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {menuItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive 
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/10' 
                  : 'hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Profile Controls & Theme Toggler */}
      <div className="p-4 border-t border-slate-800 space-y-4">
        {/* Theme Toggler */}
        <button
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-4 py-2 rounded-lg text-sm hover:bg-slate-800 transition"
        >
          <span className="flex items-center space-x-3">
            {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            <span>Mode {theme === 'dark' ? 'Sombre' : 'Clair'}</span>
          </span>
          <div className="w-8 h-4 bg-slate-700 rounded-full relative p-0.5 transition-colors">
            <div className={`w-3 h-3 bg-white rounded-full transition-transform ${theme === 'dark' ? 'translate-x-4' : ''}`} />
          </div>
        </button>

        {/* User Account Info */}
        <div className="flex items-center justify-between px-2">
          <div className="truncate">
            <p className="text-xs font-semibold text-white truncate">{user?.username}</p>
            <p className="text-[10px] text-slate-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 hover:bg-slate-800 rounded-lg text-slate-500 hover:text-red-400 transition"
            title="Se déconnecter"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
