import React from 'react';
import { useParams } from 'react-router-dom';

const mockJobDetails = {
  1: {
    model: 'Llama-3B',
    dataset: 'OpenWebText',
    status: 'running',
    createdAt: '2024-06-01T10:00:00Z',
    logs: 'Training started...\nEpoch 1/3: loss=2.1\nEpoch 2/3: loss=1.8',
    metrics: { loss: 1.8, accuracy: 0.85 },
  },
  2: {
    model: 'Qwen-4B',
    dataset: 'WikiText',
    status: 'completed',
    createdAt: '2024-05-30T14:30:00Z',
    logs: 'Training started...\nEpoch 1/3: loss=2.3\nEpoch 2/3: loss=1.9\nEpoch 3/3: loss=1.7',
    metrics: { loss: 1.7, accuracy: 0.88 },
  },
  3: {
    model: 'Gemma-1B',
    dataset: 'OpenWebText',
    status: 'failed',
    createdAt: '2024-05-28T09:15:00Z',
    logs: 'Training started...\nError: CUDA out of memory',
    metrics: { loss: null, accuracy: null },
  },
};

function JobDetail() {
  const { id } = useParams();
  const job = mockJobDetails[id];
  if (!job) return <div>Job not found.</div>;
  return (
    <div>
      <h1>Job Detail</h1>
      <ul>
        <li><b>Model:</b> {job.model}</li>
        <li><b>Dataset:</b> {job.dataset}</li>
        <li><b>Status:</b> {job.status}</li>
        <li><b>Created:</b> {new Date(job.createdAt).toLocaleString()}</li>
      </ul>
      <h3>Logs</h3>
      <pre style={{ background: '#222', color: '#fff', padding: 16, borderRadius: 8 }}>{job.logs}</pre>
      <h3>Metrics</h3>
      <ul>
        <li><b>Loss:</b> {job.metrics.loss !== null ? job.metrics.loss : 'N/A'}</li>
        <li><b>Accuracy:</b> {job.metrics.accuracy !== null ? job.metrics.accuracy : 'N/A'}</li>
      </ul>
      <div style={{ marginTop: 24 }}>
        <button disabled={job.status !== 'completed'}>Download Weights</button>{' '}
        <button disabled={job.status !== 'completed'}>Export to Hugging Face</button>{' '}
        <button disabled={job.status !== 'completed'}>Deploy Model</button>
      </div>
    </div>
  );
}

export default JobDetail;