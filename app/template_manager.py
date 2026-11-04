import os
import json
import datetime
import re
import docx

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from storage_config import get_templates_dir, get_output_dir

DEFAULT_TEMPLATE = "Resume of Raj Parikh.docx"

def get_tmpl_dir():
    return get_templates_dir()

def get_active_target_file():
    return os.path.join(get_output_dir(), "active_target.json")

def sanitize_template_filename(filename):
    cleaned = re.sub(r'[\\/*?:"<>|]', "", str(filename))
    return cleaned.strip()

def get_active_template():
    target_file = get_active_target_file()
    tmpl_dir = get_tmpl_dir()
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                tmpl = data.get("resume_template")
                if tmpl and os.path.exists(os.path.join(tmpl_dir, os.path.basename(tmpl))):
                    return os.path.basename(tmpl)
        except Exception:
            pass
    if os.path.exists(os.path.join(tmpl_dir, DEFAULT_TEMPLATE)):
        return DEFAULT_TEMPLATE
    for cand in ["Standard Executive Resume Template.md", "Standard Executive Resume Template.docx"]:
        if os.path.exists(os.path.join(tmpl_dir, cand)):
            return cand
    return DEFAULT_TEMPLATE

def set_active_template(template_name):
    tmpl_dir = get_tmpl_dir()
    clean_name = sanitize_template_filename(template_name)
    target_path = os.path.join(tmpl_dir, clean_name)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Template '{clean_name}' does not exist in template folder.")
        
    data = {}
    target_file = get_active_target_file()
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
            
    data["resume_template"] = clean_name
    data["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    return clean_name

def list_templates():
    tmpl_dir = get_tmpl_dir()
    os.makedirs(tmpl_dir, exist_ok=True)
    active_name = get_active_template()
    templates = []
    
    try:
        entries = sorted(os.listdir(tmpl_dir))
    except Exception:
        entries = []
        
    for entry in entries:
        full_path = os.path.join(tmpl_dir, entry)
        if not os.path.isfile(full_path):
            continue
            
        ext = entry.split(".")[-1].lower() if "." in entry else ""
        if ext not in ["docx", "md", "txt"]:
            continue
            
        stat = os.stat(full_path)
        size_kb = round(stat.st_size / 1024, 1)
        mod_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        is_default = (entry == DEFAULT_TEMPLATE)
        is_active = (entry == active_name)
        
        # Descriptions
        if entry == DEFAULT_TEMPLATE:
            desc = "Candidate's Master ATS Word Template (Title, Headings, Bullet Hierarchy)"
        elif entry == "Cover Letter.docx":
            desc = "Official Word Cover Letter Template"
        elif ext == "docx":
            desc = "Custom Word Layout Template (.docx)"
        elif ext == "md":
            desc = "Markdown Layout Structure Template (.md)"
        else:
            desc = "Text Formatting Template"
            
        templates.append({
            "filename": entry,
            "display_name": entry.rsplit(".", 1)[0],
            "type": ext,
            "size_kb": size_kb,
            "modified_at": mod_time,
            "is_default": is_default,
            "is_active": is_active,
            "description": desc
        })
        
    # Ensure active_template is always identified
    return {
        "active_template": active_name,
        "default_template": DEFAULT_TEMPLATE,
        "templates": templates
    }

def inspect_template_details(template_name):
    tmpl_dir = get_tmpl_dir()
    clean_name = sanitize_template_filename(template_name)
    full_path = os.path.join(tmpl_dir, clean_name)
    if not os.path.exists(full_path):
        return {"error": f"Template '{clean_name}' not found."}
        
    ext = clean_name.split(".")[-1].lower()
    details = {
        "filename": clean_name,
        "type": ext,
        "size_kb": round(os.path.getsize(full_path) / 1024, 1)
    }
    
    if ext == "docx":
        try:
            doc = docx.Document(full_path)
            details["paragraph_count"] = len(doc.paragraphs)
            details["table_count"] = len(doc.tables)
            styles = [s.name for s in doc.styles if s.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH]
            key_styles = [s for s in ['Title', 'Heading 1', 'Heading 2', 'Heading 3', 'Heading 4', 'List Bullet', 'Normal'] if s in styles]
            details["key_styles"] = key_styles
            # Sample first few paragraphs
            samples = []
            for p in doc.paragraphs[:5]:
                txt = p.text.strip()
                if txt:
                    samples.append(f"[{p.style.name}] {txt[:60]}")
            details["sample_paragraphs"] = samples
        except Exception as e:
            details["parse_error"] = str(e)
    elif ext in ["md", "txt"]:
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            details["line_count"] = len(content.splitlines())
            sections = [line.strip() for line in content.splitlines() if line.strip().startswith("#")]
            details["sections"] = sections[:10]
        except Exception as e:
            details["parse_error"] = str(e)
            
    return details

def save_uploaded_template(filename, data_bytes=None, text_content=None):
    tmpl_dir = get_tmpl_dir()
    os.makedirs(tmpl_dir, exist_ok=True)
    clean_name = sanitize_template_filename(filename)
    if not clean_name:
        raise ValueError("Invalid template filename.")
        
    ext = clean_name.split(".")[-1].lower()
    if ext not in ["docx", "md", "txt"]:
        raise ValueError("Only .docx or .md template files are accepted.")
        
    target_path = os.path.join(tmpl_dir, clean_name)
    
    if data_bytes is not None:
        with open(target_path, "wb") as f:
            f.write(data_bytes)
    elif text_content is not None:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(text_content)
    else:
        raise ValueError("No template content provided.")
        
    # Auto-activate newly uploaded template
    set_active_template(clean_name)
    return {
        "success": True,
        "filename": clean_name,
        "path": target_path,
        "size_kb": round(os.path.getsize(target_path) / 1024, 1)
    }

def extract_markdown_from_template(template_name):
    tmpl_dir = get_tmpl_dir()
    clean_name = sanitize_template_filename(template_name)
    target_path = os.path.join(tmpl_dir, clean_name)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Template '{clean_name}' not found.")
        
    ext = clean_name.split(".")[-1].lower()
    if ext in ["md", "txt"]:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
            
    if ext == "docx":
        doc = docx.Document(target_path)
        md_lines = []
        known_section_headers = {
            'summary', 'executive summary', 'skills', 'core competencies', 
            'core competencies & technical skills', 'employment history', 
            'professional experience', 'prior roles', 'qualifications', 
            'certifications', 'professional certifications & credentials', 
            'expired certifications', 'education'
        }
        
        for i, p in enumerate(doc.paragraphs):
            text = p.text.strip()
            if not text:
                continue
            style = p.style.name.lower() if p.style else ""
            
            runs_text = []
            for r in p.runs:
                t = r.text
                if not t:
                    continue
                if r.bold and r.italic and t.strip():
                    runs_text.append(f'***{t.strip()}*** ')
                elif r.bold and t.strip():
                    runs_text.append(f'**{t.strip()}** ')
                elif r.italic and t.strip():
                    runs_text.append(f'*{t.strip()}* ')
                else:
                    runs_text.append(t)
            formatted = re.sub(r'\s+', ' ', ''.join(runs_text)).strip()
            
            is_bullet = False
            try:
                if style.startswith('list') or (p._p.pPr is not None and p._p.pPr.numPr is not None):
                    is_bullet = True
            except Exception:
                pass
                
            clean_lower = text.lower().strip()
            
            if i == 0 and not is_bullet:
                md_lines.append(f'# {text}\n')
            elif clean_lower in known_section_headers or style.startswith('heading 1'):
                header_title = text.title() if text.isupper() else text
                md_lines.append(f'\n## {header_title}\n')
            elif style.startswith('heading 2'):
                md_lines.append(f'\n### {formatted}\n')
            elif is_bullet:
                md_lines.append(f'* {formatted}')
            else:
                md_lines.append(formatted)
                
        return '\n'.join(md_lines)
    
    raise ValueError(f"Unsupported template format: {ext}")

def apply_template_to_markdown(template_name):
    clean_name = sanitize_template_filename(template_name)
    try:
        set_active_template(clean_name)
    except Exception:
        pass
    md_content = extract_markdown_from_template(clean_name)
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "tailored_resume.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return {
        "success": True,
        "template": clean_name,
        "markdown": md_content,
        "length": len(md_content)
    }

