import clutter
from clutter import cogl
import gobject
import pango
from Config import config

class Button(clutter.Actor, clutter.Container):
	"""
	A button.

	Although it isn't designed to let you add arbitrary actors to it, I can't
	make it work without inheriting from clutter.Container.
	"""

	__gtype_name__ = 'Button'
	__gsignals__ = {
		'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()) }

	padding_ratio = 1./4.  # preferred ratio of padding to child height

	def __init__(self):
		clutter.Actor.__init__(self)
		self._child = None
		self.highlighted = False
		self.color = clutter.Color(0xff, 0xff, 0xff, 0xff)

		self.set_reactive(True)

		self.connect('enter-event', self.__class__.on_enter)
		self.connect('leave-event', self.__class__.on_leave)
		self.connect('button-press-event', self.__class__.on_button_press)

	# clutter.Container methods

	def do_add(self, *children):
		for child in children:
			if child is self._child:
				raise Exception("Actor %s is already a child of %s" % (
					child, self))
			if not isinstance(child, clutter.Text):
				raise Exception(
					"Attempted to add actor %s, which is not a clutter.Text, "
					"to %s" % (child, self))
			if self._child is not None:
				self._child.unparent()
			self._child = child
			child.set_parent(self)
			self.queue_relayout()
	
	def do_remove(self, *children):
		for child in children:
			if child is self._child:
				self._child = None
				child.unparent()
				self.queue_relayout()
			else:
				raise Exception("Actor %s is not a child of %s" % (
					child, self))

	def do_foreach(self, func, data=None):
		if self._child is not None:
			func(self._child, data)

	# clutter.Actor methods

	def do_get_preferred_width(self, for_height):
		min_width = 0
		natural_width = 0
		if self._child is not None and self._child.props.visible:
			child_min_width, child_natural_width = (
				self._child.get_preferred_width(for_height))
			child_natural_height = (
				self._child.get_preferred_height(child_natural_width)[1])
			min_width += child_min_width
			natural_width += (
				child_natural_width + 2*self.padding_ratio*child_natural_height)
		return (min_width, natural_width)

	def do_get_preferred_height(self, for_width):
		min_height = 0
		natural_height = 0
		if self._child is not None and self._child.props.visible:
			child_min_height, child_natural_height = (
				self._child.get_preferred_height(for_width))
			min_height = max(min_height, child_min_height)
			natural_height = max(
				natural_height, child_natural_height*(1+2*self.padding_ratio))
		return (min_height, natural_height)


	def do_allocate(self, box, flags):
		if self._child is not None and self._child.props.visible:
			# Give the child the maximum of its preferred size and our allocated
			# size
			w, h = self._child.get_preferred_size()[2:]
			w = min(w, box.get_width())
			h = min(h, box.get_height())

			# Center the child's allocation box in ours
			child_box = clutter.ActorBox()
			child_box.x1 = box.get_width()/2. - w/2.
			child_box.y1 = box.get_height()/2. - h/2.
			child_box.x2 = child_box.x1 + box.get_width()/2. + w/2.
			child_box.y2 = child_box.y1 + box.get_height()/2. + h/2.

			self._child.allocate(child_box, flags)

		clutter.Actor.do_allocate(self, box, flags)

	def set_color(self, color):
		self.color = color
		self.update_child_color()
	
	def update_child_color(self):
		if self._child is not None:
			if self.highlighted:
				self._child.set_color(clutter.Color(0, 0, 0, 0xff))
			else:
				self._child.set_color(self.color)

	def set_text(self, text):
		if self._child is None:
			self.add(clutter.Text())
			self.update_child_color()
		self._child.set_text(text)

	def on_enter(self, event):
		self.highlighted = True
		self.update_child_color()

	def on_leave(self, event):
		self.highlighted = False
		self.update_child_color()

	def on_button_press(self, event):
		self.emit('clicked')

	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		width, height = x2-x1, y2-y1

		if self.highlighted:
			cogl.set_source_color4ub(
				self.color.red, self.color.green, self.color.blue,
				self.color.alpha*self.get_paint_opacity()/255)
		else:
			cogl.set_source_color4ub(0, 0, 0, self.get_paint_opacity()/2)
		cogl.path_round_rectangle(0, 0, width, height, 5, 5)
		cogl.path_fill()

		if self._child is not None:
			self._child.paint()

# vim: set ts=4 sts=4 sw=4 ai noet :
