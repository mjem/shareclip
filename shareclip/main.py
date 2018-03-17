#!/usr/bin/env python3

"""Web shared clipboard server command line interface."""

import logging
import argparse

from shareclip import server
from shareclip import config
from shareclip import log
from shareclip.statefile import Statefile
from shareclip import demobilise

logger = logging.getLogger('main')


def read_config_file(config_file):
	"""Process a .conf configuration file and override config settings."""
	pass


def main():
	"""Command line entry point."""
	parser = argparse.ArgumentParser(add_help=False,
									 epilog=None,
									 usage='%(prog)s [options]',
									 description=None)
	# parser.add_argument('--config', '-c',
	# default=config.config_file,
	# help='Specify config file')
	# config_args, remainder = parser.parse_known_args()
	# Read configuration file from config_args.config and poke values back into config module

	# web server options
	parser.add_argument('--serve', '-s',
						action='store_true',
						help='Run web server')
	parser.add_argument('--port', '-p',
						type=int,
						default=config.PORT,
						help='Server listen port')
	parser.add_argument('--prefix',
						default=config.PREFIX,
						help='URL prefix')
	parser.add_argument('--statefile',
						default=config.STATEFILE,
						help='Chose alternative statefile location')
	parser.add_argument('--title',
						help='Web page title text',
						default=config.TITLE)
	parser.add_argument('--hide-nickname', '--hide-nicknames',
						action='store_true',
						help='Hide the web tool nicknames')
	parser.add_argument('--log',
						help='Location of log file')
	parser.add_argument('--rotating-log',
						help='Root name of daily rotating log files')
	# command line utility tool
	parser.add_argument('--clear-statefile',
						action='store_true',
						help='Clear (delete) existing statefile')
	parser.add_argument('--show-messages', '--show',
						action='store_true',
						help='Show existing messages from statefile')
	parser.add_argument('--show-undo',
						action='store_true',
						help='Show undo queue')
	parser.add_argument('--demobilise',
						action='store_true',
						help='Convert mobile friendly links to desktop friendly links')
	# meta options
	parser.add_argument('--debug',
						action='store_true',
						default=config.DEBUG,
						help='Switch on additional debug messages to logfile and server results')
	parser.add_argument('--version',
						action='store_true',
						help='Show software version')
	parser.add_argument('--help', '-h',
						action='store_true',
						help='Show this help message and exit')

	# --copy 'Copy item to clipboard'
	# --paste 'Paste clipboard content to share'
	# --open

	args = parser.parse_args()
	# args = parser.parse_args(remainder)

	log.init_log()

	if args.help:
		parser.print_help()
		parser.exit()

	if args.version:
		print(config.VERSION)
		parser.exit()

	statefile = Statefile(args.statefile)

	done_something = False

	if args.clear_statefile:
		statefile.delete()
		done_something = True

	if args.show_messages:
		statefile.show_messages()
		parser.exit()

	if args.show_undo:
		statefile.show_undo()
		parser.exit()

	if args.demobilise:
		demobilise.process_statefile(statefile)
		parser.exit()

	config.TITLE = args.title

	if args.hide_nickname:
		config.NICKNAMES = False

	if args.serve:
		server.serve(port=args.port,
					 prefix=args.prefix,
					 statefile=statefile,
					 debug=args.debug)
		parser.exit()

	if not done_something:
		parser.error('No actions specified')

if __name__ == '__main__':
	main()
