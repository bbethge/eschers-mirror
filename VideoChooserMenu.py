import gobject
import clutter
from Button import Button
from ListSelector import ListSelector

@gobject.type_register
class VideoChooserMenu(clutter.Group):
	def __init__(self, group, color):
		clutter.Group.__init__(self)
		self.group = group
		self.color = color
		
		back = Button("Back", color)
		back.set_reactive(True)
		self.add(back)
		back.set_position(0, group.stage.get_height()-back.get_height())
		back.connect('button-press-event', lambda e,d: group.move(1,0))

# vim: set ts=4 sts=4 sw=4 ai noet :
