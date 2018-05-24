from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocdsmerge',
    version='0.4',
    author='David Raznick',
    author_email='mr.raznick@gmail.com',
    url='https://github.com/open-contracting/ocds-merge',
    description='A library and reference implementation for merging OCDS releases',
    license='BSD',
    packages=['ocdsmerge', 'ocdsmerge.fixtures'],
    long_description=long_description,
    install_requires=[
        'jsonref',
        'requests',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
)
