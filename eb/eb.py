#!/usr/bin/env python3
import sys
import os
from prompt_toolkit import prompt
#from prompt_toolkit.key_binding import KeyBindings
#from curses import wrapper


class Editor:
    def __init__(self, filename=None):
        self.buffer = []
        self.filename = filename
        if self.filename is not None and os.path.isfile(self.filename):
            with open(self.filename) as f:
                self.buffer = f.readlines()
        else:
            newfile = input("File not found! Create new file? [y/n]: ") or 'n'
            if newfile == 'y':
                if self.filename is not None:
                    self.filename = input("Enter filename (" + self.filename + "): ") or self.filename
                else:
                    self.filename = input("Enter filename: ")
                with open(self.filename, 'w') as f:
                    pass
            else:
                sys.exit()
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
                if command == 'x' or command == 'w':
                    try:
                        self.save_buffer()
                        if command == 'x':
                            break
                    except:
                        print("Save failed!")
                elif command.startswith('S'):
                    self.split_from_line_to_new_file(int(command[1:])) if command[1:] != '' else self.split_from_line_to_new_file(int(input("Line number: ")))
                elif command == 'b':
                    self.add_bom()
                elif command == 'B':
                    self.remove_bom()
                elif command.startswith('p'):
                    #print(command[1:]) 
                    if command[1:] != '' and str.isdigit(command[1:].strip()):
                        # Use tail instead:
                        self.print_from(int(command[1:]))
                    elif command.endswith('r'):
                        self.print_buffer(raw=True)
                    elif command.endswith('h'):
                        self.print_buffer(hex=True)
                    elif command.endswith('l'):
                        self.print_buffer(lineNumbers=False)
                    else:
                        self.print_buffer()
                elif command.startswith('a'):
                    self.append_lines(int(command[1:])) if command[1:] != '' else self.append_lines('x')
                elif command.startswith('d'):
                    self.delete_lines(command[1:])
                elif command.startswith('s'):
                    self.substitute_lines(command[1:])
                elif command.startswith('e'):
                    selected_line_number = int(command[1:]) if command[1:] != '' else input("Line number: ")
                    self.print_context(int(selected_line_number)-1, int(2))
                    self.modify_line(int(command[1:])) if command[1:] != '' else self.modify_line(int(selected_line_number))
                elif command.startswith('k'):
                    line_num, _, comment_char = command.partition(' ')[2].partition(' ')
                    if not comment_char:
                        comment_char = '#'  # Set a default comment character if none is provided
                    if not line_num:
                        line_num = input("Line number: ")
                    self.comment_line(int(line_num)-1, comment_char)
                    #self.comment_line(int(command[1:]) if command[1:] != '' else int(input("Line number: ")), command[2:] if command[2:] != '' else '#')
                elif command.startswith('u'):
                    line_num, _, comment_char = command.partition(' ')[2].partition(' ')
                    if not comment_char:
                        comment_char = '#'  # Set a default comment character if none is provided
                    if not line_num:
                        line_num = input("Line number: ")
                    self.uncomment_line(int(line_num)-1, comment_char)
                elif command.startswith('i'):
                    self.insert_line(int(command[1:])) if command[1:] != '' else self.insert_line(0)
                elif command.startswith('m'):
                    self.print_more()
                elif command.startswith('t'):
                    self.print_tail(int(command[1:])) if command[1:] != '' else self.print_tail()
                elif command.startswith('c'):
                    line_num, _, context_num = command.partition(' ')[2].partition(' ')
                    if not context_num:
                        context_num = 5  # Set a default context number if none is provided
                    if not line_num:
                        line_num = input("Line number: ")
                    self.print_context(int(line_num)-1, int(context_num))
                    #self.print_context(int(command[1:])) if command[1:] != '' else self.print_context(0)
                elif command == 'h':
                    self.print_help()
                elif command == 'qq':
                    break
                elif command == 'q':
                    quit_not_save = input("Really quit without saving? (x in main menu eXits and saves) y/n: ") or 'n'
                    if quit_not_save == 'y':
                        break
                else:
                    print('Unknown command')
            except:
                print("FAIL!")
                #pass
                raise
    
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
                index_in = input('Insert after line: (last) ')
                if index_in.strip():
                    index = int(index_in)
                else:
                    index = len(self.buffer)
            else:
                index = arg
        print('Enter lines to append. End with a line containing a single dot.')
        new_lines = []
        while True:
            line = input()
            if line == '.':
                break
            if not line.endswith('\n'):
                line += '\n'
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
            if not text.endswith('\n'):
                text += '\n'
            self.buffer[index - 1] = text
        except ValueError:
            print('Invalid argument')

    def insert_line(self, arg):
        if arg == '' or arg == 0:
            index = int(input('Line number: '))
        else:
            index = int(arg)
        line = input('New line: ')
        if not line.endswith('\n'):
                line += '\n'
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
            prompt = 'More ({end}-{page_size})?'.format(end=end+1, page_size=min(end + page_size, len(self.buffer)))
            command = input(prompt)
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
            line_num = int(input("Line number: "))
        start = max(0, line_num - plusminus)
        end = min(len(self.buffer), line_num + plusminus)
        for i in range(start, end):
            print('{i:3d}  {buffer}'.format(i=i+1, buffer=self.buffer[i]).rstrip())

    def print_line(self, line_num):
        print('{line_num:3d}  {buffer}'.format(line_num=line_num, buffer=self.buffer[line_num - 1]))

    def modify_line(self, line_num):
        line_num -= 1
        stringtoedit = self.buffer[line_num].strip('\n')
        new_line = prompt(f"orig:{stringtoedit}\nnew :", default=stringtoedit)
        if not new_line.endswith('\n'):
                new_line += '\n'
        self.buffer[line_num] = new_line

    def comment_line(self, line_num, comment_char='#'):
        self.buffer[line_num] = comment_char + self.buffer[line_num]
    def uncomment_line(self, line_num, comment_char='#'):
        if self.buffer[line_num].startswith(comment_char):
            self.buffer[line_num] = self.buffer[line_num][1:]
    def split_from_line_to_new_file(self, line_num):
        line_num -= 1
        new_filename = input("Enter new filename: ")
        new_buffer = self.buffer[line_num:]
        self.buffer = self.buffer[:line_num]
        if os.path.isfile(new_filename):
            overwrite = input("File already exists! Overwrite? (y/N): ") or 'n'
        else:
            overwrite = 'y'
        if overwrite.lower() == 'y':
            try:
                with open(new_filename, 'w') as f:
                    f.write('\n'.join(new_buffer))
                print("File saved (original file truncated, but not saved yet)")
            except:
                print("Could not save!")
        else:
            print("File not saved!")

    def save_buffer(self):
        if self.filename is None:
            self.filename = input('Enter filename to save buffer: ')
        try:
            with open(self.filename, 'w') as f:
                content = ''.join(self.buffer)
                if self.buffer and not self.buffer[-1].endswith('\n'):
                    print("Appending newline")
                    content += '\n'
                f.write(content)
            print("File saved")
        except:
            print("Could not save!")

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        editor = Editor(filename) #if os.path.exists(filename) else Editor()
    else:
        editor = Editor()
    editor.run()
if __name__ == '__main__':
    main()