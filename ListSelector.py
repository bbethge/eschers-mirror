import gobject
import clutter

@gobject.type_register
class ListSelector(clutter.Group):
	def __init__(self, items, color):
		self.items = list(items)
		self.selected_index = 0
		self.color = color
	
	def add_item(self, item):
		self.items.append(item)
	
	def get_selected(self):
		return self.items[self.selected_index]

# vim: set ts=4 sts=4 sw=4 ai noet :
