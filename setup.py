from distutils.core import setup

from setuptools import find_packages

setup(
    name='nomad',
    version='0.1dev',
    packages=find_packages(),
      install_requires=[
          'cloudpickle',
      ],
    long_description=open('README.md').read(),
)