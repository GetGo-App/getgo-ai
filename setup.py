from setuptools import find_packages, setup

setup(
    name = 'GetGo-AI',
    version = '0.1',
    description = 'Conversational AI for GetGo app',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    author = 'Phuc Phan',
    author_email = 'phanphuc1100@gmail.com',
    maintainer = 'Phuc Phan',
    maintainer_email = 'phanphuc1100@gmail.com',
)