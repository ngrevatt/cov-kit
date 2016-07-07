#!/usr/bin/python
import re
import argparse
from coverage import CoverageData


def find_uninit_classes(input_file):
    if input_file is None:
        input_file = '.coverage'
    data = CoverageData()
    data.read_file(input_file)

    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    current_cls = None
    uninit_dict = {}

    for file_name in data.measured_files():
        with open(file_name, 'r') as f:
            for i, line in enumerate(f):
                current_line = i + 1
                if line.startswith('class'):
                    current_cls = re_cls.match(line).group(1)
                elif re_init.search(line) and (current_line) not in data.lines(file_name):
                    if file_name not in uninit_dict:
                        uninit_dict[file_name] = []
                    uninit_dict[file_name].append(current_cls)

    return uninit_dict


def output(uninit_dict):
    for file_name, cls_list in uninit_dict.items():
        for cls_name in cls_list:
            print('{}: {}'.format(file_name, cls_name))


def main():
    parser = argparse.ArgumentParser()  # parse command line arguments
    parser.add_argument('-i', '--input', help='Input file name', required=False, type=str)
    args = parser.parse_args()

    uninit = find_uninit_classes(args.input)  # create dictionary of files and uninitialized classes
    output(uninit)


if __name__ == '__main__':
    main()
