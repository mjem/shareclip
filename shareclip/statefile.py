#!/usr/bin/env python3

"""Implementation of Statefile class."""

import json
import logging
from collections import namedtuple

from shareclip import config

logger = logging.getLogger('statefile')

# not used.
# To use it we'd need a function to convert one of these to a json message
# Slot = namedtuple('Slot', 'uid timestamp text clipboard nickname source')

class Statefile():
	"""Handle the persistent state file."""

	# set a version identifier in our statefile so we can detect attempt to load an older version
	VERSION = 1

	def __init__(self, filename):
		self.filename = filename
		self.slots = None
		self.undos = None

		if self.filename.exists():
			self.load()

		else:
			self.init()

	def load(self):
		"""Load state from statefile."""

		elem = json.load(self.filename.open())

		if elem['version'] != Statefile.VERSION:
			logger.warning('Loading statefile from different version')

		self.slots = elem['slots']
		self.undos = elem['undos']

		logger.info('Loaded statefile {s} with {m} messages {u} undos'.format(
			s=self.filename, m=len(self.slots), u=len(self.undos)))

	def init(self):
		"""Create a blank state."""

		logger.info('Initialising new state')
		self.slots = []
		self.undos = []

	def save(self):
		"""Save ourselves to statefile."""

		json.dump({
			'version': Statefile.VERSION,
			'slots': self.slots,
			'undos': self.undos,
		},
				  self.filename.open('w'),
				  indent=2)
		logger.info('Saved state to {s}'.format(s=self.filename))

	def delete(self):
		"""Remove existing statefile."""

		if self.filename.exists():
			logger.info('Removing existing statefile {s}'.format(s=self.filename))
			self.filename.unlink()

		else:
			logger.info('Not removing statefile as no existing file found')

	def show_messages(self):
		"""List stored messages to terminal."""

		for m in self.slots:
			print(m)

	def show_undo(self):
		"""List undo queue to terminal."""

		for u in self.undos:
			print(u)

	def delete_slot(self, uid):
		"""Remove entry from normal queue and insert to undo queue."""

		for s in self.slots:
			if s['uid'] == uid:
				self.slots.remove(s)
				self.undos.insert(0, s)
				logging.info('Removed slot {uid} remaining {slots} undos {undos}'.format(
					uid=uid, slots=len(self.slots), undos=len(self.undos)))
				if len(self.undos) > config.undo_queue_length:
					self.undos = self.undos[:config.undo_queue_length]
					logging.info('Trimmed undo queue length to {max}'.format(
						max=config.undo_queue_length))

	def empty_undo(self):
		logging.info('Removing {u} undo slots'.format(u=len(self.undos)))
		self.undos = []

