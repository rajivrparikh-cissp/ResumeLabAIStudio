import os
import json
import shutil

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "user_storage_config.json")

DEFAULT_PATHS = {
    "kb_dir": os.path.join(BASE_DIR, "knowledge_base"),
    "templates_dir": os.path.join(BASE_DIR, "template"),
    "output_dir": os.path.join(BASE_DIR, "output"),
    "apps_dir": os.path.join(BASE_DIR, "my_applications"),
}

def load_user_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def resolve_path(key, default_fallback):
    # 1. Environment variable override
    env_var = f"RESUME_LAB_{key.upper()}"
    if os.environ.get(env_var):
        p = os.path.expanduser(os.environ[env_var].strip())
        return os.path.abspath(p)

    # 2. User config file
    cfg = load_user_config()
    if cfg.get(key):
        p = os.path.expanduser(cfg[key].strip())
        if not os.path.isabs(p):
            p = os.path.join(BASE_DIR, p)
        return os.path.abspath(p)

    # 3. Default fallback
    return default_fallback

def get_kb_dir():
    kb = resolve_path("kb_dir", DEFAULT_PATHS["kb_dir"])
    if not os.path.exists(kb):
        example_dir = os.path.join(BASE_DIR, "knowledge_base.example")
        if os.path.exists(example_dir) and not os.path.exists(DEFAULT_PATHS["kb_dir"]):
            return example_dir
    return kb

def get_templates_dir():
    tmpl = resolve_path("templates_dir", DEFAULT_PATHS["templates_dir"])
    os.makedirs(tmpl, exist_ok=True)
    return tmpl

def get_output_dir():
    out = resolve_path("output_dir", DEFAULT_PATHS["output_dir"])
    os.makedirs(out, exist_ok=True)
    return out

def get_apps_dir():
    apps = resolve_path("apps_dir", DEFAULT_PATHS["apps_dir"])
    os.makedirs(apps, exist_ok=True)
    return apps

def get_target_jd_path():
    out_jd = os.path.join(get_output_dir(), "target_jd.md")
    base_jd = os.path.join(BASE_DIR, "target_jd.md")
    if os.path.exists(out_jd):
        return out_jd
    return base_jd

def get_dir_stats(dpath):
    if not os.path.exists(dpath):
        return {"exists": False, "file_count": 0, "dir_count": 0, "size_kb": 0, "writable": False}
    try:
        files = [f for f in os.listdir(dpath) if os.path.isfile(os.path.join(dpath, f))]
        dirs = [d for d in os.listdir(dpath) if os.path.isdir(os.path.join(dpath, d))]
        total_size = sum(os.path.getsize(os.path.join(dpath, f)) for f in files)
        writable = os.access(dpath, os.W_OK)
        return {
            "exists": True,
            "file_count": len(files),
            "dir_count": len(dirs),
            "size_kb": round(total_size / 1024, 1),
            "writable": writable
        }
    except Exception:
        return {"exists": True, "file_count": 0, "dir_count": 0, "size_kb": 0, "writable": False}

def get_all_storage_paths():
    cfg = load_user_config()
    
    kb_path = get_kb_dir()
    tmpl_path = get_templates_dir()
    out_path = get_output_dir()
    apps_path = get_apps_dir()

    return {
        "kb_dir": {
            "path": kb_path,
            "default_path": DEFAULT_PATHS["kb_dir"],
            "is_custom": bool(cfg.get("kb_dir")),
            "stats": get_dir_stats(kb_path),
            "label": "Knowledge Base Folder",
            "description": "Candidate profile truth, career work history, experience matrices, and tone guide"
        },
        "templates_dir": {
            "path": tmpl_path,
            "default_path": DEFAULT_PATHS["templates_dir"],
            "is_custom": bool(cfg.get("templates_dir")),
            "stats": get_dir_stats(tmpl_path),
            "label": "Resume & Cover Letter Templates",
            "description": "Master Word (.docx) and Markdown (.md) layout templates"
        },
        "output_dir": {
            "path": out_path,
            "default_path": DEFAULT_PATHS["output_dir"],
            "is_custom": bool(cfg.get("output_dir")),
            "stats": get_dir_stats(out_path),
            "label": "Active Tailored Outputs",
            "description": "Working tailored resume, cover letter, and compliance report drafts"
        },
        "apps_dir": {
            "path": apps_path,
            "default_path": DEFAULT_PATHS["apps_dir"],
            "is_custom": bool(cfg.get("apps_dir")),
            "stats": get_dir_stats(apps_path),
            "label": "Applications Archive Library",
            "description": "Permanent library of completed, archived application folders"
        },
        "has_custom_paths": bool(cfg)
    }

def update_storage_paths(new_paths):
    cfg = load_user_config()
    valid_keys = ["kb_dir", "templates_dir", "output_dir", "apps_dir"]
    
    for k in valid_keys:
        if k in new_paths:
            val = str(new_paths[k]).strip()
            if not val or val == DEFAULT_PATHS[k]:
                cfg.pop(k, None)
            else:
                abs_p = os.path.abspath(os.path.expanduser(val))
                os.makedirs(abs_p, exist_ok=True)
                test_file = os.path.join(abs_p, ".write_test")
                try:
                    with open(test_file, "w") as tf:
                        tf.write("ok")
                    os.remove(test_file)
                except Exception as e:
                    raise PermissionError(f"Directory '{abs_p}' is not writable: {str(e)}")
                cfg[k] = abs_p

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        
    return get_all_storage_paths()

def reset_storage_paths():
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
        except Exception:
            pass
    return get_all_storage_paths()

def initialize_starter_files(target_component):
    paths = get_all_storage_paths()
    if target_component == "kb":
        dest = paths["kb_dir"]["path"]
        os.makedirs(dest, exist_ok=True)
        src = os.path.join(BASE_DIR, "knowledge_base.example")
        copied = []
        if os.path.exists(src):
            for fn in os.listdir(src):
                sfile = os.path.join(src, fn)
                dname = fn.replace(".example", "")
                dfile = os.path.join(dest, dname)
                if not os.path.exists(dfile):
                    shutil.copy2(sfile, dfile)
                    copied.append(dname)
            return {"success": True, "copied": copied, "target_dir": dest}
    elif target_component == "template":
        dest = paths["templates_dir"]["path"]
        os.makedirs(dest, exist_ok=True)
        src = os.path.join(BASE_DIR, "template")
        copied = []
        if os.path.exists(src):
            for fn in os.listdir(src):
                sfile = os.path.join(src, fn)
                dfile = os.path.join(dest, fn)
                if not os.path.exists(dfile):
                    shutil.copy2(sfile, dfile)
                    copied.append(fn)
            return {"success": True, "copied": copied, "target_dir": dest}
    return {"success": False, "error": f"Unknown component '{target_component}'"}
