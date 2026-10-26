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

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- (Optional) Local [Ollama](https://ollama.com) running `llama3.2` on port 11434

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/rajivrparikh-cissp/ResumeLabAIStudio.git
cd ResumeLabAIStudio

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Studio
```bash
python app/server.py
```
Open your browser to: **`http://localhost:5050`**

### 4. Run Automated E2E Verification
```bash
python tests/test_e2e_pipeline.py
```

---

## ☁️ Cloud Deployment (GCP Project: `passiveincome01`)

### Deploy to Google Cloud Run:
```bash
gcloud config set project passiveincome01
gcloud run deploy resume-lab-studio \
  --source . \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --port 5050
```

---

## 📄 License
Private & Proprietary • Rajiv (Raj) Parikh
