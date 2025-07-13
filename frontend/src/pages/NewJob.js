import React, { useState } from 'react';

const mockModels = [
  { name: 'Llama-3B', description: '3B parameter Llama model' },
  { name: 'Qwen-4B', description: '4B parameter Qwen model' },
  { name: 'Gemma-1B', description: '1B parameter Gemma model' },
];
const mockDatasets = [
  { name: 'OpenWebText', size: '10GB' },
  { name: 'WikiText', size: '2GB' },
];

function NewJob() {
  const [step, setStep] = useState(1);
  const [model, setModel] = useState('');
  const [dataset, setDataset] = useState('');
  const [uploadedDataset, setUploadedDataset] = useState(null);
  const [params, setParams] = useState({ learningRate: 0.001, batchSize: 4, epochs: 3, optimizer: 'adam', scheduler: 'linear' });
  const [schedule, setSchedule] = useState('now');
  const [resources, setResources] = useState({ gpu: 1, memory: 16 });
  const [customScript, setCustomScript] = useState(null);
  const [tags, setTags] = useState('');
  const [notes, setNotes] = useState('');
  const [jobCreated, setJobCreated] = useState(false);

  const next = () => setStep((s) => s + 1);
  const back = () => setStep((s) => s - 1);

  const handleCreateJob = () => {
    setJobCreated(true);
  };

  return (
    <div>
      <h1>New Training Job</h1>
      <div style={{ maxWidth: 500 }}>
        <div style={{ marginBottom: 24 }}>
          <b>Step {step} of 4</b>
        </div>
        {step === 1 && (
          <div>
            <h3>Select Model</h3>
            {mockModels.map((m) => (
              <div key={m.name} style={{ marginBottom: 12 }}>
                <label>
                  <input
                    type="radio"
                    name="model"
                    value={m.name}
                    checked={model === m.name}
                    onChange={() => setModel(m.name)}
                  />{' '}
                  <b>{m.name}</b> - {m.description}
                </label>
              </div>
            ))}
            <button disabled={!model} onClick={next}>Next</button>
          </div>
        )}
        {step === 2 && (
          <div>
            <h3>Select Dataset</h3>
            {mockDatasets.map((d) => (
              <div key={d.name} style={{ marginBottom: 12 }}>
                <label>
                  <input
                    type="radio"
                    name="dataset"
                    value={d.name}
                    checked={dataset === d.name}
                    onChange={() => { setDataset(d.name); setUploadedDataset(null); }}
                  />{' '}
                  <b>{d.name}</b> - {d.size}
                </label>
              </div>
            ))}
            <div style={{ margin: '12px 0' }}>
              <label>
                <b>Or upload new dataset:</b>
                <input type="file" style={{ display: 'block', marginTop: 8 }} onChange={e => { setUploadedDataset(e.target.files[0]); setDataset(''); }} />
                {uploadedDataset && <span style={{ fontSize: 12, color: '#222' }}>Selected: {uploadedDataset.name}</span>}
              </label>
            </div>
            <button onClick={back}>Back</button>{' '}
            <button disabled={!dataset && !uploadedDataset} onClick={next}>Next</button>
          </div>
        )}
        {step === 3 && (
          <div>
            <h3>Configure Parameters</h3>
            <div style={{ marginBottom: 12 }}>
              <label>Learning Rate: <input type="number" step="0.0001" value={params.learningRate} onChange={e => setParams(p => ({ ...p, learningRate: parseFloat(e.target.value) }))} /></label>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Batch Size: <input type="number" value={params.batchSize} onChange={e => setParams(p => ({ ...p, batchSize: parseInt(e.target.value) }))} /></label>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Epochs: <input type="number" value={params.epochs} onChange={e => setParams(p => ({ ...p, epochs: parseInt(e.target.value) }))} /></label>
            </div>
            <details style={{ marginBottom: 12 }}>
              <summary>Advanced Options</summary>
              <div style={{ marginTop: 8 }}>
                <label>Optimizer: <input type="text" value={params.optimizer} onChange={e => setParams(p => ({ ...p, optimizer: e.target.value }))} /></label>
              </div>
              <div style={{ marginTop: 8 }}>
                <label>Scheduler: <input type="text" value={params.scheduler} onChange={e => setParams(p => ({ ...p, scheduler: e.target.value }))} /></label>
              </div>
            </details>
            <div style={{ marginBottom: 12 }}>
              <label>Schedule: <select value={schedule} onChange={e => setSchedule(e.target.value)}><option value="now">Now</option><option value="later">Later</option></select></label>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>GPU: <input type="number" value={resources.gpu} min={0} max={8} onChange={e => setResources(r => ({ ...r, gpu: parseInt(e.target.value) }))} /></label>
              <label style={{ marginLeft: 16 }}>Memory (GB): <input type="number" value={resources.memory} min={1} max={256} onChange={e => setResources(r => ({ ...r, memory: parseInt(e.target.value) }))} /></label>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Custom Training Script/Plugin: <input type="file" onChange={e => setCustomScript(e.target.files[0])} /></label>
              {customScript && <span style={{ fontSize: 12, color: '#222' }}>Selected: {customScript.name}</span>}
            </div>
            <button onClick={back}>Back</button>{' '}
            <button onClick={next}>Next</button>
          </div>
        )}
        {step === 4 && (
          <div>
            <h3>Review & Launch</h3>
            <ul>
              <li><b>Model:</b> {model}</li>
              <li><b>Dataset:</b> {dataset || (uploadedDataset && uploadedDataset.name)}</li>
              <li><b>Learning Rate:</b> {params.learningRate}</li>
              <li><b>Batch Size:</b> {params.batchSize}</li>
              <li><b>Epochs:</b> {params.epochs}</li>
              <li><b>Optimizer:</b> {params.optimizer}</li>
              <li><b>Scheduler:</b> {params.scheduler}</li>
              <li><b>Schedule:</b> {schedule}</li>
              <li><b>GPU:</b> {resources.gpu}</li>
              <li><b>Memory:</b> {resources.memory} GB</li>
              <li><b>Custom Script:</b> {customScript ? customScript.name : 'None'}</li>
            </ul>
            <div style={{ marginBottom: 12 }}>
              <label>Tags: <input type="text" value={tags} onChange={e => setTags(e.target.value)} placeholder="e.g. baseline, test" /></label>
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Notes: <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Describe this experiment..." style={{ width: '100%' }} /></label>
            </div>
            <button onClick={back}>Back</button>{' '}
            <button onClick={handleCreateJob}>Create Training Job</button>
            {jobCreated && <div style={{ color: 'green', marginTop: 16 }}>Job created! (mock)</div>}
          </div>
        )}
      </div>
    </div>
  );
}

export default NewJob;