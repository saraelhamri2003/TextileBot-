import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { ChatWindow } from './components/ChatWindow';
import { DocumentManager } from './components/DocumentManager';
import { ComplianceAnalyzer } from './components/ComplianceAnalyzer';
import { api } from './services/api';
import { Sparkles, Loader2, Lock, Mail, User } from 'lucide-react';

const MainApp: React.FC = () => {
  const { token, loading, login, register } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Registration and Authentication toggles
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState(false);

  // App metrics
  const [stats, setStats] = useState({
    docsCount: 0,
    reportsCount: 0,
    convsCount: 0,
    compliantCount: 0
  });

  const fetchStats = async () => {
    if (!token) return;
    try {
      const [docs, reports, convs] = await Promise.all([
        api.get<any[]>('/documents/'),
        api.get<any[]>('/compliance/reports'),
        api.get<any[]>('/chat/conversations')
      ]);
      setStats({
        docsCount: docs.length,
        reportsCount: reports.length,
        convsCount: convs.length,
        compliantCount: reports.filter(r => r.status === 'compliant').length
      });
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (token) {
      fetchStats();
    }
  }, [token]);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthLoading(true);
    try {
      if (isRegister) {
        await register(email, username, password);
      } else {
        await login(username, password);
      }
    } catch (err: any) {
      setAuthError(err.message || "Erreur d'authentification");
    } finally {
      setAuthLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-slate-900 text-white flex-col space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-indigo-500" />
        <span className="text-sm font-medium">TextilBot démarre...</span>
      </div>
    );
  }

  // Login Screen
  if (!token) {
    return (
      <div className="min-h-full flex items-center justify-center bg-slate-900 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-xl">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg">
              <Sparkles className="h-6 w-6" />
            </div>
            <h2 className="mt-6 text-3xl font-extrabold text-white">TextilBot Compliance</h2>
            <p className="mt-2 text-sm text-slate-400">
              {isRegister ? 'Créez votre compte professionnel' : 'Accédez à votre assistant réglementaire textile'}
            </p>
          </div>
          
          <form className="mt-8 space-y-6" onSubmit={handleAuthSubmit}>
            {authError && (
              <div className="p-3 bg-red-500/10 border border-red-500 rounded-lg text-sm text-red-400 text-center">
                {authError}
              </div>
            )}
            
            <div className="rounded-md shadow-sm -space-y-px space-y-4">
              {isRegister && (
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
                  <input
                    type="email" required
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="Adresse email"
                    className="w-full pl-10 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}
              
              <div className="relative">
                <User className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
                <input
                  type="text" required
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  placeholder="Nom d'utilisateur"
                  className="w-full pl-10 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="relative">
                <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-500" />
                <input
                  type="password" required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Mot de passe"
                  className="w-full pl-10 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <button
                type="submit" disabled={authLoading}
                className="group relative w-full flex justify-center py-2.5 px-4 border border-transparent text-sm font-semibold rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {authLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : isRegister ? (
                  "S'enregistrer"
                ) : (
                  "Se connecter"
                )}
              </button>
            </div>
          </form>

          <div className="text-center">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setAuthError(null);
              }}
              className="text-sm text-indigo-400 hover:text-indigo-300"
            >
              {isRegister ? "Déjà un compte ? Connectez-vous" : "Pas de compte ? Inscrivez-vous"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Authenticated Layout
  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {activeTab === 'dashboard' && <Dashboard stats={stats} onNavigate={setActiveTab} />}
      {activeTab === 'chat' && <ChatWindow onRefreshStats={fetchStats} />}
      {activeTab === 'documents' && <DocumentManager onRefreshStats={fetchStats} />}
      {activeTab === 'compliance' && <ComplianceAnalyzer onRefreshStats={fetchStats} />}
    </Layout>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainApp />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
