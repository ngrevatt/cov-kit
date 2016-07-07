#!/usr/bin/python
import re
from coverage import CoverageData


def main():
    data = CoverageData()
    data.read_file('.coverage')

    re_cls = re.compile(r'^class\s(.+)[\(|:]')
    re_init = re.compile(r'def\s__init__')
    current_cls = None

    with open('uninitialized_classes.txt', 'w') as out:
        for file in data.measured_files():
            with open(file, 'r') as f:
                for i, line in enumerate(f):
                    if line.startswith('class'):
                        try:
                            current_cls = re_cls.match(line).group(1)
                        except AttributeError:
                            import pdb; pdb.set_trace()
                    elif re_init.search(line) and (i + 1) not in data.lines(file):
                        out.write('%s %s\n' % (file, current_cls))


if __name__ == '__main__':
    main()
