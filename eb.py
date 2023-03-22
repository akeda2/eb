#!/usr/bin/env python3
import sys
import curses
import os
#from curses import wrapper


class Editor:
    def __init__(self, filename=None):
        self.buffer = []
        self.filename = filename
        if self.filename is not None and os.path.isfile(self.filename):
            with open(self.filename) as f:
                self.buffer = f.read().splitlines()
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
                elif command == 'p':
                    self.print_buffer()
                elif command.startswith('a'):
                    self.append_lines(int(command[1:])) if command[1:] != '' else self.append_lines('x')
                elif command.startswith('d'):
                    self.delete_lines(command[1:])
                elif command.startswith('s'):
                    self.substitute_lines(command[1:])
                elif command.startswith('e'):
                    #wrapper(self.modify_line(int(command[1:]))) if command[1:] != '' else wrapper(self.modify_line(int(input("Line number: "))))
                    self.modify_line(int(command[1:])) if command[1:] != '' else self.modify_line(int(input("Line number: ")))
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

    def print_buffer(self):
        for i, line in enumerate(self.buffer, start=1):
            #if self.old_version:
            print('{i:3d}  {line}'.format(i=i, line=line))
            #else:
            #    print(f"{i:3d}  {line}")

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
        print('p  - print the buffer with line numbers')
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
    def print_more(self):
        page_size = 20
        start = 0
        end = page_size
        while True:
            for i in range(start, end):
                if i < len(self.buffer):
                    #if self.old_version:
                    print('{i:3d}  {buffer}'.format(i=i +1, buffer=self.buffer[i]))
                    #else:
                    #    print(f"{i + 1:3d}  {self.buffer[i]}")
                else:
                    break
            if end >= len(self.buffer):
                break
            #if self.old_version:
                # Use a non f-string to make it compatible with old python versions
            prompt = 'More ({end}-{page_size})?'.format(end=end+1, page_size=min(end + page_size, len(self.buffer)))
            #else:
            #    prompt = f"More ({end + 1}-{min(end + page_size, len(self.buffer))})? "
            command = input(prompt)
            if command == 'q':
                break
            start = end
            end = start + page_size

    def print_tail(self,n=10):
        start = max(0, len(self.buffer) - n)
        for i in range(start, len(self.buffer)):
            #if self.old_version:
            print('{i:3d}  {buffer}'.format(i=i+1, buffer=self.buffer[i]))
            #else:
            #    print(f"{i+1:3d}  {self.buffer[i]}")

    def print_context(self,line_num,plusminus=5):
        if line_num == 0 or line_num == '':
            line_num = int(input("Line number: "))
        start = max(0, line_num - plusminus)
        end = min(len(self.buffer), line_num + plusminus)
        for i in range(start, end):
            #if self.old_version:
            print('{i:3d}  {buffer}'.format(i=i+1, buffer=self.buffer[i]))
            #else:
            #    print(f"{i+1:3d}  {self.buffer[i]}")

    def print_line(self, line_num):
        #if self.old_version:
        print('{line_num:3d}  {buffer}'.format(line_num=line_num, buffer=self.buffer[line_num - 1]))
        #else:
        #    print(f"{line_num}:{self.buffer[line_num]}")

    """def modify_line(self, line_num, new_line):
        self.buffer[line_num] = new_line"""
    
    """def modify_line(self, line_num):
        print(f"{line_num}:{self.buffer[line_num]}")
        new_line = input("New line: {}".format(self.buffer[line_num]))
        self.buffer[line_num] = new_line"""
    def modify_line(self, line_num):
        #print(f"{line_num}:{self.buffer[line_num]}")
        line_num -= 1
        stdscr = curses.initscr()
        #curses.resizeterm(24, 80)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.clear()
        stringtoedit = self.buffer[line_num].strip()
        stdscr.addstr("Edit the following line and press Ctrl-G to save:\n\n")
        editwin = curses.newwin(1, 80, 2, 0)
        editwin.addstr(0, 0, stringtoedit)
        stdscr.refresh()
        editwin.refresh()
        curses.curs_set(1)
        
        while True:
            ch = stdscr.getch()
            # Catch the enter key:
            if ch == 10:  # Ctrl-J (ASCII linefeed character)
                new_line = editwin.instr(0, 0).decode().strip()
                break
            elif ch == 7:  # Ctrl-G (ASCII bell character)
                new_line = editwin.instr(0, 0).decode().strip()
                break
            elif ch == curses.KEY_BACKSPACE:
                #editwin.delch()
                stringtoedit = stringtoedit[:-1]
            elif ch == curses.KEY_LEFT:
                editwin.move(0, editwin.getyx()[1] - 1)
            elif ch == curses.KEY_RIGHT:
                editwin.move(0, editwin.getyx()[1] + 1)
            

            else:
                editwin.addch(ch)
                stringtoedit += chr(ch)
            #self.buffer[line_num] = stringtoedit #+ '\n'
            editwin.clear()
            editwin.addstr(0, 0, stringtoedit)
            editwin.refresh()
    
        self.buffer[line_num] = new_line #+ '\n'
        

        stdscr.refresh()
        curses.curs_set(0)
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

        #new_line = input("New line: ")
        #self.buffer[line_num] = new_line
    
    
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
                f.write('\n'.join(self.buffer))
            print("File saved")
        except:
            print("Could not save!")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        editor = Editor(filename) #if os.path.exists(filename) else Editor()
    else:
        editor = Editor()
    editor.run()