"""
A module that reads configuration options from a file on import and makes them
available as module variables.  You can assign to them and then call write() to
write the modified values to a file.
"""

import os

class Config:
	"""
	A class that loads values from a configuration file and makes them
	available as attributes.  They can be changed and then written back to the
	file.
	"""
	def __init__(self, configFile):
		self.__config = {
			'video_dir': os.path.expanduser('~/Videos'),
			'grid_rows': 2,
			'grid_cols': 3,
			'window_size': (640, 480) }
		self.__configFile = configFile
		config = {}
		try:
			execfile(configFile, {}, config)
		except IOError:
			pass
		self.__config.update(config)
	
	def __getattr__(self, name):
		return self.__config[name]
	
	def __setattr__(self, name, value):
		if name[0] == '_':
			self.__dict__[name] = value
		else:
			self.__config[name] = value
	
	def write(self):
		"""
		Write the current configuration options to the user's configuration
		file.
		"""
		f = open(self.__configFile, 'w')
		for key, value in self.__config.iteritems():
			if key[0] != '_':
				f.write('%s = %s\n' % (key, repr(value)))
		f.close()

# Create a singleton Config object
config = Config(os.path.expanduser('~/.eschers-mirror.py'))

# vim: set ai noet ts=4 sts=4 sw=4 :
