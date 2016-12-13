try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='place',
    version='0.1.2a',
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
        'Intended Audience :: Science/Research',
        'Development Status :: 3 - Alpha',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Physics'],
    url='https://github.com/johjam/PLACE',
    description= 'An open-source Python package for laboratory automation, control, and experimentation.',
    long_description=open('README.txt').read(),
    entry_points={'console_scripts':[
        'scan = place.scripts.scan:main',
        'picomove = place.scripts.picomove:main',
        'encheck = place.scripts.encheck:main'],},
    )
