from Signal import Signal

class InputSource:
	"""
	An abstract class of objects which provide signals for input events.  They
	may get these events from another InputSource, filter or transform them,
	and re-emit them.
	"""
	
	def __init__(
			self, mouseMotion=Signal(), mouseButtonDown=Signal(),
			mouseButtonUp=Signal()):
		self.mouseMotion = mouseMotion
		self.mouseButtonDown = mouseButtonDown
		self.mouseButtonUp = mouseButtonUp

class MainLoop(InputSource):
	"""
	A singleton class that runs the main loop
	"""
	def __init__(self):
		InputSource.__init__(self)
	
	def run(self):
		pass
	
	def setDelayFunc(self):
		pass

# vim: set ts=4 sts=4 sw=4 ai noet :
