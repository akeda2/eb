import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from prompt_toolkit.history import InMemoryHistory

from eb.eb import Editor


class CliSmokeTests(unittest.TestCase):
    def test_run_quit_without_save(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "sample.txt")
            with open(file_path, "w") as f:
                f.write("line1\n")

            editor = Editor(file_path)
            with patch.object(editor, "read_command", side_effect=["p", "q"]):
                with patch.object(editor, "read_line", return_value="y"):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        editor.run()

            stdout = output.getvalue()
            self.assertIn("line1", stdout)
            self.assertIn("primitive line-ebitor", stdout)

    def test_read_command_uses_in_memory_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "sample.txt")
            with open(file_path, "w") as f:
                f.write("line1\n")

            editor = Editor(file_path)
            self.assertIsInstance(editor.command_history, InMemoryHistory)

            with patch("eb.eb.prompt", return_value="p") as mock_prompt:
                command = editor.read_command("?")

            self.assertEqual(command, "p")
            self.assertEqual(mock_prompt.call_args.kwargs["history"], editor.command_history)


if __name__ == "__main__":
    unittest.main()
