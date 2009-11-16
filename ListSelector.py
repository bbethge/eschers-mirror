import gobject
import clutter
from clutter import cogl
import pango
from RoundedRectangle import RoundedRectangle
from Scrollbar import Scrollbar
from Config import config
from Button import Button

class ListItem(clutter.Actor, clutter.Container):
	__gtype_name__ = 'ListItem'
	__gsignals__ = {
		'selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()) }

	padding_ratio = 1./4.

	def __init__(self, text, color):
		clutter.Actor.__init__(self)
		self._child = None
		self.highlighted = False
		self.selected = False
		self.set_reactive(True)

		label = clutter.Text()
		label.set_text(text)
		label.set_color(color)
		label.set_ellipsize(pango.ELLIPSIZE_END)
		self.add(label)

		self.color = color

		self.connect('enter-event', self.__class__.on_enter)
		self.connect('leave-event', self.__class__.on_leave)
		self.connect('button-press-event', self.__class__.on_button_press)

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

	def do_get_preferred_width(self, for_height):
		min_width = 0
		natural_width = 0
		if self._child is not None:
			if not self._child.props.visible:
				return min_width, natural_width
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
		if self._child is not None:
			if not self._child.props.visible:
				return min_height, natural_height
			child_min_height, child_natural_height = (
				self._child.get_preferred_height(for_width))
			min_height = max(min_height, child_min_height)
			natural_height = max(
				natural_height, child_natural_height*(1+2*self.padding_ratio))
		return (min_height, natural_height)


	def do_allocate(self, box, flags):
		if self._child is not None:
			if not self._child.props.visible:
				return
			box_w, box_h = box.size
			padding = self.padding_ratio * box_h
			child_h = self._child.get_preferred_height(box_w)[1]
			child_h = min(box_h, child_h)
			child_box = clutter.ActorBox()
			child_box.x1 = padding
			child_box.y1 = box_h/2. - child_h/2.
			child_box.x2 = child_box.x1 + box.get_width() - padding
			child_box.y2 = child_box.y1 + box_h/2. + child_h/2.
			self._child.allocate(child_box, flags)
		clutter.Actor.do_allocate(self, box, flags)

	def do_foreach(self, func, data=None):
		if self._child is not None:
			func(self._child, data)

	def on_enter(self, event):
		self.highlighted = True
		self.queue_redraw()

	def on_leave(self, event):
		self.highlighted = False
		self.queue_redraw()

	def on_button_press(self, event):
		self.select()

	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		width, height = x2-x1, y2-y1

		if self.highlighted or self.selected:
			cogl.set_source_color4ub(
				self.color.red, self.color.green, self.color.blue,
				self.color.alpha*self.get_paint_opacity()/255)
			cogl.path_round_rectangle(0, 0, width, height, 5, 5)
			if self.selected:
				cogl.path_fill()
			else:
				cogl.path_stroke()

		if self._child is not None:
			self._child.paint()

	def get_text(self):
		return self._child.get_text()

	def select(self):
		if not self.selected:
			if isinstance(self._child, clutter.Text):
				self._child.set_color(clutter.Color(0, 0, 0, 0xff))
			self.selected = True
			self.emit('selected')
	
	def deselect(self):
		if isinstance(self._child, clutter.Text):
			self._child.set_color(self.color)
		self.selected = False

class ListSelector(clutter.Actor, clutter.Container):
	__gtype_name__ = 'ListSelector'

	def __init__(self, items, width, color):
		clutter.Actor.__init__(self)
		self._children = []
		
		for name in items:
			new_item = ListItem(name, color)
			new_item.connect('selected', self.item_selected_cb)
			self.add(new_item)

		self.selected = None
		self.color = color

	def do_add(self, *children):
		for child in children:
			if child in self._children:
				raise Exception(
					"Actor %s is already a child of %s" % (child, self))
			self._children.append(child)
			child.set_parent(self)
			self.queue_relayout()

	def do_remove(self, *children):
		for child in children:
			if child in self._children:
				self._children.remove(child)
				child.unparent()
				self.queue_relayout()
			else:
				raise Exception(
					"Actor %s is not a child of %s" % (child, self))

	def do_foreach(self, func, data=None):
		for child in self._children:
			func(child, data)

	def do_get_preferred_width(self, for_height):
		min_w = 0.
		pref_w = 0.
		for child in self._children:
			child_min_w, child_pref_w = child.get_preferred_width(-1)
			min_w = max(min_w, child_min_w)
			pref_w = max(pref_w, child_pref_w)
		return min_w, pref_w

	def do_get_preferred_height(self, for_width):
		min_h = 0.
		pref_h = 0.
		for child in self._children:
			child_min_h, child_pref_h = child.get_preferred_height(-1)
			min_h += child_min_h
			pref_h += child_pref_h
		return min_h, pref_h

	def do_allocate(self, box, flags):
		x, y = box.origin
		width, height = box.size

		y_off = 0.
		for child in self._children:
			child_h = child.get_preferred_height(width)[1]
			child_box = clutter.ActorBox()
			child_box.x1 = 0.
			child_box.y1 = y_off
			child_box.x2 = width
			child_box.y2 = y_off + child_h
			child.allocate(child_box, flags)
			y_off += child_h

		clutter.Actor.do_allocate(self, box, flags)

	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		w, h = x2-x1, y2-y1

		cogl.set_source_color4ub(0, 0, 0, self.get_paint_opacity()/2)
		cogl.path_round_rectangle(0, 0, w, h, 6, 5)
		cogl.path_fill()

		for child in self._children:
			child.paint()

	def do_pick(self, color):
		clutter.Actor.do_pick(self, color)
		for child in self._children:
			child.paint()
	
	def get_selected(self):
		return self.selected.get_text()

	def set_selected(self, name):
		for child in self._children:
			if child.get_text() == name:
				child.select()
				break

	def item_selected_cb(self, selected):
		if self.selected is not None:
			self.selected.deselect()
		self.selected = selected

# vim: set ts=4 sts=4 sw=4 ai noet :
