import os
import tempfile
import unittest
import io
from contextlib import redirect_stdout
from unittest.mock import patch

from eb.eb import Editor, CommandError


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
        with patch.object(self.editor, "read_line", return_value="inserted"):
            self.editor.insert_line(2)
        self.assertEqual(self.editor.buffer[1], "inserted\n")

    def test_append_lines_after_selected_index(self):
        with patch.object(self.editor, "read_line", side_effect=["new1", "new2", "."]):
            self.editor.append_lines(2)
        self.assertEqual(self.editor.buffer[2], "new1\n")
        self.assertEqual(self.editor.buffer[3], "new2\n")

    def test_append_lines_splits_pasted_multiline_input(self):
        with patch.object(self.editor, "read_line", side_effect=["new1\nnew2", "."]):
            self.editor.append_lines(2)

        self.assertEqual(self.editor.buffer[2], "new1\n")
        self.assertEqual(self.editor.buffer[3], "new2\n")

    def test_delete_and_substitute(self):
        self.editor.delete_lines("2")
        self.assertEqual(self.editor.buffer, ["line1\n"])

        self.editor.substitute_lines("1/replaced")
        self.assertEqual(self.editor.buffer[0], "replaced\n")

    def test_delete_command_prompts_for_missing_line_number(self):
        with patch.object(self.editor, "read_line", return_value="2"):
            self.editor.execute_command("d")
        self.assertEqual(self.editor.buffer, ["line1\n"])

    def test_delete_command_accepts_inline_line_number(self):
        self.editor.execute_command("d2")
        self.assertEqual(self.editor.buffer, ["line1\n"])

    def test_delete_command_rejects_zero(self):
        with self.assertRaisesRegex(CommandError, "line number must be >= 1"):
            self.editor.execute_command("d0")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_delete_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("d3")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_substitute_command_prompts_for_missing_line_number(self):
        with patch.object(self.editor, "read_line", side_effect=["2", "changed"]):
            self.editor.execute_command("s")
        self.assertEqual(self.editor.buffer[1], "changed\n")

    def test_substitute_command_accepts_inline_line_number(self):
        self.editor.execute_command("s2/changed")
        self.assertEqual(self.editor.buffer[1], "changed\n")

    def test_insert_command_prompts_for_missing_line_number(self):
        with patch.object(self.editor, "read_line", side_effect=["2", "inserted"]):
            self.editor.execute_command("i")
        self.assertEqual(self.editor.buffer[1], "inserted\n")

    def test_insert_command_rejects_zero(self):
        with self.assertRaisesRegex(CommandError, "line number must be >= 1"):
            self.editor.execute_command("i0")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_insert_command_allows_insert_at_end(self):
        with patch.object(self.editor, "read_line", return_value="inserted"):
            self.editor.execute_command("i3")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n", "inserted\n"])

    def test_insert_command_rejects_above_end(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("i4")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_substitute_command_rejects_zero(self):
        with self.assertRaisesRegex(CommandError, "line number must be >= 1"):
            self.editor.execute_command("s0/changed")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_edit_command_accepts_inline_line_number_with_space(self):
        with patch.object(self.editor, "read_line", side_effect=AssertionError("read_line should not be called")):
            with patch.object(self.editor, "print_context") as mock_print_context:
                with patch.object(self.editor, "modify_line") as mock_modify_line:
                    self.editor.execute_command("e 1")

        mock_print_context.assert_called_once_with(0, 2)
        mock_modify_line.assert_called_once_with(1)

    def test_edit_command_accepts_inline_line_number_without_space(self):
        with patch.object(self.editor, "read_line", side_effect=AssertionError("read_line should not be called")):
            with patch.object(self.editor, "print_context") as mock_print_context:
                with patch.object(self.editor, "modify_line") as mock_modify_line:
                    self.editor.execute_command("e1")

        mock_print_context.assert_called_once_with(0, 2)
        mock_modify_line.assert_called_once_with(1)

    def test_edit_line_1_does_not_prompt_for_line_number(self):
        with patch.object(self.editor, "read_line", side_effect=AssertionError("read_line should not be called")):
            with patch("eb.eb.prompt", return_value="line1-edited"):
                self.editor.execute_command("e 1")

        self.assertEqual(self.editor.buffer[0], "line1-edited\n")

    def test_edit_can_be_cancelled(self):
        with patch("eb.eb.prompt", side_effect=KeyboardInterrupt):
            output = io.StringIO()
            with redirect_stdout(output):
                self.editor.execute_command("e1")

        self.assertIn("Edit cancelled", output.getvalue())
        self.assertEqual(self.editor.buffer[0], "line1\n")

    def test_substitute_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("s3/changed")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_context_command_accepts_inline_line_number(self):
        with patch.object(self.editor, "print_context") as mock_print_context:
            self.editor.execute_command("c2")
        mock_print_context.assert_called_once_with(1, 5)

    def test_context_command_prompts_for_missing_line_number(self):
        with patch.object(self.editor, "read_line", return_value="2"):
            with patch.object(self.editor, "print_context") as mock_print_context:
                self.editor.execute_command("c")
        mock_print_context.assert_called_once_with(1, 5)

    def test_context_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("c3")

    def test_comment_command_accepts_inline_line_number(self):
        self.editor.execute_command("k2")
        self.assertEqual(self.editor.buffer[1], "#line2\n")

    def test_comment_command_prompts_for_missing_line_number(self):
        with patch.object(self.editor, "read_line", return_value="2"):
            self.editor.execute_command("k")
        self.assertEqual(self.editor.buffer[1], "#line2\n")

    def test_comment_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("k3")

    def test_uncomment_command_accepts_inline_line_number(self):
        self.editor.buffer[1] = "#line2\n"
        self.editor.execute_command("u2")
        self.assertEqual(self.editor.buffer[1], "line2\n")

    def test_uncomment_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("u3")

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

    def test_add_bom_on_empty_buffer(self):
        self.editor.buffer = []
        self.editor.add_bom()
        self.assertEqual(self.editor.buffer, ["\ufeff"])

    def test_save_buffer_appends_trailing_newline(self):
        self.editor.buffer = ["hello"]
        self.editor.save_buffer()

        with open(self.file_path, "r") as f:
            content = f.read()
        self.assertEqual(content, "hello\n")

    def test_save_buffer_preserves_existing_final_newline(self):
        original_content = "line1\nline2\n"
        with open(self.file_path, "w") as f:
            f.write(original_content)

        editor = Editor(self.file_path)
        editor.save_buffer()

        with open(self.file_path, "r") as f:
            saved_content = f.read()

        self.assertEqual(saved_content, original_content)
        self.assertTrue(saved_content.endswith("\n"))

    def test_modify_line_then_save_keeps_final_newline(self):
        with patch("eb.eb.prompt", return_value="line2-edited"):
            self.editor.modify_line(2)

        self.editor.save_buffer()

        with open(self.file_path, "r") as f:
            saved_content = f.read()

        self.assertTrue(saved_content.endswith("\n"))
        self.assertEqual(saved_content, "line1\nline2-edited\n")

    def test_crlf_save_preserves_line_endings(self):
        crlf_file = os.path.join(self.temp_dir.name, "windows.txt")
        with open(crlf_file, "wb") as f:
            f.write(b"line1\r\nline2\r\n")

        editor = Editor(crlf_file)
        editor.save_buffer()

        with open(crlf_file, "rb") as f:
            content = f.read()

        self.assertEqual(content, b"line1\r\nline2\r\n")

    def test_crlf_modify_line_then_save_preserves_crlf(self):
        crlf_file = os.path.join(self.temp_dir.name, "windows-edit.txt")
        with open(crlf_file, "wb") as f:
            f.write(b"line1\r\nline2\r\n")

        editor = Editor(crlf_file)
        with patch("eb.eb.prompt", return_value="line2-edited\r"):
            editor.modify_line(2)
        editor.save_buffer()

        with open(crlf_file, "rb") as f:
            content = f.read()

        self.assertEqual(content, b"line1\r\nline2-edited\r\n")

    def test_crlf_split_preserves_line_endings(self):
        crlf_file = os.path.join(self.temp_dir.name, "windows-split.txt")
        split_file = os.path.join(self.temp_dir.name, "windows-split-out.txt")
        with open(crlf_file, "wb") as f:
            f.write(b"line1\r\nline2\r\nline3\r\n")

        editor = Editor(crlf_file)
        with patch.object(editor, "read_line", return_value=split_file):
            editor.split_from_line_to_new_file(2)

        with open(split_file, "rb") as f:
            split_content = f.read()

        self.assertEqual(split_content, b"line2\r\nline3\r\n")

    def test_cr_only_save_does_not_append_extra_line_ending(self):
        cr_file = os.path.join(self.temp_dir.name, "mac-classic.txt")
        with open(cr_file, "wb") as f:
            f.write(b"line1\rline2\r")

        editor = Editor(cr_file)
        editor.save_buffer()

        with open(cr_file, "rb") as f:
            content = f.read()

        self.assertEqual(content, b"line1\rline2\r")

    def test_newline_command_converts_to_crlf(self):
        self.editor.buffer = ["line1\n", "line2\n"]
        self.editor.execute_command("ncrlf")
        self.assertEqual(self.editor.buffer, ["line1\r\n", "line2\r\n"])

    def test_newline_command_converts_to_cr(self):
        self.editor.buffer = ["line1\n", "line2\n"]
        self.editor.execute_command("ncr")
        self.assertEqual(self.editor.buffer, ["line1\r", "line2\r"])

    def test_newline_command_prompts_for_style(self):
        self.editor.buffer = ["line1\r\n", "line2\r\n"]
        with patch.object(self.editor, "read_line", return_value="lf"):
            self.editor.execute_command("n")
        self.assertEqual(self.editor.buffer, ["line1\n", "line2\n"])

    def test_newline_command_keeps_non_terminated_line(self):
        self.editor.buffer = ["line1\n", "line2"]
        self.editor.execute_command("ncrlf")
        self.assertEqual(self.editor.buffer, ["line1\r\n", "line2"])

    def test_split_from_line_to_new_file(self):
        self.editor.buffer = ["line1\n", "line2\n", "line3\n"]
        new_file = os.path.join(self.temp_dir.name, "split.txt")
        with patch.object(self.editor, "read_line", return_value=new_file):
            self.editor.split_from_line_to_new_file(2)

        with open(new_file, "r") as f:
            split_content = f.read()

        self.assertEqual(self.editor.buffer, ["line1\n"])
        self.assertEqual(split_content, "line2\nline3\n")

    def test_split_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("S3")

    def test_append_command_rejects_out_of_range(self):
        with self.assertRaisesRegex(CommandError, "out of range"):
            self.editor.execute_command("a3")


if __name__ == "__main__":
    unittest.main()
