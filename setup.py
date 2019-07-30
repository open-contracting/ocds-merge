from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocdsmerge',
    version='0.5.6',
    author='Open Contracting Partnership',
    author_email='data@open-contracting.org',
    url='https://github.com/open-contracting/ocds-merge',
    description='A library and reference implementation for merging OCDS releases',
    license='BSD',
    packages=find_packages(exclude=['tests']),
    long_description=long_description,
    install_requires=[
        'jsonref',
        'requests',
    ],
    extras_require={
        'test': [
            'coveralls',
            'jsonschema',
            'pytest',
            'pytest-cov',
            'pytest-vcr',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
)
