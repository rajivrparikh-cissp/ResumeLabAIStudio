import os
import sys
import shutil
import tempfile
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "app"))

from storage_config import (
    DEFAULT_PATHS,
    get_kb_dir,
    get_templates_dir,
    get_output_dir,
    get_apps_dir,
    get_all_storage_paths,
    update_storage_paths,
    reset_storage_paths,
    initialize_starter_files,
    CONFIG_FILE
)

class TestStorageConfig(unittest.TestCase):
    def setUp(self):
        # Backup user_storage_config.json if exists
        self.config_backup = None
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config_backup = f.read()
            os.remove(CONFIG_FILE)

    def tearDown(self):
        # Restore user_storage_config.json if it existed
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        if self.config_backup is not None:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(self.config_backup)

    def test_default_paths(self):
        reset_storage_paths()
        paths = get_all_storage_paths()
        self.assertFalse(paths["has_custom_paths"])
        self.assertIn("kb_dir", paths)
        self.assertIn("templates_dir", paths)
        self.assertIn("output_dir", paths)
        self.assertIn("apps_dir", paths)

    def test_custom_paths_update_and_reset(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            custom_kb = os.path.join(tmp_dir, "my_kb")
            custom_templates = os.path.join(tmp_dir, "my_templates")
            custom_output = os.path.join(tmp_dir, "my_output")
            custom_apps = os.path.join(tmp_dir, "my_apps")

            updated = update_storage_paths({
                "kb_dir": custom_kb,
                "templates_dir": custom_templates,
                "output_dir": custom_output,
                "apps_dir": custom_apps
            })

            self.assertTrue(updated["has_custom_paths"])
            self.assertEqual(get_kb_dir(), os.path.abspath(custom_kb))
            self.assertEqual(get_templates_dir(), os.path.abspath(custom_templates))
            self.assertEqual(get_output_dir(), os.path.abspath(custom_output))
            self.assertEqual(get_apps_dir(), os.path.abspath(custom_apps))

            # Test starter files initialization into custom directory
            res = initialize_starter_files("template")
            self.assertTrue(res["success"])
            self.assertTrue(len(os.listdir(custom_templates)) > 0)

            # Test reset
            resetted = reset_storage_paths()
            self.assertFalse(resetted["has_custom_paths"])
            self.assertEqual(get_templates_dir(), DEFAULT_PATHS["templates_dir"])
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
