#!/usr/bin/env python3

"""Command line shareclip client.

Will allow posting from args, post from clipboard, copy to clipboard,
delete, undo delete, shutdown, etc."""

import asyncio

import aiohttp
import async_timeout


async def fetch(session, url):
	"""Pull a single URL."""
	with async_timeout.timeout(10):
		async with session.get(url) as response:
			return await response.text()


async def main():
	"""Command line entry point."""
	async with aiohttp.ClientSession() as session:
		html = await fetch(session, 'http://localhost:8080')
		print(html)

	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
