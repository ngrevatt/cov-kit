#!/usr/bin/python
import re
from coverage import CoverageData


def find_uninit_classes(coverage_file):
    data = CoverageData()
    data.read_file('.coverage')

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
    uninit = find_uninit('.coverage')
    for file in uninit:
        print(file, uninit[file], "\n")


if __name__ == '__main__':
    main()
