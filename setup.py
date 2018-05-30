""" setup configuration file """
from setuptools import setup, find_packages

setup(
    name='place',
    version='0.7.0',
    author='Jami L. Johnson, Henrik tom Worden, Kasper van Wijk, Paul Freeman',
    author_email='email.paul.freeman@gmail.com',
    packages=find_packages(),
    scripts=[],
    license='GNU General Public License, Version 3 (LGPLv3)',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Console',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Physics'],
    url='https://github.com/PALab/place',
    description=('An open-source Python package for laboratory automation, ' +
                 'control, and experimentation.'),
    long_description=open('README.md').read(),
    entry_points={'console_scripts':[
        'place_experiment = place.experiment:main',
        'place_server = place.experiment:experiment_server',
        'place_renamer = place.utilities:column_renamer',
        'place_unpack = place.utilities:multiple_files',
        'place_pack = place.utilities:single_file'],},
    )
