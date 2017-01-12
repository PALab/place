try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='place',
    version='0.2.1',
    author='Jami L. Johnson, Henrik tom Worden, Kasper van Wijk,',
    author_email='jami.johnson@auckland.ac.nz',
    packages=[
        'place',
        'place.automate',
        'place.automate.osci_card',
        'place.automate.polytec',
        'place.automate.tektronix',
        'place.automate.xps_control',
        'place.automate.SRS',
        'place.automate.quanta_ray',
        'place.automate.new_focus',
        'place.automate.scan',
        'place.scripts'],
    scripts=['bin/example_DS345.py',
        'bin/example_oscicard_AcquireInstancesAfterCommand.py',
        'bin/example_oscicard_AverageMultipleRecords.py',
        'bin/example_QuantaRay.py',
        'bin/example_tektronix.py',
        'bin/xps_demo.py',
        'bin/xps_exampleUsageController.py'],
    license='GNU General Public License, Version 3 (LGPLv3)',
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Science/Research',
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Physics'],
    url='https://github.com/PALab/place',
    description= 'An open-source Python package for laboratory automation, control, and experimentation.',
    long_description=open('README.md').read(),
    entry_points={'console_scripts':[
        'place_scan = place.scripts.scan:main',
        'place_server = place.scripts.scan:scan_server',
        'place_picomove = place.scripts.picomove:main',
        'place_encheck = place.scripts.encheck:main'],},
    )
