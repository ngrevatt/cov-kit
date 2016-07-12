#!/usr/bin/python
import re
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
                    if file_name not in uninit_dict:
                        uninit_dict[file_name] = [percent_coverage]
                    uninit_dict[file_name].append(current_cls)
                    uninit_dict[file_name][0] = str(covered_count / line_number)
    return uninit_dict


def output(data, uninit_dict):
    s = sorted(uninit_dict.keys(), reverse=True, key=lambda x: uninit_dict[x][0])
    for file_name in s:
        print('{} ({}%):'.format(file_name, uninit_dict[file_name][0]))  # percent_coverage is the first item in the list
        for cls_name in uninit_dict[file_name][1:]:
            print('\t{}'.format(cls_name))
        print("\n")


def main():
    parser = argparse.ArgumentParser()  # parse command line arguments
    parser.add_argument('-i', '--input', default='.coverage', help='Input file name', required=False, type=str)
    args = parser.parse_args()
    data = get_cov_data(args.input)

    uninit = find_uninit_classes(data)  # create dictionary of files and uninitialized classes
    output(data, uninit)


if __name__ == '__main__':
    main()
