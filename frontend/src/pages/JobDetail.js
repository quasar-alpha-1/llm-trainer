import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const mockJobDetails = {
  1: {
    model: 'Llama-3B',
    dataset: 'OpenWebText',
    status: 'running',
    createdAt: '2024-06-01T10:00:00Z',
    logs: ['Training started...', 'Epoch 1/3: loss=2.1', 'Epoch 2/3: loss=1.8'],
    metrics: { loss: 1.8, accuracy: 0.85 },
    comments: [
      { user: 'alice', text: 'Great job!', time: '2024-06-01T12:00:00Z' },
      { user: 'bob', text: 'Try a lower learning rate.', time: '2024-06-01T12:05:00Z' },
    ],
    validation: { dataset: 'WikiText', loss: 1.7, accuracy: 0.87 },
    audit: { user: 'alice', started: '2024-06-01T10:00:00Z', env: 'Docker', recipe: 'job-1-recipe.json' },
  },
  2: {
    model: 'Qwen-4B',
    dataset: 'WikiText',
    status: 'completed',
    createdAt: '2024-05-30T14:30:00Z',
    logs: ['Training started...', 'Epoch 1/3: loss=2.3', 'Epoch 2/3: loss=1.9', 'Epoch 3/3: loss=1.7'],
    metrics: { loss: 1.7, accuracy: 0.88 },
    comments: [],
    validation: { dataset: 'OpenWebText', loss: 1.6, accuracy: 0.89 },
    audit: { user: 'bob', started: '2024-05-30T14:30:00Z', env: 'Docker', recipe: 'job-2-recipe.json' },
  },
  3: {
    model: 'Gemma-1B',
    dataset: 'OpenWebText',
    status: 'failed',
    createdAt: '2024-05-28T09:15:00Z',
    logs: ['Training started...', 'Error: CUDA out of memory'],
    metrics: { loss: null, accuracy: null },
    comments: [],
    validation: null,
    audit: { user: 'carol', started: '2024-05-28T09:15:00Z', env: 'Docker', recipe: 'job-3-recipe.json' },
  },
};

function JobDetail() {
  const { id } = useParams();
  const [logIndex, setLogIndex] = useState(1);
  const [showExport, setShowExport] = useState(false);
  const [showDownload, setShowDownload] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [comment, setComment] = useState('');
  const [job, setJob] = useState(mockJobDetails[id]);

  // Simulate real-time logs
  useEffect(() => {
    if (job && job.status === 'running' && logIndex < job.logs.length) {
      const timer = setTimeout(() => setLogIndex(logIndex + 1), 1500);
      return () => clearTimeout(timer);
    }
  }, [logIndex, job]);

  if (!job) return <div>Job not found.</div>;

  const handleCancel = () => setJob({ ...job, status: 'cancelled' });
  const handleAddComment = () => {
    if (comment.trim()) {
      setJob({
        ...job,
        comments: [
          ...job.comments,
          { user: 'you', text: comment, time: new Date().toISOString() },
        ],
      });
      setComment('');
    }
  };

  return (
    <div>
      <h1>Job Detail</h1>
      <ul>
        <li><b>Model:</b> {job.model}</li>
        <li><b>Dataset:</b> {job.dataset}</li>
        <li><b>Status:</b> {job.status}</li>
        <li><b>Created:</b> {new Date(job.createdAt).toLocaleString()}</li>
      </ul>
      <button onClick={handleCancel} disabled={job.status !== 'running'}>Cancel/Stop Job</button>
      <h3>Logs</h3>
      <div style={{ background: '#222', color: '#fff', padding: 16, borderRadius: 8, minHeight: 80 }}>
        {job.logs.slice(0, logIndex).map((line, i) => <div key={i}>{line}</div>)}
        {job.status === 'running' && logIndex < job.logs.length && <div>...</div>}
      </div>
      <div style={{ margin: '12px 0' }}>
        <progress value={logIndex} max={job.logs.length} style={{ width: 300 }} />
      </div>
      <h3>Metrics</h3>
      <ul>
        <li><b>Loss:</b> {job.metrics.loss !== null ? job.metrics.loss : 'N/A'}</li>
        <li><b>Accuracy:</b> {job.metrics.accuracy !== null ? job.metrics.accuracy : 'N/A'}</li>
      </ul>
      {job.validation && (
        <div>
          <h4>Validation on {job.validation.dataset}</h4>
          <ul>
            <li><b>Val Loss:</b> {job.validation.loss}</li>
            <li><b>Val Accuracy:</b> {job.validation.accuracy}</li>
          </ul>
        </div>
      )}
      <div style={{ marginTop: 24 }}>
        <button disabled={job.status !== 'completed'} onClick={() => setShowDownload(true)}>Download Weights</button>{' '}
        <button disabled={job.status !== 'completed'} onClick={() => setShowExport(true)}>Export to Hugging Face</button>{' '}
        <button disabled={job.status !== 'completed'}>Deploy Model</button>{' '}
        <button onClick={() => setShowImport(true)}>Import from Hugging Face</button>{' '}
        <button>Compare Experiments</button>{' '}
        <button>Download Recipe</button>
      </div>
      {showExport && (
        <div style={{ background: '#fff', border: '1px solid #ccc', padding: 16, borderRadius: 8, marginTop: 16 }}>
          <h4>Export to Hugging Face</h4>
          <label>Repo Name: <input type="text" placeholder="username/model-name" /></label><br />
          <label>Token: <input type="password" placeholder="Hugging Face token" /></label><br />
          <button>Export</button>{' '}
          <button onClick={() => setShowExport(false)}>Close</button>
        </div>
      )}
      {showDownload && (
        <div style={{ background: '#fff', border: '1px solid #ccc', padding: 16, borderRadius: 8, marginTop: 16 }}>
          <h4>Download Weights</h4>
          <label>Format: <select><option>PyTorch</option><option>ONNX</option><option>Safetensors</option></select></label><br />
          <button>Download</button>{' '}
          <button onClick={() => setShowDownload(false)}>Close</button>
        </div>
      )}
      {showImport && (
        <div style={{ background: '#fff', border: '1px solid #ccc', padding: 16, borderRadius: 8, marginTop: 16 }}>
          <h4>Import from Hugging Face</h4>
          <label>Repo URL: <input type="text" placeholder="https://huggingface.co/username/model-name" /></label><br />
          <label>Token: <input type="password" placeholder="Hugging Face token" /></label><br />
          <button>Import</button>{' '}
          <button onClick={() => setShowImport(false)}>Close</button>
        </div>
      )}
      <h3>Comments</h3>
      <div style={{ background: '#f4f4f4', padding: 12, borderRadius: 8, marginBottom: 8 }}>
        {job.comments.map((c, i) => (
          <div key={i} style={{ marginBottom: 4 }}><b>{c.user}</b>: {c.text} <span style={{ color: '#888', fontSize: 12 }}>({new Date(c.time).toLocaleString()})</span></div>
        ))}
        <div style={{ marginTop: 8 }}>
          <input type="text" value={comment} onChange={e => setComment(e.target.value)} placeholder="Add a comment..." style={{ width: '80%' }} />
          <button onClick={handleAddComment}>Add</button>
        </div>
      </div>
      <h3>Audit Trail</h3>
      <ul>
        <li><b>User:</b> {job.audit.user}</li>
        <li><b>Started:</b> {new Date(job.audit.started).toLocaleString()}</li>
        <li><b>Environment:</b> {job.audit.env}</li>
        <li><b>Recipe:</b> <button>Download Recipe</button></li>
      </ul>
    </div>
  );
}

export default JobDetail;