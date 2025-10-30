# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re, ast

# get version from __version__ variable in it_management/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('it_management/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

def parse_requirements_file(path):
    """Read requirements.txt and return a list suitable for install_requires."""
    reqs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            reqs.append(line)
    return reqs

install_requires = parse_requirements_file('requirements.txt')

setup(
    name='it_management',
    version=version,
    description='Management von IT-Bausteinen. Hierzu gehören',
    author='IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups,',
    author_email='Dienstleistungsverträge, Accounts und Internetleistungen.info@tueit.de',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
