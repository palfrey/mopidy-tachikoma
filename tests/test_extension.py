from __future__ import unicode_literals

import json
import logging
import mock

from test_helpers import \
	MockArtist, MockTrack, get_websocket, make_frontend, patched_bot
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


def test_setup():
	ext = Extension()

	class MockRegistry:
		def add(self, where, what):
			assert where == "frontend"
	ext.setup(MockRegistry())


class TestException(Exception):
	pass


def good_exit_while_loop(*args):
	raise TestException


def bad_exit_while_loop(*args):
	raise Exception("failure")


@patched_bot
def test_can_connect():
	with mock.patch("time.sleep") as mock_sleep:
		mock_sleep.side_effect = good_exit_while_loop
		frontend = make_frontend()
		try:
			frontend.doSlack()
			raise Exception("No TestException!")
		except TestException:
			pass


@patched_bot
def test_can_parse_events():
	with mock.patch("mopidy_tachikoma.bot.TachikomaFrontend.doSlackLoop") \
		as mock_loop:
		mock_loop.side_effect = good_exit_while_loop
		frontend = make_frontend()
		try:
			with mock.patch("time.sleep") as mock_sleep:
				mock_sleep.side_effect = bad_exit_while_loop
				with mock.patch("tests.test_helpers.WebSocketForTest.recv") as mock_post:
					mock_post.return_value = "{\"type\":\"foo\"}"
					frontend.doSlack()
			raise Exception("No TestException!")
		except TestException:
			pass


def test_on_connect_fail():
	with mock.patch("requests.post") as mock_post:
		mock_post.return_value = False
		try:
			make_frontend()
			raise Exception("No Exception!")
		except Exception, e:
			if e.message == "Bad Slack token?":
				pass
			else:
				raise


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
def test_gets_events_with_an_artist():
	frontend = make_frontend()
	track = MockTrack()
	track.artists = [MockArtist("Baz")]
	frontend.doSlackLoop(
		{}, track,
		[{"type": "message", "channel": "mock_channel"}])
	data = json.loads(get_websocket().data)
	assert {
		'channel': 'mock_channel',
		'text': 'Now playing *foo* by *Baz* from *bar*',
		'type': 'message'} == data


@patched_bot
def test_gets_events_with_multiple_artists():
	frontend = make_frontend()
	track = MockTrack()
	track.artists = [MockArtist("Baz"), MockArtist("Spam"), MockArtist("Eggs")]
	frontend.doSlackLoop(
		{}, track,
		[{"type": "message", "channel": "mock_channel"}])
	data = json.loads(get_websocket().data)
	assert {
		'channel': 'mock_channel',
		'text': 'Now playing *foo* by *Baz*, *Spam* and *Eggs* from *bar*',
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
def test_does_nothing_on_non_messages():
	frontend = make_frontend()
	song = MockTrack()
	get_websocket().data = None  # make sure it's cleared
	frontend.doSlackLoop(
		{}, song,
		[{"type": "something_else"}])
	assert get_websocket().data is None  # same song, no info


@patched_bot
def test_does_nothing_when_no_song():
	frontend = make_frontend()
	get_websocket().data = None  # make sure it's cleared
	frontend.doSlackLoop(
		{"mock_channel": MockTrack()}, None,
		[{"type": "message", "channel": "mock_channel"}])
	assert get_websocket().data is None  # no song, no info


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
