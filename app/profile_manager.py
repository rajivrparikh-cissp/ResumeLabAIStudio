import os
import json
import re
import subprocess
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from storage_config import get_kb_dir, get_output_dir

def get_profile_path():
    return os.path.join(get_kb_dir(), "candidate_profile.json")

DEFAULT_PROFILE = {
    "full_name": "Senior Technology Leader",
    "preferred_name": "Candidate",
    "address": "Sydney, NSW, Australia",
    "phone": "+61 400 000 000",
    "email": "candidate@example.com",
    "citizenship": "Australian Citizen / Permanent Resident",
    "linkedin": "https://www.linkedin.com/in/candidate",
    "portfolio_url": "https://github.com/candidate",
    "total_years_experience": "20+",
    "target_title": "Head of Technology & Cybersecurity / Infrastructure Director",
    "core_credentials": "CISSP | CISM | Cloud Architecture | DevOps | Executive Leadership",
    "executive_summary_baseline": "Strategic and hands-on Technology Leader with extensive experience directing infrastructure engineering, cloud operations, and cybersecurity governance within enterprise and regulated environments. Proven track record partnering with C-level executives to establish technology roadmaps, govern digital resilience, and scale secure, resilient enterprise systems."
}

def get_candidate_profile():
    profile_path = get_profile_path()
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all keys exist
                for k, v in DEFAULT_PROFILE.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return DEFAULT_PROFILE.copy()

def save_candidate_profile(data):
    current = get_candidate_profile()
    for k, v in data.items():
        if k in DEFAULT_PROFILE:
            current[k] = str(v).strip()
            
    profile_path = get_profile_path()
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
        
    # Also update formatting_guide.md and relevant KB files
    update_kb_source_files(current)
    return current

def update_kb_source_files(profile):
    formatting_guide = os.path.join(get_kb_dir(), "formatting_guide.md")
    if os.path.exists(formatting_guide):
        try:
            with open(formatting_guide, "r", encoding="utf-8") as f:
                content = f.read()
            # Update contact info example
            new_contact = f"{profile.get('address', '')} | {profile.get('phone', '')} | {profile.get('email', '')} | {profile.get('citizenship', '')}"
            content = re.sub(
                r'Contact:.*?(?=\| LinkedIn|\n|\))',
                f"Contact: {new_contact} ",
                content
            )
            with open(formatting_guide, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print("Error updating formatting_guide:", e)

def apply_profile_to_active_docs(profile=None):
    if profile is None:
        profile = get_candidate_profile()

    new_address = profile.get("address", "")
    new_phone = profile.get("phone", "")
    new_email = profile.get("email", "")
    new_years = profile.get("total_years_experience", "25+")
    new_contact_line = f"{new_address} | {new_phone} | {new_email} | {profile.get('citizenship', 'Australian Citizen')}"

    output_dir = get_output_dir()

    # 1. Update tailored_cover_letter.md
    cl_path = os.path.join(output_dir, "tailored_cover_letter.md")
    if os.path.exists(cl_path):
        try:
            with open(cl_path, "r", encoding="utf-8") as f:
                cl_text = f.read()
            # Replace address / contact line (typically line 2 or 3)
            cl_lines = cl_text.splitlines()
            for i in range(min(5, len(cl_lines))):
                if any(x in cl_lines[i] for x in ["0433", "@", "NSW", "Citizen", "Carlingford"]):
                    cl_lines[i] = new_contact_line
                    break
            updated_cl = "\n".join(cl_lines)
            
            # Replace 20+ years or 20 years with 25+ years
            updated_cl = re.sub(r'20\+?\s*years', f"{new_years} years", updated_cl, flags=re.IGNORECASE)
            # Clean any triple quote remnants
            updated_cl = re.sub(r'^"""\s*', '', updated_cl)
            updated_cl = re.sub(r'\s*"""$', '', updated_cl)
            
            with open(cl_path, "w", encoding="utf-8") as f:
                f.write(updated_cl)
        except Exception as e:
            print("Error updating tailored_cover_letter.md:", e)

    # 2. Update tailored_resume.md
    resume_path = os.path.join(output_dir, "tailored_resume.md")
    if os.path.exists(resume_path):
        try:
            with open(resume_path, "r", encoding="utf-8") as f:
                r_text = f.read()
            # Replace 20+ years with 25+ years
            r_text = re.sub(r'20\+?\s*years', f"{new_years} years", r_text, flags=re.IGNORECASE)
            with open(resume_path, "w", encoding="utf-8") as f:
                f.write(r_text)
        except Exception as e:
            print("Error updating tailored_resume.md:", e)

    # 3. Update compliance_report.md
    report_path = os.path.join(output_dir, "compliance_report.md")
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                rep_text = f.read()
            rep_text = re.sub(r'20\+?\s*years', f"{new_years} years", rep_text, flags=re.IGNORECASE)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(rep_text)
        except Exception as e:
            print("Error updating compliance_report.md:", e)

    # 4. Trigger re-compilation of Word docs
    venv_python = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable
        
    script_path = os.path.join(BASE_DIR, "scripts", "compile_docs.py")
    try:
        proc = subprocess.run([venv_python, script_path], cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
        return {
            "success": True,
            "profile": profile,
            "stdout": proc.stdout,
            "stderr": proc.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "profile": profile
        }
