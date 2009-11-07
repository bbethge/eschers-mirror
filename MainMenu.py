import clutter
import pango
import gobject
from Button import Button

@gobject.type_register
class MainMenu(clutter.Group):
	def __init__(self, group, color):
		clutter.Group.__init__(self)
		self.group = group
		stage_w = int(group.stage.get_width())
		stage_h = int(group.stage.get_height())
		
		title = clutter.Text()
		title.set_markup('<span size="xx-large">Escher\'s Mirror</span>')
		title.set_color(color)
		self.add(title)
		title_w, title_h = title.get_size()
		title.set_position(stage_w/2.-title_w/2., stage_h/2.-2.*title_h)
		
		start = Button("Start", color)
		self.add(start)
		start.set_position(stage_w/2.-start.get_width()/2., stage_h/2.)
		start.connect('button-press-event', lambda e,d: group.move(-1,0))
		
		quit = Button("Quit", color)
		self.add(quit)
		quit.set_position(
			stage_w/2.-quit.get_width()/2., stage_h/2.+start.get_height()*1.3)
		
		quit.connect('button-press-event', self.on_quit_clicked)
		
	def on_quit_clicked(self, event, data):
		timeline = self.group.move(0, 1)
		timeline.connect('completed', clutter.main_quit)

# vim: set ts=4 sts=4 noet :
