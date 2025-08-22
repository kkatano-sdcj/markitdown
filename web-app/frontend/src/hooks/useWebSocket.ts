import { useEffect, useRef, useState, useCallback } from 'react';

interface ProgressData {
  type: 'progress' | 'batch_progress' | 'completion';
  conversion_id?: string;
  batch_id?: string;
  progress?: number;
  status?: 'processing' | 'completed' | 'error';
  current_step?: string;
  file_name?: string;
  files?: Record<string, any>;
  success?: boolean;
  error_message?: string;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  progressData: Record<string, ProgressData>;
  connect: () => void;
  disconnect: () => void;
  clearProgress: (id: string) => void;
}

export const useWebSocket = (url: string = 'ws://localhost:8000/ws'): UseWebSocketReturn => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [progressData, setProgressData] = useState<Record<string, ProgressData>>({});

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(url);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        
        // Send ping to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          } else {
            clearInterval(pingInterval);
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          // Handle pong response
          if (event.data === 'pong') {
            return;
          }
          
          const data: ProgressData = JSON.parse(event.data);
          console.log('WebSocket message received:', data);
          
          if (data.type === 'progress' && data.conversion_id) {
            setProgressData(prev => {
              // Clear other conversions and keep only current one
              if (data.progress === 0) {
                // Starting new conversion, clear all others
                return {
                  [data.conversion_id!]: data
                };
              }
              return {
                ...prev,
                [data.conversion_id!]: data
              };
            });
          } else if (data.type === 'batch_progress' && data.batch_id) {
            setProgressData(prev => ({
              ...prev,
              [data.batch_id!]: data
            }));
          } else if (data.type === 'completion' && data.conversion_id) {
            setProgressData(prev => ({
              ...prev,
              [data.conversion_id!]: {
                ...prev[data.conversion_id!],
                ...data,
                progress: 100,
                status: data.success ? 'completed' : 'error'
              }
            }));
            
            // Auto-clear completed progress after 5 seconds
            setTimeout(() => {
              clearProgress(data.conversion_id!);
            }, 5000);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error, event.data);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setIsConnected(false);
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const clearProgress = useCallback((id: string) => {
    setProgressData(prev => {
      const newData = { ...prev };
      delete newData[id];
      return newData;
    });
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    progressData,
    connect,
    disconnect,
    clearProgress
  };
};