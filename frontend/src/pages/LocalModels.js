import React, { useState } from 'react';

const mockLocalModels = [
  { id: 'llama-3b-20240601', name: 'Llama-3B', savedAt: '2024-06-01T12:00:00Z', size: '1.2GB' },
  { id: 'qwen-4b-20240530', name: 'Qwen-4B', savedAt: '2024-05-30T16:00:00Z', size: '1.8GB' },
];

function LocalModels() {
  const [models, setModels] = useState(mockLocalModels);
  const handleDelete = (id) => setModels(models.filter(m => m.id !== id));
  return (
    <div>
      <h1>Local Models</h1>
      <table style={{ width: '100%', background: '#fff', borderRadius: 8, boxShadow: '0 1px 4px #0001', marginTop: 24 }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Saved At</th>
            <th>Size</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {models.map(model => (
            <tr key={model.id}>
              <td>{model.name}</td>
              <td>{new Date(model.savedAt).toLocaleString()}</td>
              <td>{model.size}</td>
              <td>
                <button>Download</button>{' '}
                <button>Export to Hugging Face</button>{' '}
                <button onClick={() => handleDelete(model.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LocalModels;