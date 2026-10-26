# 🚀 Resume Lab AI Studio

<p align="center">
  <strong>Advanced Agentic Knowledgebase-Driven Resume Tailoring, ATS Synchronization & Document Compiler</strong>
</p>

<p align="center">
  <a href="https://resume-lab-ai-studio-135378541186.australia-southeast1.run.app"><img src="https://img.shields.io/badge/Live%20Demo-Google%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Live Demo on GCP"></a>
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Ready">
  <img src="https://img.shields.io/badge/Multi--Cloud-AWS%20%7C%20Azure%20%7C%20GCP-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white" alt="Multi-Cloud Support">
  <img src="https://img.shields.io/badge/Privacy-100%25%20On--Device%20PII-10B981?style=for-the-badge&logo=shield&logoColor=white" alt="Privacy First">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

---

## 📑 Table of Contents

1. [Overview & Value Proposition](#-overview--value-proposition)
2. [5-Stage Agentic Application Lifecycle](#-5-stage-agentic-application-lifecycle)
3. [Zero-Cloud PII & Privacy Framework](#-zero-cloud-pii--privacy-framework)
4. [AI Engine: 100% Private Local LLMs vs. Cloud BYOK](#-ai-engine-options)
5. [Quickstart: Run Locally in 2 Minutes](#-quickstart-run-locally-in-2-minutes)
   - [Windows (1-Click Launch)](#-windows-1-click-launcher)
   - [macOS / Linux (1-Click Launch)](#-macos--linux-1-click-launcher)
   - [Docker & Docker Compose](#-docker--docker-compose)
   - [Manual Virtual Environment (.venv)](#-manual-python-environment)
6. [Cloud Deployment: Deploy to AWS, Azure, or GCP](#-cloud-deployment-aws-azure-gcp)
   - [Google Cloud Platform (Cloud Run)](#1-google-cloud-platform-gcp-cloud-run)
   - [Amazon Web Services (AWS App Runner)](#2-amazon-web-services-aws-app-runner)
   - [Microsoft Azure (Azure Container Apps)](#3-microsoft-azure-azure-container-apps)
7. [Custom Local Directory Structure Setup](#-custom-local-directory-structure-setup)
8. [System Architecture & Codebase Tour](#-system-architecture--codebase-tour)
9. [Developer Guide: Extending & Rebuilding Features](#-developer-guide-extending--rebuilding)
   - [Adding a New LLM Provider](#1-adding-a-new-llm-provider)
   - [Customizing the ATS Scoring Engine](#2-customizing-the-ats-scoring-algorithm)
   - [Adding Custom Word Templates & Layout Styles](#3-adding-custom-word-templates)
   - [Adding API Endpoints](#4-adding-new-api-endpoints)
   - [Running & Writing Automated Tests](#5-running--writing-automated-tests)
10. [Configuration Reference (Environment Variables)](#-configuration-reference)
11. [Contributing & Community Roadmap](#-contributing--community-roadmap)
12. [License](#-license)

---

## 💡 Overview & Value Proposition

Most generic AI resume tools send your unredacted personal information to proprietary cloud databases and invent ("hallucinate") skills or job achievements that you never performed.

**Resume Lab AI Studio** solves this with an **agentic, knowledgebase-grounded architecture**:
- **Candidate Profile Truth**: Every bullet point generated is cross-referenced against your verified career history, achievements, and technical matrix.
- **Anti-Hallucination Audits**: Forensic validation ensures historical dates, contact details, certifications, and factual metrics remain 100% intact.
- **Visual Word Layout Sync**: Re-maps sections into native Microsoft Word (`.docx`) paragraph styles (`Title`, `Heading 2`, `Heading 3`, `List Bullet`, `Normal`) without disturbing margins or typography.
- **Permanent Application Archive**: Every job application is preserved with all 6 core assets (`target_jd.md`, `tailored_resume.md`, `tailored_cover_letter.md`, `compliance_report.md`, `tailored_resume.docx`, `tailored_cover_letter.docx`).

---

## 🔄 5-Stage Agentic Application Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                RESUME LAB 5-STAGE PIPELINE                             │
└────────────────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
[Step 1: Target JD & Live Intelligence]
     ├── Analyzes target role constraints, seniority, and employer culture
     ├── Extracts core competencies, required tech stack, and keywords
     └── Computes real-time ATS match scoring (0–100%) and gap matrix
     │
     ▼
[Step 2: Tailored Resume Engine]
     ├── Queries local Knowledge Base (skills inventory & experience matrix)
     ├── Dynamically selects highest-impact verified achievements
     └── Executes Anti-Hallucination & Truth Invariant audit
     │
     ▼
[Step 3: Executive Cover Letter Generation]
     ├── Establishes authentic executive narrative & organizational alignment
     └── Adheres to Candidate Tone Guide (direct, evidence-backed, non-fluff)
     │
     ▼
[Step 4: Compliance & Technical Gap Analysis]
     ├── Verifies mandatory qualification compliance against target JD
     └── Outputs structured compliance report (`compliance_report.md`)
     │
     ▼
[Step 5: Word Document Compilation & Archiving]
     ├── Injects tailored markdown into target Word template (.docx)
     ├── Applies paragraph style re-mapping & typography preservation
     └── Archives all 6 assets into permanent library (`my_applications/<Company - Role>/`)
```

---

## 🔒 Zero-Cloud PII & Privacy Framework

Whether you run Resume Lab AI Studio locally or host it on a public cloud, your personal career data remains strictly private:

1. **Zero-Cloud PII Invariant**:
   - The `.dockerignore`, `.gcloudignore`, and `.gitignore` configurations exclude `knowledge_base/`, `output/`, `my_applications/`, and `user_storage_config.json`.
   - When deploying to Docker, AWS, Azure, or GCP, **no personal resumes or candidate files are ever included in the container image**.
2. **Client-Side Bring-Your-Own-Key (BYOK)**:
   - When entering Gemini, OpenAI, Groq, or Claude API keys, your keys are stored exclusively in your browser's local storage (`localStorage`).
   - Keys are never saved to cloud disks, databases, or application server logs.
3. **Non-Root Execution**:
   - Docker containers execute under a non-privileged system user (`appuser:10001`).

---

## 🤖 AI Engine Options

Resume Lab AI Studio provides two distinct AI intelligence modes:

| Feature | Option A: Bring Your Own API Key (BYOK) | Option B: 100% Private Local LLM |
| :--- | :--- | :--- |
| **Supported Models** | **Google Gemini** (1.5 Flash, 1.5 Pro)<br>**OpenAI** (GPT-4o, GPT-4o-mini)<br>**Groq Cloud** (LLaMA 3.3 70B @ 200+ tok/s)<br>**Anthropic** (Claude 3.5 Sonnet) | **LLaMA 3.2**<br>**Mistral**<br>**DeepSeek-R1**<br>**Qwen 2.5** |
| **Execution Environment** | Cloud or Local | Localhost only (`http://localhost:5050`) |
| **Cost** | Free tiers available (Gemini, Groq) or standard API rates | **100% Free Forever** |
| **Data Privacy** | Encrypted in-flight via HTTPS; keys in browser `localStorage` | **100% On-Device** (Zero bytes leave your computer) |
| **Setup Required** | Paste API key in Studio UI | Install [Ollama](https://ollama.com) & run `ollama run llama3.2` |

> [!NOTE]
> **Why Local Installation is Required for Local LLMs:** Web browsers enforce strict cross-origin security rules that prevent a cloud-hosted website (like Cloud Run) from opening network sockets to your private home computer (`localhost:11434`). To use Ollama or LM Studio, run Resume Lab AI Studio on your local machine.

---

## 🚀 Quickstart: Run Locally in 2 Minutes

### 🪟 Windows (1-Click Launcher)
1. **Download / Clone**:
   ```powershell
   git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
   cd ResumeLabAIStudio
   ```
2. **Double-Click**:
   ```text
   start_studio.bat
   ```
   *The script automatically provisions Python, creates `.venv`, installs requirements, and opens `http://localhost:5050`.*

---

### 🍎 macOS / Linux (1-Click Launcher)
1. **Clone and run**:
   ```bash
   git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
   cd ResumeLabAIStudio
   chmod +x start_studio.sh
   ./start_studio.sh
   ```

---

### 🐳 Docker & Docker Compose
Run an isolated container while mapping your private local directories:
```bash
docker compose up -d
```
Open **`http://localhost:5050`**. Your files persist in your local repository directories, and the container connects directly to host Ollama via `host.docker.internal:11434`.

---

### 🐍 Manual Python Environment
```bash
# 1. Clone repository
git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
cd ResumeLabAIStudio

# 2. Virtual environment setup
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Start studio server
python app/server.py
```
Open your browser to: **`http://localhost:5050`**

---

## ☁️ Cloud Deployment: AWS, Azure, GCP

The application includes a production-ready, stateless `Dockerfile` configured with non-root security and built-in health checks.

### 1. Google Cloud Platform (GCP Cloud Run)
```bash
# Authenticate & configure project
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# 1-Command Deployment
gcloud run deploy resume-lab-ai-studio \
  --source . \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --port 8080
```
*Live Reference: [https://resume-lab-ai-studio-135378541186.australia-southeast1.run.app](https://resume-lab-ai-studio-135378541186.australia-southeast1.run.app)*

---

### 2. Amazon Web Services (AWS App Runner)
```bash
AWS_REGION="ap-southeast-2" # Sydney (or us-east-1)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO_NAME="resume-lab-ai-studio"

# 1. Create ECR repository & log in
aws ecr create-repository --repository-name $REPO_NAME --region $AWS_REGION
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 2. Build & push container
docker build -t $REPO_NAME .
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest
```
*In the AWS Console: Navigate to **AWS App Runner** → Create Service from your ECR image → Set Port to `8080` → Deploy.*

---

### 3. Microsoft Azure (Azure Container Apps)
```bash
# Log in & set environment
az login
RG_NAME="rg-resumelab"
LOCATION="australiasoutheast" # or eastus
APP_NAME="resume-lab-ai-studio"

# Create resource group & deploy container app
az group create --name $RG_NAME --location $LOCATION
az containerapp up \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --source . \
  --target-port 8080 \
  --ingress external
```

---

## 📁 Custom Local Directory Structure Setup

Users can store their private career documents on any folder or external drive on their computer.

Click the **`📁 Local Storage`** badge in the UI header to configure:
- **Knowledge Base Directory (`kb_dir`)**: Where your verified career facts and profile markdown files reside.
- **Templates Directory (`templates_dir`)**: Where your master Word (`.docx`) and Markdown templates live.
- **Outputs Directory (`output_dir`)**: Where working tailored resumes, cover letters, and reports are written.
- **Applications Archive (`apps_dir`)**: Where permanent completed application bundles are stored.

All custom paths are saved locally to `user_storage_config.json` (strictly ignored by Git and Docker).

---

## 🏗️ System Architecture & Codebase Tour

```text
Resume_lab/
├── app/
│   ├── index.html              # Reactive Single-Page UI (Tailwind CSS, vanilla JS, zero build step)
│   ├── server.py               # Lightweight Python HTTP API Server (port 5050 / 8080)
│   ├── storage_config.py       # Centralized 3-tier dynamic path & storage management
│   ├── llm_copilot.py          # Grounding Copilot: multi-provider (Gemini, OpenAI, Claude, Groq, Ollama)
│   ├── intelligence_engine.py  # ATS match scoring, constraint parsing, & gap analysis
│   ├── template_manager.py     # Word template discovery, inspection, upload, and paragraph mapping
│   ├── application_manager.py  # 6-Asset application lifecycle & archive library manager
│   └── profile_manager.py      # Candidate Profile Truth invariants manager
├── knowledge_base/             # Candidate verified career files (skills, matrix, tone guide)
├── knowledge_base.example/     # Starter templates for new users
├── template/                   # Master Word (.docx) & Markdown (.md) layout templates
├── scripts/
│   └── compile_docs.py         # python-docx compiler & visual layout sync engine
├── tests/
│   ├── test_e2e_pipeline.py    # 6-Stage automated regression test suite
│   └── test_storage_config.py  # Storage path & directory unit test suite
├── docs/
│   └── DEPLOYMENT_GUIDE.md     # In-depth multi-cloud & production guide
├── Dockerfile                  # Non-root container image specification
├── docker-compose.yml          # Local containerized orchestration with host volume mapping
├── start_studio.bat            # Windows 1-click launcher
├── start_studio.sh             # macOS / Linux 1-click launcher
└── requirements.txt            # Python dependencies (python-docx, marked, etc.)
```

---

## 🛠️ Developer Guide: Extending & Rebuilding

Resume Lab AI Studio was built to be easily hackable, modular, and extensible. Here is how the community can extend each layer:

### 1. Adding a New LLM Provider
To add a new provider (e.g. Mistral API, DeepSeek API, or AWS Bedrock):
1. In `app/llm_copilot.py`:
   - Add your provider handling function in `query_llm()`:
   ```python
   def query_new_provider(prompt, model, api_key):
       # Send HTTP request to your provider endpoint
       ...
   ```
2. In `app/index.html`:
   - Add the provider name and models to `AI_PROVIDER_MODELS`:
   ```javascript
   const AI_PROVIDER_MODELS = {
     my_provider: [
       { id: "model-1", name: "My Model 1" }
     ],
     ...
   };
   ```

### 2. Customizing the ATS Scoring Algorithm
ATS keyword weighting, penalization, and role heuristics live in [`app/intelligence_engine.py`](file:///c:/Users/rajpa/OneDrive/Resume_lab/app/intelligence_engine.py):
- `extract_jd_metadata(jd_text)`: Regex and rule-based keyword extraction.
- `analyze_jd_alignment(jd_text, kb_files)`: Computes alignment scores, mandatory match percentages, and domain gap indicators.
- `simulate_ats_analysis(resume_text, jd_text)`: Evaluates keyword density, action-verb strength, formatting risks, and ATS compliance.

### 3. Adding Custom Word Templates
The layout sync engine reads your template's internal styles:
1. Place any Microsoft Word `.docx` file in the `template/` folder (or upload via the UI **Templates** tab).
2. Ensure your Word file defines standard styles: `Title`, `Heading 2`, `Heading 3`, `List Bullet`, `Normal`.
3. [`scripts/compile_docs.py`](file:///c:/Users/rajpa/OneDrive/Resume_lab/scripts/compile_docs.py) will parse markdown AST runs and automatically inject text using the template's exact font family, size, line spacing, margins, and hex colors.

### 4. Adding New API Endpoints
The server uses Python's standard `http.server.BaseHTTPRequestHandler` in [`app/server.py`](file:///c:/Users/rajpa/OneDrive/Resume_lab/app/server.py) (zero heavy framework dependencies):
```python
# To add a GET route:
def do_GET(self):
    if path == "/api/my-custom-endpoint":
        self.send_json({"data": "hello"})

# To add a POST route:
def do_POST(self):
    if path == "/api/my-custom-endpoint":
        payload = self.read_post_json()
        self.send_json({"received": payload})
```

### 5. Running & Writing Automated Tests
Run the existing automated test suites:
```bash
# E2E 6-Stage Application Pipeline Test
python tests/test_e2e_pipeline.py

# Custom Storage & Dynamic Path Resolution Test
python tests/test_storage_config.py
```
To add a new test, create a `test_*.py` file inside `tests/` utilizing Python's standard `unittest` framework.

---

## ⚙️ Configuration Reference

The following environment variables can be set locally or injected into cloud containers:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `5050` (local) / `8080` (cloud) | HTTP server port |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint for local LLMs |
| `RESUME_LAB_KB_DIR` | `./knowledge_base` | Override path for Knowledge Base folder |
| `RESUME_LAB_TEMPLATES_DIR` | `./template` | Override path for Word / MD templates |
| `RESUME_LAB_OUTPUT_DIR` | `./output` | Override path for working tailored outputs |
| `RESUME_LAB_APPS_DIR` | `./my_applications` | Override path for permanent application archive |
| `GEMINI_API_KEY` | *(Optional)* | Server-level Google Gemini fallback API key |
| `OPENAI_API_KEY` | *(Optional)* | Server-level OpenAI fallback API key |

---

## 🤝 Contributing & Community Roadmap

Contributions from the community are warmly welcomed!

### How to Contribute:
1. **Fork the Repository**: Click the **Fork** button at the top right of [GitHub](https://github.com/rajivrparikh-cissp/ResumeLabAIStudio).
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Commit Your Changes**:
   ```bash
   git commit -m "feat(ats): add semantic vector embeddings for JD scoring"
   ```
4. **Run Tests**:
   ```bash
   python tests/test_e2e_pipeline.py
   python tests/test_storage_config.py
   ```
5. **Open a Pull Request**: Submit your PR on GitHub with a description of your enhancement.

### Community Roadmap:
- [ ] Direct LinkedIn Easy Apply & Seek job description auto-fetchers.
- [ ] Semantic vector search for multi-decade career knowledge bases (ChromaDB / SQLite VSS).
- [ ] Export to PDF with OpenType ligature preservation.
- [ ] LaTeX academic CV compilation engine.
- [ ] Multi-language resume tailoring and translation.

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, distribute, and build commercial or personal solutions with this software. See `LICENSE` for details.

---

<p align="center">
  Built with ❤️ for candidate empowerment and career sovereignty.
</p>
