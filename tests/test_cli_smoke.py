import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from eb.eb import Editor


class CliSmokeTests(unittest.TestCase):
    def test_run_quit_without_save(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "sample.txt")
            with open(file_path, "w") as f:
                f.write("line1\n")

            editor = Editor(file_path)
            with patch("builtins.input", side_effect=["p", "q"]):
                with patch.object(editor, "read_line", return_value="y"):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        editor.run()

            stdout = output.getvalue()
            self.assertIn("line1", stdout)
            self.assertIn("primitive line-ebitor", stdout)


if __name__ == "__main__":
    unittest.main()
