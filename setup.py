from setuptools import setup
setup(name='ocdsmerge',
      version='0.3',
      description='OCDS Release Merge Library',
      author='David Raznick',
      author_email='mr.raznick@gmail.com',
      license='BSD',
      packages=['ocdsmerge', 'ocdsmerge.fixtures'],
      include_package_data=True,
      url='https://github.com/open-contracting/ocds-merge'
)
