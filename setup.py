from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in size_billable/__init__.py
from size_billable import __version__ as version

setup(
	name="size_billable",
	version=version,
	description="Enhanced billing and timesheet management for ERPNext",
	author="Your Company",
	author_email="support@yourcompany.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)

