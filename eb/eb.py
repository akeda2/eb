#!/usr/bin/env python3
import sys
import os
from prompt_toolkit import prompt
#from prompt_toolkit.key_binding import KeyBindings
#from curses import wrapper


class CommandError(Exception):
    """Raised when a user command cannot be parsed or executed."""


class Editor:
    def __init__(self, filename=None):
        self.buffer = []
        self.filename = filename
        if self.filename is not None and os.path.isfile(self.filename):
            with open(self.filename, newline='') as f:
                self.buffer = f.readlines()
        else:
            newfile = input("File not found! Create new file? [y/n]: ") or 'n'
            if newfile == 'y':
                if self.filename is not None:
                    self.filename = input("Enter filename (" + self.filename + "): ") or self.filename
                else:
                    self.filename = input("Enter filename: ")
                with open(self.filename, 'w', newline='') as f:
                    pass
            else:
                sys.exit()

    def read_line(self, message=''):
        return prompt(message)

    def _default_line_ending(self):
        for line in self.buffer:
            if line.endswith('\r\n'):
                return '\r\n'
            if line.endswith('\n'):
                return '\n'
            if line.endswith('\r'):
                return '\r'
        return '\n'

    def _ensure_line_ending(self, value, line_ending=None):
        if line_ending is not None:
            return value.rstrip('\r\n') + line_ending

        if value.endswith('\r\n') or value.endswith('\n') or value.endswith('\r'):
            return value
        return value + self._default_line_ending()

    def print_help(self):
        print('Available commands:')
        print('p  - print the buffer with line numbers')
        print('pr - print the buffer with line endings visible (raw)')
        print('ph - print the buffer like pr but with hex values')
        print('pl - print the buffer without line numbers')
        print('m  - print the buffer one page at the time (more-style)')
        print('c  - print near Context of a line number')
        print('t  - print the last n lines of the buffer (tail-style)\n')

        print('a  - append one or more lines to the buffer')
        print('i  - insert a line into the buffer')
        print('d  - delete a line from the buffer')
        print('s  - substitute a line in the buffer')
        print('e  - edit a line in the buffer')
        print('k  - comment out a line in the buffer')
        print('u  - Uncomment a line in the buffer\n')
        print('nlf   - convert all line endings in buffer to LF')
        print('ncr   - convert all line endings in buffer to CR')
        print('ncrlf - convert all line endings in buffer to CRLF')
        print('n     - choose line ending interactively (lf/cr/crlf)\n')
        
        print('b  - add Unicode BOM to the beginning of the file')
        print('B  - remove unicode BOM from the beginning of the file')
        print('S  - Split from line number to end of file into a new file')
        print('h  - print this Help message\n')

        print('w  - Write/Save buffer to file')
        print('q  - Quit the editor without saving changes')
        print('qq - force Quit without saving changes')
        print('x  - eXit the editor saving changes to file')
    
    def run(self):
        print("eb - a primitive line-ebitor. 'h' is help, 'q' is quit. Python version: {0}.{1}.{2}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        #print(f"eb - a primitive line-ebitor. 'h' is help, 'q' is quit. Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        self.old_version = True if sys.version_info.major == 3 and sys.version_info.minor < 6 or sys.version_info.major > 3 else False
        #self.old_version = True
        while True:
            command = input('?')
            try:
                should_exit = self.execute_command(command)
                if should_exit:
                    break
            except (CommandError, ValueError, IndexError) as err:
                print("FAIL! {0}".format(err))
            except OSError as err:
                print("FAIL! I/O error: {0}".format(err))

    def execute_command(self, command):
        if command in ('x', 'w'):
            self.save_buffer()
            return command == 'x'

        simple_dispatch = {
            'b': self.add_bom,
            'B': self.remove_bom,
            'h': self.print_help,
            'm': self.print_more,
            'qq': self._quit_now,
            'q': self._confirm_quit,
        }
        if command in simple_dispatch:
            return simple_dispatch[command]()

        if not command:
            raise CommandError('Empty command')

        prefix_dispatch = {
            'S': self._command_split,
            'p': self._command_print,
            'a': self._command_append,
            'd': self._command_delete,
            's': self._command_substitute,
            'e': self._command_edit,
            'k': self._command_comment,
            'u': self._command_uncomment,
            'i': self._command_insert,
            't': self._command_tail,
            'c': self._command_context,
            'n': self._command_newline,
        }
        handler = prefix_dispatch.get(command[0])
        if handler is None:
            print('Unknown command')
            return False

        handler(command)
        return False

    def _quit_now(self):
        return True

    def _confirm_quit(self):
        quit_not_save = self.read_line("Really quit without saving? (x in main menu eXits and saves) y/n: ") or 'n'
        return quit_not_save == 'y'

    def _command_split(self, command):
        line_text = command[1:].strip()
        line_number = self._parse_optional_line_number(line_text)
        self.split_from_line_to_new_file(line_number)

    def _command_print(self, command):
        arg = command[1:]
        if arg != '' and str.isdigit(arg.strip()):
            self.print_from(int(arg))
        elif command.endswith('r'):
            self.print_buffer(raw=True)
        elif command.endswith('h'):
            self.print_buffer(hex=True)
        elif command.endswith('l'):
            self.print_buffer(lineNumbers=False)
        else:
            self.print_buffer()

    def _command_append(self, command):
        arg = command[1:]
        self.append_lines(int(arg)) if arg != '' else self.append_lines('x')

    def _command_delete(self, command):
        arg = command[1:].strip()
        line_number = self._parse_optional_line_number(arg)
        self.delete_lines(str(line_number))

    def _command_substitute(self, command):
        arg = command[1:].strip()
        if '/' in arg:
            line_text, text = arg.split('/', 1)
            line_number = self._parse_optional_line_number(line_text.strip())
            self.substitute_lines("{0}/{1}".format(line_number, text))
            return

        line_number = self._parse_optional_line_number(arg)
        text = self.read_line('Replacement text: ')
        self.substitute_lines("{0}/{1}".format(line_number, text))

    def _command_edit(self, command):
        arg = command[1:].strip()
        selected_line_number = self._parse_optional_line_number(arg)
        self.print_context(selected_line_number - 1, 2)
        self.modify_line(selected_line_number)

    def _parse_optional_line_number(self, line_text):
        if line_text:
            return int(line_text)
        return int(self.read_line("Line number: "))

    def _parse_comment_command(self, command):
        payload = command[1:].strip()
        if not payload:
            line_num = int(self.read_line("Line number: "))
            return line_num - 1, '#'

        parts = payload.split(maxsplit=1)
        line_num = int(parts[0])
        comment_char = parts[1] if len(parts) > 1 and parts[1] else '#'
        return line_num - 1, comment_char

    def _command_comment(self, command):
        line_num, comment_char = self._parse_comment_command(command)
        self.comment_line(line_num, comment_char)

    def _command_uncomment(self, command):
        line_num, comment_char = self._parse_comment_command(command)
        self.uncomment_line(line_num, comment_char)

    def _command_insert(self, command):
        arg = command[1:].strip()
        line_number = self._parse_optional_line_number(arg)
        self.insert_line(line_number)

    def _command_tail(self, command):
        arg = command[1:]
        self.print_tail(int(arg)) if arg != '' else self.print_tail()

    def _command_context(self, command):
        payload = command[1:].strip()
        if not payload:
            line_num = self._parse_optional_line_number('')
            context_num = 5
        else:
            parts = payload.split(maxsplit=1)
            line_num = self._parse_optional_line_number(parts[0])
            context_num = int(parts[1]) if len(parts) > 1 and parts[1] else 5
        self.print_context(line_num - 1, context_num)

    def _command_newline(self, command):
        style = command[1:].strip().lower()
        if not style:
            style = self.read_line('Line ending (lf/cr/crlf): ').strip().lower()

        line_endings = {
            'lf': '\n',
            'cr': '\r',
            'crlf': '\r\n',
        }
        selected = line_endings.get(style)
        if selected is None:
            raise CommandError("Invalid line ending. Use one of: lf, cr, crlf")

        self.convert_line_endings(selected)
        print("Line endings converted to {0}".format(style.upper()))

    def convert_line_endings(self, target_line_ending):
        updated = []
        for line in self.buffer:
            if line.endswith('\r\n') or line.endswith('\n') or line.endswith('\r'):
                updated.append(line.rstrip('\r\n') + target_line_ending)
            else:
                updated.append(line)
        self.buffer = updated
    
    def print_with_hex_and_letter(self, buffer):
        for line in buffer:
            visible_line = line.replace('\n', '\\n').replace('\r', '\\r')
            print(visible_line)

            hex_lines, char_lines = self.format_hex_with_letter(line)
            for hex_line, char_line in zip(hex_lines, char_lines):
                print(char_line)
                print(hex_line)
            print()  # Optional: Separate blocks with an empty line

    def format_hex_with_letter(self,data, bytes_per_line=16):
        hex_lines = []
        char_lines = []
        while data:
            chunk = data[:bytes_per_line]
            data = data[bytes_per_line:]

            hex_chunk = ' '.join(['{:02x}'.format(b) for b in chunk.encode()])
            hex_lines.append(hex_chunk)

            # Convert to a printable string, replacing non-printable chars with '.'
            char_chunk = ''
            for b in chunk.encode():
                char = chr(b)
                if char == '\n':
                    char_chunk += '\\n'.ljust(3)
                elif char == '\r':
                    char_chunk += '\\r'.ljust(3)
                elif char == '\t':
                    char_chunk += '\\t'.ljust(3)
                #elif 32 <= b < 127:
                #    char_chunk += char.ljust(3)
                elif 32 <= b < 127 or 128 <= b <= 255:  # Printable characters in standard and extended ASCII range
                    char_chunk += chr(b).ljust(3)
                else:
                    char_chunk += ' . '.ljust(3)

            """ # Convert to a printable string, replacing non-printable chars with '.'
            char_chunk = ''.join([' ' + (chr(b) if 32 <= b < 127 else '.') + ' ' for b in chunk.encode()])"""
            char_lines.append(char_chunk.rstrip())

        return hex_lines, char_lines

    def print_with_hex(self,buffer):
        for line in buffer:#.splitlines(True):  # True keeps line endings
            visible_line = line.replace('\n', '\\n').replace('\r', '\\r')
            print(visible_line)

            hex_lines = self.format_hex(line)
            for hex_line in hex_lines:
                print(hex_line)
            print()  # Optional: Separate blocks with an empty line

    def format_hex(self,data, bytes_per_line=16):
        hex_lines = []
        while data:
            chunk = data[:bytes_per_line]
            data = data[bytes_per_line:]

            # Convert to hex, with spaces in between for each byte
            hex_chunk = ' '.join(['{:02x}'.format(b) for b in chunk.encode('latin-1')])
            hex_lines.append(hex_chunk)

        return hex_lines
    def print_from(self,n=10):
        start = n #max(0, len(self.buffer) - n)
        for i in range(start, len(self.buffer)):
            #if self.old_version:
            print('{i:3d}  {buffer}'.format(i=i+1, buffer=self.buffer[i]).rstrip())

    def print_buffer(self, raw=False, hex=False, lineNumbers=True):
        if hex:
            self.print_with_hex_and_letter(self.buffer)
        elif raw:
            for i, line in enumerate(self.buffer, start=1):
                print('{i:3d}  {line}'.format(i=i, line=line.replace('\n', '\\n').replace('\r', '\\r')))
        elif not lineNumbers:
            for i, line in enumerate(self.buffer, start=1):
                print('{line}'.format(line=line.rstrip()))
        else:
            for i, line in enumerate(self.buffer, start=1):
                print('{i:3d}  {line}'.format(i=i, line=line.rstrip()))
    
            if self.buffer and self.buffer[-1].endswith('\n') and not self.buffer.__len__() > i-1:
                print('{:3d}'.format(i+1))

    def append_lines(self,arg):
        if len(self.buffer) == 0:
            index = 0
        else:
            print(int(len(self.buffer)))
            if arg == 'x' or arg == '':
                index_in = self.read_line('Insert after line: (last) ')
                if index_in.strip():
                    index = int(index_in)
                else:
                    index = len(self.buffer)
            else:
                index = arg
        print('Enter lines to append. End with a line containing a single dot.')
        new_lines = []
        while True:
            line = self.read_line()
            if line == '.':
                break
            line = self._ensure_line_ending(line)
            new_lines.append(line)
        self.buffer[index:index] = new_lines

    def delete_lines(self, arg):
        if arg == '':
            self.buffer.pop()
        else:
            try:
                index = int(arg)
                if index <= self.buffer.__len__():
                    del self.buffer[index - 1]
                else:
                    print('Index out of range')
            except ValueError:
                print('Invalid argument')

    def substitute_lines(self, arg):
        try:
            index, text = arg.split('/')
            index = int(index)
            text = self._ensure_line_ending(text)
            self.buffer[index - 1] = text
        except ValueError:
            print('Invalid argument')

    def insert_line(self, arg):
        if arg == '' or arg == 0:
            index = int(self.read_line('Line number: '))
        else:
            index = int(arg)
        line = self.read_line('New line: ')
        line = self._ensure_line_ending(line)
        self.buffer.insert(index - 1, line)

    def add_bom(self):
        if not self.buffer[0].startswith('\ufeff'):
            if self.buffer:
                self.buffer[0] = '\ufeff' + self.buffer[0]
                print("BOM added")
            else:
                self.buffer.append('\ufeff')
        else:
            print("BOM already present")
    def remove_bom(self):
        if self.buffer and self.buffer[0].startswith('\ufeff'):
            self.buffer[0] = self.buffer[0][1:]
            print("BOM removed")
        else:
            print("No BOM present")
    def printRawWithLineEndings(self, rawbuffer):
        # Print all lines in the buffer with the line endings visible as \n and \r
        for i, line in enumerate(rawbuffer, start=1):
            print('{i:3d}  {line}'.format(i=i, line=line.replace('\n', '\\n').replace('\r', '\\r')))
    def print_more(self):
        page_size = 20
        start = 0
        end = page_size
        while True:
            for i in range(start, end):
                if i < len(self.buffer):
                    print('{i:3d}  {buffer}'.format(i=i +1, buffer=self.buffer[i]).rstrip())
                else:
                    break
            if end >= len(self.buffer):
                break
            prompt_text = 'More ({end}-{page_size})?'.format(end=end+1, page_size=min(end + page_size, len(self.buffer)))
            command = self.read_line(prompt_text)
            if command == 'q':
                break
            start = end
            end = start + page_size

    def print_tail(self,n=10):
        start = max(0, len(self.buffer) - n)
        for i in range(start, len(self.buffer)):
            print('{i:3d}  {buffer}'.format(i=i+1, buffer=self.buffer[i]).rstrip())

    def print_context(self,line_num,plusminus=5):
        if line_num == 0 or line_num == '':
            line_num = int(self.read_line("Line number: "))
        start = max(0, line_num - plusminus)
        end = min(len(self.buffer), line_num + plusminus)
        for i in range(start, end):
            print('{i:3d}  {buffer}'.format(i=i+1, buffer=self.buffer[i]).rstrip())

    def print_line(self, line_num):
        print('{line_num:3d}  {buffer}'.format(line_num=line_num, buffer=self.buffer[line_num - 1]))

    def modify_line(self, line_num):
        line_num -= 1
        original_line = self.buffer[line_num]
        if original_line.endswith('\r\n'):
            line_ending = '\r\n'
        elif original_line.endswith('\n'):
            line_ending = '\n'
        elif original_line.endswith('\r'):
            line_ending = '\r'
        else:
            line_ending = self._default_line_ending()

        stringtoedit = original_line.rstrip('\r\n')
        new_line = prompt(f"orig:{stringtoedit}\nnew :", default=stringtoedit)
        self.buffer[line_num] = self._ensure_line_ending(new_line, line_ending)

    def comment_line(self, line_num, comment_char='#'):
        self.buffer[line_num] = comment_char + self.buffer[line_num]
    def uncomment_line(self, line_num, comment_char='#'):
        if self.buffer[line_num].startswith(comment_char):
            self.buffer[line_num] = self.buffer[line_num][1:]
    def split_from_line_to_new_file(self, line_num):
        line_num -= 1
        new_filename = self.read_line("Enter new filename: ")
        new_buffer = self.buffer[line_num:]
        self.buffer = self.buffer[:line_num]
        if os.path.isfile(new_filename):
            overwrite = self.read_line("File already exists! Overwrite? (y/N): ") or 'n'
        else:
            overwrite = 'y'
        if overwrite.lower() == 'y':
            try:
                with open(new_filename, 'w', newline='') as f:
                    f.write(''.join(new_buffer))
                print("File saved (original file truncated, but not saved yet)")
            except OSError as err:
                print("Could not save! {0}".format(err))
        else:
            print("File not saved!")

    def save_buffer(self):
        if self.filename is None:
            self.filename = self.read_line('Enter filename to save buffer: ')
        try:
            with open(self.filename, 'w', newline='') as f:
                content = ''.join(self.buffer)
                if self.buffer and not self.buffer[-1].endswith('\n'):
                    print("Appending newline")
                    content += self._default_line_ending()
                f.write(content)
            print("File saved")
        except OSError as err:
            print("Could not save! {0}".format(err))

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        editor = Editor(filename) #if os.path.exists(filename) else Editor()
    else:
        editor = Editor()
    editor.run()
if __name__ == '__main__':
    main()