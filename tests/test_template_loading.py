import json
import tempfile
import unittest
from pathlib import Path

import app as app_module


class TemplateLoadingTests(unittest.TestCase):
    def test_load_templates_reads_saved_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            template_file = Path(tmpdir) / "templates.json"
            template_file.write_text(
                json.dumps({"custom_template": {"label": "Custom", "body": "Hello"}}),
                encoding="utf-8",
            )

            original_path = app_module.TEMPLATE_FILE
            app_module.TEMPLATE_FILE = template_file
            try:
                templates = app_module.load_templates()
            finally:
                app_module.TEMPLATE_FILE = original_path

            self.assertEqual(templates["custom_template"]["body"], "Hello")
            self.assertEqual(templates["custom_template"]["label"], "Custom")


if __name__ == "__main__":
    unittest.main()
