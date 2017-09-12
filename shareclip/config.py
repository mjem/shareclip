#!/usr/bin/env python3

"""This file gives application defaults, with environment variables
XDG_CONFIG_HOME and XDG_DATA_HOME used to override some.

On startup the user option -c/--config is parsed first and may override the CONFIG_FILE
config option.

After this the config file is read as an .ini file and allows other options to be overridden.

Finally the remaining command line arguments allow most options to be overridden.
"""

# maybe change everything to lower case to match config file entries?

import os

from pathlib import Path

# Software release version
VERSION = '0.1'

# Software homepage
HOMEPAGE = 'http://github.com/mjem/shareclip'

# Standard TCP port for server to listen on or client to connect to
PORT = 8080

# Web server URL prefix for all addresses
PREFIX = ''

# Installed directory where we find templates/ and static/
PROJECT_ROOT = Path(__file__).parent

# Static files for web server
STATIC_ROOT = PROJECT_ROOT.joinpath('static')

# Root of config directorys
# config_file = Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')).expanduser().
# joinpath('shareclip', 'config')

# Where to store our statefile and log and pid
DATA_DIR = Path(os.environ.get(
	'XDG_DATA_HOME', '~/.local/share')).expanduser().joinpath('shareclip')

# Name of statefile used to store slot contents between invocations of the server
STATEFILE = DATA_DIR.joinpath('state')

# Number of undo slot to retain
UNDO_QUEUE_LENGTH = 100

# Filename for log file or None for terminal
LOG_FILE = None  # data_dir.joinpath('log')

# Base name for daily rotating log files
ROTATING_LOG_FILE = None

# Switch on extra developer info in web interface and console log
DEBUG = False

# Log at info level
#  Server start - time
#  Server stop - time
#  Person enters - time and IP
#  Person leaves - time and IP
#  Message added - time, text, uid, label
#  Message deleted - time, uid
