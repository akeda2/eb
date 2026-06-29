import os
import tempfile
import unittest
from unittest.mock import patch

from eb.eb import Editor


class EditorBufferTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "sample.txt")
        with open(self.file_path, "w") as f:
            f.write("line1\nline2\n")
        self.editor = Editor(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_insert_line(self):
        with patch("builtins.input", return_value="inserted"):
            self.editor.insert_line(2)
        self.assertEqual(self.editor.buffer[1], "inserted\n")

    def test_append_lines_after_selected_index(self):
        with patch("builtins.input", side_effect=["new1", "new2", "."]):
            self.editor.append_lines(2)
        self.assertEqual(self.editor.buffer[2], "new1\n")
        self.assertEqual(self.editor.buffer[3], "new2\n")

    def test_delete_and_substitute(self):
        self.editor.delete_lines("2")
        self.assertEqual(self.editor.buffer, ["line1\n"])

        self.editor.substitute_lines("1/replaced")
        self.assertEqual(self.editor.buffer[0], "replaced\n")

    def test_comment_and_uncomment(self):
        self.editor.comment_line(0, "#")
        self.assertEqual(self.editor.buffer[0], "#line1\n")

        self.editor.uncomment_line(0, "#")
        self.assertEqual(self.editor.buffer[0], "line1\n")

    def test_bom_add_remove(self):
        self.editor.add_bom()
        self.assertTrue(self.editor.buffer[0].startswith("\ufeff"))

        self.editor.remove_bom()
        self.assertFalse(self.editor.buffer[0].startswith("\ufeff"))

    def test_save_buffer_appends_trailing_newline(self):
        self.editor.buffer = ["hello"]
        self.editor.save_buffer()

        with open(self.file_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "hello\n")

    def test_split_from_line_to_new_file(self):
        new_file = os.path.join(self.temp_dir.name, "split.txt")
        with patch("builtins.input", return_value=new_file):
            self.editor.split_from_line_to_new_file(2)

        with open(new_file, "r") as f:
            split_content = f.read()

        self.assertEqual(self.editor.buffer, ["line1\n"])
        self.assertEqual(split_content, "line2\n")


if __name__ == "__main__":
    unittest.main()
