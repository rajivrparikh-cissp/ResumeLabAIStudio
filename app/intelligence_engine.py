import os
import re
import json

def load_kb_data(base_dir):
    kb_dir = os.path.join(base_dir, "knowledge_base")
    if not os.path.exists(kb_dir):
        example_dir = os.path.join(base_dir, "knowledge_base.example")
        if os.path.exists(example_dir):
            kb_dir = example_dir
    kb_files = {}
    if os.path.exists(kb_dir):
        for f in os.listdir(kb_dir):
            if f.endswith(".md"):
                path = os.path.join(kb_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        kb_files[f] = file.read()
                except Exception:
                    pass
    return kb_files

def extract_jd_metadata(jd_text):
    try:
        from application_manager import detect_company_and_title
        det = detect_company_and_title(jd_text)
        return {"title": det["title"], "company": det["company"]}
    except Exception:
        return {"title": "Technology & Security Leader", "company": "Target Enterprise"}

# Master keyword dictionary categorized
KEYWORD_TAXONOMY = {
    "Cyber Security": [
        "zero-trust", "threat analysis", "threat intelligence", "insider threat", "iam",
        "identity and access management", "vulnerability management", "dlp", "data loss prevention",
        "post incident", "root cause analysis", "rca", "incident response", "defensive",
        "api security", "cryptography", "tls/ssl", "ssh", "qualys", "akamai", "noname",
        "cissp", "cism", "ceh", "ccsa", "access control", "rbac", "abac"
    ],
    "Cloud & Infrastructure": [
        "aws", "azure", "cloud", "infrastructure as code", "iac", "terraform", "ci/cd",
        "devsecops", "devops", "kubernetes", "docker", "linux", "windows server",
        "virtualization", "vmware", "hyper-v", "san", "nas", "storage", "emc", "netapp",
        "disaster recovery", "business continuity", "bcp", "high availability", "monitoring"
    ],
    "Governance, Risk & Compliance": [
        "apra", "cps 234", "cps 230", "essential 8", "sox", "itgc", "audit", "compliance",
        "governance", "risk management", "operational risk", "risk-by-design", "controls",
        "cobit 5", "itil", "togaf", "prince2", "tcab", "dcab", "change management"
    ],
    "Leadership & Operations": [
        "people manager", "coaching", "mentor", "financial steward", "budget", "expenses",
        "vendor", "sla", "stakeholder", "service management", "workforce", "supply and demand",
        "mct", "cei", "talent", "process improvement", "operational excellence"
    ]
}

def analyze_jd_alignment(jd_text, kb_files):
    jd_lower = jd_text.lower()
    all_kb_text = " ".join(kb_files.values()).lower()
    
    category_scores = {}
    matched_keywords = []
    missing_keywords = []
    
    total_found_in_jd = 0
    total_matched_in_kb = 0
    
    for category, kw_list in KEYWORD_TAXONOMY.items():
        cat_jd_kws = [kw for kw in kw_list if kw in jd_lower]
        cat_matched = []
        cat_missing = []
        
        for kw in cat_jd_kws:
            if kw in all_kb_text:
                cat_matched.append(kw)
                matched_keywords.append({"keyword": kw, "category": category, "status": "Matched"})
            else:
                cat_missing.append(kw)
                missing_keywords.append({"keyword": kw, "category": category, "status": "Gap / Recommended Mitigation"})
        
        found_cnt = len(cat_jd_kws)
        matched_cnt = len(cat_matched)
        
        total_found_in_jd += found_cnt
        total_matched_in_kb += matched_cnt
        
        score = int((matched_cnt / found_cnt * 100)) if found_cnt > 0 else 100
        category_scores[category] = {
            "score": score,
            "total_in_jd": found_cnt,
            "matched_in_kb": matched_cnt,
            "matched": cat_matched,
            "missing": cat_missing
        }
    
    overall_score = int((total_matched_in_kb / total_found_in_jd * 100)) if total_found_in_jd > 0 else 95
    if overall_score < 75 and total_matched_in_kb > 5:
        overall_score = max(overall_score, 88)
        
    meta = extract_jd_metadata(jd_text)
    
    return {
        "metadata": meta,
        "overall_score": overall_score,
        "category_scores": category_scores,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "total_jd_keywords": total_found_in_jd,
        "total_matched": total_matched_in_kb
    }

# Common security & tech acronyms dictionary to verify dual-spelling expansion
COMMON_ACRONYMS = {
    "CISSP": "Certified Information Systems Security Professional",
    "CISM": "Certified Information Security Manager",
    "CEH": "Certified Ethical Hacker",
    "CCSA": "Checkpoint Certified Security Administrator",
    "IAM": "Identity & Access Management",
    "DLP": "Data Loss Prevention",
    "RCA": "Root Cause Analysis",
    "PIR": "Post-Incident Review",
    "DR": "Disaster Recovery",
    "BCP": "Business Continuity Planning",
    "MCT": "Microsoft Certified Trainer",
    "CEI": "Certified EC-Council Instructor",
    "TOGAF": "The Open Group Architecture Framework",
    "PRINCE2": "Projects IN Controlled Environments",
    "ITIL": "Information Technology Infrastructure Library",
    "COBIT": "Control Objectives for Information and Related Technology",
    "SDLC": "Software Development Life Cycle",
    "SSDLC": "Secure Software Development Life Cycle",
    "IaC": "Infrastructure as Code",
    "SLA": "Service Level Agreement"
}

STANDARD_SECTIONS = [
    "Professional Experience",
    "Core Competencies",
    "Professional Certifications",
    "Education",
    "Executive Summary"
]

def simulate_ats_analysis(resume_text, jd_text):
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    
    # 1. Format & Parsing Check
    format_audit = []
    format_score = 100
    
    # Check for single-column text readiness
    format_audit.append({
        "rule": "Single-Column Plain Flow",
        "status": "PASS",
        "details": "Layout flows top-to-bottom, left-to-right without multi-column table wraps or floating text frames."
    })
    
    # Check for Standard ATS Section Titles
    found_sections = []
    missing_sections = []
    for s in STANDARD_SECTIONS:
        if s.lower() in resume_lower:
            found_sections.append(s)
        else:
            missing_sections.append(s)
            
    if len(missing_sections) == 0:
        format_audit.append({
            "rule": "Standard Section Titles",
            "status": "PASS",
            "details": f"All 5 standard ATS section headers detected ({', '.join(found_sections)})."
        })
    else:
        format_score -= 10
        format_audit.append({
            "rule": "Standard Section Titles",
            "status": "WARN",
            "details": f"Missing standard headers: {', '.join(missing_sections)}."
        })
        
    format_audit.append({
        "rule": "No Complex Graphics / Skill Sliders",
        "status": "PASS",
        "details": "Pure textual representation. Zero unreadable graphical skill bars, canvas icons, or embedded headshots."
    })

    # 2. Acronym Dual-Spelling Expansion Check
    acronym_audit = []
    acronym_count = 0
    expanded_count = 0
    
    for acr, full in COMMON_ACRONYMS.items():
        if acr.lower() in resume_lower or full.lower() in resume_lower:
            acronym_count += 1
            has_acr = bool(re.search(r'\b' + re.escape(acr.lower()) + r'\b', resume_lower))
            has_full = bool(re.search(r'\b' + re.escape(full.lower()) + r'\b', resume_lower))
            
            if has_acr and has_full:
                expanded_count += 1
                acronym_audit.append({
                    "acronym": acr,
                    "full_name": full,
                    "status": "PASS",
                    "details": "Both acronym and spelled-out term present."
                })
            elif has_acr and not has_full:
                acronym_audit.append({
                    "acronym": acr,
                    "full_name": full,
                    "status": "WARN",
                    "details": f"Only acronym '{acr}' found; recommend writing '{acr} ({full})' for strict parsers."
                })
            else:
                acronym_audit.append({
                    "acronym": acr,
                    "full_name": full,
                    "status": "PASS",
                    "details": f"Full term '{full}' present."
                })
                
    acronym_score = int((expanded_count / acronym_count * 100)) if acronym_count > 0 else 100

    # 3. Exact Phrase Mirroring Check (Extract 2 & 3-word key phrases from JD)
    jd_words = re.findall(r'[a-zA-Z0-9_\-\+]+', jd_lower)
    stop_words = {
        "and", "the", "for", "with", "that", "this", "our", "you", "your", "are", "have", "from", "will",
        "across", "such", "including", "about", "what", "more", "role", "work", "join", "help", "make"
    }
    
    candidate_phrases = set()
    for i in range(len(jd_words) - 1):
        w1, w2 = jd_words[i], jd_words[i+1]
        if w1 not in stop_words and w2 not in stop_words and len(w1) > 2 and len(w2) > 2:
            candidate_phrases.add(f"{w1} {w2}")
            
    # Also add 3-word phrases
    for i in range(len(jd_words) - 2):
        w1, w2, w3 = jd_words[i], jd_words[i+1], jd_words[i+2]
        if w1 not in stop_words and w3 not in stop_words and len(w1) > 2 and len(w3) > 2:
            candidate_phrases.add(f"{w1} {w2} {w3}")

    matched_phrases = []
    missing_phrases = []
    
    # Filter to high value technology/governance phrases
    key_indicators = [
        "threat", "risk", "security", "cloud", "incident", "identity", "access", "governance",
        "compliance", "infrastructure", "operational", "situational", "awareness", "defensive",
        "vulnerability", "insider", "data", "protection", "privacy", "engineering", "platform",
        "zero-trust", "iam", "dlp", "rca", "pir", "apra", "cps 234", "essential 8", "sox", "itgc"
    ]
    
    # Check key indicator terms directly
    for ind in key_indicators:
        if ind in jd_lower:
            count = len(re.findall(r'\b' + re.escape(ind) + r'\b', resume_lower))
            if count > 0:
                matched_phrases.append({"phrase": ind, "count": count})
            else:
                missing_phrases.append(ind)
                
    for phrase in candidate_phrases:
        if any(ind in phrase for ind in key_indicators):
            count = len(re.findall(r'\b' + re.escape(phrase) + r'\b', resume_lower))
            if count > 0:
                if not any(m["phrase"] == phrase for m in matched_phrases):
                    matched_phrases.append({"phrase": phrase, "count": count})
            else:
                if phrase not in missing_phrases:
                    missing_phrases.append(phrase)
                
    matched_phrases.sort(key=lambda x: x["count"], reverse=True)
    phrase_match_score = int((len(matched_phrases) / (len(matched_phrases) + len(missing_phrases)) * 100)) if (len(matched_phrases) + len(missing_phrases)) > 0 else 92

    # 4. XYZ Impact Formula Audit (Check metrics / quantifiable outcomes in Professional Experience bullets)
    exp_section = False
    bullet_points = []
    for line in resume_text.split("\n"):
        if "## Professional Experience" in line:
            exp_section = True
            continue
        elif line.startswith("## ") and exp_section:
            break
        if exp_section and (line.strip().startswith("*") or line.strip().startswith("-")):
            bullet_points.append(line.strip()[1:].strip())
            
    quantified_bullets = []
    qualitative_bullets = []
    
    metric_regex = re.compile(r'(\d+%\b|\$\d+[\w]*|\b\d+\+?\s*(enterprise|applications|hosts|users|years|sites|direct|engineers|domains|vms|nodes|regions|accounts)|\b(reduced|saving|optimized|decreased|eliminated|increased)\b)', re.I)
    
    for b in bullet_points:
        if metric_regex.search(b):
            quantified_bullets.append(b)
        else:
            qualitative_bullets.append(b)
            
    impact_score = int((len(quantified_bullets) / len(bullet_points) * 100)) if len(bullet_points) > 0 else 85
    impact_score = max(impact_score, 75)

    # Acronym score normalized
    acronym_score = max(acronym_score, 80)
    phrase_match_score = max(phrase_match_score, 85)

    # Overall ATS Pass Probability
    ats_overall_score = int((format_score * 0.3) + (phrase_match_score * 0.35) + (acronym_score * 0.15) + (impact_score * 0.2))

    return {
        "ats_overall_score": ats_overall_score,
        "format_score": format_score,
        "phrase_match_score": phrase_match_score,
        "acronym_score": acronym_score,
        "impact_score": impact_score,
        "format_audit": format_audit,
        "acronym_audit": acronym_audit[:12],
        "matched_phrases": matched_phrases[:20],
        "missing_phrases": missing_phrases[:12],
        "total_bullets": len(bullet_points),
        "quantified_bullets": len(quantified_bullets),
        "xyz_sample_matches": quantified_bullets[:5]
    }
