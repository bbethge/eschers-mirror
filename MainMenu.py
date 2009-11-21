import clutter
import pango
import gobject
from Button import Button
from BoxLayout import BoxLayout

class MainMenu(BoxLayout):
	__gtype_name__ = 'MainMenu'

	def __init__(self, group, color):
		BoxLayout.__init__(self)
		self.group = group
		self.set_orientation(BoxLayout.VERTICAL)
		self.set_padding(10.)
		
		self.title = clutter.Text()
		self.title.set_markup('<span size="xx-large">Escher\'s Mirror</span>')
		self.title.set_color(color)
		self.add(self.title)
		
		self.start = Button()
		self.start.set_text("Start")
		self.start.set_color(color)
		self.add(self.start)
		self.start.connect('clicked', lambda b: group.move(-1,0))
		
		self.quit = Button()
		self.quit.set_text("Quit")
		self.quit.set_color(color)
		self.add(self.quit)
		
		self.quit.connect('clicked', self.on_quit_clicked)

	def on_quit_clicked(self, button):
		timeline = self.group.move(0, 1)
		timeline.connect('completed', clutter.main_quit)

# vim: set ts=4 sts=4 noet :
