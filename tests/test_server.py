#!/usr/bin/env python3

import os
import logging
import argparse
import subprocess
import shlex
import urllib.request
import atexit
import time
import select

from selenium import webdriver

from shareclip import config
from shareclip import log

logger = logging.getLogger()

sub = None


def stop_server():
	"""Halt the asynchronous server subprocess."""
	global sub
	if sub is not None:
		sub.kill()

	sub = None


def shell(command, wait=True, stdout=True, env=None):
	"""Run a command in a subshell.

	Args:
		`command` (str): Command to execute
		`wait` (bool): If true, don't return until command completes, and return exitcode.
			If false, leave running and return Popen object
		`stdout` (bool): Capture standard output

	Return:
		Exitcode or Popen object

	"""
	global sub

	logger.info('Running command {cmd}'.format(cmd=command))
	args = shlex.split(command)
	if env is not None:
		full_env = os.environ.copy()
		full_env.update(env)

	else:
		full_env = None

	proc = subprocess.Popen(args,
							env=full_env,
							stdout=subprocess.PIPE if stdout else None,
							stderr=subprocess.PIPE if stdout else None)
	sub = proc

	if wait:
		ret = proc.wait()
		return ret

	else:
		return proc


def run_server(port):
	logger.info('Running server')
	atexit.register(stop_server)
	sub = shell('shareclip --serve --port {p}'.format(p=port),
				wait=False,
				# env={'XDG_DATA_HOME': 'tmp'},
				)
	po = select.poll()
	po.register(sub.stdout, select.POLLIN)
	po.register(sub.stderr, select.POLLIN)
	import os
	while True:
		# out, err = sub.communicate(timeout=0)
		pings = po.poll(1)
		for ping in pings:
			# print(ping[0].readline())
			buff = os.read(ping[0], 1000).decode().strip()
			logging.info('Subprocess: {lin}'.format(lin=buff))
			if 'Using selector' in buff:
				return
		# print('out ' + str(sub.stdout.read()) + ' err ' + str(sub.stderr.read()))
		# time.sleep(1)
	# wait until stdout includes "Running on"
	logger.info('Server up')


def get(url, expected_response=200):
	logging.info('Get {url}'.format(url=url))
	try:
		res = urllib.request.urlopen(url)
		logging.info('Got HTTP code {code}'.format(code=res.code))
		ret = res.read()
		return ret

	except urllib.error.HTTPError as e:
		if e.code != expected_response:
			raise

		else:
			logging.info('Got HTTP exception {code} {msg} as expected'.format(
				code=e.code, msg=e.msg))


def get_urls(server):
	"""Retrieve URLs."""
	get(server + '/')
	get(server + '/notfound', expected_response=404)


def get_browser(server):
	"""Start up the browser and wait for initialisation and first response.

	We don't even see a blank messages table until the websocket has been started
	and first response received."""
	browser = webdriver.Firefox()
	browser.set_window_size(900, 700)
	browser.get(server)
	logger.info('Title is {t}'.format(t=browser.title))
	while True:
		page_state = browser.execute_script('return document.readyState;')
		# slot table is drawn on websocket onopen handler
		slot_table = browser.find_element_by_id('slot-table')
		logging.debug('page state ' + str(page_state) + ' slot table {st}'.format(st=slot_table))
		time.sleep(1)
		if slot_table is not None:
			break

	return browser


def screenshots(browser):
	"""Simulate a brief usage session, recording screenshots"""
	browser.get_screenshot_as_file('01 - startup.png')
	post = browser.find_element_by_id('new-message')
	post.send_keys('Hello I am message')
	nick = browser.find_element_by_id('nickname')
	nick.send_keys('benji')
	browser.get_screenshot_as_file('02 - prepost.png')
	browser.find_element_by_id('post').click()
	browser.get_screenshot_as_file('03 - firstpost.png')


def test_startup():
	"""Just start up and stop a local server"""
	run_server(config.PORT)
	stop_server()


def test_basic():
	"""Start local server and retrieve URLs."""
	run_server(config.PORT)
	get_urls('http://localhost:{port}'.format(port=config.PORT))


def test_browser():
	"""Start local server and open main page."""
	run_server(config.PORT)
	browser = get_browser('http://localhost:{port}'.format(port=config.PORT))
	browser.quit()
	stop_server()


def test_screenshots():
	"""Clear state file, start local server, browse, post some messages, take screenshots."""
	run_server(config.PORT)
	browser = get_browser('http://localhost:{port}'.format(port=config.PORT))
	screenshots(browser)
	browser.quit()
	stop_server()


def main():
	parser = argparse.ArgumentParser()
	# parser.add_argument('--local', '-l',
						# action='store_true',
						# help='Run local webserver before testing it')
	parser.add_argument('--port', '-p',
						type=int,
						default=config.PORT,
						help='Port to use for local server')
	parser.add_argument('--server',
						# default='http://localhost:{p}'.format(p=config.PORT),
						help='Test against already running server, otherwise start local one')
	parser.add_argument('--startup',
						action='store_true',
						help='Just check server starts up')
	parser.add_argument('--basic',
						action='store_true',
						help='Default action. Test retrieve of some basic URLs')
	parser.add_argument('--browser',
						action='store_true',
						help='Test with synthetic browser')
	parser.add_argument('--screenshots',
						action='store_true',
						help='Make screenshots')
	args = parser.parse_args()

	log.init_log()

	if args.startup:
		run_server(args.port)
		stop_server()
		logging.info('All done')
		parser.exit()

	if args.server is None:
		run_server(args.port)
		args.server = 'http://localhost:{port}'.format(port=args.port)

	if args.browser:
		browser = get_browser(args.server)
		browser.quit()
		parser.exit()

	if args.screenshots:
		browser = get_browser(args.server)
		screenshots(browser)
		browser.quit()
		parser.exit()

	get_urls(args.server)

if __name__ == '__main__':
	main()
