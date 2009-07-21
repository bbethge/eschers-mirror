class bidict(dict):
	"""
	Bidirectional dictionary: a mapping that maintains its own inverse
	mapping in self.inv, which is another bidict.  The more complicated
	mutating methods of dict are not implemented.
	"""
	
	def __init__(self, inverse=None):
		"""
		Create an empty bidict.  For simplicity, bidict does not
		support creation with initial contents.
		"""
		if inverse == None:
			self.inv = bidict(self)
		elif isinstance(inverse, bidict):
			self.inv = inverse
		else:
			raise TypeError(
					"bidict() expected bidict instance or "
					"None")
		
	def __setitem__(self, key, val):
		dict.__setitem__(self, key, val)
		dict.__setitem__(self.inv, val, key)
	
	def __delitem__(self, key):
		dict.__delitem__(self[key])
		dict.__delitem__(key)
	
	def clear(self):
		dict.clear(self)
		dict.clear(self.inv)
	
	def pop(self, default=None):
		"Not implemented"
		raise NotImplementedError
	
	def popitem(self):
		key, val = dict.pop(self)
		dict.__delitem__(self.inv, val)
		return key, val
	
	def setdefault(self, key, default=None):
		"Not implemented"
		raise NotImplementedError
	
	def update(self, other):
		for key, val in other.iteritems():
			self[key] = val
