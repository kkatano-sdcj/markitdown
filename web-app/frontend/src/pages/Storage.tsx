import React, { useState } from 'react';
import '../styles/Storage.css';

interface FileItem {
  id: string;
  name: string;
  type: 'word' | 'excel' | 'pdf' | 'powerpoint' | 'folder';
  size: string;
  convertedFrom?: string;
  enhancement?: 'AI強化' | '標準';
  time: string;
  selected: boolean;
}

interface FileItemComponentProps {
  file: FileItem;
  onToggleSelect: (id: string) => void;
}

const FileItemComponent: React.FC<FileItemComponentProps> = ({ file, onToggleSelect }) => {
  const fileTypeConfig = {
    word: { icon: 'fa-file-word', colorClass: 'file-icon-blue' },
    excel: { icon: 'fa-file-excel', colorClass: 'file-icon-green' },
    pdf: { icon: 'fa-file-pdf', colorClass: 'file-icon-red' },
    powerpoint: { icon: 'fa-file-powerpoint', colorClass: 'file-icon-orange' },
    folder: { icon: 'fa-folder', colorClass: 'file-icon-yellow' }
  };

  const config = fileTypeConfig[file.type];

  return (
    <div className="file-item">
      <div className="file-content">
        <input
          type="checkbox"
          className="file-checkbox"
          checked={file.selected}
          onChange={() => onToggleSelect(file.id)}
        />
        <div className={`file-icon ${config.colorClass}`}>
          <i className={`fas ${config.icon}`}></i>
        </div>
        <div className="file-details">
          <div className="file-name-row">
            <p className="file-name">{file.name}</p>
            {file.enhancement && (
              <span className={`file-badge ${file.enhancement === 'AI強化' ? 'badge-ai' : 'badge-standard'}`}>
                {file.enhancement}
              </span>
            )}
          </div>
          <p className="file-info">
            {file.convertedFrom ? `${file.convertedFrom}から変換 • ` : ''}
            {file.size} • {file.time}
          </p>
        </div>
      </div>
      <div className="file-actions">
        {file.type === 'folder' ? (
          <button className="action-btn">
            <i className="fas fa-folder-open"></i>
          </button>
        ) : (
          <>
            <button className="action-btn">
              <i className="fas fa-download"></i>
            </button>
            <button className="action-btn">
              <i className="fas fa-eye"></i>
            </button>
          </>
        )}
        <button className="action-btn">
          <i className="fas fa-share"></i>
        </button>
        <button className="action-btn action-btn-danger">
          <i className="fas fa-trash"></i>
        </button>
      </div>
    </div>
  );
};

const Storage: React.FC = () => {
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [searchQuery, setSearchQuery] = useState('');
  const [files, setFiles] = useState<FileItem[]>([
    {
      id: '1',
      name: 'Annual Report 2024.md',
      type: 'word',
      size: '245 KB',
      convertedFrom: 'DOCX',
      enhancement: 'AI強化',
      time: '2分前',
      selected: false
    },
    {
      id: '2',
      name: 'Sales Data Q4.md',
      type: 'excel',
      size: '189 KB',
      convertedFrom: 'XLSX',
      enhancement: '標準',
      time: '15分前',
      selected: false
    },
    {
      id: '3',
      name: 'Project Documents',
      type: 'folder',
      size: '1.2 GB',
      time: '昨日更新',
      selected: false
    },
    {
      id: '4',
      name: 'Contract Final.md',
      type: 'pdf',
      size: '567 KB',
      convertedFrom: 'PDF',
      enhancement: 'AI強化',
      time: '1時間前',
      selected: false
    }
  ]);

  const toggleFileSelection = (id: string) => {
    setFiles(files.map(file => 
      file.id === id ? { ...file, selected: !file.selected } : file
    ));
  };

  const selectedCount = files.filter(f => f.selected).length;
  const storageUsed = 2.4;
  const storageTotal = 10;
  const storagePercentage = (storageUsed / storageTotal) * 100;

  return (
    <div className="storage">
      {/* Storage Overview */}
      <div className="storage-overview">
        <h3 className="storage-title">ストレージ概要</h3>
        <div className="document-total-container">
          <div className="document-total">
            <i className="fas fa-file-alt total-icon"></i>
            <div className="total-info">
              <p className="total-count">1,680</p>
              <p className="total-label">変換ドキュメント総数</p>
            </div>
          </div>
        </div>
      </div>

      {/* File Explorer */}
      <div className="file-explorer">
        {/* Toolbar */}
        <div className="explorer-toolbar">
          <div className="toolbar-left">
            <h3 className="explorer-title">ファイル</h3>
            <div className="view-mode-toggle">
              <button
                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode('list')}
              >
                <i className="fas fa-list"></i>
              </button>
              <button
                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode('grid')}
              >
                <i className="fas fa-th-large"></i>
              </button>
            </div>
          </div>
          
          <div className="toolbar-right">
            <div className="search-box">
              <i className="fas fa-search search-icon"></i>
              <input
                type="text"
                placeholder="ファイルを検索..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
            <button className="filter-btn">
              <i className="fas fa-filter"></i>
              フィルター
            </button>
          </div>
        </div>

        {/* File List */}
        <div className="file-list">
          {files.map(file => (
            <FileItemComponent
              key={file.id}
              file={file}
              onToggleSelect={toggleFileSelection}
            />
          ))}
        </div>

        {/* Footer Actions */}
        {selectedCount > 0 && (
          <div className="explorer-footer">
            <div className="footer-left">
              <p className="selected-count">{selectedCount} 件選択中</p>
              <button className="footer-btn btn-danger">
                <i className="fas fa-trash"></i>
                削除
              </button>
              <button className="footer-btn btn-primary">
                <i className="fas fa-download"></i>
                ダウンロード
              </button>
            </div>
            <div className="pagination">
              <button className="page-btn">
                <i className="fas fa-chevron-left"></i>
              </button>
              <button className="page-btn active">1</button>
              <button className="page-btn">2</button>
              <button className="page-btn">3</button>
              <button className="page-btn">
                <i className="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default Storage;