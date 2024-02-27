""" setup configuration file """

import os.path
from setuptools import setup, find_packages

CURRDIR = os.path.dirname(os.path.abspath(__file__))


setup(
    name="place",
    version="0.10.0",
    author="Jami L. Johnson, Henrik tom Worden, Kasper van Wijk, Paul Freeman, Jonathan Simpson",
    author_email="paul.freeman.cs@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy==1.26.4",
        "scipy==1.11.4",
        "matplotlib==3.8.0",
        "django",
        "pyserial==3.5",
        "dash==2.14.2",
        "dash-bootstrap-components==1.5.0",
    ],
    scripts=[],
    license="GNU General Public License, Version 3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Console",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    url="https://github.com/PALab/place",
    description=(
        "An open-source Python package for laboratory automation, "
        + "control, and experimentation."
    ),
    long_description=open("{}/README.md".format(CURRDIR)).read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "place_dash = placeweb.dash:start",
            "place_server = placeweb.server:start",
            "place_renamer = place.utilities:column_renamer",
            "place_unpack = place.utilities:multiple_files",
            "place_pack = place.utilities:single_file",
        ],
    },
)
