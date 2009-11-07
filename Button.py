import clutter
import gobject

@gobject.type_register
class Button(clutter.Group):
	def __init__(self, text, color):
		clutter.Group.__init__(self)
		self.set_reactive(True)
		
		self.highlight = clutter.Rectangle()
		self.add(self.highlight)
		self.highlight.set_color(clutter.Color(0, 0, 0, 0x80))
		
		self.text = clutter.Text()
		self.text.set_text(text)
		self.text.set_color(color)
		self.add(self.text)
		
		border_width = self.text.get_height() / 6.
		self.highlight.set_size(
			self.text.get_width() + 2*border_width,
			self.text.get_height() + 2*border_width)
		self.text.set_position(border_width, border_width)
		
		self.color = color
		
		self.connect('enter-event', self.enter_cb)
		self.connect('leave-event', self.leave_cb)
	
	def enter_cb(self, event, data):
		self.highlight.set_color(self.color)
		self.text.set_color(clutter.Color(0, 0, 0, 0xff))
	
	def leave_cb(self, event, data):
		self.highlight.set_color(clutter.Color(0, 0, 0, 0x80))
		self.text.set_color(self.color)

# vim: set ts=4 sts=4 sw=4 ai noet :
