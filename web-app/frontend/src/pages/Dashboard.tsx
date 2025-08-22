import React, { useState, useRef } from 'react';
import '../styles/Dashboard.css';
import { convertFiles, convertUrl, cancelConversion } from '../services/api';
import { ConversionResult } from '../types';
import ProgressBar from '../components/ProgressBar';
import PreviewModal from '../components/PreviewModal';
import { useWebSocket } from '../hooks/useWebSocket';

interface StatCardProps {
  icon: string;
  iconGradient: string;
  badge?: {
    text: string;
    color: string;
  };
  value: string | number;
  label: string;
  onClick?: () => void;
}

const StatCard: React.FC<StatCardProps> = ({ icon, iconGradient, badge, value, label, onClick }) => (
  <div className="stat-card" onClick={onClick}>
    <div className="stat-header">
      <div className={`stat-icon ${iconGradient}`}>
        <i className={`fas ${icon}`}></i>
      </div>
      {badge && (
        <span className={`stat-badge ${badge.color}`}>{badge.text}</span>
      )}
    </div>
    <h3 className="stat-value">{value}</h3>
    <p className="stat-label">{label}</p>
  </div>
);

interface ActivityItemProps {
  fileType: 'word' | 'excel' | 'pdf' | 'powerpoint';
  fileName: string;
  details: string;
  time: string;
  size: string;
}

const ActivityItem: React.FC<ActivityItemProps> = ({ fileType, fileName, details, time, size }) => {
  const fileTypeConfig = {
    word: { icon: 'fa-file-word', color: 'blue' },
    excel: { icon: 'fa-file-excel', color: 'green' },
    pdf: { icon: 'fa-file-pdf', color: 'red' },
    powerpoint: { icon: 'fa-file-powerpoint', color: 'orange' }
  };

  const config = fileTypeConfig[fileType];

  return (
    <div className="activity-item">
      <div className="activity-content">
        <div className="activity-icon-wrapper">
          <div className={`activity-icon bg-${config.color}`}>
            <i className={`fas ${config.icon}`}></i>
          </div>
        </div>
        <div className="activity-details">
          <p className="activity-filename">{fileName}</p>
          <p className="activity-info">{details}</p>
        </div>
      </div>
      <div className="activity-meta">
        <p className="activity-time">{time}</p>
        <p className="activity-size">{size}</p>
      </div>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const [aiEnhancement, setAiEnhancement] = useState(false);
  const [conversionMode, setConversionMode] = useState<'normal' | 'ai'>('normal');
  const [selectedAiModel, setSelectedAiModel] = useState('gpt-5');
  const [isDragging, setIsDragging] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [conversionResults, setConversionResults] = useState<ConversionResult[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isConvertingUrl, setIsConvertingUrl] = useState(false);
  const [currentConversionId, setCurrentConversionId] = useState<string | null>(null);
  const [previewContent, setPreviewContent] = useState<{ isOpen: boolean; content: string; fileName: string }>({
    isOpen: false,
    content: '',
    fileName: ''
  });
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // WebSocket for progress updates
  const { isConnected, progressData } = useWebSocket();
  
  // Update current conversion ID when progress data changes
  React.useEffect(() => {
    if (isConverting && Object.keys(progressData).length > 0) {
      const latestId = Object.keys(progressData)[Object.keys(progressData).length - 1];
      if (!currentConversionId || !progressData[currentConversionId]) {
        setCurrentConversionId(latestId);
        console.log('Updated conversion ID from progress data:', latestId);
      }
    }
  }, [progressData, isConverting, currentConversionId]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files ? Array.from(e.target.files) : [];
    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const handleFileConversion = async (files: File[]) => {
    setIsConverting(true);
    console.log('Starting conversion, WebSocket connected:', isConnected);
    console.log('Current progressData at start:', progressData);
    
    // Force WebSocket reconnection if not connected
    if (!isConnected) {
      console.log('WebSocket not connected, reconnecting...');
      // The useWebSocket hook should auto-reconnect
    }
    
    // Store conversion IDs to track progress
    const conversionIds: string[] = [];
    
    try {
      console.log('Converting files:', files.map(f => f.name));
      const results = await convertFiles(files, conversionMode === 'ai');
      console.log('Conversion results:', results);
      console.log('Progress data after conversion:', progressData);
      
      // Extract the first conversion ID from results
      if (results.length > 0 && results[0].id) {
        const convId = results[0].id;
        setCurrentConversionId(convId);
        conversionIds.push(convId);
        console.log('Set conversion ID:', convId);
      }
      
      setConversionResults(prev => [...prev, ...results]);
      
      // 成功メッセージを表示
      const successCount = results.filter(r => r.status === 'completed').length;
      if (successCount > 0) {
        alert(`${successCount}個のファイルが正常に変換されました`);
      }
    } catch (error) {
      console.error('変換エラー:', error);
      alert('ファイルの変換に失敗しました');
    } finally {
      setIsConverting(false);
      setCurrentConversionId(null);
    }
  };

  const handleDropZoneClick = () => {
    if (!isConverting && selectedFiles.length === 0) {
      fileInputRef.current?.click();
    }
  };

  const handleClearFiles = () => {
    setSelectedFiles([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCancelConversion = async () => {
    // Cancel using the current conversion ID if available
    if (currentConversionId) {
      try {
        await cancelConversion(currentConversionId);
        setIsConverting(false);
        setCurrentConversionId(null);
        alert('変換がキャンセルされました');
      } catch (error) {
        console.error('キャンセルエラー:', error);
        alert('キャンセルに失敗しました');
      }
    } else {
      // Fallback to canceling all progress data entries
      const conversionIds = Object.keys(progressData);
      if (conversionIds.length > 0) {
        try {
          for (const id of conversionIds) {
            await cancelConversion(id);
          }
          setIsConverting(false);
          setCurrentConversionId(null);
          alert('変換がキャンセルされました');
        } catch (error) {
          console.error('キャンセルエラー:', error);
          alert('キャンセルに失敗しました');
        }
      }
    }
  };

  const handleConvertFiles = async () => {
    if (selectedFiles.length > 0) {
      await handleFileConversion(selectedFiles);
      handleClearFiles();
    }
  };

  const handlePreview = (content: string, fileName: string) => {
    setPreviewContent({
      isOpen: true,
      content,
      fileName
    });
  };

  const handleClosePreview = () => {
    setPreviewContent({
      isOpen: false,
      content: '',
      fileName: ''
    });
  };

  const handleYoutubeUrlConvert = async () => {
    if (!youtubeUrl.trim()) return;
    
    setIsConvertingUrl(true);
    try {
      console.log('Converting YouTube URL:', youtubeUrl);
      const result = await convertUrl(youtubeUrl, conversionMode === 'ai');
      console.log('YouTube conversion result:', result);
      
      // Track conversion ID for progress
      if (result.id) {
        setCurrentConversionId(result.id);
      }
      
      setConversionResults(prev => [...prev, result]);
      setYoutubeUrl('');
      alert('YouTube URLが正常に変換されました');
    } catch (error) {
      console.error('YouTube URL変換エラー:', error);
      alert('YouTube URLの変換に失敗しました');
    } finally {
      setIsConvertingUrl(false);
      setCurrentConversionId(null);
    }
  };

  return (
    <div className="dashboard">
      {/* Welcome Section */}
      <div className="welcome-section">
        <h2 className="welcome-title">MarkItDown コンバーター</h2>
        <p className="welcome-subtitle">様々なドキュメントをMarkdown形式に変換</p>
      </div>

      {/* App Description */}
      <div className="app-info-section">
        <div className="info-card">
          <h3 className="info-title">
            <i className="fas fa-info-circle"></i> アプリについて
          </h3>
          <p className="info-description">
            このツールは、Word、Excel、PowerPoint、PDF、画像、音声ファイルなど、
            様々な形式のファイルをMarkdown形式に変換できます。
          </p>
          <div className="features-grid">
            <div className="feature-card">
              <i className="fas fa-file-alt feature-icon"></i>
              <h4>通常モード</h4>
              <p>高速で正確な標準変換</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-robot feature-icon"></i>
              <h4>AI変換モード</h4>
              <p>AIによる内容解析と最適化</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-layer-group feature-icon"></i>
              <h4>バッチ処理</h4>
              <p>複数ファイルの一括変換</p>
            </div>
            <div className="feature-card">
              <i className="fab fa-youtube feature-icon"></i>
              <h4>YouTube対応</h4>
              <p>動画情報のMarkdown化</p>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="upload-section">
        <div className="upload-header">
          <h3 className="upload-title">ファイル変換</h3>
          <div className="conversion-mode-selector">
            <button
              className={`mode-btn ${conversionMode === 'normal' ? 'active' : ''}`}
              onClick={() => {
                setConversionMode('normal');
                setAiEnhancement(false);
              }}
            >
              <i className="fas fa-file-alt"></i>
              通常モード
            </button>
            <button
              className={`mode-btn ${conversionMode === 'ai' ? 'active' : ''}`}
              onClick={() => {
                setConversionMode('ai');
                setAiEnhancement(true);
              }}
            >
              <i className="fas fa-robot"></i>
              AI変換モード
            </button>
          </div>
        </div>

        {/* AI Model Selection - Show only when AI mode is selected */}
        {conversionMode === 'ai' && (
          <div className="ai-model-section">
            <label className="ai-model-label">AIモデル選択:</label>
            <select
              value={selectedAiModel}
              onChange={(e) => setSelectedAiModel(e.target.value)}
              className="ai-model-select"
            >
              <option value="gpt-5">GPT-5 (推奨)</option>
              <option value="gpt-5-turbo">GPT-5 Turbo</option>
              <option value="gpt-5-pro">GPT-5 Pro</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="o3">O3</option>
              <option value="o3-mini">O3 Mini</option>
            </select>
          </div>
        )}

        <div
          className={`drop-zone ${isDragging ? 'dragging' : ''} ${isConverting ? 'converting' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleDropZoneClick}
          style={{ cursor: isConverting ? 'wait' : 'pointer' }}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".docx,.doc,.xlsx,.xls,.pdf,.pptx,.ppt,.jpg,.jpeg,.png,.gif,.bmp,.webp,.mp3,.wav,.ogg,.m4a,.flac,.csv,.json,.xml,.txt,.zip"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <div className="drop-zone-content">
            {selectedFiles.length === 0 && !isConverting ? (
              <>
                <div className="drop-zone-icon">
                  <i className="fas fa-cloud-upload-alt"></i>
                </div>
                <p className="drop-zone-text">
                  ファイルをドロップまたはクリックして選択
                </p>
                <p className="drop-zone-hint">
                  対応形式: DOC/DOCX, XLS/XLSX, PDF, PPT/PPTX, 画像, 音声, CSV, JSON, XML, ZIP • 最大 10MB
                </p>
              </>
            ) : isConverting ? (
              <div className="progress-section">
                {/* Show only one progress bar based on current conversion */}
                {currentConversionId && progressData[currentConversionId] ? (
                  <ProgressBar
                    progress={progressData[currentConversionId].progress || 0}
                    status={progressData[currentConversionId].status}
                    fileName={progressData[currentConversionId].file_name}
                    currentStep={progressData[currentConversionId].current_step}
                  />
                ) : (
                  <ProgressBar
                    progress={0}
                    status="processing"
                    fileName={selectedFiles.length > 0 ? selectedFiles[0].name : "ファイル"}
                    currentStep="変換処理を開始中..."
                  />
                )}
                {/* Cancel button during conversion */}
                <button 
                  className="btn btn-danger cancel-btn" 
                  onClick={handleCancelConversion}
                >
                  <i className="fas fa-stop-circle"></i> キャンセル
                </button>
              </div>
            ) : (
              <div className="selected-files-container">
                <div className="selected-files-list">
                  <p className="selected-files-title">選択されたファイル ({selectedFiles.length})</p>
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="selected-file-item">
                      <i className="fas fa-file"></i>
                      <span className="selected-file-name">{file.name}</span>
                      <span className="selected-file-size">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Action Buttons */}
        {selectedFiles.length > 0 && !isConverting && (
          <div className="action-buttons">
            <button 
              className="btn btn-secondary" 
              onClick={handleClearFiles}
            >
              <i className="fas fa-times"></i> クリア
            </button>
            <button 
              className="btn btn-primary" 
              onClick={handleConvertFiles}
            >
              <i className="fas fa-exchange-alt"></i> 変換開始
            </button>
          </div>
        )}
      </div>

      {/* YouTube URL Section */}
      <div className="youtube-section">
        <div className="youtube-header">
          <h3 className="youtube-title">
            <i className="fab fa-youtube" style={{ color: '#FF0000', marginRight: '8px' }}></i>
            YouTube URL変換
          </h3>
        </div>
        <div className="youtube-input-container">
          <input
            type="text"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="YouTube URLを入力してください（例: https://www.youtube.com/watch?v=...）"
            className="youtube-url-input"
            disabled={isConvertingUrl}
          />
          <button
            className="btn btn-youtube"
            onClick={handleYoutubeUrlConvert}
            disabled={!youtubeUrl.trim() || isConvertingUrl}
          >
            {isConvertingUrl ? (
              <>
                <i className="fas fa-spinner fa-spin"></i> 変換中...
              </>
            ) : (
              <>
                <i className="fas fa-exchange-alt"></i> URLを変換
              </>
            )}
          </button>
        </div>
        <p className="youtube-hint">
          YouTube動画のURLから動画情報とサムネイルを含むMarkdownファイルを生成します
        </p>
      </div>

      {/* Recent Activity */}
      <div className="activity-section">
        <div className="activity-header">
          <h3 className="activity-title">最近のアクティビティ</h3>
          <a href="#" className="activity-link">すべて表示 →</a>
        </div>
        <div className="activity-list">
          <ActivityItem
            fileType="word"
            fileName="Annual Report 2024.docx"
            details="Markdownに変換済み • AI強化"
            time="2分前"
            size="245 KB"
          />
          <ActivityItem
            fileType="excel"
            fileName="Sales Data Q4.xlsx"
            details="Markdownに変換済み • 標準"
            time="15分前"
            size="189 KB"
          />
          <ActivityItem
            fileType="pdf"
            fileName="Contract Final.pdf"
            details="Markdownに変換済み • AI強化"
            time="1時間前"
            size="567 KB"
          />
        </div>
      </div>

      {/* Conversion Results */}
      {conversionResults.length > 0 && (
        <div className="conversion-results-section">
          <h3 className="results-title">変換結果</h3>
          <div className="results-grid">
            {conversionResults.map((result, index) => (
              <div key={index} className={`result-card ${result.status}`}>
                <div className="result-status">
                  <i className={`fas ${result.status === 'completed' ? 'fa-check-circle' : 'fa-times-circle'}`}></i>
                </div>
                <p className="result-filename">{result.input_file}</p>
                {result.status === 'completed' && result.markdown_content && (
                  <>
                    <div className="markdown-preview">
                      <pre>{result.markdown_content.substring(0, 200)}...</pre>
                    </div>
                    <p className="result-info">
                      処理時間: {result.processing_time?.toFixed(2)}秒 | 
                      文字数: {result.markdown_content.length}
                    </p>
                  </>
                )}
                {result.status === 'completed' && result.output_file && (
                  <div className="result-actions">
                    <button
                      onClick={() => handlePreview(result.markdown_content || '', result.output_file || result.input_file)}
                      className="preview-link"
                    >
                      <i className="fas fa-eye"></i> プレビュー
                    </button>
                    <a
                      href={`http://localhost:8000/api/v1/conversion/download/${result.output_file}`}
                      download={result.output_file}
                      className="download-link"
                    >
                      <i className="fas fa-download"></i> ダウンロード
                    </a>
                  </div>
                )}
                {result.status === 'failed' && result.error_message && (
                  <p className="error-message">{result.error_message}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Floating Action Button - QuickUpload */}
      <button className="fab quick-upload" onClick={handleDropZoneClick} title="QuickUpload">
        <i className="fas fa-upload"></i>
        <span className="fab-label">QuickUpload</span>
      </button>

      {/* Preview Modal */}
      <PreviewModal
        isOpen={previewContent.isOpen}
        onClose={handleClosePreview}
        content={previewContent.content}
        fileName={previewContent.fileName}
      />
    </div>
  );
};

export default Dashboard;