from objects.common import config

class Card:
	def __init__(self, name, page):
		self.name = name 
		self.url = None
		self.html = None
		self.captched = False

class Page:
	def __init__(self, name):
		self.name = name
		self.buy_steps = config()[self.name]['buy_steps']

class Proxy:
	def __init__(self, address):
		self.address = address 
		self.captched = False


