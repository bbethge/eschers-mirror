from distutils.core import setup, Extension

VideoDecode = Extension(
	'VideoDecode',
	libraries = ['xine'],
	sources = ['VideoDecode.c'])

setup(
	name = 'VideoDecode',
	ext_modules = [VideoDecode])
