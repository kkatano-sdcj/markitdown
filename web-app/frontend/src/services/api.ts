import axios from 'axios';
import { ConversionResult, BatchConversionResult, APISettings, APITestResult } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ファイル変換API
export const convertFiles = async (files: File[], useAiMode: boolean): Promise<ConversionResult[]> => {
  // Check if any file is actually a URL
  const urlFiles = files.filter((file: any) => file.isUrl);
  const regularFiles = files.filter((file: any) => !file.isUrl);
  
  const results: ConversionResult[] = [];
  
  // Convert URLs
  for (const urlFile of urlFiles) {
    const response = await api.post<ConversionResult>(
      useAiMode ? '/api/v1/conversion/convert-youtube-enhanced' : '/api/v1/conversion/convert-url',
      useAiMode
        ? { url: (urlFile as any).url, use_ai_mode: true }
        : { url: (urlFile as any).url, use_api_enhancement: false }
    );
    results.push(response.data);
  }
  
  // Convert regular files
  if (regularFiles.length > 0) {
    // Use standard upload endpoint with AI mode parameter
    if (regularFiles.length === 1) {
      // Single file upload
      const formData = new FormData();
      formData.append('file', regularFiles[0]);
      
      const response = await api.post<ConversionResult>(
        `/api/v1/conversion/upload?use_ai_mode=${useAiMode}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      results.push(response.data);
    } else {
      // Batch upload
      const formData = new FormData();
      regularFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await api.post<BatchConversionResult>(
        `/api/v1/conversion/batch?use_ai_mode=${useAiMode}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      results.push(...response.data.results);
    }
  }

  return results;
};

// URL変換API
export const convertUrl = async (url: string, useAiMode: boolean): Promise<ConversionResult> => {
  const endpoint = useAiMode 
    ? '/api/v1/conversion/convert-youtube-enhanced'
    : '/api/v1/conversion/convert-url';
  
  const params = useAiMode
    ? { url, use_ai_mode: true }
    : { url, use_api_enhancement: false };
  
  const response = await api.post<ConversionResult>(endpoint, params);
  return response.data;
};

// ファイルダウンロード
export const downloadFile = async (filename: string): Promise<Blob> => {
  const response = await api.get(`/api/v1/conversion/download/${filename}`, {
    responseType: 'blob',
  });
  return response.data;
};

// サポートされているファイル形式を取得
export const getSupportedFormats = async (): Promise<string[]> => {
  const response = await api.get<{ formats: string[] }>('/api/v1/conversion/supported-formats');
  return response.data.formats;
};

// API設定を取得
export const getAPISettings = async (): Promise<APISettings> => {
  const response = await api.get<APISettings>('/api/v1/settings/api');
  return response.data;
};

// APIキーを設定
export const configureAPI = async (apiKey: string): Promise<APISettings> => {
  const response = await api.post<APISettings>('/api/v1/settings/api/configure', {
    api_key: apiKey,
  });
  return response.data;
};

// API接続をテスト
export const testAPIConnection = async (apiKey: string): Promise<APITestResult> => {
  const response = await api.post<APITestResult>('/api/v1/settings/api/test', {
    api_key: apiKey,
  });
  return response.data;
};

// 変換をキャンセル
export const cancelConversion = async (conversionId: string): Promise<{ success: boolean; message: string }> => {
  const response = await api.post<{ success: boolean; message: string }>(`/api/v1/conversion/cancel/${conversionId}`);
  return response.data;
};