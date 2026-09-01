import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { authService } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const savedUser = localStorage.getItem('soar_user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('soar_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      const savedToken = localStorage.getItem('soar_token');
      if (savedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          localStorage.setItem('soar_user', JSON.stringify(userData));
        } catch (err) {
          localStorage.removeItem('soar_token');
          localStorage.removeItem('soar_user');
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    const data = await authService.login({ username, password });
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('soar_token', data.access_token);
    localStorage.setItem('soar_user', JSON.stringify(data.user));
  };

  const logout = () => {
    localStorage.removeItem('soar_token');
    localStorage.removeItem('soar_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
