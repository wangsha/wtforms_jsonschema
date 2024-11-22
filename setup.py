from setuptools import setup, find_packages
# To use a consistent encoding
from os import path
import os



here = path.abspath(path.dirname(__file__))



long_description = ""

extras = {
    'fab': ['Flask-AppBuilder>=1.13.0', 'pillow'],
    'geofab': ['fab-addon-geoalchemy', 'Flask-AppBuilder>=1.13.0', 'pillow'],
    'test': ['pytest', 'pytest-cov']
}


setup(
    name="wtforms_jsonschema2",
    version='0.7.0',
    description="Package to convert WTForms to JSON Schema",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/dolfandringa/wtforms_jsonschema",
    author="Dolf Andringa",
    author_email="dolfandringa@gmail.com",
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,
    package_data={'': ['LICENSE']},
    install_requires=['wtforms'],
    setup_requires=['pytest-runner'],
    tests_require=extras['test']+extras['fab']+extras['geofab'],
    extras_require=extras,
    dependency_links=[
        'http://github.com/dolfandringa/Flask-AppBuilder/tarball/develop#egg=Flask-AppBuilder-1.13.0'
    ],
    project_urls={
        'Source': 'https://github.com/dolfandringa/wtforms_jsonschema/'
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
    ],
    keywords='wtforms jsonschema'
)
