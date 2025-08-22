import React from 'react';
import '../styles/Settings.css';

const Settings: React.FC = () => {

  const handleSaveChanges = () => {
    // Save settings logic
    console.log('Saving changes...');
  };

  return (
    <div className="settings">
      {/* Header */}
      <div className="settings-header">
        <h2 className="settings-page-title">プロフィール設定</h2>
        <p className="settings-page-subtitle">ユーザー情報と環境設定を管理</p>
      </div>

      {/* Settings Content */}
        <div className="settings-content">
          {/* User Profile */}
          <div className="settings-card">
            <div className="card-header">
              <div>
                <h3 className="card-title">ユーザープロフィール</h3>
                <p className="card-description">アカウント情報とプリファレンスを管理</p>
              </div>
            </div>

            <div className="card-content">
              {/* Profile Picture */}
              <div className="profile-section">
                <div className="profile-picture-container">
                  <div className="profile-picture">
                    <i className="fas fa-user"></i>
                  </div>
                  <button className="btn btn-outline">
                    <i className="fas fa-camera"></i>
                    画像を変更
                  </button>
                </div>
              </div>

              {/* User Information */}
              <div className="form-group">
                <label className="form-label">ユーザー名</label>
                <input
                  type="text"
                  className="form-input"
                  defaultValue="user_123"
                  placeholder="ユーザー名を入力"
                />
              </div>

              <div className="form-group">
                <label className="form-label">メールアドレス</label>
                <input
                  type="email"
                  className="form-input"
                  defaultValue="user@example.com"
                  placeholder="メールアドレスを入力"
                />
              </div>

              <div className="form-group">
                <label className="form-label">表示名</label>
                <input
                  type="text"
                  className="form-input"
                  defaultValue="変換太郎"
                  placeholder="表示名を入力"
                />
              </div>

              {/* Language Preference */}
              <div className="form-group">
                <label className="form-label">言語設定</label>
                <select className="form-select">
                  <option value="ja">日本語</option>
                  <option value="en">English</option>
                  <option value="zh">中文</option>
                  <option value="ko">한국어</option>
                </select>
              </div>

              {/* Timezone */}
              <div className="form-group">
                <label className="form-label">タイムゾーン</label>
                <select className="form-select">
                  <option value="Asia/Tokyo">東京 (GMT+9)</option>
                  <option value="Asia/Seoul">ソウル (GMT+9)</option>
                  <option value="Asia/Shanghai">上海 (GMT+8)</option>
                  <option value="America/New_York">ニューヨーク (GMT-5)</option>
                  <option value="Europe/London">ロンドン (GMT+0)</option>
                </select>
              </div>

              {/* Save Button */}
              <div className="action-buttons">
                <button className="btn btn-primary" onClick={handleSaveChanges}>
                  <i className="fas fa-save"></i>
                  変更を保存
                </button>
              </div>
            </div>
          </div>

          {/* Preferences */}
          <div className="settings-card">
            <div className="card-header">
              <div>
                <h3 className="card-title">環境設定</h3>
                <p className="card-description">アプリケーションの動作設定</p>
              </div>
            </div>

            <div className="card-content">
              {/* Theme Selection */}
              <div className="form-group">
                <label className="form-label">テーマ</label>
                <div className="theme-selector">
                  <button className="theme-option active">
                    <i className="fas fa-sun"></i>
                    ライト
                  </button>
                  <button className="theme-option">
                    <i className="fas fa-moon"></i>
                    ダーク
                  </button>
                  <button className="theme-option">
                    <i className="fas fa-desktop"></i>
                    システム
                  </button>
                </div>
              </div>

              {/* Auto Save */}
              <div className="toggle-option">
                <div className="toggle-info">
                  <h4 className="toggle-title">自動保存</h4>
                  <p className="toggle-description">変換結果を自動的に保存</p>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>

              {/* Show Preview */}
              <div className="toggle-option">
                <div className="toggle-info">
                  <h4 className="toggle-title">プレビュー表示</h4>
                  <p className="toggle-description">変換後に自動的にプレビューを表示</p>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>

              {/* Keep Original Files */}
              <div className="toggle-option">
                <div className="toggle-info">
                  <h4 className="toggle-title">オリジナルファイルを保持</h4>
                  <p className="toggle-description">変換後も元のファイルを保持</p>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>

          {/* Account Actions */}
          <div className="settings-card">
            <div className="card-header">
              <div>
                <h3 className="card-title">アカウント管理</h3>
                <p className="card-description">アカウントのエクスポートと削除</p>
              </div>
            </div>

            <div className="card-content">
              <div className="account-actions">
                <button className="btn btn-outline">
                  <i className="fas fa-download"></i>
                  データをエクスポート
                </button>
                <button className="btn btn-outline-danger">
                  <i className="fas fa-trash"></i>
                  アカウントを削除
                </button>
              </div>
            </div>
          </div>
        </div>

      {/* Success Toast (Hidden by default) */}
      <div className="toast toast-success" style={{ display: 'none' }}>
        <i className="fas fa-check-circle"></i>
        <span>設定が正常に保存されました！</span>
      </div>
    </div>
  );
};

export default Settings;