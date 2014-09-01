try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='PLACE',
    version='0.1.0',
    author='Jami L. Johnson, Henrik tom Worden, Kasper van Wijk,',
    author_email='jami.johnson@auckland.ac.nz',
    packages=['place','place.analysis','place.automate','place.automate.osci_card','place.automate.polytec','place.automate.tektronix','place.automate.xps_control','place.automate.SRS'],
    scripts=['bin/Scan.py','bin/example_PALplots.py'],
    license='GNU General Public License, Version 3 (LGPLv3)',
    url='https://github.com/johjam/PLACE',
    description= 'An open-source Python package for laboratory automation, control, and experimentation.',
    long_description=open('README.txt').read(),
    install_requires=['numpy>1.0.0', 'obspy','scipy', 'matplotlib', 'h5py', 'obspyh5','pyserial']
    )
