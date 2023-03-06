#!/usr/bin/env python3
import sys
#import re

class Editor:
    def __init__(self, filename=None):
        self.buffer = []
        self.filename = filename
        if self.filename is not None:
            with open(self.filename) as f:
                self.buffer = f.read().splitlines()

    def run(self):
        print("eb - a primitive line-ebitor. Enter commands or 'q' to quit.")
        while True:
            command = input('?')
            try:
                if command == 'x':
                    try:
                        self.save_buffer()
                        break
                    except:
                        print("Save failed!")
                elif command == 'p':
                    self.print_buffer()
                elif command.startswith('a'):
                    self.append_lines(int(command[1:])) if command[1:] != '' else self.append_lines('x')
                elif command.startswith('d'):
                    self.delete_lines(command[1:])
                elif command.startswith('s'):
                    self.substitute_lines(command[1:])
                elif command.startswith('i'):
                    self.insert_line(int(command[1:])) if command[1:] != '' else self.insert_line(0)
                elif command.startswith('m'):
                    self.print_more()
                elif command.startswith('t'):
                    self.print_tail(int(command[1:])) if command[1:] != '' else self.print_tail()
                elif command.startswith('c'):
                    self.print_context(int(command[1:])) if command[1:] != '' else self.print_context(0)
                elif command == 'h':
                    self.print_help()
                elif command == 'q':
                    quit_not_save = input("Really quit without saving? (x in main menu eXits and saves) y/n: ") or 'n'
                    if quit_not_save == 'y':
                        break
                else:
                    print('Unknown command')
            except:
                print("FAIL!")
                pass

    def print_buffer(self):
        for i, line in enumerate(self.buffer, start=1):
            print(f"{i:3d}  {line}")

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

    def insert_line(self, arg):
        if arg == '' or arg == 0:
            index = int(input('Line number: '))
        else:
            index = int(arg)
        line = input('New line: ')
        self.buffer.insert(index - 1, line)

    def print_help(self):
        print('Available commands:')
        print('p - print the buffer with line numbers')
        print('m - print the buffer one page at the time (more-style)')
        print('c - print near Context of a line number')
        print('a - append one or more lines to the buffer')
        print('d - delete a line from the buffer')
        print('s - substitute a line in the buffer')
        print('i - insert a line into the buffer')
        print('h - print this help message')
        print('q - quit the editor without saving changes')
        print('x - eXit the editor saving changes to file')

    def print_more(self):
        page_size = 20
        start = 0
        end = page_size
        while True:
            for i in range(start, end):
                if i < len(self.buffer):
                    print(f"{i + 1:3d}  {self.buffer[i]}")
                else:
                    break
            if end >= len(self.buffer):
                break
            prompt = f"More ({end + 1}-{min(end + page_size, len(self.buffer))})? "
            command = input(prompt)
            if command == 'q':
                break
            start = end
            end = start + page_size

    def print_tail(self,n=10):
        start = max(0, len(self.buffer) - n)
        for i in range(start, len(self.buffer)):
            print(f"{i+1}:{self.buffer[i]}")

    def print_context(self,line_num,plusminus=5):
        if line_num == 0 or line_num == '':
            line_num = int(input("Line number: "))
        start = max(0, line_num - 5)
        end = min(len(self.buffer), line_num + 5)
        for i in range(start, end):
            print(f"{i+1}:{self.buffer[i]}")



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