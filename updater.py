import threading
import time
from dateutil.tz import tzlocal
from datetime import datetime, timedelta
from config import Config

class ItemUpdater:
	def __init__(self, cli):
		self.cli = cli

	def updateItem(self, item):
		item.info = self.cli.getItemInfo(item.id)
		item.last_update = datetime.now(tzlocal())
		self.rescheduleItem(item)

	def rescheduleItem(self, item):
		delta = item.info['timedelta']

		if delta < timedelta():
			return
		elif(delta > timedelta(2, 0, 0)):
			interval = 86400
		elif(delta > timedelta(1, 0, 0)):
			interval = 3600
		elif(delta > timedelta(0, 3600, 0)):
			interval = 600
		elif(delta > timedelta(0, 600, 0)):
			interval = 300
		elif(delta < timedelta(0, 600, 0) and delta > timedelta(0, 300, 0)):
			interval = 60
		else:
			interval = 30

		print "set interval %d for delta %s" % (interval, delta)
		timer = threading.Timer(interval, self.updateItem, [item])
		timer.start()

	def start(self):
		for item in Config.items.values():
			self.updateItem(item)


