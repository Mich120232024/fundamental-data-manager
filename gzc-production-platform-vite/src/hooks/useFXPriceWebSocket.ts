import { useEffect, useRef, useState, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';

interface FXPriceData {
  pair: string;
  spot?: {
    bid?: {
      rate: number;
      bank: string;
      timestamp: string;
    };
    ask?: {
      rate: number;
      bank: string;
      timestamp: string;
    };
  };
  forward?: {
    bid?: {
      rate: number;
      bank: string;
      timestamp: string;
      tenor: string;
      amount: number;
    };
    ask?: {
      rate: number;
      bank: string;
      timestamp: string;
      tenor: string;
      amount: number;
    };
  };
  timestamp: string;
}

interface UseFXPriceWebSocketOptions {
  currencyPairs: string[];
  enabled?: boolean;
  token?: string;
  onPriceUpdate?: (prices: { [pair: string]: FXPriceData }) => void;
}

export const useFXPriceWebSocket = ({
  currencyPairs,
  enabled = true,
  token = 'dummy-token', // Will be replaced with real MSAL token
  onPriceUpdate
}: UseFXPriceWebSocketOptions) => {
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [prices, setPrices] = useState<{ [pair: string]: FXPriceData }>({});
  const [error, setError] = useState<string | null>(null);

  const connect = useCallback(() => {
    if (!enabled || socketRef.current?.connected) return;

    try {
      // Connect to WebSocket with authentication  
      // For now, connect to main HTTP API until WebSocket is ready
      const socket = io('ws://localhost:8001/ws', {
        auth: {
          token
        },
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });

      socketRef.current = socket;

      // Connection events
      socket.on('connect', () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        
        // Subscribe to FX prices
        if (currencyPairs.length > 0) {
          socket.emit('subscribe_fx_prices', {
            pairs: currencyPairs
          });
        }
      });

      socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      });

      socket.on('error', (error: any) => {
        console.error('WebSocket error:', error);
        setError(error.message || 'WebSocket error');
      });

      // FX price events
      socket.on('fx_prices_subscribed', (data: any) => {
        console.log('Subscribed to FX prices:', data);
      });

      socket.on('fx_prices_initial', (data: any) => {
        console.log('Initial FX prices:', data);
        if (data.prices) {
          setPrices(data.prices);
          onPriceUpdate?.(data.prices);
        }
      });

      socket.on('fx_price_update', (data: any) => {
        if (data.pair && data.data) {
          setPrices(prev => ({
            ...prev,
            [data.pair]: data.data
          }));
          
          onPriceUpdate?.({
            ...prices,
            [data.pair]: data.data
          });
        }
      });

    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
      setError('Failed to connect to price feed');
    }
  }, [enabled, token, currencyPairs, onPriceUpdate]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.emit('unsubscribe_fx_prices');
      socketRef.current.disconnect();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const updateSubscription = useCallback((newPairs: string[]) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('subscribe_fx_prices', {
        pairs: newPairs
      });
    }
  }, []);

  // Connect on mount and handle cleanup
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Update subscription when currency pairs change
  useEffect(() => {
    if (isConnected && currencyPairs.length > 0) {
      updateSubscription(currencyPairs);
    }
  }, [currencyPairs, isConnected, updateSubscription]);

  return {
    prices,
    isConnected,
    error,
    connect,
    disconnect,
    updateSubscription
  };
};