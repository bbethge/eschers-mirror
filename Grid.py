import gobject
import clutter
from clutter import cogl
import cluttergst
import gst
import time
from Config import config

class Grid(clutter.Actor):
	"""
	The base class for all grid types, which manage the state of a puzzle.
	"""

	__gtype_name__ = 'Grid'

	def __init__(self, video_file):
		clutter.Actor.__init__(self)
		self.clutter_texture = cluttergst.VideoTexture()
		self.clutter_texture.set_sync_size(True)
		# HACK to make clutter_texture.get_preferred_{width,height} work
		self.clutter_texture.set_parent(self)
		self.clutter_texture.connect('pixbuf-change', self.on_pixbuf_change)
		self.clutter_texture.set_filename(video_file)

	def start(self):
		self.clutter_texture.set_playing(True)

	def get_material(self):
		return self.clutter_texture.get_cogl_material()

	def on_pixbuf_change(self, texture):
		self.queue_redraw()

	def do_get_preferred_width(self, for_height):
		texture_width = self.clutter_texture.get_preferred_width(-1)[1]
		texture_height = self.clutter_texture.get_preferred_height(-1)[1]

		if for_height > 0:
			return 1, float(texture_width) / texture_height * for_height
		else:
			return 1, texture_width

	def do_get_preferred_height(self, for_width):
		texture_width = self.clutter_texture.get_preferred_width(-1)[1]
		texture_height = self.clutter_texture.get_preferred_height(-1)[1]

		if for_width > 0:
			# FIXME: texture_width == 0 ?!
			return 1, float(texture_height) / texture_width * for_width
		else:
			return 1, texture_height

	def is_solved(self):
		"""
		Does self have all its tiles in the right place?
		"""
	
	def shuffle(self):
		"""
		Randomize the locations of the tiles
		"""

# vim: set ts=4 sts=4 sw=4 ai noet :
