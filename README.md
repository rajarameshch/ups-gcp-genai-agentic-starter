# UPS GCP GenAI + Agentic AI Starter Repo

This repository is a **starter kit** for building a UPS customer-facing GenAI + Agentic AI solution on **Google Cloud Platform (GCP)**.

It includes:
- **Terraform** to provision core GCP resources (APIs, IAM, Artifact Registry, Cloud Run, Pub/Sub, Cloud Storage, Secret Manager, BigQuery dataset).
- **FastAPI services**:
  - `api-gateway` (public entrypoint)
  - `agent-service` (LangGraph skeleton + sample workflows)
  - `retrieval-service` (document ingest + simple retrieval stub)
- **Agent graph skeleton** (LangGraph) with tool calling, routing, and workflow execution pattern.
- Sample workflows for common logistics use cases (shipment ETA Q&A, exception triage, claims intake).

> ⚠️ Note: This repo is designed to be safe-by-default and runnable locally with mock LLM responses.
> To connect to **Vertex AI (Gemini)**, set the environment variables described below.

---

## Architecture (high level)

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/86fbc3d9-3e11-4cbf-8b0d-a73ad770c8df" />


---

## Repo layout

```
infra/terraform/           # GCP provisioning
services/
  api-gateway/             # public API (auth hook + routing)
  agent-service/           # agent graph + workflows
  retrieval-service/       # ingest + retrieval stub
shared/                    # shared config + models + utils
workflows/                 # sample workflow definitions (YAML)
scripts/                   # local helpers
.github/workflows/         # CI
docker-compose.yml
Makefile
```

---

## Quickstart (local)

### 1) Create a virtualenv and install deps
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2) Run locally with Docker Compose
```bash
docker compose up --build
```

### 3) Try the API
```bash
curl http://localhost:8080/healthz
curl -X POST http://localhost:8080/v1/chat -H "Content-Type: application/json" -d '{"message":"Where is tracking 1Z999AA10123456784?"}'
curl -X POST http://localhost:8080/v1/workflows/run -H "Content-Type: application/json" -d '{"workflow_id":"shipment_exception_triage","inputs":{"tracking_id":"1Z999AA10123456784"}}'
```

---

## Optional: Connect to Vertex AI (Gemini)

### Prereqs
- A GCP project with **Vertex AI API** enabled
- Application Default Credentials (ADC) set up:
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Env vars
Set these for `agent-service`:
- `GOOGLE_CLOUD_PROJECT` (required)
- `GOOGLE_CLOUD_LOCATION` (default: `us-central1`)
- `VERTEX_MODEL` (default: `gemini-1.5-pro`)

When unset, the system uses a mock LLM provider.

---

## Terraform (GCP provisioning)

### 1) Initialize
```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

### 2) Build & deploy services (Cloud Run)
This starter includes Terraform resources for Cloud Run services, but you still need to build images.
Example (Cloud Build):
```bash
gcloud builds submit --tag us-docker.pkg.dev/YOUR_PROJECT_ID/ups-genai/api-gateway:latest services/api-gateway
gcloud builds submit --tag us-docker.pkg.dev/YOUR_PROJECT_ID/ups-genai/agent-service:latest services/agent-service
gcloud builds submit --tag us-docker.pkg.dev/YOUR_PROJECT_ID/ups-genai/retrieval-service:latest services/retrieval-service
```

Then update the Cloud Run image tags via `terraform apply` or `gcloud run services update ...`.

---

## Security notes (for enterprise)
- Add your SSO/JWT validation in `api-gateway` (middleware scaffold included).
- Use **Secret Manager** for API keys and service credentials.
- Enable **Cloud Armor** / WAF if exposing public endpoints.
- Use **VPC Service Controls** for data exfiltration protection if needed.
- Add **Audit logs** and centralized observability (Cloud Logging + Cloud Trace).

---

## License
MIT (see `LICENSE`).
