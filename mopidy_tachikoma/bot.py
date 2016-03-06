from __future__ import unicode_literals

import logging
import thread
import time

from mopidy import core
import pykka
from slackclient import SlackClient

logger = logging.getLogger(__name__)


class TachikomaFrontend(pykka.ThreadingActor, core.CoreListener):
	def __init__(self, config, core):
		super(TachikomaFrontend, self).__init__()
		self.daemon = True
		self.slackToken = config['tachikoma']['slack_token'],
		self.core = core
		self.sc = SlackClient(self.slackToken)
		if not self.sc.rtm_connect():
			raise Exception("Bad Slack token?")
		thread.start_new_thread(self.doSlack, ())

	def doSlack(self):
		logger.info("Tachikoma is listening to Slack")
		logger.info(self.core.playback.get_current_track().get())
		last_track_told = None
		while True:
			last_track_told = self.doSlackLoop(last_track_told)
			time.sleep(1)

	def doSlackLoop(self, last_track_told):
		items = self.sc.rtm_read()
		if items != []:
			current_track = self.core.playback.get_current_track().get(3)
			for item in self.sc.rtm_read():
				if item[u"type"] != u"message":
					continue  # don't care
				logger.info(item)
				if current_track is None:
					logger.debug("No current track")
				elif last_track_told == current_track:
					logger.debug("Already told them about that track")
				else:
					logger.debug("New track!")
					artists = [x.name for x in current_track.artists]
					if len(artists) == 0:
						artists = None
					elif len(artists) == 1:
						artists = artists[0]
					else:
						artists = ", ".join(artists[:-1]) + " and " + artists[-1]
					msg = "Now playing *%s*" % current_track.name
					if artists is not None:
						msg += " by *%s*" % artists
					if current_track.album is not None and \
						current_track.album.name is not None and current_track.album.name != "":
						msg += " from *%s*" % current_track.album.name
					self.sc.rtm_send_message(item[u"channel"], msg)
					logger.debug("sent '%s' to channel with id %s" % (msg, item[u"channel"]))
					last_track_told = current_track
		return last_track_told

if __name__ == "__main__":
	config = {"tachikoma": {"slack_token": "sdfdsfdf"}}
	core = None
	TachikomaFrontend(config, core)
	while True:
		time.sleep(1)
