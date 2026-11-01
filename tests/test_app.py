import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_navigation_and_missing_key(self):
        app = AppTest.from_file("../app.py", default_timeout=15).run()
        self.assertFalse(app.exception)
        for tool in ("Resume Roaster", "Video to Blog", "Regex Generator"):
            app.radio[0].set_value(tool).run()
            self.assertFalse(app.exception)
            app.button[0].click().run()
            self.assertIn("API key", app.error[0].value)

    def test_theme_switch_persists_when_navigating(self):
        app = AppTest.from_file("../app.py", default_timeout=15).run()
        self.assertFalse(app.toggle[0].value)
        app.toggle[0].set_value(True).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("#101827" in item.value for item in app.markdown))
        app.radio[0].set_value("Regex Generator").run()
        self.assertTrue(app.toggle[0].value)
        self.assertTrue(any("#101827" in item.value for item in app.markdown))
        app.toggle[0].set_value(False).run()
        self.assertFalse(any("#101827" in item.value for item in app.markdown))

    def test_regex_generation_and_download(self):
        with patch("toolkit.llm.generate", return_value="## Pattern\n```\n\\d+\n```") as generate:
            app = AppTest.from_file("../app.py", default_timeout=15).run()
            app.radio[0].set_value("Regex Generator").run()
            app.text_input[0].set_value("sk-test")
            app.text_area[0].set_value("Match digits")
            app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            self.assertTrue(any("Pattern" in item.value for item in app.markdown))
            generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
