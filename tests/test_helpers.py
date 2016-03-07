from __future__ import unicode_literals

import zlib
from functools import wraps

import mock
import vcr
import websocket

from mopidy_tachikoma import bot


def decompress_response(response):
	if 'content-encoding' in response['headers'] \
		and response['headers']['content-encoding'] == ["gzip"]:
		body = zlib.decompress(response['body']['string'], 16 + zlib.MAX_WBITS)
		response['body']['string'] = body
		del response['headers']['content-encoding']
	return response


class WebSocketForTest(websocket.WebSocket):
	def __init__(self, *args, **kwargs):
		super(WebSocketForTest, self).__init__(*args, **kwargs)

		class MockSock:
			def setblocking(self, value):
				pass

			def send(self, data):
				self.data = data

		self.sock = MockSock()
		self._websocket = MockSock()
		self.connected = True
		self.data = None

	def send(self, payload, opcode=None):
		self.data = payload

	def recv(self):
		return ''

_websocket = None


def get_websocket():
	global _websocket
	return _websocket


def patched_bot(func):
	@wraps(func)
	def func_wrapper(*args, **kwargs):
		with vcr.use_cassette(
			"tests/slack_responses.yaml",
			record_mode='new_episodes',
			filter_post_data_parameters=['token'],
			before_record_response=decompress_response):
			global _websocket
			_websocket = WebSocketForTest()
			with mock.patch(
				"slackclient._server.create_connection",
				return_value=_websocket):
				func(*args, **kwargs)
	return func_wrapper


class MockArtist:
	def __init__(self, name):
		self.name = name


class MockTrack:
	artists = []
	name = "foo"

	class MockAlbum:
		name = "bar"
	album = MockAlbum


class MockCore:
	class MockPlayback:
		def get_current_track(self):
			class MockProxy:
				def get(self, timeout=None):
					return MockTrack()
			return MockProxy()
	playback = MockPlayback()


def make_frontend():
	config = {"tachikoma": {"slack_token": "junk-token"}}
	core = MockCore()
	return bot.TachikomaFrontend(config, core)
