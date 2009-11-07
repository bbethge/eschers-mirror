import clutter
import gobject
from MainMenu import MainMenu
from VideoChooserMenu import VideoChooserMenu

@gobject.type_register
class MenuGroup(clutter.Group):
	"""
	A group that contains all the menus so that they can be scrolled together
	
	Public members:
		stage: the stage we belong to
	"""
	
	def __init__(self, stage, color):
		clutter.Group.__init__(self)
		self.stage = stage
		
		main = MainMenu(self, color)
		self.add(main)
		main.set_position(0, 0)
		
		chooser = VideoChooserMenu(self, color)
		self.add(chooser)
		chooser.set_position(stage.get_width(), 0)
	
	def move(self, x_amount, y_amount):
		"""
		Move the all the menus with animation by x_amount screen widths
		horizontally and y_amount screen heights vertically
		
		Returns: the timeline of the animation
		"""
		timeline = clutter.Timeline(500)
		alpha = clutter.Alpha(timeline, clutter.LINEAR)
		
		x, y = self.get_position()
		width, height = self.stage.get_size()
		
		path = clutter.Path()
		path.add_move_to(int(x), int(y))
		path.add_rel_curve_to(
			int(x_amount*width*2/3), int(y_amount*height*2/3),
			int(x_amount*width/3), int(y_amount*height/3),
			int(x_amount*width), int(y_amount*height))
		
		self.behaviour = clutter.BehaviourPath(alpha, path)
		self.behaviour.apply(self)
		
		timeline.start()
		return timeline

# vim: set ts=4 sts=4 sw=4 ai noet :
