from setuptools import setup, find_packages

setup(
    name='kraldesk',
    version='0.1dev',
    license='GPL v3',
    packages=find_packages(),
    data_files=[('kraldesk',['sample-data/*.csv'])]
)
