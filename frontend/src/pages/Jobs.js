import React from 'react';
import { Link } from 'react-router-dom';

const mockJobs = [
  { id: 1, model: 'Llama-3B', dataset: 'OpenWebText', status: 'running', createdAt: '2024-06-01T10:00:00Z' },
  { id: 2, model: 'Qwen-4B', dataset: 'WikiText', status: 'completed', createdAt: '2024-05-30T14:30:00Z' },
  { id: 3, model: 'Gemma-1B', dataset: 'OpenWebText', status: 'failed', createdAt: '2024-05-28T09:15:00Z' },
];

function Jobs() {
  return (
    <div>
      <h1>Jobs</h1>
      <table style={{ width: '100%', background: '#fff', borderRadius: 8, boxShadow: '0 1px 4px #0001', marginTop: 24 }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Model</th>
            <th>Dataset</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {mockJobs.map(job => (
            <tr key={job.id}>
              <td><Link to={`/jobs/${job.id}`}>{job.id}</Link></td>
              <td>{job.model}</td>
              <td>{job.dataset}</td>
              <td>{job.status}</td>
              <td>{new Date(job.createdAt).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Jobs;