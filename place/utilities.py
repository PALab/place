"""Helper utilities for PLACE data"""

from sys import argv
from os import remove
from os.path import basename, isdir, isfile
from itertools import count
from glob import glob
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

def single_file():
    """Pack the individual row files into one NumPy structured array"""
    if not (len(argv) == 2 and isdir(argv[1])):
        print('Usage: {} [DIRECTORY]')
        print('Pack PLACE scan_data_XXX.npy files into a single file.')
        return
    directory = argv[1]
    files = sorted(glob('{}/scan_data_*.npy'.format(directory)))
    num = len(files)
    if num == 0:
        print('No PLACE scan_data_*.npy files found in {}'.format(directory))
        return
    with open(files[0], 'rb') as file_p:
        row = np.load(file_p)
    data = np.resize(row, (num,))
    for i, filename in enumerate(files):
        with open(filename, 'rb') as file_p:
            row = np.load(file_p)
        data[i] = row[0]
    with open('{}/scan_data.npy'.format(directory), 'xb') as file_p:
        np.save(file_p, data)
    for filename in files:
        remove(filename)

def multiple_files():
    """Unpack one NumPy structured array into individual row files"""
    if not (len(argv) == 2 and isdir(argv[1])):
        print('Usage: {} [DIRECTORY]')
        print('Unpack PLACE scan_data.npy file into multiple files.')
        return
    directory = argv[1]
    with open('{}/scan_data.npy'.format(directory), 'rb') as file_p:
        data = np.load(file_p)
    for i, row in enumerate(data):
        with open('{}/scan_data_{:03d}.npy'.format(directory, i), 'xb') as file_p:
            np.save(file_p, [row])
    remove('{}/scan_data.npy'.format(directory))
