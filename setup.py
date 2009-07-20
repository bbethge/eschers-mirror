from distutils.core import setup, Extension

VideoDecode = Extension(
	'VideoDecode',
	include_dirs = ['/usr/include/SDL'],  # TODO: portability
	define_macros = [('_REENTRANT', None), ('_GNU_SOURCE', 1)],
	libraries = ['xine', 'SDL'],
	sources = ['VideoDecode.c'])

setup(
	name = 'VideoDecode',
	ext_modules = [VideoDecode])
