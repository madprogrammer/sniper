import threading
import operator, os, sys
import cherrypy
import template
from config import Config
from model import Item
from updater import ItemUpdater
from form import ItemForm
from formencode import Invalid
from genshi.input import HTML
from genshi.filters import HTMLFormFiller, HTMLSanitizer
from ebay import ItemNotFoundException

class Root(object):
	def __init__(self, updater):
		self.updater = updater

	@cherrypy.expose
	@template.output("index.html")
	def index(self):
		return template.render(items=Config.items.values())

	@cherrypy.expose
	def delete(self, id=None, *args, **kw):
		id = int(id)
		if id in Config.items:
			del Config.items[id]
		raise cherrypy.HTTPRedirect('/')

	@cherrypy.expose
	@template.output('submit.html')
	def submit(self, cancel=False, **data):
		if cherrypy.request.method == 'POST':
			if cancel:
				raise cherrypy.HTTPRedirect('/')
			form = ItemForm()
			try:
				data = form.to_python(data)
				item = Item(**data)
				self.updater.updateItem(item)
				Config.items[item.id] = item
				raise cherrypy.HTTPRedirect('/')
			except Invalid, e:
				errors = e.unpack_errors()
			except ItemNotFoundException, e:
				errors = { "id" : e }
		else:
			errors = {}

		return template.render(errors=errors) | HTMLFormFiller(data=data)

class WebServer(threading.Thread):
	def __init__(self, cli, updater):
		threading.Thread.__init__(self)
		self.cli = cli
		self.updater = updater

	def stop(self):
		cherrypy.engine.exit()

	def subscribe(self, callback):
		if hasattr(cherrypy.engine, 'subscribe'):
			cherrypy.engine.subscribe('stop', callback)
		else:
			cherrypy.engine.on_stop_engine_list.append(callback)

	def run(self):
		cherrypy.config.update({ 'global': {
			'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
			'log.screen': False,
			'engine.SIGHUP': None,
			'engine.SIGTERM': None
			}
		})
		cherrypy.quickstart(Root(self.updater), '/', "cherrypy.conf")


