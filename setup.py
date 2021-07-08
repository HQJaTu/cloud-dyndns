#!/usr/bin/env python3

from distutils.core import setup
from setuptools import find_packages
import pathlib


# Sample from: https://github.com/pypa/sampleproject/blob/master/setup.py
setup(name='cloud-dyndns',
      version='0.8.0',
      description='Systemd service to maintain DNS-entry for system with dynamic IP-address in a cloud-based DNS',
      author='Jari Turkia',
      author_email='jatu@hqcodeshop.fi',
      url='https://github.com/HQJaTu/cloud-dyndns',
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',

          # Indicate who your project is intended for
          'Intended Audience :: System Administrators',

          # Specify the Python versions you support here.
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ],
      python_requires='>=3.7, <4',
      install_requires=['netifaces', 'requests'],
      scripts=['cloud-dyndns.py'],
      include_package_data=True,
      packages=find_packages()
      )
