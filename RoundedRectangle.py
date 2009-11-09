import gobject
import clutter
from clutter import cogl

@gobject.type_register
class RoundedRectangle(clutter.Rectangle):
	def __init__(self):
		clutter.Rectangle.__init__(self)
		self.corner_size = 0
		self.filled = True
	
	def set_corner_size(self, size):
		self.corner_size = size
		self.queue_redraw()
	
	def get_corner_size(self):
		return self.corner_size

	def set_filled(self, filled):
		self.filled = filled
		self.queue_redraw()

	def get_filled(self):
		return self.filled

	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		width, height = x2-x1, y2-y1
		
		c = self.get_color()
		cogl.set_source_color4ub(
			c.red, c.green, c.blue, c.alpha*self.get_paint_opacity()/255)
		cogl.path_round_rectangle(0, 0, width, height, self.corner_size, 5)
		if self.filled:
			cogl.path_fill()
		else:
			cogl.path_stroke()

# vim: set ts=4 sts=4 sw=4 ai noet :
