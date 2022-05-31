from setuptools import setup, find_packages
print(find_packages())

setup(name='MonteScene',
version='0.1',
description='MonteScene package',
url='https://github.com/vevenom/MonteScene',
author='vevenom',
author_email='sinisa.stekovic@icg.tugraz.at',
license='BSD 3-Clause Clear License',
packages=find_packages(),
include_package_data=True,
zip_safe=False)
