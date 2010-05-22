#!/usr/bin/env python

import signal, sys, os, traceback, pickle
from ebay import EBayClient
from web  import WebServer
from updater import ItemUpdater
from watcher import ItemWatcher
from config import Config

cli = EBayClient()
itemUpdater = ItemUpdater(cli)
itemWatcher = ItemWatcher(cli)
webServer = WebServer(cli, itemUpdater)

def signalHandler(signum, frame):
	if (signum == signal.SIGINT):
		print 'Caught SIGINT, shutting down...'
		exit(1)

def exit(code):
	webServer.stop()
	sys.exit(code)

def main(filename):
	signal.signal(signal.SIGINT, signalHandler)

	if os.path.exists(filename):
		fileObj = open(filename, "rb")
		try:
			Config.items = pickle.load(fileObj)
		finally:
			fileObj.close()
	else:
		Config.items = { }

	def _saveData():
		fileObj = open(filename, "wb")
		try:
			pickle.dump(Config.items, fileObj)
		finally:
			fileObj.close()
	
	try:
		webServer.subscribe(_saveData)
		webServer.start()
		itemUpdater.start()
		itemWatcher.start()

		raw_input("Press Ctrl+C key to exit\n")
		print "Shutting down..."
		exit(0)
	except Exception, e:
		print "Caught error: %s" % e
		traceback.print_exc(file=sys.stdout)
		exit(2)

if __name__ == "__main__":
	main("snipe.db")
