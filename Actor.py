class Actor:
	"""
	A class for objects that behave on their own
	"""
	def __init__(self, parent):
		"""
		parent: the Container this Actor belongs to
		"""
		self.parent = parent
		parent.add(self)
	
	def update(self, deltaT):
		"""
		This is called by the parent before every frame so the object can update
		its state.
		deltaT: time in seconds since last update; zero if this is the first
		        update
		"""
	
	def die(self):
		self.parent.remove(self)
	
	def onMouseMotion(self, event):
		pass
	
	def onMouseButtonDown(self, event):
		pass
	
	def onMouseButtonUp(self, event):
		pass
	
	def draw(self):
		pass

# vim: set ts=4 sts=4 sw=4 noet :
