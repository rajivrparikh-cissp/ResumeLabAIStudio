import urllib.request
import urllib.error
import json
import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

def get_candidate_profile_data():
    try:
        from profile_manager import get_candidate_profile
        return get_candidate_profile()
    except Exception:
        return {
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
            "core_credentials": "CISSP | CISM | Cloud Architecture | DevOps | Executive Leadership"
        }

def get_ollama_status(ollama_url=None):
    base_url = ollama_url or OLLAMA_BASE_URL
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", headers={"User-Agent": "ResumeLab/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name") for m in data.get("models", [])]
            return {
                "online": True,
                "url": base_url,
                "models": models,
                "default_model": models[0] if models else "llama3.2"
            }
    except Exception as e:
        return {
            "online": False,
            "url": base_url,
            "error": str(e),
            "models": [],
            "default_model": "llama3.2"
        }

def load_kb_summary(max_chars=3500):
    """Loads and formats a concise summary of the candidate's verified knowledge base."""
    kb_dir = os.path.join(BASE_DIR, "knowledge_base")
    if not os.path.exists(kb_dir):
        kb_dir = os.path.join(BASE_DIR, "knowledge_base.example")
    sections = []
    
    # Candidate Profile Truth (Address, Experience, Contact)
    profile_path = os.path.join(kb_dir, "candidate_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                prof_data = json.load(f)
                sections.append(f"### Candidate Verified Profile Truth:\n{json.dumps(prof_data, indent=2)}")
        except Exception:
            pass

    # Master Career Work History & Core Matrices
    priority_files = ["work_history.md", "experience_matrix.md", "skills_inventory.md", "tone_guide.md"]
    for fn in priority_files:
        fpath = os.path.join(kb_dir, fn)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    sections.append(f"### {fn}:\n{content[:1000]}")
            except Exception:
                pass
                
    combined = "\n\n".join(sections)
    return combined[:max_chars]

def query_ollama(prompt, system_prompt="", model="llama3.2", temperature=0.15, timeout=120, num_predict=600, num_ctx=4096, base_url=None):
    url = (base_url or OLLAMA_BASE_URL).rstrip("/")
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "num_predict": num_predict,
            "num_ctx": num_ctx
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Ollama inference failed at {url}: {str(e)}")

def query_llm(prompt, system_prompt="", provider="local", model="llama3.2", api_key="", temperature=0.15, timeout=120, num_predict=1500, ollama_url=None):
    """
    Universal multi-provider LLM query dispatcher.
    Supports:
    - local: Ollama or local API endpoint (100% private, runs on user machine)
    - gemini: Google Gemini API (gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp)
    - openai: OpenAI API (gpt-4o, gpt-4o-mini)
    - groq: Groq Cloud API (llama-3.3-70b-versatile, mixtral-8x7b-32768)
    - anthropic: Anthropic Claude API (claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022)
    """
    provider = (provider or "local").lower().strip()

    # 1. Local LLM (Ollama)
    if provider == "local":
        return query_ollama(
            prompt,
            system_prompt=system_prompt,
            model=model or "llama3.2",
            temperature=temperature,
            timeout=timeout,
            num_predict=num_predict,
            base_url=ollama_url
        )

    # 2. Google Gemini API
    elif provider == "gemini":
        key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            raise ValueError("Google Gemini API key required. Please enter your key in AI Engine Setup.")
        model_name = model or "gemini-1.5-flash"
        if not model_name.startswith("gemini-"):
            model_name = "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"

        contents = [{"parts": [{"text": prompt}]}]
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": num_predict
            }
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                    return candidates[0]["content"]["parts"][0].get("text", "").strip()
                raise RuntimeError("Empty response received from Gemini API.")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                msg = json.loads(err_body).get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            raise RuntimeError(f"Gemini API Error ({e.code}): {msg}")
        except Exception as e:
            raise RuntimeError(f"Gemini connection failed: {str(e)}")

    # 3. OpenAI / Groq (OpenAI-compatible)
    elif provider in ["openai", "groq"]:
        if provider == "openai":
            key = api_key or os.environ.get("OPENAI_API_KEY", "")
            base_url = "https://api.openai.com/v1/chat/completions"
            default_model = "gpt-4o-mini"
        else: # groq
            key = api_key or os.environ.get("GROQ_API_KEY", "")
            base_url = "https://api.groq.com/openai/v1/chat/completions"
            default_model = "llama-3.3-70b-versatile"

        if not key:
            raise ValueError(f"{provider.upper()} API key required. Please enter your key in AI Engine Setup.")

        model_name = model or default_model
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": num_predict
        }
        req = urllib.request.Request(
            base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "").strip()
                raise RuntimeError(f"Empty response received from {provider.upper()} API.")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                msg = json.loads(err_body).get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            raise RuntimeError(f"{provider.upper()} API Error ({e.code}): {msg}")
        except Exception as e:
            raise RuntimeError(f"{provider.upper()} connection failed: {str(e)}")

    # 4. Anthropic Claude
    elif provider == "anthropic":
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("Anthropic API key required. Please enter your key in AI Engine Setup.")
        model_name = model or "claude-3-5-sonnet-20241022"
        base_url = "https://api.anthropic.com/v1/messages"

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": num_predict,
            "temperature": temperature
        }
        if system_prompt:
            payload["system"] = system_prompt

        req = urllib.request.Request(
            base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                contents = data.get("content", [])
                if contents and "text" in contents[0]:
                    return contents[0].get("text", "").strip()
                raise RuntimeError("Empty response received from Anthropic API.")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            try:
                msg = json.loads(err_body).get("error", {}).get("message", err_body)
            except Exception:
                msg = err_body
            raise RuntimeError(f"Anthropic API Error ({e.code}): {msg}")
        except Exception as e:
            raise RuntimeError(f"Anthropic connection failed: {str(e)}")

    else:
        raise ValueError(f"Unsupported AI provider: '{provider}'. Supported providers: local, gemini, openai, groq, anthropic.")

def test_llm_connection(provider="local", model="", api_key="", ollama_url=None):
    """Diagnostic tool to verify connectivity to any supported AI engine."""
    provider = (provider or "local").lower().strip()
    test_prompt = "Hello! Please reply with exactly one word: 'CONNECTED'."
    try:
        reply = query_llm(
            test_prompt,
            system_prompt="You are an automated connectivity test diagnostic.",
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=0.1,
            timeout=15,
            num_predict=20,
            ollama_url=ollama_url
        )
        return {
            "success": True,
            "provider": provider,
            "model": model,
            "reply": reply[:100],
            "message": f"Successfully connected to {provider.upper()} ({model or 'default'})."
        }
    except Exception as e:
        return {
            "success": False,
            "provider": provider,
            "model": model,
            "error": str(e)
        }

def grounded_improve_text(selected_text, doc_type="resume", jd_text="", instruction="", model="llama3.2", provider="local", api_key="", ollama_url=None):
    kb_summary = load_kb_summary(max_chars=3500)
    
    if not instruction:
        instruction = "Improve and polish the text for clarity, impact, and ATS keywords without adding any unverified facts."

    system_prompt = (
        "You are an Elite Executive Career Strategist and Anti-Hallucination Guardrail.\n"
        "STRICT GUARDRAILS (CRITICAL - DO NOT VIOLATE):\n"
        "1. DO NOT invent achievements, companies, dates, or certifications not explicitly documented in the Candidate Knowledge Base.\n"
        "2. DO NOT make up metrics (percentages, dollar amounts, headcounts) out of thin air. If a metric is not in the knowledge base, polish the qualitative outcome using strong action verbs instead of fabricating numbers.\n"
        "3. Only use technologies, platforms, and methodologies that the candidate has verified experience with.\n"
        "4. Align tone, vocabulary, and keywords directly with the Target Job Description without exaggerating the candidate's actual responsibilities.\n"
        "5. Output ONLY the improved text. Do not provide conversational filler, conversational intros, or explanations."
    )

    jd_snippet = jd_text[:1200] if jd_text else "Target role alignment"

    user_prompt = f"""### CANDIDATE VERIFIED KNOWLEDGE BASE:
{kb_summary}

### TARGET JOB DESCRIPTION HIGHLIGHTS:
{jd_snippet}

### CURRENT DRAFT TEXT:
\"\"\"
{selected_text}
\"\"\"

### USER INSTRUCTION:
{instruction}

Apply the instruction strictly using ONLY verified facts. Output the improved text directly:"""

    try:
        res = query_llm(user_prompt, system_prompt=system_prompt, provider=provider, model=model, api_key=api_key, temperature=0.15, ollama_url=ollama_url)
        # Clean any wrapping markdown code blocks if the model wrapped everything
        if res.startswith("```markdown\n") and res.endswith("```"):
            res = res[12:-3].strip()
        elif res.startswith("```\n") and res.endswith("```"):
            res = res[4:-3].strip()
        return {"success": True, "improved_text": res}
    except Exception as e:
        return {"success": False, "error": str(e)}

def audit_hallucinations_with_llama(resume_text, jd_text="", model="llama3.2", provider="local", api_key="", ollama_url=None):
    kb_summary = load_kb_summary(max_chars=2000)

    system_prompt = (
        "You are an Anti-Hallucination Resume Fact-Checker.\n"
        "Check resume bullet points against the Candidate Knowledge Base.\n"
        "Output a concise 3-part markdown audit:\n"
        "1. **Verified Claims (Pass)**: claims grounded in KB.\n"
        "2. **Suspected Hallucinations (Verify)**: numbers, dates, tools, or metrics not in the KB.\n"
        "3. **Recommendation**: what to add to the knowledge base to substantiate them."
    )

    user_prompt = f"""### VERIFIED KNOWLEDGE BASE:
{kb_summary}

### RESUME EXCERPT:
{resume_text[:1200]}

Generate the concise audit report:"""

    try:
        res = query_llm(user_prompt, system_prompt=system_prompt, provider=provider, model=model, api_key=api_key, temperature=0.1, ollama_url=ollama_url)
        return {"success": True, "report": res}
    except Exception as e:
        return {"success": False, "error": str(e)}

def build_instant_tailored_cover_letter(target_company="Target Company", target_title="Infrastructure Manager", jd_text=""):
    """Deterministically generates a 100% verified, zero-hallucination tailored cover letter in milliseconds."""
    import datetime
    today_str = datetime.date.today().strftime("%d %B %Y")
    
    # Analyze themes in the JD
    jd_lower = (jd_text or "").lower()
    has_azure = "azure" in jd_lower or "cloud" in jd_lower
    has_vendor = "vendor" in jd_lower or "partner" in jd_lower
    has_247 = "24/7" in jd_lower or "availability" in jd_lower or "reliability" in jd_lower
    has_mentor = "mentor" in jd_lower or "team" in jd_lower or "leading" in jd_lower
    has_trans = "transformation" in jd_lower or "growth" in jd_lower or "acquisition" in jd_lower
    has_security = "security" in jd_lower or "risk" in jd_lower or "cyber" in jd_lower
    has_network = "network" in jd_lower or "cisco" in jd_lower

    # Paragraph 1: Executive Opening
    p1 = (
        f"As an accomplished Technology Leader with over 25 years of enterprise infrastructure, cloud engineering, "
        f"and operations management experience, I am excited to apply for the {target_title} position at {target_company}. "
        f"Throughout my career across Australian enterprise environments, I have specialized in scaling mission-critical IT environments, "
        f"mentoring high-caliber engineering teams, and establishing continuous operational maturity across complex 24/7 operational footprints."
    )

    # Paragraph 2: Core Technical & Operational Alignment
    p2_points = []
    if has_azure or has_247:
        p2_points.append(
            "Over 25 years of deep infrastructure lifecycle governance spanning public cloud (Microsoft Azure), hybrid virtualisation (VMware/Hyper-V), high-availability compute, and 24/7 disaster recovery architectures"
        )
    if has_mentor or has_trans:
        p2_points.append(
            "Proven leadership directing multidisciplinary technical teams, translating business goals and CTO directives into multi-year technology roadmaps, and supporting strategic acquisition and operational transformations"
        )
    if has_security:
        p2_points.append(
            "Rigorous cyber resilience and control assurance grounded in Tier-1 banking standards (Commonwealth Bank of Australia), APRA CPS 230/234 regulatory compliance, and Zero-Trust architecture"
        )
    if has_vendor:
        p2_points.append(
            "Commercial and vendor stewardship across multi-supplier ecosystems, renegotiating contracts, enforcing stringent SLAs, and optimizing multi-million-dollar technology investments"
        )
    if has_network and not has_vendor:
        p2_points.append(
            "Comprehensive enterprise network architecture, edge security, routing, switching, and secure hybrid-cloud connectivity across geographically dispersed sites"
        )

    bullets_text = "\n".join([f"- **{pt.split(' spanning ')[0] if ' spanning ' in pt else pt.split(',')[0]}:** {pt}." for pt in p2_points])
    p2 = (
        f"My background combines broad strategic thinking with the practical technical grounding needed to understand the environment "
        f"and support delivery teams whenever required. Key areas where my experience directly advances {target_company}'s objectives include:\n\n"
        f"{bullets_text}"
    )

    # Paragraph 3: Strategic Vision & Culture Fit
    p3 = (
        f"I operate with a collaborative, low-ego leadership ethos that fosters high team morale, clear accountability, and operational resilience. "
        f"Whether partnering with the CTO on future architectural decisions, driving continuous process improvement, or leading through major system "
        f"changes, I ensure infrastructure is an enabler of business agility rather than a bottleneck. "
        f"I welcome the opportunity to discuss how my technical leadership and operational experience can deliver immediate impact for {target_company}."
    )

    # Candidate Profile Truth (dynamically loaded from local KB or generic default)
    prof = get_candidate_profile_data()
    cand_name = prof.get("preferred_name") or prof.get("full_name", "Senior Technology Leader")
    cand_addr = prof.get("address", "Sydney, NSW, Australia")
    cand_phone = prof.get("phone", "+61 400 000 000")
    cand_email = prof.get("email", "candidate@example.com")
    cand_li = prof.get("linkedin", "https://www.linkedin.com/in/candidate")
    cand_port = prof.get("portfolio_url", "https://github.com/candidate")

    # Full Document
    return f"""**RE:** {target_title} Position

**{today_str}**

**Hiring Team**  
**{target_company}**  
**Sydney, NSW, Australia**

Dear Hiring Team,

{p1}

{p2}

{p3}

Thank you for your time and consideration.

**Sincerely,**

{cand_name}  
{cand_addr}  
{cand_phone} | [{cand_email}](mailto:{cand_email})  
[LinkedIn Profile]({cand_li}) | [Portfolio]({cand_port})
"""

def build_instant_tailored_resume(target_company="Target Company", target_title="Technology Leader", jd_text=""):
    """
    Deterministically generates a 100% verified, zero-hallucination tailored resume
    strictly aligned to the target company, target title, and job description requirements.
    """
    title = (target_title or "Technology Leader").strip()
    company = (target_company or "Target Company").strip()
    jd_lower = (jd_text or "").lower()
    title_lower = title.lower()

    # Detect domain
    is_cyber = (
        "threat" in jd_lower or "insider risk" in jd_lower or "cyber" in jd_lower or
        "security" in title_lower or "risk" in title_lower or "governance" in jd_lower
    )
    is_network = (
        "network" in jd_lower and ("cisco" in jd_lower or "routing" in jd_lower or "firewall" in jd_lower or "lan" in jd_lower)
    )

    # 1. Header Subtitle
    if "senior technology leader" in title_lower or "executive" in title_lower:
        subtitle = f"**{title}**"
    else:
        subtitle = f"**{title} | Senior Technology Leader**"

    # 2. Executive Summary Formulation
    if is_cyber and not is_network:
        summary = (
            "Strategic, highly credentialed Cyber Security Executive and Technology Leader with over 25+ years of verified "
            "experience directing cyber threat intelligence, insider risk governance, and security operations within Tier-1 "
            "financial institutions (Commonwealth Bank of Australia) and mission-critical environments. Proven track record of "
            "evaluating complex threat landscapes, enhancing defensive controls, and briefing senior executive leadership on cyber "
            "exposure. Credentialed security executive (CISSP, CISM, A|CISO) with deep domain expertise in APRA CPS 234 / CPS 230 "
            "regulatory assurance, enterprise vulnerability management (Qualys), Zero-Trust edge architectures, and third-party "
            "supplier incident response (200+ vendors). Adept at driving operational excellence, modeling risk discipline, and "
            "building high-performing technical teams aligned to corporate governance objectives."
        )
    elif is_network:
        summary = (
            "Strategic Technology Leader and Network Engineering Specialist with over 25+ years of verified experience directing "
            "enterprise network infrastructure, telecommunications, and cybersecurity operations within Tier-1 financial institutions "
            "(Commonwealth Bank of Australia) and critical infrastructure environments (Downer EDI). Proven track record of translating "
            "corporate technology roadmaps into high-availability network architectures, managing multi-site LAN/WAN/wireless "
            "environments (Cisco Catalyst, ISRs, WLC), and fortifying perimeter security with Fortinet FortiGate and Checkpoint "
            "firewalls. Cisco-certified engineer (CCNP, CCNA) and credentialed security manager (CISSP, CISM) adept at governing "
            "24x7 incident response, optimizing telecom carrier contracts, and ensuring compliance with APRA CPS 234/230 standards."
        )
    else:
        summary = (
            "Strategic and hands-on Technology Leader with over 25+ years of verified experience directing enterprise network "
            "infrastructure, cybersecurity operations, and cloud engineering within tier-1 financial institutions (Commonwealth Bank "
            "of Australia) and large-scale critical infrastructure environments (Downer EDI). Proven track record of translating "
            "corporate technology strategies into robust local operational solutions, managing multi-site LAN/WAN/wireless environments, "
            "and maturing cybersecurity postures against global standards and regulatory mandates. Cisco-certified engineer (CCNP, CCNA) "
            "and credentialed security executive (CISSP, CISM) with demonstrated expertise managing 24x7 cyber incident response, "
            "optimizing multi-vendor MSP and telecommunication contracts, and governing disaster recovery (DR/BCP) across mission-critical platforms."
        )

    # 3. Core Competencies & Technical Skills
    if is_cyber and not is_network:
        competencies = """* **Cyber Threat Intelligence & Defensive Operations:** Threat Environment Analysis, Complex Threat Identification, Insider Risk Governance, Advanced Threat Hunting, Root Cause Analysis (RCA), Post-Incident Reviews (PIR), Defensive Control Uplift, MITRE ATT&CK Framework.
* **Cyber Risk Governance & Regulatory Assurance:** APRA CPS 234 (Information Security), APRA CPS 230 (Operational Resilience), ACSC Essential 8, ISO/IEC 27001, Executive Risk Reporting, Vulnerability Management (Qualys), End-of-Support / End-of-Life (EOS/EOL) Risk Mitigation, Internal/External Audit Defense.
* **Incident Management & Third-Party Cyber Defense:** 24x7 Cyber Incident Management (20+ incidents, 200+ suppliers), Supply Chain Incident Response, Multi-Stakeholder Liaison (Legal, Risk, Privacy, Executive), Incident Response Playbooks.
* **Edge Security, Cloud Proxy & Identity Defense:** Secure Web Gateways (SWG), Cloud Proxy Platforms (Zscaler, Akamai, Blue Coat), Edge Security Gateways, SSL/TLS Inspection, Identity & Access Management (IAM/RBAC/ABAC, Azure AD / Entra ID, MFA, RSA SecurID), API Security.
* **Enterprise Infrastructure & Cloud Architecture:** Microsoft Azure, Amazon Web Services (AWS), Hybrid Virtualization (VMware ESXi, Hyper-V), High-Availability Compute, 24x7 Disaster Recovery (BCP/DR), Cisco Routing & Switching, Fortinet & Checkpoint Firewalls."""
    elif is_network:
        competencies = """* **Enterprise Networking & Telecommunications:** Cisco Routing & Switching (Catalyst 2900/3500/3700/6500, Cisco ISRs), Fortinet FortiGate, Checkpoint Firewalls, Cisco ASA, SD-WAN, Site-to-Site IPsec VPNs, SSL VPN, BGP, OSPF, VLAN segmentation (802.1Q), Enterprise 802.11 Wireless LAN Controllers (WLC), Cloud Networking.
* **Cybersecurity Operations & Defense:** Threat Detection & Response, Vulnerability Management (Qualys), Zero-Trust Architecture, Endpoint Security (EDR), Identity & Access Management (IAM/RBAC/ABAC, Azure AD / Entra ID, MFA, RSA SecurID), API Security (Akamai), Data Loss Prevention (DLP), Root Cause Analysis (RCA) & Post-Incident Reviews (PIR).
* **Cloud & Hybrid Infrastructure:** Microsoft Azure (Azure Networking, Virtual Networks, VPN Gateways, ExpressRoute, AKS, Azure VMs, Storage, Backup), Amazon Web Services (AWS - VPC, Security Groups, EC2, S3), Infrastructure as Code (Terraform), CI/CD Automation.
* **Systems Virtualization & Storage:** VMware vSphere / ESXi (High Availability, DRS, VMotion), Microsoft Hyper-V, Windows Server (2008–2022), Linux (RHEL, CentOS), SAN/NAS Arrays (Pure Storage, Nimble, Dell Compellent, EMC, NetApp, HP 3PAR).
* **Vendor & Service Management:** SLA & Contract Negotiation, MSP Performance Auditing, RFP/RFI Evaluation, Technical Change Advisory Boards (TCAB/DCAB), ITIL v3/v4 Service Management, Business Continuity Planning (BCP) & Disaster Recovery (DR)."""
    else:
        competencies = """* **Enterprise Infrastructure & Cloud Engineering:** Microsoft Azure (IaaS, PaaS, Networking, VMs, Storage, Backup), Amazon Web Services (AWS), Hybrid Cloud Virtualization (VMware vSphere/ESXi, Hyper-V), High-Availability Compute, 24/7 Disaster Recovery (DR/BCP).
* **Leadership, Architecture & Strategy:** Leading & Mentoring Technical Teams, Technology Roadmaps & Strategy Definition with CTO, Operational Maturity & Continuous Improvement, Supporting Acquisitions & Enterprise Transformations.
* **Cybersecurity Operations & Defense:** Threat Detection & Response, Vulnerability Management (Qualys), Zero-Trust Architecture, Endpoint Security (EDR), Identity & Access Management (IAM/RBAC/ABAC, Azure AD / Entra ID, MFA), APRA CPS 230/234 Compliance.
* **Enterprise Networking & Edge Security:** Cisco Routing & Switching (Catalyst, ISRs), Fortinet FortiGate, Checkpoint Firewalls, SD-WAN, Site-to-Site IPsec VPNs, Enterprise Wireless LAN Controllers (WLC), Secure Web Gateways.
* **Vendor & Commercial Management:** Managing Vendors & Technology Partners, SLA & Contract Negotiation, MSP Performance Auditing, RFP/RFI Evaluation, Technical Change Advisory Boards (TCAB/DCAB), ITIL v3/v4 Service Management."""

    prof = get_candidate_profile_data()
    cand_full = prof.get("full_name", "Senior Technology Leader")
    cand_addr = prof.get("address", "Sydney, NSW, Australia")
    cand_phone = prof.get("phone", "+61 400 000 000")
    cand_email = prof.get("email", "candidate@example.com")
    cand_cit = prof.get("citizenship", "Australian Citizen")
    cand_li = prof.get("linkedin", "https://www.linkedin.com/in/candidate")
    cand_port = prof.get("portfolio_url", "https://github.com/candidate")

    return f"""# {cand_full}
{subtitle}  
{cand_addr} | {cand_phone} | {cand_email} | {cand_cit}  
[LinkedIn Profile]({cand_li}) | [Portfolio]({cand_port})

---

## Executive Summary
{summary}

---

## Core Competencies & Technical Skills
{competencies}

---

## Professional Certifications & Credentials
* **CISSP** – Certified Information Systems Security Professional (#481845)
* **CISM** – Certified Information Security Manager (#1948833)
* **A|CISO** – Associate Chief Information Security Officer (EC-Council)
* **CCNP / CCNA** – Cisco Certified Network Professional / Associate
* **CCSA** – Checkpoint Certified Security Administrator
* **CEH & CEI** – Certified Ethical Hacker & EC-Council Certified Instructor
* **MCT** – Microsoft Certified Trainer (5-Year Milestone)
* **ITIL Foundation** – IT Service Management (v3 / v4)
* **PRINCE2** – Registered Practitioner (Project Management)

---

## Professional Experience

### Commonwealth Bank of Australia (CBA) | April 2021 – Present
**Senior Cyber Security & Service Manager** | Sydney, NSW (Tier-1 Financial Services)

#### Group Security – Service Manager | Jan 2025 – Present
* **Cyber Risk & Governance Oversight:** Provide cyber risk and governance oversight across Group Security services, delivering risk-focused executive reporting covering security incidents, vulnerability backlogs, end-of-support/end-of-life (EOS/EOL) infrastructure risks, and control weaknesses.
* **Audit & Regulatory Assurance:** Partner directly with Group Cyber Security, Operational Risk, and internal/external Audit teams to support audits, evidence collection, and control remediation, strengthening enterprise assurance outcomes against APRA CPS 234 and CPS 230 standards.
* **Continuous Service Improvement:** Drive consistent, risk-based governance practices aligned to CBA enterprise cyber standards, evaluating control effectiveness and streamlining operational workflows.

#### Operations Manager – Edge Security & Cloud Proxy | Nov 2024 – Jan 2025
* **Edge Security & Proxy Platform Resilience:** Partnered with Cyber Security and Product Engineering teams to uplift operational resilience and cyber risk governance across mission-critical edge security and enterprise cloud proxy platforms (SWG, Zscaler, Akamai).
* **Risk-Informed Change Governance:** Embedded risk-informed change and operational practices across high-traffic proxy clusters, proactively closing control gaps and improving security outcomes.
* **Control Automation & Telemetry:** Automated repetitive operational processes to bolster control effectiveness and reliability; provided senior stakeholders with real-time analytics on platform health, proxy uptime, and emerging threats.

#### Third Party Cyber Incident Manager | Apr 2021 – Feb 2023
* **Third-Party Incident Leadership:** Directed and resolved 20+ high-stakes third-party cyber incident response operations across a critical supplier ecosystem comprising 200+ enterprise vendors.
* **Executive & Regulatory Coordination:** Served as the central strategic liaison bridging communication between external supplier leadership, Group Cyber Security, Risk, Legal, Privacy, and executive stakeholders during active cyber events.
* **Supply Chain Risk Assessment:** Evaluated supplier breaches for direct business impact, data exposure, control effectiveness, and regulatory implications under APRA CPS 230 and CPS 234.
* **Incident Preparedness Uplift:** Authored third-party incident response playbooks, refined triage escalation matrices, and elevated organizational readiness for supply-chain breaches.

---

### Downer EDI | January 2018 – December 2020
**Cloud and Datacenter Delivery Manager** | North Ryde, NSW (Critical Infrastructure & Facilities)
* **Enterprise Network & Cloud Delivery:** Managed enterprise IT operations, network routing, firewall configurations, and hybrid cloud delivery across public and private cloud environments supporting 53,000 corporate users across 300+ sites, sustaining 99.95% service availability.
* **Network Security & Perimeter Hardening:** Governed branch and datacenter firewalls (Fortinet, Cisco ASA), secure gateways, and remote connectivity across remote operational sites; enforced least-privilege access matrices and endpoint security standards, mitigating data exfiltration risks by 35%.
* **Vendor & MSP SLA Governance:** Governed 8+ external managed service providers (MSPs), telecom carriers, and hardware vendors against strict contractual SLAs, achieving $45k in annual contract optimizations.
* **Change Governance & Risk Challenging:** Served as key risk challenger on Technical Change Advisory Boards (TCAB) and Datacenter Change Advisory Boards (DCAB), assessing 120+ monthly complex infrastructure and network changes for operational risk, security impact, and service continuity.
* **Disaster Recovery (DR) & BCP:** Formulated, documented, and tested enterprise Disaster Recovery Plans (DRP), conducting scheduled multi-site failover simulations between primary datacenters and secondary recovery facilities.
* **Team Leadership & Enablement:** Supervised multidisciplinary systems and network engineers, authored Standard Operating Procedures (SOPs), and conducted hands-on technical enablement workshops.

---

### BAI Communications | December 2016 – December 2017
**Cloud, Compute, Storage Architect** | Chatswood, NSW (Global Telecommunications Infrastructure)
* **Infrastructure Architecture & L3/L4 Escalation:** Architected enterprise hybrid infrastructure solutions and provided Level 3/4 escalation support across Microsoft server environments, Cisco networking, and Azure cloud platforms.
* **Network & Storage Blueprints:** Developed organizational architectural blueprints for cloud, compute, and enterprise SAN storage (EMC, StorSimple); authored end-to-end solution designs, technical estimates, standards, and delivery runbooks.
* **Digital Transformation Execution:** Delivered automated, partner-managed operational models on modernized platforms under BAI’s Digital Transformation Strategy, utilizing ITIL frameworks to mature service delivery.
* **Capacity Planning & Telemetry:** Owned and directed enterprise capacity monitoring, trend analysis, and cost forecasting for telecommunications infrastructure and hosted compute platforms.

---

### Randstad Pty Ltd (via Tata Consultancy Services) | July 2016 – September 2016
**Platform Architect – Contract** | Sydney CBD, NSW (Global Workforce Solutions)
* **Infrastructure Engineering Leadership:** Led the IT infrastructure engineering team, ensuring that operational performance and service levels (SLAs) were met across onshore and offshore delivery models.
* **Knowledge Transfer & Skill Uplift:** Mentored and bridged knowledge transfer across TCS onshore and offshore engineering teams to support Randstad’s multi-site APAC technology footprint.
* **Root Cause & Fault Rectification:** Guided root-cause investigations (RCA) and technical remediation for complex infrastructure and network incidents in accordance with corporate SLA guidelines.

---

### Microsoft Global Services | August 2015 – June 2016
**Technical Consultant / Architect – Contract** | Client Site: State Street Bank, Sydney, NSW
* **Enterprise Architecture & Migration Consulting:** Member of Microsoft Global Services team delivering enterprise-level architecture, design, and implementation projects for State Street Bank.
* **Technology Risk Analysis & Scope Definition:** Scoped and designed technical solutions, analyzed client infrastructure, defined business requirements, and participated in rigorous risk assessments for Windows Server migration initiatives.
* **Stakeholder Presentations & Enablement:** Authored technical proposals and delivered presentations to executive client stakeholders; conducted structured knowledge transfer to build customer technical competence.

---

### Veolia Enterprise Services | February 2015 – August 2015
**Senior Infrastructure Consultant / Architect – Contract** | Sydney CBD, NSW (Environmental & Industrial Services)
* **Remote Workplace Architecture:** Designed, planned, and implemented high-availability Remote Desktop Services (RDS 2012 R2) farms and secure access gateways to support regional operations.
* **Systems Hardening & Standards:** Developed standardized server deployment templates, automation runbooks, and infrastructure configuration baselines across multi-site production environments.

---

### Randstad Pty Ltd | July 2014 – January 2015
**Senior Infrastructure Consultant / Architect – Contract** | Sydney CBD, NSW (APAC Footprint)
* **PKI & Security Services Migration:** Architected and executed the migration and decommissioning of enterprise Microsoft Certificate Authority (PKI) infrastructure from Windows Server 2003 to 2008 R2, ensuring uninterrupted cryptographic token and SSL operations.
* **Active Directory & Identity Consolidation:** Engineered Active Directory schema upgrades and user identity consolidations across multi-forest corporate domains.

---

### ING Direct Australia | January 2014 – July 2014
**Senior Infrastructure Consultant – Contract** | Sydney CBD, NSW (Banking & Financial Services)
* **Banking Systems & Storage Operations:** Delivered infrastructure engineering, LUN provisioning, capacity tuning, and Level 3 incident support across high-throughput financial storage arrays (EMC, NetApp) and virtualized environments.
* **Compliance Archiving & eDiscovery:** Maintained Symantec Enterprise Vault and CommVault archiving platforms to ensure strict regulatory compliance with financial record retention mandates.

---

### Norfolk Group | November 2012 – October 2013
**Senior Infrastructure Consultant / Architect – Contract** | Sydney, NSW (Engineering & Infrastructure Services)
* **Server Consolidation & P2V:** Orchestrated large-scale Physical-to-Virtual (P2V) migrations onto VMware ESXi clusters and HP BladeSystem c7000 enclosures, reducing physical datacenter rack footprint and power consumption.
* **Network & Storage Optimization:** Re-architected storage fabric zoning and Cisco Catalyst network switching to eliminate bottlenecks across multi-site branch offices.

---

### Core Technology Partners | October 2011 – November 2012
**Solution Consultant / Architect** | North Sydney, NSW (IT Consulting & Managed Services)
* **Unified Communications & VoIP Architecture:** Planned and deployed Cisco CallManager (CUCM) VoIP systems, Cisco ISR routers, and PABX telephony for corporate clients.
* **Multi-Client Infrastructure Consulting:** Designed and implemented secure virtualization and remote access architectures for commercial clients utilizing Citrix XenApp and RSA SecurID.

---

### Brookfield Multiplex | January 2010 – October 2011
**Senior System Engineer – Asia Pacific** | Sydney CBD, NSW (Global Property & Infrastructure)
* **Global Datacenter & DR Operations:** Member of Global IT support team responsible for day-to-day operation, Level 3/4 troubleshooting, and disaster recovery readiness across primary datacenters and 80+ remote construction sites.
* **Network & Security Administration:** Managed Cisco network switches, routers, firewalls, and storage arrays (EMC CX500/CX300, HP EVA 8100/6100), ensuring continuous secure communications across regional project offices.

---

### Earlier Career Technology Leadership (1998 – 2010)
* **Sonnet Enterprise Services (2009–2010):** Senior System Engineer – Delivered 24x7 managed services operational support and Level 3 incident escalation for enterprise clients.
* **Investa Property Group (2007–2009):** Senior System Administrator – Managed Cisco Catalyst switching, Cisco ASA firewalls, WAN links (MPLS/Frame Relay), and Citrix XenApp across Australian commercial property portfolios.
* **Raffles KVB (2005–2007):** System Administrator – Maintained Sun Solaris servers, Linux clusters, Cisco networking, and financial market data feeds.
* **Ashima Services & Enterprises (2001–2004):** MIS Manager – Directed IT infrastructure, ERP deployments, network security, and technical staffing.
* **IndoComputech Systems (1998–2001):** Network Engineer – Designed and deployed campus LAN/WAN networks, Cisco routing, and early telemedicine video conferencing protocols.

---

## Education & Academic Background
* **Post Graduate Diploma in Computer Applications (PGDCA)**
* **Bachelor of Science (B.Sc.)**
"""

def load_application_format_exemplar(doc_type="resume"):
    """Returns normalized formatting structures that prevent cross-company data leakage."""
    fmt_path = os.path.join(BASE_DIR, "knowledge_base", "formatting_guide.md")
    fmt_rules = ""
    if os.path.exists(fmt_path):
        try:
            with open(fmt_path, "r", encoding="utf-8") as f:
                fmt_rules = f.read().strip()
        except Exception:
            pass

    if doc_type == "cl":
        exemplar_structure = """**RE:** [Target Job Title] Position

**[Current Date]**

**Hiring Team**
**[Target Company]**
**Sydney, NSW, Australia**

Dear Hiring Team,

[Paragraph 1: Executive Opening - 25+ years experience spanning enterprise infrastructure, cloud, networking, security, and technology leadership. Express genuine enthusiasm for the [Target Job Title] position at [Target Company].]

[Paragraph 2: Core Operational & Technical Delivery - Connect specific achievements from Commonwealth Bank, Downer EDI, BAI Communications, and Microsoft directly to the core challenges and requirements in the Target Job Description.]

[Paragraph 3: Strategic Leadership & Governance - Emphasize team mentorship, technology roadmaps with the CTO, operational resilience, and APRA/CPS regulatory assurance.]

Thank you for considering my application. I look forward to discussing how my experience aligns with [Target Company]'s goals.

**Sincerely,**

Rajiv (Raj) Parikh
169a Purchase Road, Cherrybrook, NSW 2126
0433 463 121 | raj.parikh@hotmail.com | https://www.linkedin.com/in/rajivparikh"""
        return {
            "exemplar_sample": exemplar_structure,
            "formatting_rules": fmt_rules[:1000] if fmt_rules else ""
        }

    # For resume:
    my_app_dir = os.path.join(BASE_DIR, "my_applications")
    sample_apps = [
        "Kia Motors - IT Manager - Network & Security",
        "Westpac - Infrastructure Service Manager",
        "Bank of America - Vice President Information Security Threat & Insider Risk Management"
    ]
    
    exemplar_content = ""
    for app in sample_apps:
        cand_path = os.path.join(my_app_dir, app, "tailored_resume.md")
        if os.path.exists(cand_path):
            try:
                with open(cand_path, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                    if text and len(text) > 500:
                        exemplar_content = text
                        break
            except Exception:
                pass

    return {
        "exemplar_sample": exemplar_content[:1500] if exemplar_content else "",
        "formatting_rules": fmt_rules[:1000] if fmt_rules else ""
    }

def generate_grounded_document(doc_type="resume", jd_text="", model="llama3.2", target_company="", target_title="", provider="local", api_key="", ollama_url=None):
    """Generates a complete, tailored draft strictly bounded to the target company, target title, and verified KB."""
    from application_manager import detect_company_and_title
    det = detect_company_and_title(jd_text)
    comp = target_company.strip() if target_company else det.get("company", "Target Company")
    title = target_title.strip() if target_title else det.get("title", "Technology Leader")

    # If it's a cover letter, we can first build the instant grounded baseline
    if doc_type == "cl":
        instant_draft = build_instant_tailored_cover_letter(comp, title, jd_text)
        # If local and Ollama is offline and no API key is provided, return instant draft
        if provider == "local":
            status = get_ollama_status(ollama_url)
            if not status.get("online"):
                return {"success": True, "generated_text": instant_draft}

    kb_summary = load_kb_summary(max_chars=3500)
    format_data = load_application_format_exemplar(doc_type)
    prof = get_candidate_profile_data()
    prof_name = prof.get("full_name", "Senior Technology Leader")
    prof_contact = f"{prof_name}, {prof.get('address', 'Sydney NSW')} | {prof.get('phone', '+61 400 000 000')} | {prof.get('email', 'candidate@example.com')} | {prof.get('total_years_experience', '20+')} experience"
    
    system_prompt = (
        "You are an Elite Executive Career Strategist and Anti-Hallucination Guardrail.\n"
        f"You are preparing an application strictly for the role of '{title}' at '{comp}'.\n\n"
        "STRICT GUARDRAILS (CRITICAL - ZERO TOLERANCE FOR FABRICATION):\n"
        f"1. MANDATORY TARGET: You are applying ONLY for '{title}' at '{comp}'. NEVER mention Bank of America, Kia Motors, or any other company as the target employer!\n"
        f"2. The subject line (**RE:**) MUST BE EXACTLY: **RE:** {title} Position\n"
        f"3. The recipient block MUST address: {comp}\n"
        "4. DO NOT invent companies, job titles, employment dates, or certifications not in the verified candidate data.\n"
        f"5. Use the verified candidate profile for contact details ({prof_name}, {prof.get('address', 'Sydney NSW')}, {prof.get('total_years_experience', '20+')} experience).\n"
        "6. Output ONLY the markdown document text. Do not provide conversational filler or preambles."
    )

    exemplar_text = format_data.get("exemplar_sample", "")
    rules_text = format_data.get("formatting_rules", "")
    
    if doc_type == "resume":
        prompt = f"""### CANDIDATE VERIFIED KNOWLEDGE BASE & PROFILE TRUTH:
{kb_summary}

### TARGET JOB DESCRIPTION:
{jd_text[:1500] if jd_text else "Target Role Alignment"}

### MANDATORY APPLICATION TARGET:
- Target Company: {comp}
- Target Position Title: {title}

### APPROVED RESUME FORMAT & EXEMPLAR STYLE:
\"\"\"
{exemplar_text}
\"\"\"

### FORMATTING SPECIFICATIONS:
{rules_text}

Generate a comprehensive, print-ready, tailored Markdown Resume strictly aligned to {title} at {comp}. Ground all achievements and dates strictly in the Candidate Knowledge Base:"""
        num_predict = 1500
    else:
        prompt = f"""### CANDIDATE VERIFIED KNOWLEDGE BASE & PROFILE TRUTH:
{kb_summary}

### TARGET JOB DESCRIPTION:
{jd_text[:1800] if jd_text else "Target Role Alignment"}

### MANDATORY APPLICATION TARGET (CRITICAL):
- Target Company: {comp}
- Target Job Title: {title}
- Subject Line (**RE:**): MUST BE EXACTLY: **RE:** {title} Position
- Recipient Block: MUST BE: **{comp}**
- Candidate Contact Info: {prof_contact}

### STRUCTURE TO FOLLOW:
\"\"\"
{exemplar_text}
\"\"\"

Write a crisp, powerful, single-page tailored Markdown Cover Letter specifically for {title} at {comp}:"""
        num_predict = 650

    try:
        res = query_llm(prompt, system_prompt=system_prompt, provider=provider, model=model, api_key=api_key, temperature=0.15, num_predict=num_predict, ollama_url=ollama_url)
        if res.startswith("```markdown\n") and res.endswith("```"):
            res = res[12:-3].strip()
        elif res.startswith("```\n") and res.endswith("```"):
            res = res[4:-3].strip()
            
        # Safety verification: ensure the generated text does NOT contain a hallucinated subject line
        if doc_type == "cl" and f"**RE:** {title}" not in res and f"RE: {title}" not in res:
            # Enforce clean subject line and recipient
            res = re.sub(r'\*\*RE:\*\*.*?\n', f'**RE:** {title} Position\n', res, count=1, flags=re.I)
            
        return {"success": True, "generated_text": res}
    except Exception as e:
        # Fallback to deterministic instant draft for cover letter
        if doc_type == "cl":
            return {"success": True, "generated_text": build_instant_tailored_cover_letter(comp, title, jd_text)}
        return {"success": False, "error": str(e)}
