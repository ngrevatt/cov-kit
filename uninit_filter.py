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


def find_uncovered(analysis):
    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    re_func = re.compile(r'^def\s(.+)[\(|:]')
    current_cls = None
    current_func = None
    coverages = {}
    classes = {}
    functions = {}

    for file_name in analysis:  # keys in analysis are file_names
        with open(file_name, 'r') as f:
            _, executable_lines, excluded_lines, missing_lines, __ = analysis[file_name]
            uncov_classes = []
            uncov_functions = []
            in_init = False
            in_func = False
            for line_number, line in enumerate(f, 1):
                # handling uninitialized classes
                if line.startswith('class'):
                    current_cls = re_cls.match(line).group(1)
                elif re_init.search(line):
                    in_init = True
                elif in_init and line_number in executable_lines:
                    if line_number in missing_lines:
                        uncov_classes.append(current_cls)
                    in_init = False
                # handling uninitalized functions
                if line.startswith('def'):
                    current_func = re_func.match(line).group(1)
                    in_func = True
                elif in_func and line_number in executable_lines:
                    if line_number in missing_lines:
                        uncov_functions.append(current_func)
                    in_func = False
            if executable_lines:
                coverages[file_name] = (len(executable_lines) - len(missing_lines)) / len(executable_lines)
            if uncov_classes:
                classes[file_name] = uncov_classes 
            if uncov_functions:
                functions[file_name] = uncov_functions 
    return coverages, classes, functions


def trim_file_name(data, file_name):
    directory_path = os.path.dirname(os.path.commonpath(data.measured_files()))
    return file_name.split(directory_path)[-1]


def output(data, coverages, classes, functions):
    s = sorted(coverages, reverse=True, key=coverages.get)
    for file_name in s:
        if file_name in classes or file_name in functions:
            trimmed_name = trim_file_name(data, file_name)
            # percent_cmverage is the first item in the list
            print('{} ({:2.2f}%):'.format(trimmed_name, coverages[file_name]*100))
            if file_name in classes:
                print('Uninitialized Classes:')
                for cls_name in classes[file_name]:
                    print('\t{}'.format(cls_name))
            if file_name in functions:
                print('Unused Functions:')
                for func_name in functions[file_name]:
                    print('\t{}'.format(func_name))
            print('\n')


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='.coverage', help='Input file name', required=False, type=str)
    args = parser.parse_args()
    cov = get_cov(args.input)
    data = get_cov_data(args.input)
    analysis = get_analysis(cov, data)

    # create dictionary of files and uninitialized classes
    coverages, classes, functions = find_uncovered(analysis)
    output(data, coverages, classes, functions)


if __name__ == '__main__':
    main()
