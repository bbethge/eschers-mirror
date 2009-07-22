from distutils.core import setup, Extension
import subprocess

includes = []
defines = []
libs = ['xine']
lib_dirs = []
sdlConfig = subprocess.Popen(
	['sdl-config', '--libs', '--cflags'], stdout=subprocess.PIPE,
	stderr=subprocess.STDOUT
	).communicate()[0]
for opt in sdlConfig.split():
	if opt[:2] == '-D':
		eqIdx = opt.find('=')
		if eqIdx >= 0:
			defines += [ (opt[2:eqIdx], opt[eqIdx:]) ]
		else:
			defines += [ (opt[2:], None) ]
	elif opt[:2] == '-I':
		includes += [opt[2:]]
	elif opt[:2] == '-l':
		libs += [opt[2:]]
	elif opt[:2] == '-L':
		lib_dirs += [opt[2:]]

VideoDecode = Extension(
	'VideoDecode',
	include_dirs = includes,
	define_macros = defines,
	libraries = libs,
	sources = ['VideoDecode.c'])

setup(
	name = 'VideoDecode',
	ext_modules = [VideoDecode])
