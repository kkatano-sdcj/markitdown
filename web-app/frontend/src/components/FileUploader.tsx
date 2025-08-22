import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import './FileUploader.css';
import { getSupportedFormats } from '../services/api';

interface FileUploaderProps {
  onFilesSelected: (files: File[]) => void;
  isConverting: boolean;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFilesSelected, isConverting }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [supportedFormats, setSupportedFormats] = useState<string[]>([]);
  const [urlInput, setUrlInput] = useState<string>('');
  const [urlMode, setUrlMode] = useState<boolean>(false);

  useEffect(() => {
    // サポートされているファイル形式を取得
    getSupportedFormats().then(setSupportedFormats).catch(console.error);
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setSelectedFiles(acceptedFiles);
    setUrlMode(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: supportedFormats.reduce((acc, format) => {
      acc[`.${format}`] = [];
      return acc;
    }, {} as Record<string, string[]>),
    disabled: isConverting,
  });

  const handleConvert = () => {
    if (selectedFiles.length > 0) {
      onFilesSelected(selectedFiles);
    }
  };

  const handleUrlSubmit = () => {
    if (urlInput.trim()) {
      // Create a pseudo-file for URL
      const urlFile = new File([urlInput], 'url.txt', { type: 'text/plain' });
      (urlFile as any).isUrl = true;
      (urlFile as any).url = urlInput;
      onFilesSelected([urlFile]);
      setUrlInput('');
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  return (
    <div className="file-uploader">
      <div className="upload-tabs">
        <button 
          className={`tab ${!urlMode ? 'active' : ''}`}
          onClick={() => setUrlMode(false)}
        >
          ファイルアップロード
        </button>
        <button 
          className={`tab ${urlMode ? 'active' : ''}`}
          onClick={() => setUrlMode(true)}
        >
          URL変換
        </button>
      </div>

      {!urlMode ? (
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''} ${isConverting ? 'disabled' : ''}`}
        >
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>ファイルをここにドロップしてください...</p>
          ) : (
            <div>
              <p>ファイルをドラッグ＆ドロップ、またはクリックして選択</p>
              <p className="supported-formats">
                対応形式: {supportedFormats.map(f => `.${f}`).join(', ')}
              </p>
              <p className="supported-formats">
                画像・音声・CSV・JSON・XML・ZIPファイルも対応
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="url-input-container">
          <input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="YouTube URLを入力してください"
            className="url-input"
            disabled={isConverting}
          />
          <button
            onClick={handleUrlSubmit}
            disabled={!urlInput.trim() || isConverting}
            className="convert-button"
          >
            URLを変換
          </button>
        </div>
      )}

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <h3>選択されたファイル:</h3>
          <ul>
            {selectedFiles.map((file, index) => (
              <li key={index}>
                <span>{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  disabled={isConverting}
                  className="remove-button"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          <button
            onClick={handleConvert}
            disabled={isConverting}
            className="convert-button"
          >
            {isConverting ? '変換中...' : 'ファイルを変換'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;