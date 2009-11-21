import clutter
from clutter import cogl
import gobject
import pango
from Config import config

class Frame(clutter.Actor, clutter.Container):
	"""
	A container that adds space around its single child.  If expand_child is
	set, the child will get all the space except for optional padding.
	Otherwise, the child gets its preferred size if possible.
	"""

	__gtype_name__ = 'Frame'

	def __init__(self):
		clutter.Actor.__init__(self)
		self._child = None
		self.expand_child = False
		self.padding = 0.

	def set_expand_child(self, expand_child):
		self.expand_child = expand_child
		self.queue_relayout()
	
	def set_padding(self, padding):
		self.padding = padding
		self.queue_relayout()

	# clutter.Container methods

	def do_add(self, *children):
		for child in children:
			if child is self._child:
				raise Exception("Actor %s is already a child of %s" % (
					child, self))
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
			natural_width += child_natural_width + 2*self.padding
		return min_width, natural_width

	def do_get_preferred_height(self, for_width):
		min_height = 0
		natural_height = 0
		if self._child is not None and self._child.props.visible:
			child_min_height, child_natural_height = (
				self._child.get_preferred_height(for_width))
			min_height = max(min_height, child_min_height)
			natural_height = max(
				natural_height, child_natural_height + 2*self.padding)
		return min_height, natural_height


	def do_allocate(self, box, flags):
		if self._child is not None and self._child.props.visible:
			w, h = box.size
			if self.expand_child:
				child_w = w - 2*self.padding
				child_h = h - 2*self.padding
			else:
				child_pref_w, child_pref_h = (
					self._child.get_preferred_size()[2:])
				child_w = min(child_pref_w, w)
				child_h = min(child_pref_h, h)

			# Center the child's allocation box in ours
			child_box = clutter.ActorBox()
			child_box.x1 = w/2. - child_w/2.
			child_box.y1 = h/2. - child_h/2.
			child_box.x2 = w/2. + child_w/2.
			child_box.y2 = h/2. + child_h/2.

			self._child.allocate(child_box, flags)

		clutter.Actor.do_allocate(self, box, flags)

	def do_paint(self):
		if self._child is not None:
			self._child.paint()
	
	def do_pick(self, color):
		clutter.Actor.do_pick(self, color)
		if self._child is not None:
			self._child.paint()

# vim: set ts=4 sts=4 sw=4 ai noet :
