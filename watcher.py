import threading
import time
from dateutil.tz import tzlocal
from datetime import datetime, timedelta
from config import Config
from ebay import EBayClient

class ItemWatcher(threading.Thread):
	def __init__(self, cli):
		threading.Thread.__init__(self)
		self.cli = EBayClient()
		self.logged_in = False

	def timeLeft(self, item):
		if item.info == None:
			return None
		return item.info['endtime'] - datetime.now(tzlocal())

	def watchItem(self, item):
		if item.info == None:
			return

		time_left = self.timeLeft(item)
		if (time_left == timedelta()):
			return
		
		if time_left < timedelta(0, Config.bidtime, 0) and not item.ignore:
			try:
				if item.maxbid >= item.info['minbid']:
					print "Sniping item %d (our bid %d)" % (item.id, item.maxbid)
					self.cli.bid(item.id, item.maxbid)
					print "Successful bid at %s! Hope you win!" % (self.timeLeft(item))
				else:
					print "Skipping item %d as our max bid is lower than current minimum" % (item.maxbid)
			except Exception, e:
				print "BID FAILED: %s" % e
			finally:
				self.logged_in = False
				item.ignore = True

		elif time_left < timedelta(0, 300, 0) and not self.logged_in:
			try:
				print "Logging in to eBay as %s..." % Config.username
				self.cli.login(Config.username, Config.password)
				self.logged_in = True
			except Exception, e:
				print "FATAL: Login failed: %s" % e


	def run(self):
		while True:
			time.sleep(1)
			for item in Config.items.values():
				self.watchItem(item)



