from objects.common import config

"""Objects used in buyer.py to do the buying process."""

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


