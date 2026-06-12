import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

interface User {
  id: number;
  email: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Auto load active user from stored token
  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        // We will fetch list of documents or compliance reports as a test of token validity,
        // or a dedicated /auth/me endpoint if needed.
        // Let's call /documents as a simple validation, or decode token claims.
        // Let's fetch list of conversations, if fails, token is invalid.
        await api.get('/chat/conversations');
        
        // Recover user claims from token payload directly
        const payloadBase64 = token.split('.')[1];
        const payload = JSON.parse(atob(payloadBase64));
        setUser({
          id: payload.user_id,
          username: payload.sub,
          email: payload.email
        });
      } catch (err) {
        logout();
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, [token]);

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const data = await api.post<{ access_token: string }>('/auth/login', formData);
    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
  };

  const register = async (email: string, username: string, password: string) => {
    await api.post('/auth/register', { email, username, password });
    // Auto login after registration
    await login(username, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
