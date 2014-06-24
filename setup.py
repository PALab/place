try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='PyPAL',
    version='0.1.0',
    author='Jami L. Johnson, Henrik tom Worden, Kasper van Wijk,',
    author_email='jami.johnson@auckland.ac.nz',
    packages=['pypal','pypal.analysis','pypal.automate','pypal.automate.osci_card','pypal.automate.polytec','pypal.automate.tektronix','pypal.automate.xps_control'],
    scripts=['bin/Scan.py','bin/example_PALplots.py'],
    license='GNU General Public License, Version 3 (LGPLv3)',
    url='https://github.com/johjam/PyPal',
    description= 'An open-source Python package for laboratory automation and analysis.',
    long_description=open('README.txt').read(),
    install_requires=['numpy>1.0.0', 'obspy','scipy', 'matplotlib', 'h5py', 'obspyh5']
    )
