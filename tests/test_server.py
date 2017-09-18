#!/usr/bin/env python3

import logging
import argparse
import subprocess
import shlex
import urllib.request
import atexit
import time

from selenium import webdriver

from shareclip import config
from shareclip import log

logger = logging.getLogger()

sub = None


def stop_server():
	global sub
	if sub is not None:
		sub.kill()

	sub = None


def shell(command, wait=True, stdout=True):
	global sub

	logger.info('Running command {cmd}'.format(cmd=command))
	args = shlex.split(command)
	proc = subprocess.Popen(args,
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
	sub = shell('shareclip --serve --port {p}'.format(p=port), wait=False)
	import select
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
	browser = webdriver.Firefox()
	browser.get(server)
	logger.info('title is {t}'.format(t=browser.title))
	time.sleep(10)
	browser.quit()


def test_startup():
	"""Just start up and stop a local server"""
	run_server(config.PORT)
	stop_server()


def test_basic():
	"""Start local server and retrieve URLs."""
	run_server(config.PORT)
	get_urls('http://localhost:{port}'.format(port=port))


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
	args = parser.parse_args()

	log.init_log()

	if args.startup:
		test_startup(args.port)
		logging.info('All done')
		parser.exit()

	if args.server is None:
		run_server(args.port)
		args.server = 'http://localhost:{port}'.format(port=args.port)

	if args.browser:
		get_browser(args.server)
		parser.exit()

	get_urls(args.server)

if __name__ == '__main__':
	main()
