import clutter
import pango
import gobject
from Button import Button

@gobject.type_register
class MainMenu(clutter.Group):
	def __init__(self, group, color):
		clutter.Group.__init__(self)
		self.group = group
		
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

	def do_allocate(self, box, flags):	
		x, y = box.origin
		w, h = box.size

		title_w, title_h = self.title.get_size()
		self.title.set_position(w/2.-title_w/2., h/2.-2.*title_h)
		self.start.set_position(w/2.-self.start.get_width()/2., h/2.)
		self.quit.set_position(
			w/2.-self.quit.get_width()/2., h/2.+self.start.get_height()*1.3)
		clutter.Group.do_allocate(self, box, flags)

		return

		title_w = self.title.get_preferred_width(-1)[1]
		title_h = self.title.get_preferred_height(-1)[1]
		child_box = clutter.ActorBox()
		child_box.x1 = w/2. - title_w/2.
		child_box.y1 = h/2. - 2.*title_h
		child_box.x2 = w/2. + title_w/2.
		child_box.y2 = h/2. - title_h
		self.title.allocate(child_box, flags)

		start_w = self.start.get_preferred_width(-1)[1]
		start_h = self.start.get_preferred_height(-1)[1]
		child_box = clutter.ActorBox()
		child_box.x1 = w/2. - start_w/2.
		child_box.y1 = h/2.
		child_box.x2 = w/2. + start_w/2.
		child_box.y2 = h/2. + start_h
		self.start.allocate(child_box, flags)

		quit_w = self.quit.get_preferred_width(-1)[1]
		quit_h = self.quit.get_preferred_height(-1)[1]
		child_box = clutter.ActorBox()
		child_box.x1 = w/2. - quit_w/2.
		child_box.y1 = h/2. + 1.3*quit_h
		child_box.x2 = w/2. + quit_w/2.
		child_box.y2 = h/2. + 2.3*quit_h
		self.quit.allocate(child_box, flags)
	
	def on_quit_clicked(self, button):
		timeline = self.group.move(0, 1)
		timeline.connect('completed', clutter.main_quit)

# vim: set ts=4 sts=4 noet :
