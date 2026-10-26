# Complete Installation & Cloud Hosting Guide

**Resume Lab AI Studio** can be run 100% locally on your personal machine or hosted as a stateless serverless container on **Google Cloud Platform (GCP)**, **Amazon Web Services (AWS)**, or **Microsoft Azure**.

---

## Table of Contents
1. [Privacy & Security Architecture (Read First)](#privacy--security-architecture)
2. [Local Installation Methods](#local-installation-methods)
   - [Method A: 1-Click Launchers (Recommended for Non-Technical Users)](#method-a-1-click-launchers-recommended)
   - [Method B: Python Virtual Environment (.venv)](#method-b-python-virtual-environment)
   - [Method C: Docker & Docker Compose](#method-c-docker--docker-compose)
3. [Cloud Hosting: Google Cloud Platform (GCP Cloud Run)](#cloud-hosting-google-cloud-platform-gcp)
4. [Cloud Hosting: Amazon Web Services (AWS App Runner)](#cloud-hosting-amazon-web-services-aws)
5. [Cloud Hosting: Microsoft Azure (Azure Container Apps)](#cloud-hosting-microsoft-azure)
6. [Configuring AI Models: Local LLM vs. Cloud BYOK](#configuring-ai-models)

---

## 🔒 Privacy & Security Architecture

Before deploying anywhere, understanding how your career data is protected is critical:

- **Zero-Cloud PII Invariant**: The repository includes `.dockerignore`, `.gcloudignore`, and `.gitignore` preventing your private knowledge base (`knowledge_base/`), tailored resumes/cover letters (`output/`), past application archives (`my_applications/`), and local machine path configurations (`user_storage_config.json`) from ever being packaged into Docker images or committed to GitHub.
- **Client-Side API Key Storage**: When using cloud GenAI (Gemini, OpenAI, Groq, Claude), your API keys are stored solely in your personal browser's `localStorage`. They are never stored in databases, logs, or persistent cloud disks.
- **Non-Root Execution**: Docker containers execute under a non-privileged system user (`appuser:10001`).

---

## 💻 Local Installation Methods

Running locally is recommended if you want to use **100% free, private Local LLMs** (like LLaMA 3.2 via Ollama) and keep all file modifications directly on your local hard drive.

### Method A: 1-Click Launchers (Recommended)

No command-line expertise required.

#### 🪟 Windows:
1. Download or clone this repository:
   ```bash
   git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
   ```
2. Double-click the file:
   ```text
   start_studio.bat
   ```
   *The script automatically verifies Python 3.10+, provisions `.venv`, installs dependencies, and launches `http://localhost:5050` in your default browser.*

#### 🍎 macOS / Linux:
1. Download or clone the repository:
   ```bash
   git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
   cd ResumeLabAIStudio
   ```
2. Make the launcher executable and run it:
   ```bash
   chmod +x start_studio.sh
   ./start_studio.sh
   ```

---

### Method B: Python Virtual Environment

For developers and advanced users:

```bash
# 1. Clone the repository
git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
cd ResumeLabAIStudio

# 2. Create and activate a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Studio server
python app/server.py
```
Open your browser to: **`http://localhost:5050`**

To run automated pipeline and regression tests:
```bash
python tests/test_e2e_pipeline.py
python tests/test_storage_config.py
```

---

### Method C: Docker & Docker Compose

Run the studio inside an isolated container while mounting your local folders so documents persist on your machine:

```bash
# Start the studio container in background
docker compose up -d

# View logs
docker compose logs -f
```
Open your browser to: **`http://localhost:5050`**

*Note: The `docker-compose.yml` mounts your local `./knowledge_base`, `./template`, `./output`, and `./my_applications` folders directly into the container and enables communication with your host machine's Ollama via `host.docker.internal`.*

To stop the container:
```bash
docker compose down
```

---

## ☁️ Cloud Hosting: Google Cloud Platform (GCP)

Deploy to **Google Cloud Run** for a serverless, scalable, and cost-effective cloud instance (scales to zero when not in use).

### Prerequisites:
- [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed and authenticated.
- A GCP Project with billing enabled.

### 1-Command Deployment:
```bash
# 1. Set your GCP project ID
gcloud config set project YOUR_PROJECT_ID

# 2. Enable necessary Google Cloud services
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# 3. Build and deploy directly from the source directory
gcloud run deploy resume-lab-ai-studio \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```
When deployment finishes, `gcloud` outputs your live HTTPS URL (e.g. `https://resume-lab-ai-studio-xxxx.run.app`).

---

## ☁️ Cloud Hosting: Amazon Web Services (AWS)

Deploy to **AWS App Runner** — AWS's fully managed service for building and deploying containerized web apps directly from source or container registries without configuring VPCs or clusters.

### Prerequisites:
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured (`aws configure`).
- Docker installed locally (or AWS CodeBuild).

### Step 1: Create Amazon ECR Repository and Push Image
```bash
# Set your AWS variables
AWS_REGION="ap-southeast-2" # Sydney (or us-east-1)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO_NAME="resume-lab-ai-studio"

# 1. Create ECR repository
aws ecr create-repository --repository-name $REPO_NAME --region $AWS_REGION

# 2. Authenticate Docker with ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 3. Build container image
docker build -t $REPO_NAME .

# 4. Tag and push to ECR
docker tag $REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest
```

### Step 2: Deploy to AWS App Runner
In the AWS Console:
1. Navigate to **AWS App Runner** -> **Create Service**.
2. Select **Container Registry** -> **Amazon ECR**.
3. Choose the image `$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/resume-lab-ai-studio:latest`.
4. Under **Port**, set `8080`.
5. Click **Create & Deploy**.

App Runner provides an automatic HTTPS URL (e.g. `https://xxxx.ap-southeast-2.awsapprunner.com`).

---

## ☁️ Cloud Hosting: Microsoft Azure

Deploy to **Azure Container Apps (ACA)** — Microsoft's serverless container platform built on Kubernetes with zero-scale support.

### Prerequisites:
- [Azure CLI (`az`)](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in (`az login`).

### 1-Command Deployment with `az containerapp up`:
```bash
# 1. Set your resource group and location
RG_NAME="rg-resumelab"
LOCATION="australiasoutheast" # or eastus
APP_NAME="resume-lab-ai-studio"

# 2. Create resource group
az group create --name $RG_NAME --location $LOCATION

# 3. Deploy container app directly from the current directory
az containerapp up \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --source . \
  --target-port 8080 \
  --ingress external
```
Azure will build the container, provision the container registry and Container Apps environment, and output your live HTTPS domain (`https://resume-lab-ai-studio.xxxx.azurecontainerapps.io`).

---

## 🤖 Configuring AI Models

Once running locally or on your cloud host:

1. Click the **AI Engine Badge** (`🤖`) in the top navigation bar.
2. Select your preferred intelligence provider:
   - **Local LLM (Ollama)**: Free, private, running on your computer.
   - **Google Gemini**: Fast, high nuance, free tier API key via [Google AI Studio](https://aistudio.google.com/app/apikey).
   - **OpenAI**: GPT-4o / GPT-4o-mini via [OpenAI Platform](https://platform.openai.com/api-keys).
   - **Groq Cloud**: Ultra-fast (200+ tok/s) LLaMA 3.3 70B via [Groq Console](https://console.groq.com/keys).
   - **Anthropic**: Claude 3.5 Sonnet via [Anthropic Console](https://console.anthropic.com/settings/keys).
3. Click **Activate** — all prompt grounding and audits will immediately use your chosen engine.
