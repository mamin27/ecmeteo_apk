#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='MeteoPoint',
    version='0.0.1',
    description='A simple To-Do list app',
    author='Marian Minar',
    author_email='mminar7@gmail.com',
    license='GNU Affero General Public License',
    packages=find_packages(
        exclude=['docs', 'tests', 'android']
    ),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU Affero General Public License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
    ],
    install_requires=[
        'toga>=0.4.0',  # BeeWare's GUI toolkit for Android
        'requests>=2.28.0',  # For HTTP requests
        'pyjnius>=1.4.0',  # For Android API access
    ],
    options={
        'app': {
            'formal_name': 'MeteoPoint',
            'bundle': 'org.ecomet.meteopoint'
        },
    }
)
