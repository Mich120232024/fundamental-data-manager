import React, { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';

/**
 * AuthBridge - Connects GZC's MSAL authentication with our auth system
 * Preserves ALL GZC auth logic while syncing with our state
 * The engineer's authentication flow remains completely intact
 */
export const AuthBridge: React.FC<{ 
  children: React.ReactNode,
  msalToken?: string 
}> = ({ children, msalToken }) => {
  const { setToken, setUser } = useAuthStore();

  useEffect(() => {
    // Bridge GZC's MSAL token to our auth system
    if (msalToken) {
      setToken(msalToken);
      // You can decode the token to get user info if needed
      // This is just syncing - GZC's auth logic remains untouched
      console.log('[AuthBridge] Synced MSAL token to our auth store');
    }
  }, [msalToken, setToken]);

  // All GZC authentication logic continues to work exactly as designed
  return <>{children}</>;
};