#!/usr/bin/env python3

import os
import shutil
from pathlib import Path

from fabric.api import local

HERE = Path('.')
ENV = Path('env')
THIRDPARTY = Path('thirdparty')
STATIC = Path('shareclip', 'static')
ACTIVATE = Path('activate')
DOCS = Path('docs')

BOOTSTRAP_VERSION = '4.0.0-beta'
RMODAL_JS_VERSION = '1.0.26'
ANIMATE_CSS_VERSION = '3.5.2'

THIRDPARTY_FILES = (
	{
		'url': 'https://github.com/twbs/bootstrap/releases/download/v{v}/bootstrap-{v}-dist.zip'.format(
			v=BOOTSTRAP_VERSION),
	},
	{
		'url': 'https://github.com/zewish/rmodal.js/archive/{v}.tar.gz'.format(v=RMODAL_JS_VERSION),
		'file': 'rmodal.js-{v}.tar.gz'.format(v=RMODAL_JS_VERSION),
	},
	{
		'url': 'https://github.com/daneden/animate.css/archive/{v}.tar.gz'.format(v=ANIMATE_CSS_VERSION),
		'file': 'animate.css-{v}.tar.gz'.format(v=ANIMATE_CSS_VERSION),
	},
	{
		'url': 'https://www.gnu.org/licenses/gpl.md',
	},
)

def dist():
	"""Create a distributable archive file."""
	local('python setup.py sdist')


def test():
	test_doctests()
	test_pytest()


def test_doctests():
	"""Search for and run all docstring doctests."""
	local('python -m doctest `find shareclip -name \'*.py\'` -v')


def test_pytest():
	local('mkdir -p test_tmp')
	os.chdir('test_tmp')
	local('pytest ../tests/test_server.py')


def lint():
	"""Lint all checkeable files."""
	lint_python()
	lint_javascript()
	lint_rst()
	lint_html()
	# lint_images()
	# lint_prose()
	# lint_files()


def lint_javascript():
	"""Lint all javascript files."""
	lint_javascript_eslint()
	lint_javascript_jshint()


def lint_javascript_jscs():
	"""Run jshint via pip-based wrapper"""
	local('jshint_scanner.py shareclip/static/index.js')


def lint_javascript_eslint():
	"""Run eslint tool (merged from jscs)."""
	local('eslint shareclip/static/index.js')


def lint_html():
	# http://www.html-tidy.org
	lint_html_tidy()
	lint_html_html_lint()


def lint_html_tidy():
	"""Run tidy from http://tidy.sourceforge.net or http://www.html-tidy.org"""
	local('tidy shareclip/templates/*.html')


def lint_html_html_lint():
	"""Run html_lint.py tool from https://github.com/sk-/html-linter"""
	# or deezer
	local('html_lint.py --disable=tabs shareclip/templates/index.html')


# def lint_images():
	# lint_jpeg()
	# lint_gif()
	# lint_png()
	# pass


def lint_rst():
	"""Check all reStructuredText files for errors."""
	# https://github.com/twolfson/restructuredtext-lint

	# doesn't give much useful info
	local('restructuredtext-lint README.rst')

	# just to report problems
	local('pandoc README.rst -o README.html')

	# just to report problems
	local('rst2html5.py README.rst README.html')


def lint_python():
	"""Lint all python files for automatically detectable errors."""
	lint_python_pylint()
	lint_python_pycodestyle()
	lint_python_pydocstyle()
	# vale or other prose checker over comments


def lint_python_pylint():
	"""Run pylint over all python source files."""
	local('pylint shareclip')


def lint_python_pycodestyle():
	"""Run pycodestyle (ex pep8) over all python source files."""
	local('pycodestyle shareclip')


def lint_python_pydocstyle():
	"""Run pydocstyle (ex pep257) over all python source files."""
	local('pydocstyle shareclip')


def lint_files():
	"""Run generic filesystem linters."""
	lint_files_rmlint()
	# lint_files_fslint()


def lint_files_rmlint():
	"""Run rmlint filesystem checker over all files."""
	local('rmlint shareclip')


def lint_prose():
	"""Run spell- and grammar-checkers over the documentation and code comments."""
	lint_prose_vale()
	lint_prose_languagetool()
	lint_prose_proselint()


def lint_prose_vale():
	"""Run vale prose lint tool from https://valelint.github.io."""
	# supposed to have support for source code checking, do .py and .js too?
	local('vale README.rst')


def lint_prose_languagetool():
	"""Run languagetool from https://languagetool.org."""
	# no built in support for rst or source code handling
	local('languagetool README.rst')


def lint_prose_proselint():
	"""Run proselint tool from http://proselint.com."""
	# Does not appear to give useful results
	local('languagetool README.rst shareclip')


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
	# os.chdir(THIRDPARTY)

	for d in downloads:
		if 'file' in d:
			filename = Path(d['file'])

		else:
			filename = Path(d['url']).name

		fullname = THIRDPARTY.joinpath(filename)

		print('download {d} package {p} exists {e}'.format(d=d['url'], p=fullname, e=fullname.exists()))
		if not fullname.exists():
			local('wget {d} -O {p}'.format(d=d['url'], p=fullname))


	# local('wget https://github.com/h5bp/html5-boilerplate/releases/download/5.3.0/html5-boilerplate_v5.3.0.zip')
	# bootstrap_file = Path('bootstrap-{v}-dist.zip'.format(v=BOOTSTRAP_VERSION))
	# if not bootstrap_file.exists():
		# local('wget https://github.com/twbs/bootstrap/releases/download/v{v}/{f}'.format(
			# v=BOOTSTRAP_VERSION, f=bootstrap_file))

	# else:
		# print('{f} exists'.format(f=bootstrap_file))

	# gpl_file = pathlib.Path('gpl.md')
	# if not gpl_file.exists():
		# local('wget https://www.gnu.org/licenses/gpl.md')

	# else:
		# print('{f} exists'.format(f=gpl_file))

	# normalise
	# os.chdir('..')


def _copy(src, dest):
	print('Copy {src} to {dest}'.format(src=src, dest=dest))
	shutil.copy(src, dest)


def thirdparty_unpack():
	"""Take files from the 3rdparty/ directory and transfer the bits we need to static/.

	These files are checked into source code management, to ensure the repo is self contained.
	3rd party licenses must allow this."""

	# unzip bootstrap, copy css
	# copy animate.css
	# convert gpl, copy
	# unzip rmodal, copy css and js

	os.chdir(THIRDPARTY)
	local('unzip -u bootstrap-{v}-dist.zip'.format(v=BOOTSTRAP_VERSION))
	local('tar xf rmodal.js-{v}.tar.gz'.format(v=RMODAL_JS_VERSION))
	os.chdir('..')

	_copy(THIRDPARTY.joinpath('css', 'bootstrap.min.css'), STATIC)

	_copy(THIRDPARTY.joinpath('rmodal.js-{v}'.format(v=RMODAL_JS_VERSION),
							  'dist',
							  'rmodal.min.js'),
		  STATIC)
	_copy(THIRDPARTY.joinpath('rmodal.js-{v}'.format(v=RMODAL_JS_VERSION),
							  'dist',
							  'rmodal.css'),
		  STATIC)
	local('pandoc --from=markdown --to=rst --output=LICENSE.rst {thirdparty}/gpl.md'.format(
		thirdparty=THIRDPARTY))


def doc():
	"""Generate html and pdf versions of RST documents."""
	doc_screenshots()
	doc_thumbnails()
	doc_readme()
	doc_sphinx()


def doc_screenshots():
	"""Use autotests to create screenshots for readme and sphinx docs."""
	pass


def doc_thumbnails():
	"""Process full sized screenshots to thumbnails."""
	os.chdir(DOCS)
	local('convert main.png -resize 500 main-sm.png')


def doc_sphinx():
	"""Generate sphinx documents from docs/ directory."""
	local('sphinx-build -b html docs html')


def doc_readme():
	"""Create (and test format) README.html from README.rst."""
	# local('pandoc -r rst -w html -o README.html README.rst')
	local('rst2html5.py README.rst README.html')

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
