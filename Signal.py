import weakref

class Signal:
	"""
	A Signal object maintains a list of callbacks which are added and removed by 
	parts of the code which are interested in the corresponding event.  When the
	Signal's owner calls the emit method, all the currently registered callbacks 
	are called.
	"""
	def __init__(self):
		self.callbacks = set()
	
	def addHandler(self, handler, obj=None):
		"""
		Add a signal handler.
		handler: a function or an unbound method
		obj: if handler is an unbound method, this is the object to call the
		     method on
		Passing a bound method (with obj==None) should work, but will keep the 
		object that the method is bound to alive until the handler is explicitly 
		removed.  Passing the object and the method separately allows the
		handler to be automatically removed when the object is no longer needed.
		"""
		if obj is None:
			self.callbacks.add( (handler,None) )
		else:
			self.callbacks.add( (handler,weakref.ref(obj)) )
	
	def removeHandler(self, handler, obj=None):
		if obj is None:
			self.callbacks.remove( (handler,None) )
		else:
			# The weakref we stored previously must still be valid, becase the
			# object is still referenced through obj.
			self.callbacks.remove( (handler,weakref.ref(obj)) )
	
	def emit(self, *args, **kwargs):
		# Iterate over a copy of self.callbacks since we will be removing any
		# method callbacks to dead objects as we go.
		for handler, ref in set(self.callbacks):
			if ref is None:
				handler(*args, **kwargs)
			obj = ref()
			if obj is None:
				self.callbacks.remove( (handler,ref) )
			else:
				handler(obj, *args, **kwargs)

# vim: set ts=4 sts=4 sw=4 noet :
