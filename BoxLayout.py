import clutter
from clutter import cogl
import gobject

class BoxLayoutChildMeta(clutter.ChildMeta):
	__gtype_name__ = 'BoxLayoutChildMeta'
	__gproperties__ = {
		'expand': (
			gobject.TYPE_BOOLEAN, "Expand",
			"Expand to use all available space", False,
			gobject.PARAM_CONSTRUCT|gobject.PARAM_READWRITE),
		'fill': (
			gobject.TYPE_BOOLEAN, "Fill", "Fill all available space", False,
			gobject.PARAM_CONSTRUCT|gobject.PARAM_READWRITE) }

	def __init__(self):
		self.expand = False
		self.fill = False
	
	def do_get_property(self, pspec):
		if pspec.name == 'expand':
			return self.expand
		elif pspec.name == 'fill':
			return self.fill

	def do_set_property(self, pspec, value):
		if pspec.name == 'expand':
			self.expand = value
		elif pspec.name == 'fill':
			self.fill = value

class BoxLayout(clutter.Actor, clutter.Container):
	__gtype_name__ = 'BoxLayout'

	HORIZONTAL = 0
	VERTICAL = 1

	def __init__(self):
		clutter.Actor.__init__(self)
		self.children = []
		self.orientation = self.HORIZONTAL
		self.padding = 0.

	def set_padding(self, padding):
		self.padding = padding
		self.queue_relayout()
	
	def set_orientation(self, orientation):
		self.orientation = orientation
		self.queue_relayout()

	def do_add(self, *children):
		for child in children:
			if child in self.children:
				raise Exception(
					"Actor %s is already a child of %s" % (child, self))
			self.children.append(child)
			child.set_parent(self)
			self.queue_relayout()

	def do_remove(self, *children):
		for child in children:
			if child in self.children:
				self.children.remove(child)
				child.unparent()
				self.queue_relayout()
			else:
				raise Exception("Actor %s is not a child of %s" % (child, self))

	def do_foreach(self, func, data):
		for child in self.children:
			func(child, data)
	
	def do_get_preferred_width(self, for_height):
		min_w = 0.
		pref_w = 0.
		if self.orientation == self.HORIZONTAL:
			for child in self.children:
				child_min_w, child_pref_w = (
					child.get_preferred_width(for_height))
				min_w += child_min_w
				pref_w += child_pref_w
			pref_w += (len(self.children)-1) * self.padding
		else:
			for child in self.children:
				child_min_w, child_pref_w = child.get_preferred_width(-1)
				min_w = max(min_w, child_min_w)
				pref_w = max(pref_w, child_pref_w)
		return min_w, pref_w

	def do_get_preferred_height(self, for_width):
		min_h = 0.
		pref_h = 0.
		if self.orientation == self.HORIZONTAL:
			for child in self.children:
				child_min_h, child_pref_h = child.get_preferred_height(-1)
				min_h = max(min_h, child_min_h)
				pref_h = max(pref_h, child_pref_h)
		else:
			for child in self.children:
				child_min_h, child_pref_h = (
					child.get_preferred_height(for_width))
				min_h += child_min_h
				pref_h += child_pref_h
			pref_h += (len(self.children)-1) * self.padding
		return min_h, pref_h

	def do_allocate(self, box, flags):
		clutter.Actor.do_allocate(self, box, flags)

		w, h = box.size

		if self.orientation == self.HORIZONTAL:
			base_min_w = 0.
			base_pref_w = 0.
			min_widths = []
			pref_widths = []
			num_expanded = 0
			for child in self.children:
				child_min_w, child_pref_w = child.get_preferred_width(h)
				base_min_w += child_min_w
				base_pref_w += child_pref_w
				min_widths.append(child_min_w)
				pref_widths.append(child_pref_w)
				if self.child_get_property(child, 'expand'):
					num_expanded += 1
			if w < base_pref_w:
				widths = min_widths
				if len(self.children) > 1:
					padding = (w-base_min_w) / (len(self.children)-1)
			elif w < base_pref_w + (len(self.children)-1)*self.padding:
				widths = pref_widths
				if len(self.children) > 1:
					padding = (w-base_pref_w) / (len(self.children)-1)
			else:
				widths = pref_widths
				# FIXME: is this consistent with our size request?
				padding = self.padding

				if num_expanded > 0:
					extra_w = w - base_pref_w - (len(self.children)-1)*padding
					for i in range(len(self.children)):
						if self.child_get_property(self.children[i], 'expand'):
							widths[i] += float(extra_w) / num_expanded
			x = 0.
			for i in range(len(self.children)):
				child_box = clutter.ActorBox()
				if self.child_get_property(self.children[i], 'fill'):
					child_box.x1 = x
					child_box.y1 = 0.
					child_box.x2 = x + widths[i]
					child_box.y2 = h
				else:
					child_pref_w, child_pref_h = (
						self.children[i].get_preferred_size()[2:])
					child_w = min(widths[i], child_pref_w)
					child_h = min(h, child_pref_h)
					child_box.x1 = x + widths[i]/2. - child_w/2.
					child_box.y1 = h/2. - child_h/2.
					child_box.x2 = x + widths[i]/2. + child_w/2.
					child_box.y2 = h/2. + child_h/2.
				x += widths[i] + padding
				self.children[i].allocate(child_box, flags)
		else:
			base_min_h = 0.
			base_pref_h = 0.
			min_heights = []
			pref_heights = []
			num_expanded = 0
			for child in self.children:
				child_min_h, child_pref_h = child.get_preferred_height(h)
				base_min_h += child_min_h
				base_pref_h += child_pref_h
				min_heights.append(child_min_h)
				pref_heights.append(child_pref_h)
				if self.child_get_property(child, 'expand'):
					num_expanded += 1
			if h < base_pref_h:
				heights = min_heights
				if len(self.children) > 1:
					padding = (h-base_min_h) / (len(self.children)-1)
			elif h < base_pref_h + (len(self.children)-1)*self.padding:
				heights = pref_heights
				if len(self.children) > 1:
					padding = (h-base_pref_h) / (len(self.children)-1)
			else:
				heights = pref_heights
				padding = self.padding
				if num_expanded > 0:
					extra_h = h - base_pref_h - (len(self.children)-1)*padding
					for i in range(len(self.children)):
						if self.child_get_property(self.children[i], 'expand'):
							heights[i] += float(extra_h) / num_expanded
			y = 0.
			for i in range(len(self.children)):
				child_box = clutter.ActorBox()
				if self.child_get_property(self.children[i], 'fill'):
					child_box.x1 = 0.
					child_box.y1 = y
					child_box.x2 = w
					child_box.y2 = y + heights[i]
				else:
					child_pref_w, child_pref_h = (
						self.children[i].get_preferred_size()[2:])
					child_w = min(w, child_pref_w)
					child_h = min(heights[i], child_pref_h)
					child_box.x1 = w/2. - child_w/2.
					child_box.y1 = y + heights[i]/2. - child_h/2.
					child_box.x2 = w/2. + child_w/2.
					child_box.y2 = y + heights[i]/2. + child_h/2.
				y += heights[i] + padding
				self.children[i].allocate(child_box, flags)

	def do_paint(self):
		for child in self.children:
			child.paint()
	
	def do_pick(self, color):
		clutter.Actor.do_pick(self, color)
		for child in self.children:
			child.paint()
	
	def pack(self, child, expand=False, fill=False):
		self.add(child)
		self.child_set_property(child, 'expand', expand)
		self.child_set_property(child, 'fill', fill)

BoxLayout.install_child_meta(BoxLayoutChildMeta)

# vim: set ts=4 sts=4 sw=4 ai noet :
