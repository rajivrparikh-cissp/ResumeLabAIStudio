import os
import sys
import json
import re
import datetime
import zipfile

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "app"))

from application_manager import set_active_target, get_active_target, detect_company_and_title
from llm_copilot import build_instant_tailored_resume, build_instant_tailored_cover_letter
from intelligence_engine import load_kb_data, analyze_jd_alignment

def run_test_suite():
    results = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": 6,
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    def record_test(name, passed, details="", errors=None):
        test_entry = {
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "details": details,
            "errors": errors or []
        }
        results["tests"].append(test_entry)
        if passed:
            results["passed"] += 1
            print(f" [PASS] {name}: {details}")
        else:
            results["failed"] += 1
            print(f" [FAIL] {name}: {details}")
            if errors:
                for err in errors:
                    print(f"        -> {err}")

    print("=" * 70)
    print(" RESUME LAB AUTOMATED E2E PIPELINE & REGRESSION TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: Role Generation & Cross-Contamination Test (Bank of America VP)
    # -------------------------------------------------------------
    try:
        t1_company = "Bank of America"
        t1_title = "Vice President, Information Security Threat & Insider Risk Management Specialist"
        t1_jd = (
            "This job is responsible for leading evaluations of cyber security threats and enhancing defensive capabilities. "
            "Key responsibilities include threat analysis, situational awareness, insider risk oversight, and managerial responsibilities."
        )

        res1 = build_instant_tailored_resume(t1_company, t1_title, t1_jd)
        cl1 = build_instant_tailored_cover_letter(t1_company, t1_title, t1_jd)

        t1_errors = []
        if "Infrastructure Manager" in res1:
            t1_errors.append("Resume contains stale title 'Infrastructure Manager'")
        if t1_title not in res1:
            t1_errors.append(f"Resume does not contain expected title '{t1_title}'")
        if "cyber threat intelligence" not in res1.lower():
            t1_errors.append("Resume executive summary does not emphasize cyber threat intelligence")
        if f"**RE:** {t1_title} Position" not in cl1:
            t1_errors.append("Cover letter has mismatched subject line")
        if t1_company not in cl1:
            t1_errors.append(f"Cover letter does not mention '{t1_company}'")

        record_test(
            "Test 1: Target Role Assembly & Cross-Contamination Check (Bank of America VP)",
            len(t1_errors) == 0,
            f"Verified resume & CL for {t1_company} without stale 'Infrastructure Manager' artifacts",
            t1_errors
        )
    except Exception as e:
        record_test("Test 1: Target Role Assembly (Bank of America VP)", False, "Exception occurred", [str(e)])

    # -------------------------------------------------------------
    # TEST 2: Role Switching & Clean Separation Test (Kia Motors IT Manager)
    # -------------------------------------------------------------
    try:
        t2_company = "Kia Motors"
        t2_title = "IT Manager - Network & Security"
        t2_jd = (
            "Responsible for enterprise networking, Cisco switching, Fortinet firewalls, SD-WAN, and telecommunications. "
            "Manage infrastructure and cybersecurity for automotive corporate sites."
        )

        res2 = build_instant_tailored_resume(t2_company, t2_title, t2_jd)
        cl2 = build_instant_tailored_cover_letter(t2_company, t2_title, t2_jd)

        t2_errors = []
        if "Bank of America" in res2 or "Bank of America" in cl2:
            t2_errors.append("Kia Motors documents contain leaked 'Bank of America' text")
        if "Vice President" in res2:
            t2_errors.append("Kia Motors resume contains leaked 'Vice President' title")
        if "IT Manager - Network & Security" not in res2:
            t2_errors.append("Kia Motors resume does not contain 'IT Manager - Network & Security'")
        if "Cisco" not in res2:
            t2_errors.append("Kia Motors resume does not contain expected Cisco networking competencies")
        if f"**RE:** {t2_title} Position" not in cl2:
            t2_errors.append("Kia Motors cover letter has mismatched subject line")

        record_test(
            "Test 2: Switching Role Cleanliness (Kia Motors IT Manager - Network & Security)",
            len(t2_errors) == 0,
            f"Verified clean switch to {t2_company} with zero cross-contamination from prior roles",
            t2_errors
        )
    except Exception as e:
        record_test("Test 2: Switching Role Cleanliness", False, "Exception occurred", [str(e)])

    # -------------------------------------------------------------
    # TEST 3: Master Candidate Profile Grounding & Truth Invariants
    # -------------------------------------------------------------
    try:
        t3_errors = []
        required_profile_strings = [
            "Rajiv (Raj) Parikh",
            "169a Purchase Road, Cherrybrook, NSW 2126",
            "0433 463 121",
            "raj.parikh@hotmail.com",
            "25+ years"
        ]

        # Check in res1 and res2
        for s in required_profile_strings:
            if s.lower() not in res1.lower():
                t3_errors.append(f"Resume 1 missing profile truth '{s}'")
            if s.lower() not in res2.lower():
                t3_errors.append(f"Resume 2 missing profile truth '{s}'")

        # Check certifications
        for cert in ["CISSP", "CISM", "A|CISO"]:
            if cert not in res1 or cert not in res2:
                t3_errors.append(f"Missing core certification '{cert}'")

        record_test(
            "Test 3: Anti-Hallucination & Candidate Profile Truth Invariants",
            len(t3_errors) == 0,
            "Confirmed Cherrybrook address, phone, email, 25+ years experience, and certifications intact",
            t3_errors
        )
    except Exception as e:
        record_test("Test 3: Candidate Profile Truth Invariants", False, "Exception occurred", [str(e)])

    # -------------------------------------------------------------
    # TEST 4: Word Document Compilation Pipeline (.docx validity)
    # -------------------------------------------------------------
    try:
        import subprocess
        compile_script = os.path.join(BASE_DIR, "scripts", "compile_docs.py")
        c_proc = subprocess.run([sys.executable, compile_script], capture_output=True, text=True, cwd=BASE_DIR, timeout=30)
        
        t4_errors = []
        if c_proc.returncode != 0:
            t4_errors.append(f"Compiler process failed with code {c_proc.returncode}: {c_proc.stderr}")

        res_docx = os.path.join(BASE_DIR, "output", "tailored_resume.docx")
        cl_docx = os.path.join(BASE_DIR, "output", "tailored_cover_letter.docx")

        if not os.path.exists(res_docx) or os.path.getsize(res_docx) < 5000:
            t4_errors.append("tailored_resume.docx is missing or smaller than 5KB")
        else:
            try:
                with zipfile.ZipFile(res_docx, 'r') as zf:
                    if "word/document.xml" not in zf.namelist():
                        t4_errors.append("tailored_resume.docx is not a valid OpenXML Word document")
            except Exception as ze:
                t4_errors.append(f"tailored_resume.docx zip check failed: {ze}")

        if not os.path.exists(cl_docx) or os.path.getsize(cl_docx) < 2000:
            t4_errors.append("tailored_cover_letter.docx is missing or smaller than 2KB")
        else:
            try:
                with zipfile.ZipFile(cl_docx, 'r') as zf:
                    if "word/document.xml" not in zf.namelist():
                        t4_errors.append("tailored_cover_letter.docx is not a valid OpenXML Word document")
            except Exception as ze:
                t4_errors.append(f"tailored_cover_letter.docx zip check failed: {ze}")

        record_test(
            "Test 4: Word Document Compilation Pipeline (.docx validity)",
            len(t4_errors) == 0,
            f"Successfully compiled print-ready Word resume ({os.path.getsize(res_docx) if os.path.exists(res_docx) else 0} bytes) & cover letter",
            t4_errors
        )
    except Exception as e:
        record_test("Test 4: Word Document Compilation Pipeline", False, "Exception occurred", [str(e)])

    # -------------------------------------------------------------
    # TEST 5: Permanent Archiving & Library Storage Protocol
    # -------------------------------------------------------------
    try:
        t5_errors = []
        target = get_active_target() or {}
        comp = target.get("company", "Bank of America")
        tit = target.get("title", "Vice President, Information Security Threat & Insider Risk Management Specialist")
        folder_name = f"{comp} - {tit}"
        app_folder = os.path.join(BASE_DIR, "my_applications", folder_name)

        if not os.path.exists(app_folder):
            # Create archive for active role
            from scripts.compile_docs import archive_to_application_folder
            app_folder = archive_to_application_folder()

        if not os.path.exists(app_folder):
            t5_errors.append(f"Application archive folder not found: {app_folder}")
        else:
            required_files = [
                "target_jd.md",
                "tailored_resume.md",
                "tailored_cover_letter.md",
                "compliance_report.md",
                "tailored_resume.docx",
                "tailored_cover_letter.docx",
                "application_meta.json"
            ]
            for rf in required_files:
                fpath = os.path.join(app_folder, rf)
                if not os.path.exists(fpath):
                    t5_errors.append(f"Missing archived asset: {rf}")

        record_test(
            "Test 5: Permanent Archiving & Library Storage Protocol (6 Assets)",
            len(t5_errors) == 0,
            f"All 6 assets + meta.json verified in permanent storage: {os.path.basename(app_folder)}",
            t5_errors
        )
    except Exception as e:
        record_test("Test 5: Permanent Archiving Protocol", False, "Exception occurred", [str(e)])

    # -------------------------------------------------------------
    # TEST 6: Template Visual Layout Sync & Custom Template Verification
    # -------------------------------------------------------------
    try:
        from template_manager import list_templates, get_active_template, set_active_template, inspect_template_details
        from scripts.compile_docs import compile_resume

        t6_errors = []
        tmpl_data = list_templates()
        if not tmpl_data.get("templates"):
            t6_errors.append("No templates discovered in template/ directory")
        
        active_tmpl = get_active_template()
        if not active_tmpl:
            t6_errors.append("No active template resolved")

        # Inspect default template
        insp = inspect_template_details("Resume of Raj Parikh.docx")
        if "key_styles" not in insp or "Heading 2" not in insp["key_styles"]:
            t6_errors.append("Resume of Raj Parikh.docx is missing standard 'Heading 2' or key paragraph styles")

        # Run layout sync compiler test
        res_md = os.path.join(BASE_DIR, "output", "tailored_resume.md")
        tmpl_docx = os.path.join(BASE_DIR, "template", "Resume of Raj Parikh.docx")
        test_out_docx = os.path.join(BASE_DIR, "output", "test_sync_resume.docx")
        
        sync_stats = compile_resume(res_md, tmpl_docx, test_out_docx)
        if not sync_stats.get("success"):
            t6_errors.append(f"Layout sync compile failed: {sync_stats.get('error')}")
        if sync_stats.get("bullets", 0) < 5:
            t6_errors.append(f"Unexpected low bullet count in sync result: {sync_stats.get('bullets')}")
        if sync_stats.get("sections", 0) < 3:
            t6_errors.append(f"Unexpected low section count in sync result: {sync_stats.get('sections')}")

        if os.path.exists(test_out_docx):
            os.remove(test_out_docx)

        record_test(
            "Test 6: Template Visual Layout Sync & Paragraph Style Re-Mapping",
            len(t6_errors) == 0,
            f"Successfully synced resume against '{active_tmpl}' ({sync_stats.get('sections', 0)} sections, {sync_stats.get('bullets', 0)} bullets mapped)",
            t6_errors
        )
    except Exception as e:
        record_test("Test 6: Template Visual Layout Sync", False, "Exception occurred", [str(e)])

    # Save summary report to JSON
    report_path = os.path.join(BASE_DIR, "output", "e2e_test_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("=" * 70)
    print(f" TEST RUN COMPLETE: {results['passed']}/{results['total_tests']} PASSED, {results['failed']} FAILED")
    print("=" * 70)
    return results

if __name__ == "__main__":
    res = run_test_suite()
    sys.exit(0 if res["failed"] == 0 else 1)
