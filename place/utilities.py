"""Helper utilities for PLACE data"""

from sys import argv
from os.path import basename, isfile
from itertools import count
import numpy as np

def column_renamer():
    """Tool for renaming the columns in a NumPy structured array file"""
    if not (len(argv) > 1 and argv[1].endswith('.npy') and isfile(argv[1])):
        print('Usage:')
        print('  To display column headings:')
        print('    {} [FILE]'.format(basename(argv[0])))
        print('  To rename a column heading (or multiple headings):')
        print('    {} [FILE] [COLUMN_NUM] [NEW_COLUMN_NAME]...'.format(basename(argv[0])))
        print('')
        print('Example:')
        print('    {} scan_data_001.npy 1 trace 2 data'.format(basename(argv[0])))
        return
    with open(argv[1], 'rb') as file_p:
        data = np.load(file_p)
    if len(argv) == 2:
        for i, name in enumerate(data.dtype.names):
            print('{:2} {}'.format(i, name))
        return
    names = list(data.dtype.names)
    for i in count(start=4, step=2):
        if len(argv) > i:
            names[int(argv[i-2])] = argv[i-1]
        elif len(argv) == i:
            names[int(argv[i-2])] = argv[i-1]
            break
        else:
            print('Invalid number of arguments - no changes made')
            return
    data.dtype.names = names
    print('Applying changes...', end='')
    with open(argv[1], 'wb') as file_p:
        np.save(file_p, data)
    print('done!')
