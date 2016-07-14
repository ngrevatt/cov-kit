#!/usr/bin/python
import re
import os
import argparse
from coverage import Coverage, CoverageData


def get_cov(input_file):
    cov = Coverage(data_file=input_file)
    cov.load()
    return cov


def get_cov_data(input_file):
    data = CoverageData()
    data.read_file(input_file)
    return data


def get_analysis(cov, data):
    analysis = {}
    for file_name in data.measured_files():
        analysis[file_name] = cov.analysis2(file_name)
    return analysis


def find_uninit_classes(analysis):
    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    current_cls = None
    uninit_dict = {}

    for file_name in analysis:  # keys in analysis are file_names
        with open(file_name, 'r') as f:
            _, executable_lines, excluded_lines, missing_lines, __ = analysis[file_name]
            uninit_list = []
            in_init = False
            for line_number, line in enumerate(f, 1):
                if line.startswith('class'):
                    current_cls = re_cls.match(line).group(1)
                elif re_init.search(line):
                    in_init = True
                elif in_init and line_number in executable_lines and line_number in missing_lines:
                    uninit_list.append(current_cls)
                    in_init = False
            if uninit_list:
                uninit_dict[file_name] = ((len(executable_lines) - len(missing_lines)) / len(executable_lines), uninit_list)
    return uninit_dict


def trim_file_name(data, file_name):
    directory_path = os.path.dirname(os.path.commonpath(data.measured_files()))
    return file_name.split(directory_path)[-1]


def output(data, uninit_dict):
    s = sorted(uninit_dict.keys(), reverse=True, key=lambda x: uninit_dict[x][0])
    for file_name in s:
        trimmed_name = trim_file_name(data, file_name)
        # unpack, coverage is first index, followed by classes
        coverage, uninit_list = uninit_dict[file_name]
        # percent_cmverage is the first item in the list
        print('{} ({}%):'.format(trimmed_name, coverage))
        for cls_name in uninit_list:
            print('\t{}'.format(cls_name))
        print("\n")


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='.coverage', help='Input file name', required=False, type=str)
    args = parser.parse_args()
    cov = get_cov(args.input)
    data = get_cov_data(args.input)
    analysis = get_analysis(cov, data)

    # create dictionary of files and uninitialized classes
    uninit = find_uninit_classes(analysis)
    output(data, uninit)


if __name__ == '__main__':
    main()
