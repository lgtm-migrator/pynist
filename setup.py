#!/usr/bin/env python
"""Setup script"""

import sys

from __pkginfo__ import \
    author,           author_email,       install_requires,          \
    license,          long_description,   classifiers,               \
    entry_points,     modname,            py_modules,                \
    short_desc,       VERSION,            web

from setuptools import setup, find_packages, Extension

arch = "x64" if sys.maxsize > 2**32 else "x86"

m = Extension(
		name='pynist._core',
		define_macros=[
				('INTERNALBUILD', '1'),
				('WIN32', '1'),
				('MSTXTDATA', '1'),
				],
		libraries=[f'{arch}/nistdl'],
		sources=['pynist/pynist.c'],
		)


setup(
		author             = author,
		author_email       = author_email,
		classifiers        = classifiers,
		description        = short_desc,
		entry_points       = entry_points,
		install_requires   = install_requires,
		license            = license,
		long_description   = long_description,
		name               = modname,
		packages           = find_packages(exclude=("tests",)),
		py_modules         = py_modules,
		url                = web,
		version            = VERSION,
		ext_modules = [m],
		data_files = [('', [f'{arch}/NISTDL.dll', f'{arch}/ctNt66.dll'])],
		)
