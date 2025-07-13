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
  const [params, setParams] = useState({ learningRate: 0.001, batchSize: 4, epochs: 3 });
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
                    onChange={() => setDataset(d.name)}
                  />{' '}
                  <b>{d.name}</b> - {d.size}
                </label>
              </div>
            ))}
            <div style={{ margin: '12px 0' }}>
              <label>
                <b>Or upload new dataset:</b>
                <input type="file" style={{ display: 'block', marginTop: 8 }} disabled />
                <span style={{ fontSize: 12, color: '#888' }}>(Upload not implemented in mockup)</span>
              </label>
            </div>
            <button onClick={back}>Back</button>{' '}
            <button disabled={!dataset} onClick={next}>Next</button>
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
            <button onClick={back}>Back</button>{' '}
            <button onClick={next}>Next</button>
          </div>
        )}
        {step === 4 && (
          <div>
            <h3>Review & Launch</h3>
            <ul>
              <li><b>Model:</b> {model}</li>
              <li><b>Dataset:</b> {dataset}</li>
              <li><b>Learning Rate:</b> {params.learningRate}</li>
              <li><b>Batch Size:</b> {params.batchSize}</li>
              <li><b>Epochs:</b> {params.epochs}</li>
            </ul>
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