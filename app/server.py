import http.server
import socketserver
import urllib.parse
import json
import os
import sys
import subprocess
import datetime
import traceback

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from intelligence_engine import load_kb_data, analyze_jd_alignment, extract_jd_metadata, simulate_ats_analysis
from application_manager import list_applications, save_application, load_application_files, detect_company_and_title, MY_APPS_DIR, get_active_target, set_active_target
from llm_copilot import (
    get_ollama_status, grounded_improve_text, audit_hallucinations_with_llama, 
    generate_grounded_document, build_instant_tailored_resume, build_instant_tailored_cover_letter,
    test_llm_connection, query_llm
)
from profile_manager import get_candidate_profile, save_candidate_profile, apply_profile_to_active_docs
from template_manager import list_templates, get_active_template, set_active_template, inspect_template_details, save_uploaded_template

PORT = int(os.environ.get("PORT", 5050))

class ResumeLabHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def read_post_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(post_data)
        except Exception:
            return {}

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.serve_file(os.path.join(os.path.dirname(__file__), "index.html"), "text/html")
        elif path == "/api/status":
            self.handle_get_status()
        elif path == "/api/jd":
            self.handle_get_jd()
        elif path == "/api/outputs":
            self.handle_get_outputs()
        elif path == "/api/kb":
            self.handle_get_kb()
        elif path == "/api/history":
            self.handle_get_history()
        elif path == "/api/ats-audit":
            self.handle_ats_audit()
        elif path == "/api/applications":
            self.handle_get_applications()
        elif path == "/api/applications/detect":
            self.handle_detect_application()
        elif path == "/api/applications/download":
            self.handle_download_application_file(parsed)
        elif path == "/api/llm/status":
            self.handle_llm_status()
        elif path == "/api/profile":
            self.handle_get_profile()
        elif path == "/api/target":
            self.handle_get_target()
        elif path == "/api/auto-tailor-resume":
            self.handle_auto_tailor_resume()
        elif path == "/api/run-e2e-tests":
            self.handle_run_e2e_tests()
        elif path == "/api/templates":
            self.handle_get_templates()
        elif path == "/api/templates/inspect":
            self.handle_inspect_template(parsed)
        elif path.startswith("/api/download/"):
            filename = os.path.basename(path)
            file_path = os.path.join(BASE_DIR, "output", filename)
            if not os.path.exists(file_path):
                file_path = os.path.join(BASE_DIR, filename)
            if not os.path.exists(file_path):
                file_path = os.path.join(BASE_DIR, "template", filename)
            if os.path.exists(file_path):
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if filename.endswith(".docx") else "text/markdown"
                self.serve_file(file_path, content_type, as_attachment=True, download_name=filename)
            else:
                self.send_json({"error": "File not found"}, 404)
        else:
            self.send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/jd":
            self.handle_save_jd()
        elif path == "/api/analyze":
            self.handle_analyze()
        elif path == "/api/ats-audit":
            self.handle_ats_audit()
        elif path == "/api/save-outputs":
            self.handle_save_outputs()
        elif path == "/api/compile":
            self.handle_compile()
        elif path == "/api/kb":
            self.handle_save_kb()
        elif path == "/api/load-history":
            self.handle_load_history()
        elif path == "/api/applications/save":
            self.handle_save_application()
        elif path == "/api/applications/load":
            self.handle_load_application()
        elif path == "/api/llm/improve":
            self.handle_llm_improve()
        elif path == "/api/llm/audit":
            self.handle_llm_audit()
        elif path == "/api/llm/generate":
            self.handle_llm_generate()
        elif path == "/api/llm/test-connection":
            self.handle_llm_test_connection()
        elif path == "/api/profile":
            self.handle_save_profile()
        elif path == "/api/profile/apply":
            self.handle_apply_profile()
        elif path == "/api/target":
            self.handle_save_target()
        elif path == "/api/auto-tailor-resume":
            self.handle_auto_tailor_resume()
        elif path == "/api/run-e2e-tests":
            self.handle_run_e2e_tests()
        elif path == "/api/templates/select":
            self.handle_select_template()
        elif path == "/api/templates/upload":
            self.handle_upload_template()
        elif path == "/api/format-resume-template":
            self.handle_format_resume_template()
        else:
            self.send_json({"error": "Not Found"}, 404)

    def serve_file(self, file_path, content_type, as_attachment=False, download_name=None):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            if as_attachment:
                name = download_name or os.path.basename(file_path)
                self.send_header("Content-Disposition", f'attachment; filename="{name}"')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_get_status(self):
        jd_path = os.path.join(BASE_DIR, "target_jd.md")
        resume_docx = os.path.join(BASE_DIR, "output", "tailored_resume.docx")
        cl_docx = os.path.join(BASE_DIR, "output", "tailored_cover_letter.docx")
        resume_md = os.path.join(BASE_DIR, "output", "tailored_resume.md")
        cl_md = os.path.join(BASE_DIR, "output", "tailored_cover_letter.md")
        report_md = os.path.join(BASE_DIR, "output", "compliance_report.md")

        jd_text = ""
        if os.path.exists(jd_path):
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        
        target = get_active_target()
        if target and target.get("company"):
            meta = target
        else:
            meta = extract_jd_metadata(jd_text)

        status_data = {
            "active_role": meta["title"],
            "active_company": meta["company"],
            "active_template": get_active_template(),
            "jd_updated": datetime.datetime.fromtimestamp(os.path.getmtime(jd_path)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(jd_path) else None,
            "has_resume_docx": os.path.exists(resume_docx),
            "resume_docx_updated": datetime.datetime.fromtimestamp(os.path.getmtime(resume_docx)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(resume_docx) else None,
            "has_cl_docx": os.path.exists(cl_docx),
            "cl_docx_updated": datetime.datetime.fromtimestamp(os.path.getmtime(cl_docx)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(cl_docx) else None,
            "has_resume_md": os.path.exists(resume_md),
            "has_cl_md": os.path.exists(cl_md),
            "has_report_md": os.path.exists(report_md)
        }
        self.send_json(status_data)

    def handle_get_jd(self):
        jd_path = os.path.join(BASE_DIR, "target_jd.md")
        jd_text = ""
        if os.path.exists(jd_path):
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        
        kb_files = load_kb_data(BASE_DIR)
        analysis = analyze_jd_alignment(jd_text, kb_files)
        target = get_active_target()
        if target:
            analysis["metadata"] = {"company": target["company"], "title": target["title"]}
        self.send_json({"jd": jd_text, "analysis": analysis, "target": target})

    def handle_save_jd(self):
        data = self.read_post_json()
        jd_text = data.get("jd", "").strip()
        company = data.get("company", "").strip()
        title = data.get("title", "").strip()

        # Update active target if company or title supplied
        if company or title:
            curr = get_active_target() or {}
            c = company or curr.get("company", "Target Company")
            t = title or curr.get("title", "Infrastructure Manager")
            set_active_target(c, t)
        else:
            det = detect_company_and_title(jd_text)
            set_active_target(det["company"], det["title"])

        jd_path = os.path.join(BASE_DIR, "target_jd.md")
        with open(jd_path, "w", encoding="utf-8") as f:
            f.write(jd_text)
        
        kb_files = load_kb_data(BASE_DIR)
        analysis = analyze_jd_alignment(jd_text, kb_files)
        target = get_active_target()
        if target:
            analysis["metadata"] = {"company": target["company"], "title": target["title"]}

        # CRITICAL AUTO-REGENERATION:
        # Immediately build freshly tailored resume & cover letter matching new role & company!
        t_comp = target["company"] if target else "Target Company"
        t_tit = target["title"] if target else "Technology Leader"
        
        tailored_resume = build_instant_tailored_resume(t_comp, t_tit, jd_text)
        with open(os.path.join(BASE_DIR, "output", "tailored_resume.md"), "w", encoding="utf-8") as f:
            f.write(tailored_resume)
            
        tailored_cl = build_instant_tailored_cover_letter(t_comp, t_tit, jd_text)
        with open(os.path.join(BASE_DIR, "output", "tailored_cover_letter.md"), "w", encoding="utf-8") as f:
            f.write(tailored_cl)

        self.send_json({
            "success": True, 
            "analysis": analysis, 
            "target": target,
            "resume": tailored_resume,
            "cover_letter": tailored_cl
        })

    def handle_get_target(self):
        target = get_active_target()
        if not target or "responsibilities" in target.get("title", "").lower():
            jd_path = os.path.join(BASE_DIR, "target_jd.md")
            jd_text = ""
            if os.path.exists(jd_path):
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
            target = detect_company_and_title(jd_text)
            set_active_target(target["company"], target["title"])
        self.send_json(target)

    def handle_save_target(self):
        data = self.read_post_json()
        company = data.get("company", "").strip()
        title = data.get("title", "").strip()
        target = set_active_target(company, title)
        
        # When target is updated, realign resume & cover letter
        jd_path = os.path.join(BASE_DIR, "target_jd.md")
        jd_text = ""
        if os.path.exists(jd_path):
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()

        tailored_resume = build_instant_tailored_resume(target["company"], target["title"], jd_text)
        with open(os.path.join(BASE_DIR, "output", "tailored_resume.md"), "w", encoding="utf-8") as f:
            f.write(tailored_resume)
            
        tailored_cl = build_instant_tailored_cover_letter(target["company"], target["title"], jd_text)
        with open(os.path.join(BASE_DIR, "output", "tailored_cover_letter.md"), "w", encoding="utf-8") as f:
            f.write(tailored_cl)

        self.send_json({
            "success": True, 
            "target": target,
            "resume": tailored_resume,
            "cover_letter": tailored_cl
        })

    def handle_auto_tailor_resume(self):
        data = self.read_post_json() if self.command == "POST" else {}
        target = get_active_target() or {}
        company = data.get("company") or target.get("company", "Target Company")
        title = data.get("title") or target.get("title", "Technology Leader")
        jd_path = os.path.join(BASE_DIR, "target_jd.md")
        jd_text = data.get("jd") or ""
        if not jd_text and os.path.exists(jd_path):
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()

        tailored_resume = build_instant_tailored_resume(company, title, jd_text)
        with open(os.path.join(BASE_DIR, "output", "tailored_resume.md"), "w", encoding="utf-8") as f:
            f.write(tailored_resume)

        self.send_json({
            "success": True, 
            "generated_text": tailored_resume,
            "company": company,
            "title": title
        })

    def handle_run_e2e_tests(self):
        try:
            test_script = os.path.join(BASE_DIR, "tests", "test_e2e_pipeline.py")
            if not os.path.exists(test_script):
                self.send_json({"success": False, "error": "Test suite script not found"}, 404)
                return
            result = subprocess.run(
                [sys.executable, test_script],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                timeout=60
            )
            report_path = os.path.join(BASE_DIR, "output", "e2e_test_report.json")
            report_data = {}
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)
            self.send_json({
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "report": report_data
            })
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

    def handle_analyze(self):
        data = self.read_post_json()
        jd_text = data.get("jd", "")
        if not jd_text:
            jd_path = os.path.join(BASE_DIR, "target_jd.md")
            if os.path.exists(jd_path):
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
        kb_files = load_kb_data(BASE_DIR)
        analysis = analyze_jd_alignment(jd_text, kb_files)
        self.send_json(analysis)

    def handle_ats_audit(self):
        data = {}
        if self.command == "POST":
            data = self.read_post_json()
        
        resume_text = data.get("resume")
        if not resume_text:
            resume_path = os.path.join(BASE_DIR, "output", "tailored_resume.md")
            if os.path.exists(resume_path):
                with open(resume_path, "r", encoding="utf-8") as f:
                    resume_text = f.read()
            else:
                resume_text = ""
                
        jd_text = data.get("jd")
        if not jd_text:
            jd_path = os.path.join(BASE_DIR, "target_jd.md")
            if os.path.exists(jd_path):
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
            else:
                jd_text = ""
                
        ats_results = simulate_ats_analysis(resume_text, jd_text)
        self.send_json(ats_results)

    def handle_get_outputs(self):
        def read_file(name):
            p = os.path.join(BASE_DIR, "output", name)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
            return ""

        outputs = {
            "resume": read_file("tailored_resume.md"),
            "cover_letter": read_file("tailored_cover_letter.md"),
            "compliance_report": read_file("compliance_report.md")
        }
        self.send_json(outputs)

    def handle_save_outputs(self):
        data = self.read_post_json()
        out_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(out_dir, exist_ok=True)
        
        if "resume" in data:
            with open(os.path.join(out_dir, "tailored_resume.md"), "w", encoding="utf-8") as f:
                f.write(data["resume"])
        if "cover_letter" in data:
            with open(os.path.join(out_dir, "tailored_cover_letter.md"), "w", encoding="utf-8") as f:
                f.write(data["cover_letter"])
        if "compliance_report" in data:
            with open(os.path.join(out_dir, "compliance_report.md"), "w", encoding="utf-8") as f:
                f.write(data["compliance_report"])

        self.send_json({"success": True, "message": "Outputs saved successfully"})

    def handle_compile(self):
        try:
            data = self.read_post_json() if self.headers.get('Content-Length') else {}
            template_name = data.get("template") or get_active_template()
            
            venv_python = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
            if not os.path.exists(venv_python):
                venv_python = sys.executable
            
            script_path = os.path.join(BASE_DIR, "scripts", "compile_docs.py")
            cmd = [venv_python, script_path, "--resume-template", template_name]
            res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=45)
            
            if res.returncode == 0:
                self.send_json({
                    "success": True, 
                    "template_used": template_name,
                    "stdout": res.stdout,
                    "compiled_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            else:
                self.send_json({
                    "success": False, 
                    "error": res.stderr or res.stdout
                }, 500)
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

    def handle_get_kb(self):
        kb_files = load_kb_data(BASE_DIR)
        self.send_json(kb_files)

    def handle_save_kb(self):
        data = self.read_post_json()
        filename = data.get("filename")
        content = data.get("content")
        if filename and content is not None:
            safe_name = os.path.basename(filename)
            kb_path = os.path.join(BASE_DIR, "knowledge_base", safe_name)
            with open(kb_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.send_json({"success": True, "message": f"{safe_name} saved"})
        else:
            self.send_json({"error": "Invalid payload"}, 400)

    def handle_get_history(self):
        history = [
            {"title": "Vice President, Information Security Threat & Insider Risk", "company": "Bank of America", "tag": "Active (Latest)"},
            {"title": "Senior Manager Technology Operational Risk Management", "company": "Macquarie Group", "tag": "Financial Services"},
            {"title": "Head of Technology - Workplace Operations", "company": "icare", "tag": "Workforce & Operations"},
            {"title": "Head of Infrastructure & Security", "company": "DataMesh Group", "tag": "Fintech / Payments"},
            {"title": "Cyber Incident Response Manager", "company": "Critical Infrastructure", "tag": "Cyber Operations"},
            {"title": "IT Manager (Systems, ERP & Operations)", "company": "Tilray Brands", "tag": "CPG & ERP"},
            {"title": "IT Manager (Automation/OEM)", "company": "Geely", "tag": "Automotive & OEM"}
        ]
        self.send_json(history)

    def handle_load_history(self):
        data = self.read_post_json()
        target = data.get("company", "")
        # Check my_applications directory for matching files
        my_app_dir = os.path.join(BASE_DIR, "my_applications")
        loaded_jd = ""
        
        if os.path.exists(my_app_dir):
            for entry in os.listdir(my_app_dir):
                if target.lower() in entry.lower():
                    cand_path = os.path.join(my_app_dir, entry, "JD.docx")
                    if os.path.exists(cand_path):
                        try:
                            import docx
                            doc = docx.Document(cand_path)
                            loaded_jd = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                        except Exception:
                            pass
        
        if loaded_jd:
            jd_path = os.path.join(BASE_DIR, "target_jd.md")
            with open(jd_path, "w", encoding="utf-8") as f:
                f.write(loaded_jd)
            kb_files = load_kb_data(BASE_DIR)
            analysis = analyze_jd_alignment(loaded_jd, kb_files)
            self.send_json({"success": True, "jd": loaded_jd, "analysis": analysis})
        else:
            self.send_json({"error": "Historical JD document not found for that company"}, 404)

    def handle_get_applications(self):
        apps = list_applications()
        self.send_json({"applications": apps, "total": len(apps)})

    def handle_detect_application(self):
        jd_path = os.path.join(BASE_DIR, "target_jd.md")
        jd_text = ""
        if os.path.exists(jd_path):
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        det = detect_company_and_title(jd_text)
        self.send_json(det)

    def handle_save_application(self):
        data = self.read_post_json()
        company = data.get("company")
        title = data.get("title")
        custom_folder = data.get("custom_folder")
        if not company or not title:
            jd_path = os.path.join(BASE_DIR, "target_jd.md")
            jd_text = ""
            if os.path.exists(jd_path):
                with open(jd_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
            det = detect_company_and_title(jd_text)
            company = company or det["company"]
            title = title or det["title"]

        res = save_application(company, title, custom_folder)
        self.send_json(res)

    def handle_load_application(self):
        data = self.read_post_json()
        folder_name = data.get("folder_name")
        if not folder_name:
            self.send_json({"error": "Folder name required"}, 400)
            return
        try:
            res = load_application_files(folder_name)
            kb_files = load_kb_data(BASE_DIR)
            res["analysis"] = analyze_jd_alignment(res["jd"], kb_files)
            self.send_json({"success": True, **res})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_download_application_file(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        folder = qs.get("folder", [""])[0]
        fname = qs.get("file", [""])[0]
        if not folder or not fname:
            self.send_json({"error": "Missing folder or file parameter"}, 400)
            return
        safe_folder = os.path.basename(folder)
        safe_fname = os.path.basename(fname)
        fpath = os.path.join(MY_APPS_DIR, safe_folder, safe_fname)
        if os.path.exists(fpath):
            ctype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if safe_fname.endswith(".docx") else "text/markdown"
            self.serve_file(fpath, ctype, as_attachment=True, download_name=safe_fname)
        else:
            self.send_json({"error": "File not found"}, 404)

    def handle_llm_status(self):
        ollama_status = get_ollama_status()
        self.send_json({
            **ollama_status,
            "supported_providers": [
                {
                    "id": "local",
                    "name": "Local LLM (Ollama / LM Studio)",
                    "requires_local_app": True,
                    "description": "100% Private, Free, Runs on your machine. (Requires running app on localhost)",
                    "default_model": ollama_status.get("default_model", "llama3.2"),
                    "models": ollama_status.get("models", ["llama3.2", "mistral", "deepseek-r1"])
                },
                {
                    "id": "gemini",
                    "name": "Google Gemini API (BYOK)",
                    "requires_local_app": False,
                    "description": "High intelligence, fast, generous free tier at Google AI Studio. Works in Cloud or Local.",
                    "default_model": "gemini-1.5-flash",
                    "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
                    "has_env_key": bool(os.environ.get("GEMINI_API_KEY"))
                },
                {
                    "id": "openai",
                    "name": "OpenAI API (BYOK)",
                    "requires_local_app": False,
                    "description": "Industry standard GPT-4o & GPT-4o-mini models. Works in Cloud or Local.",
                    "default_model": "gpt-4o-mini",
                    "models": ["gpt-4o-mini", "gpt-4o"],
                    "has_env_key": bool(os.environ.get("OPENAI_API_KEY"))
                },
                {
                    "id": "groq",
                    "name": "Groq Cloud API (BYOK - Ultra Fast)",
                    "requires_local_app": False,
                    "description": "Instant generation with open-source models (LLaMA 3.3 70B). Free tier available.",
                    "default_model": "llama-3.3-70b-versatile",
                    "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
                    "has_env_key": bool(os.environ.get("GROQ_API_KEY"))
                },
                {
                    "id": "anthropic",
                    "name": "Anthropic Claude API (BYOK)",
                    "requires_local_app": False,
                    "description": "Exceptional nuance and executive prose style (Claude 3.5 Sonnet).",
                    "default_model": "claude-3-5-sonnet-20241022",
                    "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                    "has_env_key": bool(os.environ.get("ANTHROPIC_API_KEY"))
                }
            ]
        })

    def handle_llm_test_connection(self):
        data = self.read_post_json()
        provider = data.get("provider", "local")
        model = data.get("model", "")
        api_key = data.get("api_key", "")
        ollama_url = data.get("ollama_url", None)
        result = test_llm_connection(provider=provider, model=model, api_key=api_key, ollama_url=ollama_url)
        status_code = 200 if result.get("success") else 400
        self.send_json(result, status_code)

    def handle_llm_improve(self):
        data = self.read_post_json()
        text = data.get("text", "")
        doc_type = data.get("doc_type", "resume")
        jd_text = data.get("jd_text", "")
        instructions = data.get("instructions", "")
        model = data.get("model", "llama3.2")
        provider = data.get("provider", "local")
        api_key = data.get("api_key", "")
        ollama_url = data.get("ollama_url", None)
        if not text:
            self.send_json({"error": "No text provided to improve"}, 400)
            return
        result = grounded_improve_text(text, doc_type, jd_text, instructions, model=model, provider=provider, api_key=api_key, ollama_url=ollama_url)
        self.send_json(result)

    def handle_llm_audit(self):
        data = self.read_post_json()
        resume_text = data.get("resume_text", "")
        jd_text = data.get("jd_text", "")
        model = data.get("model", "llama3.2")
        provider = data.get("provider", "local")
        api_key = data.get("api_key", "")
        ollama_url = data.get("ollama_url", None)
        if not resume_text:
            r_path = os.path.join(BASE_DIR, "output", "tailored_resume.md")
            if os.path.exists(r_path):
                with open(r_path, "r", encoding="utf-8") as f:
                    resume_text = f.read()
            else:
                self.send_json({"error": "No resume text provided or found in output"}, 400)
                return
        result = audit_hallucinations_with_llama(resume_text, jd_text, model=model, provider=provider, api_key=api_key, ollama_url=ollama_url)
        self.send_json(result)

    def handle_llm_generate(self):
        data = self.read_post_json()
        doc_type = data.get("doc_type", "resume")
        jd_text = data.get("jd_text", "")
        model = data.get("model", "llama3.2")
        provider = data.get("provider", "local")
        api_key = data.get("api_key", "")
        ollama_url = data.get("ollama_url", None)
        company = data.get("company", "")
        title = data.get("title", "")
        instant = data.get("instant", False)
        if not jd_text:
            jd_path = os.path.join(BASE_DIR, "target_jd.md")
            if os.path.exists(jd_path):
                try:
                    with open(jd_path, "r", encoding="utf-8") as f:
                        jd_text = f.read()
                except Exception:
                    pass
        if not company or not title:
            det = detect_company_and_title(jd_text)
            company = company or det.get("company", "Target Company")
            title = title or det.get("title", "Infrastructure Manager")

        if instant and doc_type == "cl":
            from llm_copilot import build_instant_tailored_cover_letter
            result = {"success": True, "generated_text": build_instant_tailored_cover_letter(company, title, jd_text)}
        else:
            result = generate_grounded_document(doc_type=doc_type, jd_text=jd_text, model=model, target_company=company, target_title=title, provider=provider, api_key=api_key, ollama_url=ollama_url)
        self.send_json(result)

    def handle_get_profile(self):
        prof = get_candidate_profile()
        self.send_json(prof)

    def handle_save_profile(self):
        data = self.read_post_json()
        saved = save_candidate_profile(data)
        self.send_json({"success": True, "profile": saved})

    def handle_apply_profile(self):
        data = self.read_post_json()
        if data:
            saved = save_candidate_profile(data)
        else:
            saved = get_candidate_profile()
        res = apply_profile_to_active_docs(saved)
        self.send_json(res)

    def handle_get_templates(self):
        data = list_templates()
        self.send_json(data)

    def handle_inspect_template(self, parsed):
        qs = urllib.parse.parse_qs(parsed.query)
        template_name = qs.get("name", [""])[0]
        if not template_name:
            template_name = get_active_template()
        details = inspect_template_details(template_name)
        self.send_json(details)

    def handle_select_template(self):
        data = self.read_post_json()
        template_name = data.get("template")
        if not template_name:
            self.send_json({"error": "No template specified"}, 400)
            return
        try:
            active = set_active_template(template_name)
            self.send_json({"success": True, "active_template": active})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 400)

    def handle_upload_template(self):
        data = self.read_post_json()
        filename = data.get("filename")
        if not filename:
            self.send_json({"error": "No filename provided"}, 400)
            return
            
        import base64
        try:
            if "content_base64" in data:
                raw_bytes = base64.b64decode(data["content_base64"])
                res = save_uploaded_template(filename, data_bytes=raw_bytes)
            elif "content_text" in data:
                res = save_uploaded_template(filename, text_content=data["content_text"])
            else:
                self.send_json({"error": "No content provided in upload payload"}, 400)
                return
                
            res["templates_list"] = list_templates()
            self.send_json(res)
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

    def handle_format_resume_template(self):
        try:
            data = self.read_post_json()
            template_name = data.get("template") or get_active_template()
            if template_name:
                try:
                    set_active_template(template_name)
                except Exception:
                    pass
                
            venv_python = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
            if not os.path.exists(venv_python):
                venv_python = sys.executable
                
            script_path = os.path.join(BASE_DIR, "scripts", "compile_docs.py")
            cmd = [venv_python, script_path, "--resume-template", template_name, "--resume-only", "--skip-archive"]
            res = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
            
            docx_path = os.path.join(BASE_DIR, "output", "tailored_resume.docx")
            docx_exists = os.path.exists(docx_path)
            docx_size = os.path.getsize(docx_path) if docx_exists else 0
            
            if res.returncode == 0 and docx_exists:
                self.send_json({
                    "success": True,
                    "template": template_name,
                    "docx_bytes": docx_size,
                    "compiled_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "stdout": res.stdout
                })
            else:
                self.send_json({
                    "success": False,
                    "error": res.stderr or res.stdout
                }, 500)
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ('', PORT)
    httpd = socketserver.TCPServer(server_address, ResumeLabHandler)
    print(f"Resume Lab Intelligent Studio running on port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
