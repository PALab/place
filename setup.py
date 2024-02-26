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
        "numpy>=1.25,<1.26",
        "scipy>=1.11,<1.12",
        "pandas>=2.1,<2.2",
        "matplotlib>=3.7,<3.8",
        "django>=5.0,<5.1",
        "pyserial>=3.5,<3.6",
        "pyyaml>=6.0,<6.1",
        "setuptools>=69.1,<69.2",
        "pylint>=2.16,<2.17",
        "dash>=2.1,<2.2",
        "dash-bootstrap-components>=1.5,<1.6",
    ],
    scripts=[],
    license="GNU General Public License, Version 3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Console",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
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
            "place_dash = place_dash_app.app:start",
            "place_server = placeweb.server:start",
            "place_renamer = place.utilities:column_renamer",
            "place_unpack = place.utilities:multiple_files",
            "place_pack = place.utilities:single_file",
        ],
    },
)
