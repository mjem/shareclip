#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='shareclip',
    version='0.1',
    packages=find_packages(),

    # scripts=['shareclip.py'],
	entry_points = {'console_scripts': ['shareclip = shareclip.cmd:main'] },

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
		'docutils>=0.3',
		'aiohttp>=2.2.5',
		'aiohttp-jinja2>=0.13.0',
		'Fabric3>=1.13.1',
		'Sphinx>=1.6.3',
	],

    package_data={
        '': [
			'static/*.js',
			'static/*.css',
			'templates/*.html',
		],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
    },

	data_files=[
		('.', [
			'LICENSE.rst',
			'ChangeLog.rst',
			'requirements.txt',
		]),
		('docs', [
			'docs/conf.py',
			'docs/Makefile',
		]),
	],

    # metadata for upload to PyPI
    author='Mike Elson',
    author_email='mike.elson@gmail.com',
    description='Web server to share multiple clipboard entries',
    license='GPLv3',
    keywords='web share clipboard messages vuejs websockets',
    url='https://github.com/mjem/shareclip',  # project home page, if any

	classifiers=[
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPLv3)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
    ]
)
