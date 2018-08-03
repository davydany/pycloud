#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'boto>=2.49.0',
    'PyYAML>=3.0',
    'paramiko>=2.4.1'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="David Daniel",
    author_email='davydany@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="PyCloud",
    entry_points={
        'console_scripts': [
            'pycloud=pycloud.core.cli:pycloud',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pycloud',
    name='pycloud',
    packages=find_packages(include=['pycloud']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/davydany/pycloud',
    version='0.1.0',
    zip_safe=False,
)
