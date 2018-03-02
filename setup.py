from setuptools import setup
import sys,os
home=os.path.expanduser('~')

setup(
    name = 'kraldesk',
    version = '0.1dev',
    description = '',
    license='GPL v3',
    packages=['pdproject'],
    package_data={'kraldesk': ['sample-data/*.csv']},
    install_requires=['reportlab','pandas','numpy']
)
