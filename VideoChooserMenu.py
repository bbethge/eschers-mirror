import gobject
import clutter
import cluttergst
import gst
import os
from Button import Button
from ListSelector import ListSelector
from RectGrid import RectGrid
from BoxLayout import BoxLayout
from Frame import Frame
from Config import config

class VideoChooserMenu(BoxLayout):
	__gtype_name__ = 'VideoChooserMenu'

	def __init__(self, group, color):
		BoxLayout.__init__(self)
		self.set_orientation(BoxLayout.VERTICAL)
		self.group = group
		self.color = color
		
		file_names = []
		for root, dirs, dir_files in os.walk(config.video_dir):
			file_names += dir_files
		self.chooser = ListSelector(file_names, 100, color)
		self.add(self.chooser)
		#self.chooser.set_size(100, group.stage.get_height()/2.)
		self.chooser.set_selected(file_names[0])
		
		self.hbox = BoxLayout()
		self.hbox.set_orientation(BoxLayout.HORIZONTAL)
		self.pack(self.hbox, expand=True, fill=True)

		# FIXME: put back and go buttons in lower corners of the screen
		back = Button()
		back.set_text("Back")
		back.set_color(color)
		self.hbox.add(back)
		#back.set_position(0, group.stage.get_height()-back.get_height())
		back.connect('clicked', lambda b: group.move(1,0))

		self.hbox.pack(Frame(), expand=True, fill=True)

		go = Button()
		go.set_text("Go")
		go.set_color(color)
		self.hbox.add(go)
		#go.set_position(
		#	group.stage.get_width() - go.get_width(),
		#	group.stage.get_height() - go.get_height())
		go.connect('clicked', self.on_go_clicked)

	def on_go_clicked(self, button):
		self.group.move(-1, 0).connect('completed', self.start_video)

	def start_video(self, timeline):
		filename = os.path.join(config.video_dir, self.chooser.get_selected())
		grid = RectGrid(filename, 3, 4)
		self.group.add(grid)
		grid.set_x(2*self.group.stage.get_width())
		grid.start()
	
# vim: set ts=4 sts=4 sw=4 ai noet :
