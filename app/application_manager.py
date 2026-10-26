import os
import re
import json
import shutil
import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MY_APPS_DIR = os.path.join(BASE_DIR, "my_applications")

ACTIVE_TARGET_FILE = os.path.join(BASE_DIR, "output", "active_target.json")

def sanitize_filename(name):
    if not name:
        return ""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", str(name))
    return re.sub(r'\s+', " ", cleaned).strip()

def get_active_target():
    if os.path.exists(ACTIVE_TARGET_FILE):
        try:
            with open(ACTIVE_TARGET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("company") and data.get("title"):
                    return data
        except Exception:
            pass
    return None

def set_active_target(company, title):
    os.makedirs(os.path.dirname(ACTIVE_TARGET_FILE), exist_ok=True)
    clean_company = sanitize_filename(company) or "Target Company"
    clean_title = sanitize_filename(title) or "Target Role"
    data = {
        "company": clean_company,
        "title": clean_title,
        "folder_name": f"{clean_company} - {clean_title}",
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(ACTIVE_TARGET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data

def detect_company_and_title(jd_text):
    # 1. Check explicit markdown bold markers first
    if jd_text:
        m_co = re.search(r'\*\*Company:\*\*\s*(.+)', jd_text, re.I)
        m_ti = re.search(r'\*\*Job Title:\*\*\s*(.+)', jd_text, re.I)
        if m_co and m_ti:
            c = sanitize_filename(m_co.group(1).split("|")[0].strip())
            t = sanitize_filename(m_ti.group(1).split("|")[0].strip())
            return {"company": c, "title": t, "folder_name": f"{c} - {t}"}

    # 2. Check active target explicitly set by user
    active = get_active_target()
    if active and active.get("company") and active.get("title") and active["company"] != "Target Company":
        if "responsibilities" not in active["title"].lower():
            return active

    company = "Target Company"
    title = "Target Role"
    
    if not jd_text:
        if active and active.get("company"):
            return active
        return {"company": company, "title": title, "folder_name": f"{company} - {title}"}
        
    lines = [l.strip() for l in jd_text.strip().split("\n") if l.strip()]
    
    # 1. Check explicit markdown bold markers
    m_co = re.search(r'\*\*Company:\*\*\s*(.+)', jd_text, re.I)
    if m_co:
        company = m_co.group(1).split("|")[0].strip()
    else:
        # Check known brands
        lower_jd = jd_text.lower()
        if "kia" in lower_jd:
            company = "Kia Motors"
        elif "bank of america" in lower_jd:
            company = "Bank of America"
        elif "macquarie" in lower_jd:
            company = "Macquarie Group"
        elif "tilray" in lower_jd:
            company = "Tilray Brands"
        elif "datamesh" in lower_jd:
            company = "DataMesh Group"
        elif "icare" in lower_jd:
            company = "icare"
        elif "geely" in lower_jd:
            company = "Geely"
        elif "anthropic" in lower_jd:
            company = "Anthropic"
        elif "amazon" in lower_jd:
            company = "Amazon"
        elif "atlassian" in lower_jd:
            company = "Atlassian"
        else:
            # Pattern like "About [Company]" ignoring common section headers
            for line in lines[:10]:
                m_about = re.search(r'About\s+([A-Za-z0-9\s&,]+?)(?:,|\.|\n|Inc|Pty|Ltd|$)', line, re.I)
                if m_about:
                    cand = m_about.group(1).strip()
                    if cand.lower() not in ["the role", "the job", "you", "us", "this role"]:
                        company = cand
                        break

    # 2. Check title
    m_ti = re.search(r'\*\*Job Title:\*\*\s*(.+)', jd_text, re.I)
    m_as = re.search(r'As\s+([A-Za-z0-9\s/&-]+(?:Manager|Leader|Director|Architect|Lead|Engineer|Consultant|Specialist)),?\s+you', jd_text, re.I)
    if m_ti:
        title = m_ti.group(1).split("|")[0].strip()
    elif m_as:
        title = m_as.group(1).strip()
    else:
        lower_jd = jd_text.lower()
        if "network and security" in lower_jd or "security and network" in lower_jd:
            title = "IT Manager - Network & Security"
        elif "threat" in lower_jd and "insider risk" in lower_jd:
            title = "Vice President - Information Security Threat & Insider Risk"
        elif "threat" in lower_jd and "cyber security" in lower_jd:
            title = "Cyber Security Threat Management Lead"
        elif "operational risk" in lower_jd and "technology" in lower_jd:
            title = "Senior Manager Technology Operational Risk Management"
        elif "infrastructure manager" in lower_jd:
            title = "Infrastructure Manager"
        else:
            for line in lines[:30]:
                line_clean = line.replace("#", "").replace("**", "").replace(":", "").strip()
                line_lower = line_clean.lower()
                if any(bad in line_lower for bad in ["responsibilities", "requirements", "qualifications", "overview", "summary", "description", "opportunity", "about you", "about the", "why this", "key responsibilities"]):
                    continue
                if any(kw in line_lower for kw in ["manager", "architect", "lead", "engineer", "director", "head of", "vice president", "specialist"]):
                    if len(line_clean) < 80 and not line_lower.startswith("about") and not line_lower.startswith("why"):
                        title = line_clean.split("|")[0].replace("Job role and title -", "").strip()
                        break

    safe_company = sanitize_filename(company)
    safe_title = sanitize_filename(title)
    return {
        "company": safe_company,
        "title": safe_title,
        "folder_name": f"{safe_company} - {safe_title}"
    }

def list_applications():
    os.makedirs(MY_APPS_DIR, exist_ok=True)
    results = []
    
    try:
        entries = os.listdir(MY_APPS_DIR)
    except Exception:
        return []

    for entry in entries:
        folder_path = os.path.join(MY_APPS_DIR, entry)
        if not os.path.isdir(folder_path):
            continue
            
        # Parse company and title from folder name
        parts = entry.split(" - ", 1)
        company = parts[0].strip() if len(parts) > 0 else entry
        title = parts[1].strip() if len(parts) > 1 else ""

        # Check existing files
        has_jd = os.path.exists(os.path.join(folder_path, "target_jd.md")) or \
                 os.path.exists(os.path.join(folder_path, "job_description.md")) or \
                 os.path.exists(os.path.join(folder_path, "JD.docx"))
                 
        has_resume_docx = os.path.exists(os.path.join(folder_path, "tailored_resume.docx"))
        has_cl_docx = os.path.exists(os.path.join(folder_path, "tailored_cover_letter.docx"))
        has_resume_md = os.path.exists(os.path.join(folder_path, "tailored_resume.md"))
        has_cl_md = os.path.exists(os.path.join(folder_path, "tailored_cover_letter.md"))
        has_report = os.path.exists(os.path.join(folder_path, "compliance_report.md"))

        meta_file = os.path.join(folder_path, "application_meta.json")
        meta_data = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as mf:
                    meta_data = json.load(mf)
            except Exception:
                pass

        mtime = os.path.getmtime(folder_path)
        updated_at = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')

        results.append({
            "folder_name": entry,
            "company": meta_data.get("company", company),
            "title": meta_data.get("title", title),
            "updated_at": meta_data.get("archived_at", updated_at),
            "has_jd": has_jd,
            "has_resume_docx": has_resume_docx,
            "has_cl_docx": has_cl_docx,
            "has_resume_md": has_resume_md,
            "has_cl_md": has_cl_md,
            "has_report": has_report,
            "is_complete": has_resume_docx and has_cl_docx and has_jd,
            "meta": meta_data
        })

    # Sort: Complete and newly modified first
    results.sort(key=lambda x: (x["is_complete"], x["updated_at"]), reverse=True)
    return results

def save_application(company, title, custom_folder=None):
    os.makedirs(MY_APPS_DIR, exist_ok=True)
    
    if custom_folder:
        folder_name = sanitize_filename(custom_folder)
    else:
        safe_co = sanitize_filename(company or "Company")
        safe_ti = sanitize_filename(title or "Role")
        folder_name = f"{safe_co} - {safe_ti}"

    dest_dir = os.path.join(MY_APPS_DIR, folder_name)
    os.makedirs(dest_dir, exist_ok=True)

    files_map = [
        (os.path.join(BASE_DIR, "target_jd.md"), "target_jd.md"),
        (os.path.join(BASE_DIR, "output", "tailored_resume.md"), "tailored_resume.md"),
        (os.path.join(BASE_DIR, "output", "tailored_cover_letter.md"), "tailored_cover_letter.md"),
        (os.path.join(BASE_DIR, "output", "compliance_report.md"), "compliance_report.md"),
        (os.path.join(BASE_DIR, "output", "tailored_resume.docx"), "tailored_resume.docx"),
        (os.path.join(BASE_DIR, "output", "tailored_cover_letter.docx"), "tailored_cover_letter.docx")
    ]

    saved_files = []
    for src, dst_name in files_map:
        if os.path.exists(src):
            dst = os.path.join(dest_dir, dst_name)
            shutil.copy2(src, dst)
            saved_files.append(dst_name)

    meta = {
        "company": company,
        "title": title,
        "folder_name": folder_name,
        "archived_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "files": saved_files
    }
    with open(os.path.join(dest_dir, "application_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {
        "success": True,
        "folder_name": folder_name,
        "folder_path": dest_dir,
        "saved_files": saved_files,
        "archived_at": meta["archived_at"]
    }

def load_application_files(folder_name):
    folder_path = os.path.join(MY_APPS_DIR, folder_name)
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Application folder '{folder_name}' not found.")

    output_dir = os.path.join(BASE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Restore JD
    jd_text = ""
    target_jd_md = os.path.join(folder_path, "target_jd.md")
    job_desc_md = os.path.join(folder_path, "job_description.md")
    jd_docx = os.path.join(folder_path, "JD.docx")

    if os.path.exists(target_jd_md):
        with open(target_jd_md, "r", encoding="utf-8") as f:
            jd_text = f.read()
    elif os.path.exists(job_desc_md):
        with open(job_desc_md, "r", encoding="utf-8") as f:
            jd_text = f.read()
    elif os.path.exists(jd_docx):
        try:
            import docx
            doc = docx.Document(jd_docx)
            jd_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception:
            pass

    if jd_text:
        with open(os.path.join(BASE_DIR, "target_jd.md"), "w", encoding="utf-8") as f:
            f.write(jd_text)

    # 2. Restore Markdown outputs
    md_files = [
        ("tailored_resume.md", os.path.join(output_dir, "tailored_resume.md")),
        ("tailored_cover_letter.md", os.path.join(output_dir, "tailored_cover_letter.md")),
        ("compliance_report.md", os.path.join(output_dir, "compliance_report.md"))
    ]
    restored_texts = {}
    for fname, target_path in md_files:
        src = os.path.join(folder_path, fname)
        if os.path.exists(src):
            shutil.copy2(src, target_path)
            with open(src, "r", encoding="utf-8") as f:
                restored_texts[fname] = f.read()
        else:
            restored_texts[fname] = ""

    # 3. Restore Word outputs
    docx_files = ["tailored_resume.docx", "tailored_cover_letter.docx"]
    for dname in docx_files:
        src = os.path.join(folder_path, dname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(output_dir, dname))

    return {
        "folder_name": folder_name,
        "jd": jd_text,
        "resume": restored_texts.get("tailored_resume.md", ""),
        "cover_letter": restored_texts.get("tailored_cover_letter.md", ""),
        "compliance_report": restored_texts.get("compliance_report.md", "")
    }
