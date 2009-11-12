import gobject
import clutter
from clutter import cogl
from Config import config
from RoundedRectangle import RoundedRectangle

@gobject.type_register
class Triangle(clutter.Rectangle):

	def do_paint(self):
		color = self.get_color()
		x1, y1, x2, y2 = self.get_allocation_box()
		width, height = x2-x1, y2-y1

		cogl.set_source_color4ub(
			color.red, color.green, color.blue,
			color.alpha * self.get_paint_opacity() / 255)
		cogl.path_move_to(0, height)
		cogl.path_line_to(width, height)
		cogl.path_line_to(width/2., 0)
		cogl.path_close()
		cogl.path_fill()

@gobject.type_register
class Scrollbar(clutter.Group):
	__gsignals__ = {
		'scrolled': (
			gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
			(gobject.TYPE_DOUBLE,)) }

	arrow_aspect = 1.
	max_slider_aspect = 1.
	
	def __init__(self):
		clutter.Group.__init__(self)

		self.up_arrow = Triangle()
		self.add(self.up_arrow)
		self.up_arrow.set_reactive(True)
		self.up_arrow.connect(
			'button-press-event',
			lambda e,d: self.set_value(self.value-self.page_size/5.))

		self.down_arrow = Triangle()
		self.add(self.down_arrow)
		self.down_arrow.set_reactive(True)
		self.down_arrow.connect(
			'button-press-event',
			lambda e,d: self.set_value(self.value+self.page_size/5.))

		self.line = clutter.Rectangle()
		self.add(self.line)

		self.slider = RoundedRectangle()
		self.add(self.slider)

		self.arrow_height = 1.
		self.value = 0.
		self.page_size = 1.

	def set_color(self, color):
		self.foreach(lambda a, n: a.set_color(color), None)

	def get_value(self):
		return self.value

	def set_value(self, value):
		new_value = max(0., min(value, 1.))
		if new_value != self.value:
			change = new_value - self.value
			self.value = new_value
			self.queue_relayout()
			self.emit('scrolled', change)

	def set_page_size(self, page_size):
		self.page_size = page_size
		self.queue_relayout()

	def do_get_preferred_width(self, for_height):
		return 3, config.em
	
	def do_get_preferred_height(self, for_width):
		return (
			for_width * (2*self.arrow_aspect+self.max_slider_aspect) + 1,
			for_width * (2*self.arrow_aspect+2*self.max_slider_aspect))
	
	def do_allocate(self, box, flags):
		x, y = box.origin
		width, height = box.size

		self.arrow_height = width/self.arrow_aspect
		line_width = width/10.

		# For some reason this doesn't work if we give parent-relative
		# coordinates
		self.up_arrow.allocate(
			clutter.ActorBox(x, y, x+width, y+self.arrow_height), flags)
		self.down_arrow.allocate(
			clutter.ActorBox(x, y+height-self.arrow_height, x+width, y+height),
			flags)
		self.line.allocate(
			clutter.ActorBox(
				x+width/2.-line_width/2., y+self.arrow_height,
				x+width/2.+line_width/2., y+height-self.arrow_height),
			flags)

		slider_height = max(
			self.page_size * (height-2*self.arrow_height),
			width * self.max_slider_aspect)
		self.slider.allocate(
			clutter.ActorBox(
				x,
				y + self.arrow_height
					+ self.value * (height-2*self.arrow_height-slider_height),
				x + width,
				y + self.arrow_height + slider_height
					+ self.value * (height-2*self.arrow_height-slider_height)),
			flags)
		self.slider.set_corner_size(width/2.)

		self.down_arrow.set_rotation(
			clutter.Z_AXIS, 180, width/2., self.arrow_height/2., 0.)

# vim: set ts=4 sts=4 sw=4 ai noet :
