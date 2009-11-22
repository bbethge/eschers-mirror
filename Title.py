import xml
import xml.parsers
import xml.parsers.expat
import random
import clutter
from clutter import cogl

class Title(clutter.Actor):
	__gtype_name__ = 'Title'

	def __init__(self, svgFileName):
		clutter.Actor.__init__(self)

		parser = xml.parsers.expat.ParserCreate()
		self.letters = []
		self.inLayerGroup = False
		parser.StartElementHandler = self.on_start_element
		parser.EndElementHandler = self.on_end_element

		file = open(svgFileName)
		parser.ParseFile(file)
		file.close()

		self.velocities = (
			[ random.uniform(-5,5) for n in range(len(self.letters)) ])
		self.positions = [0.] * len(self.letters)

		# TODO: fix hard-coded path
		texture = cogl.texture_new_from_file(
			'/home/ben/background.jpg', cogl.TEXTURE_NONE,
			cogl.PIXEL_FORMAT_ANY)
		self.material = cogl.Material()
		self.material.set_layer(0, texture)

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
				self.letters.append(clutter.Path(attrs['d']))
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
		for i in range(len(self.letters)):
			self.positions[i] += self.velocities[i] * delta / 1000.
		self.queue_redraw()

	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		w, h = x2-x1, y2-y1

		scale = w / self.logo_width
		cogl.scale(scale, scale, 1.)
		cogl.translate(0., (h-self.logo_height*scale) / 2., 0.)

		matrix = cogl.Matrix()

		cogl.set_source(self.material)
		for n in range(len(self.letters)):
			matrix.init_identity()
			matrix.rotate(self.positions[n], 0, 0, 1)
			self.material.set_layer_matrix(0, matrix)
			for i in range(self.letters[n].get_n_nodes()):
				node = self.letters[n].get_node(i)
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
			cogl.path_move_to(0, 0)

# vim: set ts=4 sts=4 sw=4 ai noet :
