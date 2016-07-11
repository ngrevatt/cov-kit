#!/usr/bin/python
import re
import argparse
from coverage import CoverageData


def get_cov_data(input_file):
    if input_file is None:
        input_file = '.coverage'
    data = CoverageData()
    data.read_file(input_file)
    return data


def find_uninit_classes(input_file):
    if input_file is None:
        input_file = '.coverage'
    data = get_cov_data(input_file)

    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    current_cls = None
    uninit_dict = {}

    for file_name in data.measured_files():
        with open(file_name, 'r') as f:
            covered_lines = set(data.lines(file_name))
            for i, line in enumerate(f):
                current_line = i
                if line.startswith('class'):
                    current_cls = re_cls.match(line).group(1)
                elif re_init.search(line) and current_line not in covered_lines:
                    if file_name not in uninit_dict:
                        uninit_dict[file_name] = []
                    uninit_dict[file_name].append(current_cls)

    return uninit_dict


def output(input_file, uninit_dict):
    data = get_cov_data(input_file)
    output_map = data.line_counts(fullpath=True)
    s = sorted(uninit_dict.keys(), reverse=True, key=lambda x: output_map[x])
    for file_name in s:
        print(file_name + ":")
        for cls_name in uninit_dict[file_name]:
            print('\t{}'.format(cls_name))
        print("\n")


def main():
    parser = argparse.ArgumentParser()  # parse command line arguments
    parser.add_argument('-i', '--input', help='Input file name', required=False, type=str)
    args = parser.parse_args()

    uninit = find_uninit_classes(args.input)  # create dictionary of files and uninitialized classes
    output(args.input, uninit)


if __name__ == '__main__':
    main()
