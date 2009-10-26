class Actor:
	"""
	A class for objects that behave on their own
	"""
	def __init__(self, grid):
		"""
		grid: the grid (puzzle) object that manages this object
		"""
		self.grid = grid
		grid.add(self)
	
	def update(self, deltaT):
		"""
		This is called by the grid before every frame so the object can update
		its state.
		deltaT: time in seconds since last update; zero if this is the first
		        update
		"""
		pass
	
	def die(self):
		self.grid.remove(self)

# vim: set ts=4 sts=4 sw=4 noet :
