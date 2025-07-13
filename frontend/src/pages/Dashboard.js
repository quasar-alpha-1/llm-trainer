import React from 'react';
import { Link } from 'react-router-dom';

const mockJobs = [
  { id: 1, model: 'Llama-3B', status: 'running' },
  { id: 2, model: 'Qwen-4B', status: 'completed' },
];
const mockModels = [
  { id: 'llama-3b-20240601', name: 'Llama-3B' },
  { id: 'qwen-4b-20240530', name: 'Qwen-4B' },
];
const mockDatasets = [
  { name: 'OpenWebText' },
  { name: 'WikiText' },
];

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ display: 'flex', gap: 32, marginBottom: 32 }}>
        <div style={{ background: '#fff', padding: 24, borderRadius: 8, minWidth: 200 }}>
          <h3>Recent Jobs</h3>
          <ul>
            {mockJobs.map(job => (
              <li key={job.id}><Link to={`/jobs/${job.id}`}>{job.model} ({job.status})</Link></li>
            ))}
          </ul>
          <Link to="/jobs">View all jobs</Link>
        </div>
        <div style={{ background: '#fff', padding: 24, borderRadius: 8, minWidth: 200 }}>
          <h3>Models</h3>
          <ul>
            {mockModels.map(model => (
              <li key={model.id}>{model.name}</li>
            ))}
          </ul>
          <Link to="/local-models">View all models</Link>
        </div>
        <div style={{ background: '#fff', padding: 24, borderRadius: 8, minWidth: 200 }}>
          <h3>Datasets</h3>
          <ul>
            {mockDatasets.map(ds => (
              <li key={ds.name}>{ds.name}</li>
            ))}
          </ul>
        </div>
      </div>
      <div>
        <Link to="/new-job"><button>Create New Training Job</button></Link>
      </div>
    </div>
  );
}

export default Dashboard;