
class Item(object):
	def __init__(self, id, maxbid):
		self.id = id
		self.maxbid = maxbid
		self.info = None
		self.last_update = None
		self.ignore = False

