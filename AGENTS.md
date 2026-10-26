# Advanced Knowledgebase-Driven Resume Lab Blueprint

## Execution Protocol

### Step 1: Scan and Interrogate Knowledge Base (Local - Qwen3.6)
1. Read `target_jd.md` to identify the target position's core requirements.
2. Read `knowledge_base/skills_inventory.md` and `knowledge_base/experience_matrix.md`.
3. Highlight the specific achievements and keywords from the knowledge base that directly answer the target job description's constraints.

### Step 2: Assemble Tailored Resume (Local - Gemma4)
1. Generate an optimized resume draft inside `output/tailored_resume.md`.
2. Pull the most relevant, high-impact bullet points identified from `knowledge_base/experience_matrix.md`.
3. Format the text according to the layout styles defined in `knowledge_base/tone_guide.md`.
4. **Guardrail:** Do not alter historical employment dates or invent any achievements not explicitly found in the knowledge base.

### Step 3: Polish Narrative & Cover Letter (Cloud - GLM-5.2)
1. Pass the generated resume draft along with the styling rules in `knowledge_base/tone_guide.md` to the cloud endpoint.
2. Generate a cohesive, single-page cover letter inside `output/tailored_cover_letter.md`. 
3. Ensure the writing matches the user's natural storytelling voice perfectly.

### Step 4: Technical Gap Analysis & Compliance Check (Cloud - Kimi)
1. Compare `output/tailored_resume.md` back against `target_jd.md`.
2. Verify that all mandatory keywords from the job description are accurately accounted for.
3. Output a structured feedback table inside `output/compliance_report.md` detailing match scoring and outlining potential improvement areas.

### Step 5: Compile Documents to Word Format (Local)
1. Use the local virtual environment `.venv` to run the python compiler script:
   `python scripts/compile_docs.py`
2. This script loads the template files `C:\Users\rajpa\OneDrive\Resume_lab\template\Resume of Raj Parikh.docx` and `C:\Users\rajpa\OneDrive\Resume_lab\template\Cover Letter.docx` to preserve the candidate's exact formatting, margins, and typography.
3. Outputs `output/tailored_resume.docx` and `output/tailored_cover_letter.docx` as print-ready Word files.

### Step 6: Permanent Application Archiving & Library Storage (Local)
1. Automatically archive the complete application bundle into the candidate's permanent storage library:
   `my_applications/<CompanyName> - <Job Title>/`
2. The folder contains all 6 core application assets:
   - `target_jd.md`: The verbatim target job description.
   - `tailored_resume.md`: The markdown resume tailored for the role.
   - `tailored_cover_letter.md`: The tailored single-page cover letter.
   - `compliance_report.md`: The technical gap analysis and match scorecard.
   - `tailored_resume.docx`: The print-ready, ATS-compliant Word resume.
   - `tailored_cover_letter.docx`: The print-ready Word cover letter.
   - `application_meta.json`: Application metadata (company, title, timestamp, files).
3. The candidate can search, inspect, or reload any past application into the studio from this folder at any time.