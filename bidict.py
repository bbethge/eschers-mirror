class bidict(dict):
	"""
	Bidirectional dictionary: a dictionary that ensures that (d[a] == b
	iff d[b] == a) and (a not in d iff b not in d).  This is useful if you
	want a two-way mapping and the domain and range are disjoint.
	
	I have only overridden enough methods to ensure the invariant holds.  In
	particular, fromkeys returns a plain dict, which may or may not be what
	you want if you actually want to use it.
	"""
	
	def __init__(self):
		"""
		Create an empty bidict.  For simplicity, bidict does not
		support creation with initial contents.
		"""
		dict.__init__(self)
	
	def __delitem__(self, item):
		other = self[item]
		dict.__delitem__(self, item)
		dict.__delitem__(self, other)
	
	def __setitem__(self, item, other):
		dict.__setitem__(self, item, other)
		dict.__setitem__(self, other, item)
	
	def popitem(self):
		result = dict.popitem(self)
		dict.__delitem__(self, result[1])
	
	def pop(self, item, *default):
		if item in self:
			result = self[item]
			del self[item]
		else:
			if len(default) == 1:
				result = default[0]
			elif len(default) == 0:
				raise KeyError
			else:
				raise TypeError
		return result
	
	def setdefault(self, *args):
		"""Not implemented"""
		raise NotImplementedError
	
	def update(self, other):
		"""Not implemented"""
		raise NotImplementedError
