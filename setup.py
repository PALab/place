try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='PLACE',
    version='0.1.0',
    author='Jami L. Johnson, Henrik tom Worden, Kasper van Wijk,',
    author_email='jami.johnson@auckland.ac.nz',
    packages=['place','place.automate','place.automate.osci_card','place.automate.polytec','place.automate.tektronix','place.automate.xps_control','place.automate.SRS','place.automate.quanta_ray','place.automate.scan', 'place.automate.new_focus'],
    scripts=['bin/automation_scripts/Scan.py','bin/example_DS345.py','bin/example_oscicard_AcquireInstancesAfterCommand.py','bin/example_oscicard_AverageMultipleRecords.py','bin/example_QuantaRay.py','bin/example_tektronix.py','bin/xps_demo.py','bin/xps_exampleUsageController.py'],
    license='GNU General Public License, Version 3 (LGPLv3)',
    url='https://github.com/johjam/PLACE',
    description= 'An open-source Python package for laboratory automation, control, and experimentation.',
    long_description=open('README.txt').read(),
    install_requires=['numpy>1.0.0', 'obspy','scipy', 'matplotlib', 'h5py', 'obspyh5','pyserial']
    )
