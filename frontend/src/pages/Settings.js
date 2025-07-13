import React, { useState } from 'react';

function Settings() {
  const [hfToken, setHfToken] = useState('');
  const [notifications, setNotifications] = useState(true);
  return (
    <div>
      <h1>Settings</h1>
      <div style={{ background: '#fff', padding: 24, borderRadius: 8, maxWidth: 500 }}>
        <h3>Hugging Face Integration</h3>
        <label>
          Hugging Face Token:
          <input
            type="password"
            value={hfToken}
            onChange={e => setHfToken(e.target.value)}
            style={{ width: '100%', marginTop: 8 }}
            placeholder="Enter your HF token"
          />
        </label>
        <div style={{ margin: '16px 0' }}>
          <button disabled={!hfToken}>Save Token</button>
        </div>
        <h3>Notifications</h3>
        <label>
          <input
            type="checkbox"
            checked={notifications}
            onChange={e => setNotifications(e.target.checked)}
          />
          Enable job completion notifications
        </label>
      </div>
    </div>
  );
}

export default Settings;