from __future__ import unicode_literals

import json
import logging
import mock

from test_helpers import MockTrack, get_websocket, make_frontend, patched_bot
from mopidy_tachikoma import Extension

logging.basicConfig(level=logging.DEBUG)


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


class TestException(Exception):
	pass


def exit_while_loop(*args):
	raise TestException


@patched_bot
def test_can_connect():
	with mock.patch("time.sleep") as mock_sleep:
		mock_sleep.side_effect = exit_while_loop
		frontend = make_frontend()
		try:
			frontend.doSlack()
			raise Exception("No TestException!")
		except TestException:
			pass


@patched_bot
def test_gets_events():
	frontend = make_frontend()
	frontend.doSlackLoop(
		{}, MockTrack(),
		[{"type": "message", "channel": "mock_channel"}])
	data = json.loads(get_websocket().data)
	assert {
		'channel': 'mock_channel',
		'text': 'Now playing *foo* from *bar*',
		'type': 'message'} == data


@patched_bot
def test_says_one_thing_per_channel():
	frontend = make_frontend()
	song = MockTrack()
	get_websocket().data = None  # make sure it's cleared
	frontend.doSlackLoop(
		{"mock_channel": song}, song,
		[{"type": "message", "channel": "mock_channel"}])
	assert get_websocket().data is None  # same song, no info


@patched_bot
def test_says_things_per_channel():
	frontend = make_frontend()
	song = MockTrack()
	get_websocket().data = "{}"  # make sure it's cleared
	frontend.doSlackLoop(
		{"mock_channel": song}, song,
		[{"type": "message", "channel": "mock_second_channel"}])
	data = json.loads(get_websocket().data)
	assert {
		'channel': 'mock_second_channel',
		'text': 'Now playing *foo* from *bar*',
		'type': 'message'} == data
