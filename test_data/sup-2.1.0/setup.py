from setuptools import setup, find_packages

setup(
    name='sup',
    version='2.1.0',
    entry_points={'console_scripts': ['sup=sup:hello_sup']},
    packages=find_packages(),
)
