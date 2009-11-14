import gobject
import clutter
import os
from Button import Button
from ListSelector import ListSelector
from Config import config

@gobject.type_register
class VideoChooserMenu(clutter.Group):
	def __init__(self, group, color):
		clutter.Group.__init__(self)
		self.group = group
		self.color = color
		
		file_names = []
		for root, dirs, dir_files in os.walk(config.video_dir):
			file_names += dir_files
		self.chooser = ListSelector(file_names, 100, color)
		self.add(self.chooser)
		self.chooser.set_size(100, group.stage.get_height()/2.)
		
		back = Button("Back", color)
		back.set_reactive(True)
		self.add(back)
		back.set_position(0, group.stage.get_height()-back.get_height())
		back.connect('clicked', lambda b: group.move(1,0))

# vim: set ts=4 sts=4 sw=4 ai noet :
