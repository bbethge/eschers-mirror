"""
This file wraps the minimum set of Xine functions needed by our program, using
ctypes.  We don't use pyxine because it is no longer maintained and doesn't
support the raw output plugin, which we need.
"""

from ctypes import *
from ctypes import util
xine = CDLL(util.find_library('xine'))

check_version = xine.xine_check_version
check_version.argtypes = [ c_int ] * 3
check_version.restype = c_int

class xine_t(Structure):
	pass

new = xine.xine_new
new.argtypes = []
new.restype = POINTER(xine_t)

config_load = xine.xine_config_load
config_load.argtypes = [ POINTER(xine_t), c_char_p ]
config_load.restype = None

init = xine.xine_init
init.argtypes = [ POINTER(xine_t) ]
init.restype = None

raw_output_cb_t = CFUNCTYPE(
	None, c_void_p, c_int, c_int, c_int, c_double, POINTER(c_ubyte),
	c_void_p, c_void_p)

class raw_overlay_t(Structure):
	pass

raw_overlay_cb_t = CFUNCTYPE(None, c_void_p, c_int, POINTER(raw_overlay_t))

class raw_visual_t(Structure):
	_fields_ = [
		('user_data', c_void_p), ('supported_formats', c_int),
		('raw_output_cb', raw_output_cb_t),
		('raw_overlay_cb', raw_overlay_cb_t)]

VORAW_RGB = 4
VISUAL_TYPE_RAW = 12

class audio_port_t(Structure):
	pass

open_audio_driver = xine.xine_open_audio_driver
open_audio_driver.argtypes = [ POINTER(xine_t), c_char_p, c_void_p ]
open_audio_driver.restype = POINTER(audio_port_t)

class video_port_t(Structure):
	pass

open_video_driver = xine.xine_open_video_driver
open_video_driver.argtypes = [
	POINTER(xine_t), c_char_p, c_int, POINTER(raw_visual_t) ]
open_video_driver.restype = POINTER(video_port_t)


class stream_t(Structure):
	pass

stream_new = xine.xine_stream_new
stream_new.argtypes = [
	POINTER(xine_t), POINTER(audio_port_t), POINTER(video_port_t) ]
stream_new.restype = POINTER(stream_t)

open_ = xine.xine_open
open_.argtypes = [ POINTER(stream_t), c_char_p ]
open_.restype = c_int

get_error = xine.xine_get_error
get_error.argtypes = [ POINTER(stream_t) ]
get_error.restype = c_int

close_audio_driver = xine.xine_close_audio_driver
close_audio_driver.argtypes = [ POINTER(xine_t), POINTER(audio_port_t) ]
close_audio_driver.restype = None

close_video_driver = xine.xine_close_video_driver
close_video_driver.argtypes = [ POINTER(xine_t), POINTER(video_port_t) ]
close_video_driver.restype = None

play = xine.xine_play
play.argtypes = [ POINTER(stream_t), c_int, c_int ]
play.restype = c_int

stop = xine.xine_stop
stop.argtypes = [ POINTER(stream_t) ]
stop.restype = None

close = xine.xine_close
close.argtypes = [ POINTER(stream_t) ]
close.restype = None

exit = xine.xine_exit
exit.argtypes = [ POINTER(xine_t) ]
exit.restype = None

get_pos_length = xine.xine_get_pos_length
get_pos_length.argtypes = [
	POINTER(stream_t), POINTER(c_int), POINTER(c_int), POINTER(c_int) ]

# This doesn't seem to work
#__all__ = [
#	'check_version', 'xine_t', 'new', 'config_load', 'init',
#	'raw_output_cb_t', 'raw_overlay_t', 'raw_overlay_cb_t', 'raw_visual_t',
#	'VORAW_RGB', 'VISUAL_TYPE_RAW', 'audio_port_t', 'open_audio_driver',
#	'video_port_t', 'open_video_driver', 'stream_t', 'stream_new', 'open_',
#	'get_error', 'close_audio_driver', 'close_video_driver', 'play', 'stop',
#	'close', 'exit', 'get_pos_length' ]
