import React from 'react';
import './ConversionResults.css';
import { ConversionResult } from '../types';
import { downloadFile } from '../services/api';

interface ConversionResultsProps {
  results: ConversionResult[];
}

const ConversionResults: React.FC<ConversionResultsProps> = ({ results }) => {
  const handleDownload = async (filename: string) => {
    try {
      const blob = await downloadFile(filename);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('ダウンロードエラー:', error);
      alert('ファイルのダウンロードに失敗しました');
    }
  };

  const getStatusIcon = (status: ConversionResult['status']) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      case 'processing':
        return '⏳';
      default:
        return '⏸️';
    }
  };

  const getStatusText = (status: ConversionResult['status']) => {
    switch (status) {
      case 'completed':
        return '完了';
      case 'failed':
        return '失敗';
      case 'processing':
        return '処理中';
      default:
        return '待機中';
    }
  };

  return (
    <div className="conversion-results">
      <h2>変換結果</h2>
      <div className="results-summary">
        <p>
          総ファイル数: {results.length} | 
          成功: {results.filter(r => r.status === 'completed').length} | 
          失敗: {results.filter(r => r.status === 'failed').length}
        </p>
      </div>
      <div className="results-list">
        {results.map((result) => (
          <div key={result.id} className={`result-item ${result.status}`}>
            <div className="result-info">
              <span className="status-icon">{getStatusIcon(result.status)}</span>
              <div className="file-info">
                <span className="filename">{result.input_file}</span>
                <span className="status-text">{getStatusText(result.status)}</span>
                {result.processing_time && (
                  <span className="processing-time">
                    処理時間: {result.processing_time.toFixed(2)}秒
                  </span>
                )}
              </div>
            </div>
            {result.status === 'completed' && result.output_file && (
              <button
                className="download-button"
                onClick={() => handleDownload(result.output_file!)}
              >
                ダウンロード
              </button>
            )}
            {result.status === 'failed' && result.error_message && (
              <div className="error-message">{result.error_message}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversionResults;