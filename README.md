# Train-Your-Own-LLM Platform

A production-grade platform for fine-tuning Large Language Models using Unsloth GRPO, featuring an integrated AI agent, Hugging Face interoperability, and a polished web UI.

## 🚀 Vision

Transform experimental Colab notebooks into a robust, self-serve platform that:
- **Hides boilerplate** of RLHF/GRPO training
- **Guides users** with an intelligent AI agent
- **Deploys models** in formats practitioners actually need
- **Scales efficiently** with multi-tenant GPU orchestration

## 🏗️ Architecture

```
┌───────────────────────────────┐
│        React / Next.js        │  Web UI (WASM tokenizer for live previews)
└─────────────▲─────────────────┘
              │ GraphQL / REST
┌─────────────┴─────────────┐
│      API‑Gateway (FastAPI)│  AuthN/Z, rate‑limit
└─────────────▲─────────────┘
              │ gRPC / HTTP
┌─────────────┴─────────────┐        ┌─────────────────────────┐
│  Job Orchestrator (K8s)   │◀──────▶│  GPU Node Pool (A100/T4)│
│  – "trainer‑svc"          │        └─────────────────────────┘
│  – "agent‑svc"            │
│  – "dataset‑svc"          │
└─────────────▲─────────────┘
              │
┌─────────────┴───────────┐
│  Postgres / MinIO / HF  │  metadata, artifacts, datasets
└─────────────────────────┘
```

## 🎯 Key Features

### Model Hub
- Browse or import any HF model (Llama-3 3B-Instruct, DeepSeek R1, Qwen 3 4B, Gemma 3 1B)
- FastLanguageModel.from_pretrained() with tokenizer templating

### Dataset Studio
- Drag-and-drop CSV/JSON/Parquet files
- Search Hugging Face datasets
- Connect S3/GCS buckets
- Preview and label data

### Training & RLHF/GRPO Pipeline
- One-click fine-tune with LoRA, 4-bit, or full weights
- Live reward charts and metrics
- GRPOTrainer with custom reward functions
- LoRA saving & merging

### AI Agent Co-pilot
- Auto-detect dataset schema
- Suggest optimal hyperparameters
- Flag GPU memory limits
- Auto-repair failed training runs

### Deployment
- Export to Hugging Face, GGUF, Ollama, or vLLM server
- Generate curl/UI snippets for integration

## 🛠️ Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| UI | React + Chakra UI | Quick component library, theming |
| API | FastAPI | Async, pydantic schemas, Python-friendly for ML |
| Orchestration | Kubernetes + NVIDIA GPU Operator | Multi-tenant GPU scheduling, node autoscaling |
| Training | Unsloth + TRL | Optimized GRPO training |
| Model Serving | vLLM | Fast KV-cache, streamed tokens |
| Storage | MinIO (S3-compatible) | On-prem or cloud-portable |
| Auth | OAuth2 / OIDC | Enterprise SSO readiness |
| Observability | Prometheus + Grafana, Loki | GPU & job metrics |

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- NVIDIA GPU with CUDA support
- Kubernetes cluster (for production)

### Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd train-your-own-llm-platform
```

2. **Start the development stack**
```bash
docker-compose up -d
```

3. **Access the platform**
- Web UI: http://localhost:3000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### Production Deployment

1. **Deploy to Kubernetes**
```bash
kubectl apply -f k8s/
```

2. **Configure GPU nodes**
```bash
kubectl apply -f k8s/gpu-operator/
```

## 📋 Roadmap

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 0. Bootstrap | 2 wks | Repo scaffolding, Dockerfiles, HF import API |
| 1. MVP | 4 wks | Single-tenant trainer, basic UI, manual hyper-params, export to HF |
| 2. Agent α | 3 wks | Data inspector, VRAM estimator, retry logic |
| 3. Multi-tenant & Billing | 4 wks | Org/project model, quota tracking, Stripe |
| 4. Auto-eval & Leaderboards | 2 wks | Built-in GSM8K, MMLU, custom test-sets |
| 5. Marketplace & Plugins | 3 wks | Users share reward functions / datasets |
| 6. On-device edge build | 4 wks | GGUF pipeline, Ollama auto-push |

## 🔧 Development

### Project Structure
```
├── backend/                 # FastAPI backend services
│   ├── trainer-service/     # Training orchestration
│   ├── agent-service/       # AI agent logic
│   ├── dataset-service/     # Dataset management
│   └── api-gateway/         # Main API gateway
├── frontend/                # React web UI
├── core/                    # Shared training logic
│   ├── unsloth_trainer/     # Abstracted notebook logic
│   └── templates/           # Chat templates & prompts
├── k8s/                     # Kubernetes manifests
├── docker/                  # Docker configurations
└── docs/                    # Documentation
```

### Core Training Logic

The platform abstracts the four Unsloth GRPO notebooks into a reusable Python package:

```python
from core.unsloth_trainer import run_grpo, TrainConfig

# All four notebook variants boil down to this pattern
run_handle = run_grpo(
    model_id="unsloth/gemma-3-1b-it",
    dataset_uri="s3://bucket/dataset.parquet",
    cfg=TrainConfig(
        max_seq_length=1024,
        learning_rate=5e-6,
        num_epochs=1,
        reward_functions=["format_match", "answer_check"]
    )
)
```

## 🔒 Security & Compliance

- TLS everywhere, short-lived presigned URLs
- Role-based access: project viewer, editor, admin
- Audit log of dataset access and model exports
- GDPR: user-initiated data deletion pipeline

## 📊 Scaling & Cost Controls

- Spot-instance GPU pools for low-priority jobs
- Quota-aware scheduler: deny jobs whose estimated vRAM > pool capacity
- Optional "CPU-only LoRA preview" path using 8-bit and small sequence length
- Automatic idle-GPU shutdown after N minutes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Discord: [Join our community](https://discord.gg/unsloth)
- Documentation: [Platform docs](https://docs.unsloth.ai)
- Issues: [GitHub Issues](https://github.com/unslothai/unsloth/issues)

---

Built with ❤️ by the Unsloth team