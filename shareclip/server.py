#!/usr/bin/env python3

"""HTTP webserver."""

import atexit
import uuid
import datetime
import binascii
import logging

from aiohttp import web
from aiohttp import WSMsgType
import aiohttp_jinja2
import jinja2

try:
	import aiohttp_debugtoolbar
except ImportError:
	aiohttp_debugtoolbar = None

from shareclip import config

logger = logging.getLogger('server')

# See https://pastebin.com/xDSACmdV for a template for writing server as a class

# class WebSocket():
# web.json_response
# pass


def datetime_to_iso8601(dt):
	"""Encode a datetime in text form.

	>>> datetime_to_iso8601(datetime.datetime(2017, 6, 1, 10, 9, 8))
	'2017-06-01T10:09:08'
	"""

	return dt.isoformat()


def shutdown(app):
	"""Handler called during graceful shutdown sequence."""

	app['statefile'].save()


@aiohttp_jinja2.template('index.html')
async def render_index(request):
	"""Return main webpage."""

	app = request.app

	return {'ws_url': app.router['ws'].url_for(),
			'all_url': app.router['all'].url_for(),
			'info_url': app.router['info'].url_for(),
			'undo_url': app.router['undo'].url_for(),
			'title': config.TITLE,
			'nicknames': config.NICKNAMES,
	}


@aiohttp_jinja2.template('all.html')
async def render_all(request):
	"""Return "Open all as page" page."""

	app = request.app
	return {'slots': app['statefile'].slots}


@aiohttp_jinja2.template('info.html')
async def render_info(request):
	"""Return server Info page."""

	app = request.app
	logger.debug('render info clients ' + str(app['clients']))
	return {
		'homepage': config.HOMEPAGE,
		'version': config.VERSION,
		'clients': app['hosts'].values(),
		'messages': len(app['statefile'].slots),
		'undos': len(app['statefile'].undos),
	}


async def render_undo(request):
	"""A client requests undo delete."""

	undo_delete(request.app)
	return web.Response(text='')


def is_url(url):
	"""Test if `s` looks like a URL."""

	return url.startswith('http://') or url.startswith('https://')


def add_slot(app, nickname, text, host):
	"""Create a new slot in response to a client posting a new message."""

	if is_url(text):
		show_text = '<a href="{text}" target="_blank">{text}</a>'.format(text=text)
		clipboard = text

	else:
		show_text = text
		clipboard = None

	# prepare the new slot as a data structure ...
	new_slot = {'uid': binascii.hexlify(uuid.uuid4().bytes).decode(),
				'timestamp': datetime_to_iso8601(datetime.datetime.utcnow()),
				'nickname': nickname,
				'text': show_text,
				'clipboard': clipboard,
				'source': host}
	app['statefile'].slots.append(new_slot)

	# ... and message to send to all clients
	message = {'type': 'new_slot'}
	message.update(new_slot)
	broadcast(app, message)


def broadcast(app, message):
	"""Take a message structure and broadcast to all active clients."""

	logger.debug('Broadcasting message {m}'.format(m=message))
	for ws in app['clients']:
		logger.debug('    to {c}'.format(c=str(id(ws))))
		ws.send_json(message)


def welcome_client(app, ws):
	"""Welcome a new client by sending all current slots to them."""

	logger.debug('Welcoming {ws} with {s} initial messages'.format(
		ws=id(ws), s=len(app['statefile'].slots)))
	for s in app['statefile'].slots:
		message = {'type': 'new_slot'}
		message.update(s)
		ws.send_json(message)


def delete_slot(app, uid):
	"""Respond to a client request to delete a slot.

	Remove it from the internal list then broadcast the change to all clients,
	including the originator."""

	state = app['statefile']
	state.delete_slot(uid)
	broadcast(app,
			  {'type': 'delete_slot',
			   'uid': uid})


def undo_delete(app):
	"""Pop the last entry from app undos, add to current messages and inform clients."""

	state = app['statefile']

	if len(state.undos) > 0:
		logger.info('Undo')
		bless = state.undos.pop(0)
		state.slots.insert(0, bless)
		message = {'type': 'new_slot'}
		message.update(bless)
		broadcast(app, message)

	else:
		logger.info('No messages to undo')


async def websocket_handler(request):
	"""Client requests a WebSocket for 2-way updates."""

	app = request.app
	state = app['statefile']
	ws = web.WebSocketResponse()
	logger.info('New client {ip} requests a socket giving {ws}'.format(ip=request.host, ws=id(ws)))

	await ws.prepare(request)
	app['clients'].append(ws)
	logger.debug('clients length ' + str(len(app['clients'])))
	app['hosts'][ws] = request.host

	async for msg in ws:
		if msg.type == WSMsgType.TEXT:
			if msg.data == 'close':
				await ws.close()

			else:
				logger.info('Got the message {msg}'.format(msg=msg.data))
				msg_struct = msg.json()

				if msg_struct['type'] == 'helo':
					welcome_client(app, ws)

				elif msg_struct['type'] == 'post':
					add_slot(app=app,
							 nickname=msg_struct['nickname'],
							 text=msg_struct['message'],
							 host=request.host)

				elif msg_struct['type'] == 'delete':
					delete_slot(app, msg_struct['uid'])

				elif msg_struct['type'] == 'delete_all':
					for uid in list(s['uid'] for s in state.slots):
						delete_slot(app, uid)

				elif msg_struct['type'] == 'empty_undo':
					state.empty_undo()

				elif msg.type == WSMsgType.ERROR:
					logger.error('WebSocket closed: {exc}'.format(exc=ws.exception()))

				else:
					logger.error('Unkwown message {t}'.format(t=msg_struct['type']))

	logger.info('WebSocket {ws} closed'.format(ws=id(ws)))
	app['clients'].remove(ws)
	del app['hosts'][ws]
	return web.Response(text='')


def serve(port, prefix, statefile, debug=True):
	"""Run webserver.

	Args:
		`port` (int): TCP port to listen on
		`statefile` (Statefile): Persistent state of messages and undo queue
		`debug` (bool): Run web server in debug mode with more verbose error traces
	"""

	if debug:
		middlewares = [aiohttp_debugtoolbar.toolbar_middleware_factory]

	else:
		middlewares = None

	app = web.Application(middlewares=middlewares)

	if debug:
		aiohttp_debugtoolbar.setup(app)

	# initial post text
	app['value'] = 'initial'

	# current clients
	app['clients'] = []
	app['hosts'] = {}

	# persistent state
	app['statefile'] = statefile

	app.router.add_get(prefix + '', render_index)
	app.router.add_get(prefix + '/all', render_all, name='all')
	app.router.add_get(prefix + '/info', render_info, name='info')
	app.router.add_get(prefix + '/ws', websocket_handler, name='ws')
	app.router.add_get(prefix + '/undo', render_undo, name='undo')
	app.router.add_static(prefix + '/static',
						  config.STATIC_ROOT,
						  show_index=True,
						  follow_symlinks=True,
						  name='static')

	aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('shareclip', 'templates'))
	atexit.register(shutdown, app=app)
	logger.info('Starting server on port {p} prefix {pr}'.format(p=port, pr=prefix))
	web.run_app(app, port=port)
