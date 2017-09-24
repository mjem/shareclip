#!/usr/bin/env python3

from setuptools import setup, find_packages

from shareclip import config

setup(
    name='shareclip',
    version=config.version,
    packages=find_packages(),

    # scripts=['shareclip.py'],
	entry_points = {'console_scripts': ['shareclip = shareclip.main:main'] },

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
		# 'docutils>=0.3',
		'aiohttp>=2.2.5',
		'aiohttp-jinja2>=0.13.0',
		# 'Fabric3>=1.13.1',
		# 'Sphinx>=1.6.3',
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

	# not sure if these are used
	data_files=[
		('', [
			'README.rst',
			'LICENSE.rst',
			'ChangeLog.rst',
			'requirements.txt',
			'requirements-dev.txt',
			'docs/conf.py',
			'docs/Makefile',
			'docs/*.png',
			'docs/*.rst',
			'extra/shareclip.service',
		]),
		# does not appear to be used
		# ('docs', [
			# 'main.png',
			# 'conf.py',
			# 'Makefile',
		# ]),
	],

    # metadata for upload to PyPI
    author='Mike Elson',
    author_email='mike.elson@gmail.com',
    description='Web server to share multiple clipboard entries',
    license='GPLv3',
    keywords='web share clipboard messages vuejs websockets',
    url=config.homepage,

	classifiers=[
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPLv3)',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python',
    ]
)
