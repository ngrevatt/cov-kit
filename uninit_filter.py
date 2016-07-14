#!/usr/bin/python
import re
import os
import argparse
from coverage import CoverageData


def get_cov_data(input_file):
    data = CoverageData()
    data.read_file(input_file)
    return data


def find_uninit_classes(data):
    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    current_cls = None
    uninit_dict = {}

    for file_name in data.measured_files():
        with open(file_name, 'r') as f:
            covered_lines = set(data.lines(file_name))
            covered_count = len(covered_lines)
            percent_coverage = 0
            for i, line in enumerate(f):
                line_number = i + 1
                if line.startswith('class'):
                    current_cls = re_cls.match(line).group(1)
                elif re_init.search(line) and line_number not in covered_lines:
                    uninit_dict.setdefault(file_name, [percent_coverage]).append(current_cls)
                    uninit_dict[file_name][0] = str(covered_count / line_number)

    return uninit_dict


def trim_file_name(data, file_name):
    directory_path = os.path.dirname(os.path.commonpath(data.measured_files()))
    return file_name.split(directory_path)[-1]


def output(data, uninit_dict):
    s = sorted(uninit_dict.keys(), reverse=True, key=lambda x: uninit_dict[x][0])
    for file_name in s:
        trimmed_name = trim_file_name(data, file_name)
        # unpack, coverage is first index, followed by classes
        coverage, *classes = uninit_dict[file_name]
        # percent_cmverage is the first item in the list
        print('{} ({}%):'.format(trimmed_name, coverage))
        for cls_name in classes:
            print('\t{}'.format(cls_name))
        print("\n")


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='.coverage', help='Input file name', required=False, type=str)
    args = parser.parse_args()
    data = get_cov_data(args.input)

    # create dictionary of files and uninitialized classes
    uninit = find_uninit_classes(data)
    output(data, uninit)


if __name__ == '__main__':
    main()
