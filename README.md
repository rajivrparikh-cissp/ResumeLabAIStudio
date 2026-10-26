# Resume Lab AI Studio

> **Advanced Agentic Knowledgebase-Driven Tailoring, ATS Synchronization & Document Compiler**

Resume Lab AI Studio is an enterprise-grade AI resume and application studio designed to tailor resumes, generate executive cover letters, and compile print-ready, ATS-compliant Word documents (`.docx`) strictly grounded in a verified career knowledge base.

---

## 🌟 Key Capabilities

1. **5-Stage Application Lifecycle**:
   - **Step 1: Target JD & Live Intelligence**: Real-time keyword extraction, match scoring (0–100%), and domain competency gap analysis.
   - **Step 2: Tailored Resume**: AI-grounded resume drafting with action-verb polish and forensic anti-hallucination audits.
   - **Step 3: Targeted Cover Letter**: Executive storytelling aligned with hiring organization values and candidate voice.
   - **Step 4: Compliance Audit**: Technical gap analysis comparing drafted documents against mandatory JD criteria.
   - **Step 5: Word Document Compiler & Archiving**: Compiles print-ready Word files preserving candidate typography, margins, and section styles.

2. **Resume Template Layout & Synchronization Engine**:
   - Dynamic selection between standard and custom Word (`.docx`) and Markdown (`.md`) templates.
   - In-browser template upload and style inspection.
   - Visual layout sync re-mapping sections into template paragraph styles (`Title`, `Heading 2`, `Heading 3`, `List Bullet`, `Normal`).

3. **Candidate Truth & Anti-Hallucination Guardrails**:
   - Grounded across 26+ local knowledge base files (skills inventory, experience matrix, verified CBA & Tier-1 financial achievements).
   - Strict invariant checks preserving candidate contact details, certifications, and factual employment timelines.

4. **Automated 6-Stage E2E Testing Suite**:
   - In-app **E2E Test SME** modal verifying role switching, cross-contamination prevention, OpenXML validity, and permanent storage.

---

## 🏗️ Project Structure

```text
Resume_lab/
├── app/
│   ├── index.html              # Interactive Web Studio UI & Control Center
│   ├── server.py               # Local Python HTTP API Server (Port 5050)
│   ├── llm_copilot.py          # Grounded document generation & instant tailoring
│   ├── intelligence_engine.py  # JD constraint parser & ATS scoring engine
│   ├── template_manager.py     # Template management, upload, & style inspector
│   ├── application_manager.py  # Application lifecycle & library archiver
│   └── profile_manager.py      # Candidate profile truth management
├── knowledge_base/             # 26+ Grounding files (skills, matrix, tone guides)
├── template/                   # Master Word (.docx) & Markdown (.md) templates
├── scripts/
│   └── compile_docs.py         # Word compiler & visual layout sync engine
├── tests/
│   └── test_e2e_pipeline.py    # 6-Stage automated regression test suite
├── output/                     # Active working documents (.md and .docx)
├── my_applications/            # Permanent library of completed application bundles
└── requirements.txt            # Python dependencies
```

---

## 🤖 AI Engine Flexibility: Cloud GenAI (BYOK) vs. 100% Private Local LLM

Resume Lab AI Studio offers flexible, privacy-first AI intelligence. Choose the setup that fits your workflow:

### Option A: Bring Your Own GenAI API Key (Cloud or Local)
- **Supported Providers**:
  - **Google Gemini** (Gemini 1.5 Flash, Gemini 1.5 Pro) — *Generous free tier at [aistudio.google.com](https://aistudio.google.com/app/apikey)*
  - **OpenAI** (GPT-4o, GPT-4o-mini)
  - **Groq Cloud** (LLaMA 3.3 70B @ 200+ tok/s) — *Free tier at [console.groq.com](https://console.groq.com)*
  - **Anthropic Claude** (Claude 3.5 Sonnet)
- **Works Anywhere**: Use in the live Cloud Run deployment or on your local machine.
- **Client-Side Privacy**: Your API key is stored **only in your browser's local storage** (`localStorage`) and is never written to cloud disks or databases.

### Option B: 100% Private Local LLM (Ollama / LM Studio)
- **Supported Models**: `llama3.2`, `mistral`, `deepseek-r1`, `qwen2.5`, etc.
- **Complete Privacy**: Zero data or prompts ever leave your personal computer. Free forever with no API limits.
- **⚠️ Why Local Installation is Required for Local LLMs**:
  A cloud-hosted website (like Google Cloud Run) **cannot connect to your home computer's `http://localhost:11434`** due to browser cross-origin network security rules. To use your private local Ollama instance, you simply run this app locally on your machine (`http://localhost:5050`).

---

## 🚀 Easy 2-Minute Setup (Non-Technical Friendly)

### 🪟 Windows (1-Click Launch)
1. **Install Ollama** (if using local AI): Download from [ollama.com](https://ollama.com) and run `ollama run llama3.2`.
2. **Download or Clone this App**: Extract the folder onto your computer.
3. **Double-Click `start_studio.bat`**: That's it! It automatically verifies Python, sets up dependencies, and opens `http://localhost:5050` in your default browser.

### 🍎 macOS / Linux (1-Click Launch)
1. **Install Ollama**: Download from [ollama.com](https://ollama.com) and run `ollama run llama3.2`.
2. **Run the Script**: Open Terminal in this folder and type:
   ```bash
   ./start_studio.sh
   ```
   The studio will launch and open automatically in your browser.

---

## 🛠️ Developer & Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
cd ResumeLabAIStudio

# 2. Virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Start Server
python app/server.py
```
Open your browser to: **`http://localhost:5050`**

### Run Automated E2E Verification Suite
```bash
python tests/test_e2e_pipeline.py
```

---

## ☁️ Google Cloud Run Live Deployment

- **Live URL**: [https://resume-lab-ai-studio-135378541186.australia-southeast1.run.app](https://resume-lab-ai-studio-135378541186.australia-southeast1.run.app)
- **GCP Project**: `passiveincome01`
- **Region**: `australia-southeast1` (Sydney)
- **Security Policy**: Zero-Cloud PII Architecture. Strictly stateless compute with non-root Docker execution (`appuser:10001`). All user resumes and knowledge base files remain on each user's local machine.

---

## 📄 License
MIT License • Open Source for personal career empowerment.
