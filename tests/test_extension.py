from __future__ import unicode_literals

import json
import zlib
from functools import wraps

import mock
import vcr
import websocket

from mopidy_tachikoma import Extension, bot


def test_get_default_config():
	ext = Extension()

	config = ext.get_default_config()

	assert '[tachikoma]' in config
	assert 'enabled = true' in config
	assert 'slack_token = ' in config


def test_get_config_schema():
	ext = Extension()
	schema = ext.get_config_schema()
	assert 'slack_token' in schema


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
		self.websocket = MockSock()
		self.connected = True

	def send(self, payload, opcode=None):
		self.data = payload

	def recv(self):
		return '{"type":"message","channel":"mock_channel"}'

websocket = None


def patched_bot(func):
	@wraps(func)
	def func_wrapper(*args, **kwargs):
		with vcr.use_cassette(
			"tests/slack_responses.yaml",
			record_mode='new_episodes',
			filter_post_data_parameters=['token'],
			before_record_response=decompress_response):
			global websocket
			websocket = WebSocketForTest()
			with mock.patch(
				"slackclient._server.create_connection",
				return_value=websocket) as mock_connection:
				print "calling with decorator", mock_connection
				func(*args, **kwargs)
	return func_wrapper


class MockCore:
	class MockPlayback:
		def get_current_track(self):
			class MockProxy:
				def get(self, timeout=None):
					class MockTrack:
						artists = []
						name = "foo"

						class MockAlbum:
							name = "bar"
						album = MockAlbum
					return MockTrack()
			return MockProxy()
	playback = MockPlayback()


def make_frontend():
	config = {"tachikoma": {"slack_token": "junk-token"}}
	core = MockCore()
	return bot.TachikomaFrontend(config, core)


@patched_bot
def test_can_connect():
	make_frontend()


@patched_bot
def test_gets_events():
	frontend = make_frontend()
	frontend.doSlackLoop(None)
	data = json.loads(websocket.data)
	assert {
		'channel': 'mock_channel',
		'text': 'Now playing *foo* from *bar*',
		'type': 'message'} == data
