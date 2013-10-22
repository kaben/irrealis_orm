from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='irrealis_orm',
      version=version,
      description="SQLAlchemy-based ORM configuration",
      long_description="""\
Tool to quickly setup SQLAlchemy object relation mappings""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='SQLAlchemy ORM',
      author='Kaben Nanlohy',
      author_email='kaben.nanlohy@gmail.com',
      url='https://github.com/kaben/irrealis_orm',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "SQLAlchemy>=0.8.2",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
