from Signal import Signal

class Container:
	"""
	An abstract class of objects which contain Actors
	"""
	
	def __init__(self):
		self.actors = set()
	
	# TODO: rename to addActor
	def add(self, actor):
		self.actors.add(actor)
	
	# TODO: rename to removeActor
	def remove(self, actor):
		self.actors.remove(actor)

# vim: set ts=4 sts=4 sw=4 ai noet :
