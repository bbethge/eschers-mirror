import gobject
import clutter
import pango
from RoundedRectangle import RoundedRectangle
from Config import config

@gobject.type_register
class ListItem(clutter.Group):
	__gsignals__ = {
		'selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()) }

	def __init__(self, text, width, color):
		clutter.Group.__init__(self)
		self.set_reactive(True)

		self.label = clutter.Text()
		self.label.set_text(text)
		self.label.set_color(color)
		attrs = pango.AttrList()
		attrs.insert(
			pango.AttrSize(int(1000*config.em), 0, len(self.label.get_text())))
		self.label.set_attributes(attrs)
		self.add(self.label)

		label_w, label_h = self.label.get_size()
		self.border_width = label_h / 4.
		self.label.set_position(self.border_width, self.border_width)

		self.highlight = RoundedRectangle()
		self.highlight.set_size(
			label_w+2*self.border_width, label_h+2*self.border_width)
		self.highlight.set_color(color)
		self.highlight.set_corner_size(2*self.border_width)
		self.highlight.set_filled(False)
		self.add(self.highlight)
		self.highlight.lower_bottom()
		self.highlight.hide()

		self.selected = False
		self.color = color

		self.connect('enter-event', self.enter_cb)
		self.connect('leave-event', self.leave_cb)
		self.connect('button-press-event', lambda e,d: self.select())

	def enter_cb(self, event, data):
		self.highlight.show()
	
	def leave_cb(self, event, data):
		if not self.selected:
			self.highlight.hide()

	def set_width(self, width):
		self.label.set_clip(
			0, 0, width-self.border_width, self.label.get_height())
		self.highlight.set_width(width)

	def get_text(self):
		return self.label.get_text()

	def select(self):
		self.highlight.set_filled(True)
		self.label.set_color(clutter.Color(0, 0, 0, 0xff))
		self.selected = True
		self.emit('selected')
	
	def deselect(self):
		self.highlight.set_filled(False)
		self.highlight.hide()
		self.label.set_color(self.color)
		self.selected = False

@gobject.type_register
class ListSelector(clutter.Group):
	def __init__(self, items, width, color):
		clutter.Group.__init__(self)
		
		self.background = clutter.Rectangle()
		self.background.set_color(clutter.Color(0, 0, 0, 0x80))
		self.add(self.background)
		
		self.items = []
		y = 0.
		for name in items:
			new_item = ListItem(name, width, color)
			new_item.connect('selected', self.item_selected_cb)
			self.items.append(new_item)
			self.add(new_item)
			new_item.set_position(0, y)
			y += new_item.get_height()
		
		self.selected = None
		self.color = color
	
	def set_size(self, width, height):  
		self.background.set_size(width, height)
		self.set_clip(0, 0, width, height)
		for item in self.items:
			item.set_width(width)
	
	def get_selected(self):
		return self.selected
	
	def item_selected_cb(self, selected):
		for item in self.items:
			if item is not selected:
				item.deselect()
		self.selected = selected

# vim: set ts=4 sts=4 sw=4 ai noet :
