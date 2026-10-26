import docx
import os
import re
import json
import sys
import argparse

def clean_xml_string(s):
    # docx library doesn't like some control characters in text strings
    # We clean out anything that is not printable or standard whitespace
    return "".join(ch for ch in s if ch.isprintable() or ch in '\n\r\t')

def load_candidate_profile():
    profile_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "candidate_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def load_active_target():
    target_path = os.path.join(os.path.dirname(__file__), "..", "output", "active_target.json")
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def parse_markdown_line(line):
    line = line.strip()
    if not line:
        return 'empty', ''
    
    # Check headers
    if line.startswith('# '):
        return 'h1', line[2:]
    elif line.startswith('## '):
        return 'h2', line[3:]
    elif line.startswith('### '):
        return 'h3', line[4:]
    elif line.startswith('#### '):
        return 'h4', line[5:]
    
    # Check bullet lists
    if line.startswith('* ') or line.startswith('- '):
        return 'bullet', line[2:]
    
    # Check horizontal rule
    if line == '---' or line == '***' or line == '___':
        return 'hr', ''
        
    return 'p', line

def add_paragraph_with_formatting(doc, text, style_name):
    # Check if style exists
    if style_name in doc.styles:
        p = doc.add_paragraph(style=style_name)
    else:
        # Fallback to Normal
        p = doc.add_paragraph(style='Normal')
        if style_name == 'List Bullet':
            # Add bullet prefix manually
            p.paragraph_format.left_indent = docx.shared.Inches(0.25)
            p.add_run("• ")
            
    # Find all bold markers **...**
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(clean_xml_string(part[2:-2]))
            run.bold = True
        else:
            p.add_run(clean_xml_string(part))
    return p

def resolve_template_path(template_name_or_path, default_filename="Resume of Raj Parikh.docx"):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(base_dir, "template")
    
    if not template_name_or_path:
        active = load_active_target()
        if active and active.get("resume_template"):
            template_name_or_path = active["resume_template"]
        else:
            template_name_or_path = default_filename
            
    # If it's an absolute or direct relative path that exists
    if os.path.exists(template_name_or_path):
        return os.path.abspath(template_name_or_path)
        
    # Check inside template/ folder
    candidate = os.path.join(template_dir, os.path.basename(template_name_or_path))
    if os.path.exists(candidate):
        return candidate
        
    # Fallback to default
    fallback = os.path.join(template_dir, default_filename)
    if os.path.exists(fallback):
        return fallback
        
    return candidate

def compile_resume(md_path, template_path, output_path):
    if not os.path.exists(md_path):
        print(f"MD file not found: {md_path}")
        return {"success": False, "error": f"MD file not found: {md_path}"}
        
    # If the provided template is a markdown file, we use the master docx for base layout styles
    actual_docx_template = template_path
    if template_path.endswith(".md"):
        master_docx = resolve_template_path(None, "Resume of Raj Parikh.docx")
        if os.path.exists(master_docx):
            actual_docx_template = master_docx
        else:
            actual_docx_template = None
            
    if actual_docx_template and os.path.exists(actual_docx_template):
        doc = docx.Document(actual_docx_template)
    else:
        # Create a fresh document with standard clean typography
        doc = docx.Document()
        
    profile = load_candidate_profile()
    active_target = load_active_target()
    
    # Read Markdown lines
    with open(md_path, 'r', encoding='utf-8') as f:
        md_lines = f.readlines()
        
    header_data = []
    content_lines = []
    
    # Check if md has explicit header block (starts with # Name)
    has_explicit_header = False
    name_hints = []
    if profile and profile.get("full_name"):
        name_hints.extend([p.lower() for p in profile.get("full_name", "").split() if len(p) > 2])
    name_hints.extend(["rajiv", "parikh", "raj", "candidate", "resume", "curriculum vitae"])
    
    for line in md_lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.startswith("# "):
            lower_line = line_strip.lower()
            if any(x in lower_line for x in name_hints):
                has_explicit_header = True
                break
            
    if has_explicit_header:
        for line in md_lines:
            line_strip = line.strip()
            if not line_strip:
                continue
            if len(header_data) < 3:
                clean_line = re.sub(r'[#\*\_]', '', line_strip)
                header_data.append(clean_line)
            else:
                content_lines.append(line_strip)
    else:
        content_lines = [l.strip() for l in md_lines if l.strip()]

    # Normalize years in content_lines
    years_str = profile.get("total_years_experience", "25+") if profile else "25+"
    content_lines = [re.sub(r'20\+?\s*years', f"{years_str} years", l, flags=re.IGNORECASE) for l in content_lines]

    # Resolve active target role title for header
    target_role_title = ""
    if active_target and active_target.get("title") and active_target["title"] != "Target Role":
        target_role_title = active_target["title"]
    elif len(header_data) > 1 and header_data[1]:
        target_role_title = header_data[1]
    elif profile:
        target_role_title = profile.get("target_title", "Head of Infrastructure & Security / Technology Leader")

    # Update the first 3 paragraphs of the template (Header block)
    if profile:
        # Paragraph 0: Full Name
        if len(doc.paragraphs) > 0:
            p0 = doc.paragraphs[0]
            p0.text = ""
            r0 = p0.add_run(clean_xml_string(profile.get("full_name", "Rajiv (Raj) Parikh")))
            r0.bold = True
            r0.font.size = docx.shared.Pt(20)
            
        # Paragraph 1: Target Role Title
        if len(doc.paragraphs) > 1:
            p1 = doc.paragraphs[1]
            p1.text = ""
            r1 = p1.add_run(clean_xml_string(target_role_title))
            r1.bold = True
            r1.font.size = docx.shared.Pt(11)
            
        # Paragraph 2: Contact Info (Authoritative Address, Phone, Email, Citizenship)
        if len(doc.paragraphs) > 2:
            p2 = doc.paragraphs[2]
            p2.text = ""
            contact_parts = []
            if profile.get("address"): contact_parts.append(profile["address"])
            if profile.get("phone"): contact_parts.append(profile["phone"])
            if profile.get("email"): contact_parts.append(profile["email"])
            if profile.get("citizenship"): contact_parts.append(profile["citizenship"])
            contact_line = " | ".join(contact_parts)
            r2 = p2.add_run(clean_xml_string(contact_line))
            r2.font.size = docx.shared.Pt(10)
    elif header_data:
        for i in range(min(3, len(header_data))):
            if i < len(doc.paragraphs):
                p = doc.paragraphs[i]
                p.text = ""
                run = p.add_run(clean_xml_string(header_data[i]))
                if i == 0:
                    run.bold = True
                    run.font.size = docx.shared.Pt(20)
                elif i == 1:
                    run.bold = True
                    run.font.size = docx.shared.Pt(11)
                else:
                    run.font.size = docx.shared.Pt(10)

    # Delete all other paragraphs starting from index 3
    while len(doc.paragraphs) > 3:
        p = doc.paragraphs[3]
        p._element.getparent().remove(p._element)
        
    # Clear tables and other elements in the body
    for t in list(doc.tables):
        t._element.getparent().remove(t._element)
        
    # Parse and append content with visual style re-mapping
    stats = {
        "sections": 0,
        "bullets": 0,
        "paragraphs": 0,
        "template_name": os.path.basename(actual_docx_template)
    }

    for line in content_lines:
        line_type, text = parse_markdown_line(line)
        if line_type == 'empty':
            continue
        elif line_type == 'h1':
            stats["sections"] += 1
            add_paragraph_with_formatting(doc, text, 'Heading 1')
        elif line_type == 'h2':
            stats["sections"] += 1
            add_paragraph_with_formatting(doc, text, 'Heading 2')
        elif line_type == 'h3':
            stats["sections"] += 1
            add_paragraph_with_formatting(doc, text, 'Heading 3')
        elif line_type == 'h4':
            # Role sub-heading (e.g. Group Security – Service Manager | Jan 2025 – Present)
            if 'Heading 4' in doc.styles:
                add_paragraph_with_formatting(doc, text, 'Heading 4')
            else:
                p = add_paragraph_with_formatting(doc, f"**{text}**", 'Normal')
                p.paragraph_format.space_before = docx.shared.Pt(4)
                p.paragraph_format.space_after = docx.shared.Pt(2)
        elif line_type == 'bullet':
            stats["bullets"] += 1
            add_paragraph_with_formatting(doc, text, 'List Bullet')
        elif line_type == 'hr':
            p = doc.add_paragraph()
            p.paragraph_format.space_before = docx.shared.Pt(2)
            p.paragraph_format.space_after = docx.shared.Pt(2)
        elif line_type == 'p':
            stats["paragraphs"] += 1
            add_paragraph_with_formatting(doc, text, 'Normal')
            
    # Ensure parent directory of output exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    stats["docx_bytes"] = os.path.getsize(output_path)
    stats["success"] = True
    print(f"Compiled Resume using [{stats['template_name']}]: {output_path} ({stats['docx_bytes']} bytes)")
    return stats

def compile_cover_letter(md_path, template_path, output_path):
    if not os.path.exists(md_path):
        print(f"MD file not found: {md_path}")
        return {"success": False, "error": f"MD file not found: {md_path}"}
    if os.path.exists(template_path):
        doc = docx.Document(template_path)
        # Clear all paragraphs in the template
        while len(doc.paragraphs) > 0:
            p = doc.paragraphs[0]
            p._element.getparent().remove(p._element)
            
        # Clear tables
        for t in list(doc.tables):
            t._element.getparent().remove(t._element)
    else:
        doc = docx.Document()
        
    profile = load_candidate_profile()
    with open(md_path, 'r', encoding='utf-8') as f:
        md_lines = f.readlines()
        
    years_str = profile.get("total_years_experience", "25+") if profile else "25+"

    # Parse and append content
    stats = {"paragraphs": 0, "bullets": 0}
    for line in md_lines:
        line_strip = line.strip()
        if not line_strip:
            doc.add_paragraph()
            continue
            
        # Clean any triple quotes
        line_strip = re.sub(r'^"""\s*', '', line_strip)
        line_strip = re.sub(r'\s*"""$', '', line_strip)
        if not line_strip:
            continue

        # If profile exists and line looks like contact line, inject latest profile contact line
        if profile and any(x in line_strip for x in ["0433", "@", "Citizen", "Carlingford", "Cherrybrook"]):
            contact_parts = []
            if profile.get("address"): contact_parts.append(profile["address"])
            if profile.get("phone"): contact_parts.append(profile["phone"])
            if profile.get("email"): contact_parts.append(profile["email"])
            if profile.get("citizenship"): contact_parts.append(profile["citizenship"])
            line_strip = " | ".join(contact_parts)

        # Normalize 20+ years -> 25+ years
        line_strip = re.sub(r'20\+?\s*years', f"{years_str} years", line_strip, flags=re.IGNORECASE)

        line_type, text = parse_markdown_line(line_strip)
        if line_type == 'bullet':
            stats["bullets"] += 1
            add_paragraph_with_formatting(doc, text, 'List Bullet')
        elif line_type in ['p', 'h1', 'h2', 'h3', 'h4']:
            stats["paragraphs"] += 1
            p = add_paragraph_with_formatting(doc, text, 'Normal')
            p.paragraph_format.space_after = docx.shared.Pt(6)
            
    # Ensure parent directory of output exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    stats["docx_bytes"] = os.path.getsize(output_path)
    stats["success"] = True
    print(f"Compiled Cover Letter: {output_path} ({stats['docx_bytes']} bytes)")
    return stats

def archive_to_application_folder(base_dir=None):
    if not base_dir:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    import sys
    sys.path.insert(0, os.path.join(base_dir, "app"))
    from application_manager import detect_company_and_title, save_application, get_active_target
    
    active = get_active_target()
    if active and active.get("company") and active.get("title") and active["company"] != "Target Company":
        company = active["company"]
        title = active["title"]
    else:
        jd_path = os.path.join(base_dir, "target_jd.md")
        jd_text = ""
        if os.path.exists(jd_path):
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_text = f.read()
        det = detect_company_and_title(jd_text)
        company = det["company"]
        title = det["title"]

    res = save_application(company, title)
    print(f"Permanently archived {len(res['saved_files'])} files to: {res['folder_path']}")
    return res["folder_path"]

def main():
    parser = argparse.ArgumentParser(description="Resume Lab Document Compiler & Template Synchronizer")
    parser.add_argument("--resume-template", type=str, default=None, help="Resume template filename or path (.docx or .md)")
    parser.add_argument("--cover-template", type=str, default=None, help="Cover letter template filename or path (.docx)")
    parser.add_argument("--resume-only", action="store_true", help="Only compile/format the tailored resume")
    parser.add_argument("--skip-archive", action="store_true", help="Skip permanent archiving step")
    args = parser.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    resume_md = os.path.join(base_dir, "output", "tailored_resume.md")
    resume_template = resolve_template_path(args.resume_template, "Resume of Raj Parikh.docx")
    resume_docx = os.path.join(base_dir, "output", "tailored_resume.docx")
    
    cl_md = os.path.join(base_dir, "output", "tailored_cover_letter.md")
    cl_template = resolve_template_path(args.cover_template, "Cover Letter.docx")
    cl_docx = os.path.join(base_dir, "output", "tailored_cover_letter.docx")
    
    print("Compiling documents with template layout sync...")
    r_stats = compile_resume(resume_md, resume_template, resume_docx)
    
    if not args.resume_only:
        c_stats = compile_cover_letter(cl_md, cl_template, cl_docx)
        if not args.skip_archive:
            archive_to_application_folder(base_dir)
            
    print("Compilation complete!")
    return r_stats

if __name__ == '__main__':
    main()
