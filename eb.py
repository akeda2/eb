#!/usr/bin/python3
import sys

class Editor:
    def __init__(self, filename=None):
        self.buffer = []
        self.filename = filename
        if self.filename is not None:
            with open(self.filename) as f:
                self.buffer = f.read().splitlines()

    def run(self):
        print("Welcome to the ed-like line editor! Enter commands or 'q' to quit.")
        while True:
            command = input('?')
            if command == 'q':
                try:
                    self.save_buffer()
                    break
                except:
                    print("Save failed!")
            elif command == 'p':
                self.print_buffer()
            elif command.startswith('a'):
                self.append_lines()
            elif command.startswith('d'):
                self.delete_lines(command[1:])
            elif command.startswith('s'):
                self.substitute_lines(command[1:])
            elif command.startswith('i'):
                self.insert_line()
            elif command == 'h':
                self.print_help()
            elif command == 'x':
                quit_not_save = input("Really quit without saving? ") or 'n'
                if quit_not_save == 'y':
                    break
            else:
                print('Unknown command')

    def print_buffer(self):
        for i, line in enumerate(self.buffer, start=1):
            print(f"{i:3d}  {line}")

    def append_lines(self):
        if len(self.buffer) == 0:
            index = 0
        else:
            index = int(input('Insert after line: '))
        print('Enter lines to append. End with a line containing a single dot.')
        new_lines = []
        while True:
            line = input()
            if line == '.':
                break
            new_lines.append(line)
        self.buffer[index:index] = new_lines

    def delete_lines(self, arg):
        if arg == '':
            self.buffer.pop()
        else:
            try:
                index = int(arg)
                del self.buffer[index - 1]
            except ValueError:
                print('Invalid argument')

    def substitute_lines(self, arg):
        try:
            index, text = arg.split('/')
            index = int(index)
            self.buffer[index - 1] = text
        except ValueError:
            print('Invalid argument')

    def insert_line(self):
        index = int(input('Line number: '))
        line = input('New line: ')
        self.buffer.insert(index - 1, line)

    def print_help(self):
        print('Available commands:')
        print('p - print the buffer with line numbers')
        print('a - append one or more lines to the buffer')
        print('d - delete a line from the buffer')
        print('s - substitute a line in the buffer')
        print('i - insert a line into the buffer')
        print('h - print this help message')
        print('q - quit the editor and save changes to file')
        print('x - eXit the editor without saving changes')

    def save_buffer(self):
        if self.filename is None:
            self.filename = input('Enter filename to save buffer: ')
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.buffer))
            print("File saved")
        except:
            print("Could not save!")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        editor = Editor(filename)
    else:
        editor = Editor()
    editor.run()
