from setuptools import setup
import sys,os
home=os.path.expanduser('~')

setup(
    name = 'pdproject',
    version = '0.2dev',
    description = '',
    license='GPL v3',
    package_dir = {'': 'src'},
   # package_data={'kraldesk': ['sample-data/*.csv']},
    install_requires=['reportlab','pandas','numpy']
)
