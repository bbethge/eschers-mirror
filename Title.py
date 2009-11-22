import xml
import xml.parsers
import xml.parsers.expat
import random
import clutter
from clutter import cogl

class Character:
	def __init__(self, path_string, material, logo_w, logo_h):
		self.path = clutter.Path(path_string)
		self.material = material

		x1, y1 = self.path.get_node(0)[0]
		x2, y2 = x1, y1
		for n in range(1, self.path.get_n_nodes()):
			node = self.path.get_node(n)
			if (
					node.type == clutter.PATH_MOVE_TO
					or node.type == clutter.PATH_LINE_TO
			):
				x1 = min(x1, node[0][0])
				y1 = min(y1, node[0][1])
				x2 = max(x2, node[0][0])
				y2 = max(y2, node[0][1])

		self.x = x1 / logo_w
		self.y = y1 / logo_h
		self.vel_x = random.uniform(-0.2, 0.2)
		self.vel_y = random.uniform(-0.2, 0.2)
		self.width = (x2-x1) / logo_w
		self.height = (y2-y1) / logo_h

	def update(self, delta):
		self.x += self.vel_x * delta / 1000.
		if self.x < 0.:
			self.x = 0.
			self.vel_x = abs(self.vel_x)
		elif self.x + self.width > 1.:
			self.x = 1. - self.width
			self.vel_x = -abs(self.vel_x)

		self.y += self.vel_y * delta / 1000.
		if self.y < 0.:
			self.y = 0.
			self.vel_y = abs(self.vel_y)
		elif self.y + self.height > 1.:
			self.y = 1. - self.height
			self.vel_y = -abs(self.vel_y)
	
	def paint(self):
		matrix = cogl.Matrix()
		matrix.translate(self.x, self.y, 0.)
		matrix.scale(self.width, self.height, 1.)
		self.material.set_layer_matrix(0, matrix)
		cogl.set_source(self.material)
		cogl.path_new()
		for n in range(self.path.get_n_nodes()):
			node = self.path.get_node(n)
			if node.type == clutter.PATH_MOVE_TO:
				cogl.path_move_to(*node[0])
			elif node.type == clutter.PATH_LINE_TO:
				cogl.path_line_to(*node[0])
			elif node.type == clutter.PATH_REL_MOVE_TO:
				cogl.path_rel_move_to(*node[0])
			elif node.type == clutter.PATH_REL_LINE_TO:
				cogl.path_rel_line_to(*node[0])
			elif node.type == clutter.PATH_CLOSE:
				cogl.path_close()
		cogl.path_fill()

class Title(clutter.Actor):
	__gtype_name__ = 'Title'

	def __init__(self, svgFileName):
		clutter.Actor.__init__(self)

		# TODO: fix hard-coded path
		texture = cogl.texture_new_from_file(
			'/home/ben/background.jpg', cogl.TEXTURE_NONE,
			cogl.PIXEL_FORMAT_ANY)
		self.material = cogl.Material()
		self.material.set_layer(0, texture)

		parser = xml.parsers.expat.ParserCreate()
		self.letters = []
		self.inLayerGroup = False
		parser.StartElementHandler = self.on_start_element
		parser.EndElementHandler = self.on_end_element

		file = open(svgFileName)
		parser.ParseFile(file)
		file.close()

		self.timeline = clutter.Timeline(1000)
		self.timeline.set_loop(True)
		self.timeline.connect('new-frame', lambda t,p: self.on_new_frame())
		self.timeline.start()
	
	def on_start_element(self, name, attrs):
		if name == 'g':
			if not self.inLayerGroup:
				self.inLayerGroup = True
			else:
				raise RuntimeError("Unexpected SVG file structure")
		elif name == 'path':
			if self.inLayerGroup:
				self.letters.append(
					Character(
						attrs['d'], self.material,
						self.logo_width, self.logo_height))
			else:
				raise RuntimeError("Unexpected SVG file structure")
		elif name == 'svg':
			self.logo_width = float(attrs['width'])
			self.logo_height = float(attrs['height'])

	def on_end_element(self, name):
		if name == 'g':
			if self.inLayerGroup:
				self.inLayerGroup = False

	def on_new_frame(self):
		delta = self.timeline.get_delta()
		for letter in self.letters:
			letter.update(delta)
		self.queue_redraw()

	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		w, h = x2-x1, y2-y1

		scale = w / self.logo_width
		cogl.scale(scale, scale, 1.)
		cogl.translate(0., (h-self.logo_height*scale) / 2., 0.)

		matrix = cogl.Matrix()
		matrix.init_identity()
		self.material.set_layer_matrix(0, matrix)
		cogl.set_source(self.material)
		cogl.rectangle(0, 0, self.logo_width, self.logo_height)

		for letter in self.letters:
			letter.paint()

# vim: set ts=4 sts=4 sw=4 ai noet :
