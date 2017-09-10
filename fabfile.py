#!/usr/bin/env python3

import os
import shutil
import pathlib

from fabric.api import local

HERE = pathlib.Path('.')
ENV = pathlib.Path('env')
SEP = '/'
THIRDPARTY = pathlib.Path('thirdparty')
BOOTSTRAP_VERSION = '4.0.0-beta'
STATIC = pathlib.Path('shareclip', 'static')
ACTIVATE = pathlib.Path('activate')

def dist():
	"""Create a distributable archive file."""

	pass


# def clean():
	# """Restore directory to original download state."""
	# zap_list = []
	# for zap_ext in ('__pycache__', '*.pyc', '*.pyo'):
		# for zap_item in Path('.').rglob(zap_ext):
			# if str(zap_item).startswith(str(ENV) + SEP):
				# continue
			# print('unlink ' + str(zap_item))
			# zap_list.append(zap_item)
	# for zap_item in zap_list:
		# if zap_item.exists():
			# if zap_item.is_file():
				# print('unlink {i}'.format(i=zap_item))
				# zap_item.unlink()
			# else:
				# print('rmtree {i}'.format(i=zap_item))
				# shutil.rmtree(zap_item)
	# generated html documentation
	# test results
	# activate file
	# setup temporary files
	# if ACTIVATE.exists():
		# ACTIVATE.unlink()
# def veryclean():
	# """Remove all generated files, even 3rd party files checked into source code control.
	# Run 'fab thirdparty env' afterwards to restore useable state.
	# """
	# clean()
	# clean_thirdparty()
	# clean_env()
	# Path('LICENSE.rst').unlink()
	# STATIC.joinpath('bootstrap.min.js').unlink()
	# STATIC.joinpath('bootstrap.min.css').unlink()
# def clean_env():
	# """Delete existing env/ directory."""
	# if ENV.exists():
		# shutil.rmtree(ENV)


def test():
	# test_doctests()
	# test_pytest()
	pass


def lint():
	"""Lint all checkeable files."""

	lint_javascript()
	lint_python()
	# lint_css()
	# lint_images()
	# lint_files()
	# lint_setup()
	# lint_ini()
	# lint_git()
	lint_rst()
	lint_html()


def lint_javascript():
	"""Lint all javascript files."""
	lint_jscs()
	# lint_jshint()


def lint_html():
	# https://github.com/deezer/html-linter
	# http://www.html-tidy.org
	pass


def lint_images():
	# lint_jpeg()
	# lint_gif()
	# lint_png()
	pass


def lint_jscs():
	"""Run jscs (http://jscs.info) over all javascript.

	Run "jscs <file>" over all .js files."""

	pass


def lint_rst():
	"""Check all reStructuredText files for errors."""

	# https://github.com/twolfson/restructuredtext-lint
	# pandoc
	# rst2html5.py
	pass


def lint_python():
	"""Lint all python files for automatically detectable errors."""

	lint_pylint()
	lint_pcodestyle()
	lint_pydocstyle()
	# vale prose
	# the other prose checker


def lint_pylint():
	pass


def lint_pycodestyle():
	pass


def lint_pydocstyle():
	pass


def thirdparty():
	"""Recreate the thirdparty directory and scatter files into our static/ directory."""

	thirdparty_clean()
	thirdparty_download()
	thirdparty_unpack()


def thirdparty_clean():
	"""Remove existing thirdparty directory and created files."""

	# if THIRDPARTY.exists():
		# shutil.rmtree(THIRDPARTY)
	for f in (STATIC.joinpath('bootstrap.min.css'),
			  STATIC.joinpath('bootstrap.min.js')):
		if f.exists():
			print('unlink {f}'.format(f=f))
			f.unlink()


def thirdparty_download():
	"""Grab source packages for the files we need from other projects."""

	if not THIRDPARTY.exists():
		THIRDPARTY.mkdir()

	# with lcd(THIRDPARTY):
	os.chdir(THIRDPARTY)

	# local('wget https://github.com/h5bp/html5-boilerplate/releases/download/5.3.0/html5-boilerplate_v5.3.0.zip')
	bootstrap_file = pathlib.Path('bootstrap-{v}-dist.zip'.format(v=BOOTSTRAP_VERSION))
	if not bootstrap_file.exists():
		local('wget https://github.com/twbs/bootstrap/releases/download/v{v}/{f}'.format(
			v=BOOTSTRAP_VERSION, f=bootstrap_file))

	else:
		print('{f} exists'.format(f=bootstrap_file))

	gpl_file = pathlib.Path('gpl.md')
	if not gpl_file.exists():
		local('wget https://www.gnu.org/licenses/gpl.md')

	else:
		print('{f} exists'.format(f=gpl_file))

	# normalise
	os.chdir('..')


def _copy(src, dest):
	print('Copy {src} to {dest}'.format(src=src, dest=dest))
	shutil.copy(src, dest)


def thirdparty_unpack():
	"""Take files from the 3rdparty/ directory and transfer the bits we need to static/.

	These files are checked into source code management, to ensure the repo is self contained.
	3rd party licenses must allow this.
	"""

	os.chdir(THIRDPARTY)
	local('unzip -u bootstrap-{v}-dist.zip'.format(v=BOOTSTRAP_VERSION))
	os.chdir('..')
	_copy(THIRDPARTY.joinpath('css', 'bootstrap.min.css'), STATIC)
	_copy(THIRDPARTY.joinpath('js', 'bootstrap.min.js'), STATIC)
	local('pandoc --from=markdown --to=rst --output=LICENSE.rst thirdparty/gpl.md')


def doc():
	"""Generate html and pdf versions of RST documents."""
	doc_readme()
	doc_docs()


def doc_docs():
	"""Generate sphinx documents from docs/ directory."""

	local('sphinx-build -b html docs html')


def doc_readme():
	"""Create (and test format) README.html from README.rst."""

	local('pandoc -r rst -w html -o README.html README.rst')

def activate():
	"""Create an `activate` file that can be sourced to set up the project ready to run."""

	ACTIVATE.open('w').write("""#!/bin/bash

# Set up environment variables for project development

PROJ={HERE}
. $PROJ/env/bin/activate
export PATH=$PROJ/bin:$PATH
export PYTHONPATH=$PROJ/shareclip:$PYTHONPATH
""".format(HERE=HERE.absolute()))
	print('Wrote {a}'.format(a=ACTIVATE))
