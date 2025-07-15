import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: {
    id: string;
    email: string;
    name: string;
  } | null;
  isAuthenticated: boolean;
  setToken: (token: string | null) => void;
  setUser: (user: AuthState['user']) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        token: null,
        user: null,
        isAuthenticated: false,
        
        setToken: (token) => 
          set({ 
            token, 
            isAuthenticated: !!token 
          }),
        
        setUser: (user) => 
          set({ user }),
        
        logout: () => 
          set({ 
            token: null, 
            user: null, 
            isAuthenticated: false 
          }),
      }),
      {
        name: 'auth-storage',
      }
    )
  )
);