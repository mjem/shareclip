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
version = '0.1'

# Standard TCP port for server to listen on or client to connect to
port = 8080

# Web server URL prefix for all addresses
prefix = ''

# Installed directory where we find templates/ and static/
project_root = Path(__file__).parent

# Static files for web server
static_root = project_root.joinpath('static')

# Root of config directorys
# config_file = Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')).expanduser().
# joinpath('shareclip', 'config')

# Where to store our statefile and log and pid
data_dir = Path(os.environ.get('XDG_DATA_HOME', '~/.local/share')).expanduser().joinpath('shareclip')

# Name of statefile used to store slot contents between invocations of the server
statefile = data_dir.joinpath('state')

# Number of undo slot to retain
undo_queue_length = 100

# Filename for log file or None for terminal
log_file = None  # data_dir.joinpath('log')

# Base name for daily rotating log files
rotating_log_file = None

# Switch on extra developer info in web interface and console log
debug = False

# Log at info level
#  Server start - time
#  Server stop - time
#  Person enters - time and IP
#  Person leaves - time and IP
#  Message added - time, text, uid, label
#  Message deleted - time, uid
