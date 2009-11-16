import gobject
import clutter
import cluttergst
import gst
import os
from Button import Button
from ListSelector import ListSelector
from RectGrid import RectGrid
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
		self.chooser.set_selected(file_names[0])
		
		back = Button("Back", color)
		back.set_reactive(True)
		self.add(back)
		back.set_position(0, group.stage.get_height()-back.get_height())
		back.connect('clicked', lambda b: group.move(1,0))

		go = Button("Go", color)
		go.set_reactive(True)
		self.add(go)
		go.set_position(
			group.stage.get_width() - go.get_width(),
			group.stage.get_height() - go.get_height())
		go.connect('clicked', self.on_go_clicked)

	def on_go_clicked(self, button):
		self.group.move(-1, 0).connect('completed', self.start_video)

	def start_video(self, timeline):
		filename = os.path.join(config.video_dir, self.chooser.get_selected())
		uri = 'file://' + filename.replace(os.sep, '/')
		grid = RectGrid(uri, 3, 4)
		self.group.add(grid)
		grid.set_x(2*self.group.stage.get_width())
		grid.start()
	
# vim: set ts=4 sts=4 sw=4 ai noet :
