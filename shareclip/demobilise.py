#!/usr/bin/env python3

import logging
from pathlib import Path

logger = logging.getLogger()

BACKUP_SUFFIX = '.bak'

replacements = (
	('mobile.twitter.com', 'www.twitter.com'),
	('en.m.wikipedia.com', 'en.wikipedia.com'),
	)

def process_statefile(statefile):
	statefile.save(suffix=BACKUP_SUFFIX)
	changes = 0
	for slot in statefile.slots:
		changed = False
		for orig, repl in replacements:
			if orig in slot['text']:
				slot['text'] = slot['text'].replace(orig, repl)
				changed = True

			if slot['clipboard'] is not None and orig in slot['clipboard']:
				slot['clipboard'] = slot['clipboard'].replace(orig, repl)
				changed = True

		if changed:
			changes += 1

	logger.info('Changed {cc} slots'.format(cc=changes))

	if changes > 0:
		statefile.save()

