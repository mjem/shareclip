#!/usr/bin/env python3

import logging

def init_log():
	logging.basicConfig(level=logging.DEBUG,
						handlers=[logging.StreamHandler()])
