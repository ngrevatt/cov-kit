#!/usr/bin/python
import re
import sys
import getopt
from coverage import CoverageData


def find_uninit_classes(input_file):
    data = CoverageData()
    data.read_file(input_file)

    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    current_cls = None
    uninit_dict = {}

    for file in data.measured_files():
        with open(file, 'r') as f:
            for i, line in enumerate(f):
                current_line = i + 1
                if line.startswith('class'):
                    current_cls = re_cls.match(line).group(1)
                elif re_init.search(line) and (current_line) not in data.lines(file):
                    if file not in uninit_dict:
                        uninit_dict[file] = []
                    uninit_dict[file].append(current_cls)

    return uninit_dict


def main():
    ifile = '.coverage'  # set defaults
    ofile = None

    opts, args = getopt.getopt(sys.argv[1:], "i:o:")  # parse command line args
    for opt, arg in opts:
        if opt == '-i':
            ifile = arg
        elif opt == '-o':
            ofile = arg

    uninit = find_uninit_classes(ifile)  # create dictionary of files and uninitialized classes

    if ofile is not None:  # output
        with open(ofile, 'w') as out:
            for file in uninit:
                out.write(file + str(uninit[file]) + "\n")
    else:
        for file in uninit:
            print(file, uninit[file], "\n")


if __name__ == '__main__':
    main()
