import clutter
from clutter import cogl
import gobject
import pango
from Config import config
from RoundedRectangle import RoundedRectangle

@gobject.type_register
class Button(clutter.Group):
	def __init__(self, text, color):
		clutter.Group.__init__(self)
		self.set_reactive(True)
		
		self.text = clutter.Text()
		self.text.set_text(text)
		self.text.set_color(color)
		attrs = pango.AttrList()
		attrs.insert(
			pango.AttrSize(int(1000*config.em), 0, len(self.text.get_text())))
		self.text.set_attributes(attrs)
		self.add(self.text)

		self.border_width = self.text.get_height()/4.
		self.text.set_position(self.border_width, self.border_width)

		self.background = RoundedRectangle()
		self.background.set_size(
			self.text.get_width()+2*self.border_width,
			self.text.get_height()+2*self.border_width)
		self.background.set_corner_size(2*self.border_width)
		self.background.set_color(clutter.Color(0, 0, 0, 0x80))
		self.add(self.background)
		self.background.lower_bottom()
		
		self.color = color
		
		self.connect('enter-event', self.enter_cb)
		self.connect('leave-event', self.leave_cb)
	
	def enter_cb(self, event, data):
		self.background.set_color(self.color)
		self.text.set_color(clutter.Color(0, 0, 0, 0xff))
	
	def leave_cb(self, event, data):
		self.background.set_color(clutter.Color(0, 0, 0, 0x80))
		self.text.set_color(self.color)

# vim: set ts=4 sts=4 sw=4 ai noet :
