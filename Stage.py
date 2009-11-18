import clutter
import gobject
from MenuGroup import MenuGroup
from Config import config

@gobject.type_register
class Stage(clutter.Stage):
	def __init__(self):
		clutter.Stage.__init__(self)
		self.set_color(clutter.Color(0x80, 0x80, 0x80, 0xff))
		width, height = config.window_size
		self.set_size(width, height)
		self.set_title("Escher's Mirror")
		self.connect('destroy', clutter.main_quit)
		
		color = clutter.Color(0xa0, 0xff, 0x90, 0xff)
		menu_group = MenuGroup(color)
		self.add(menu_group)

# vim: set ts=4 sts=4 sw=4 ai noet :
