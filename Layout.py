import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import pygame
from pygame.locals import *
import pango
import cairo
import pangocairo
import numpy as np

def nextPowerOf2(n):
	result = 1
	while result < n:
		result *= 2
	return result

class Layout:
	"""
	An object that manages a Pango layout with a particular location on the
	screen and renders it to a texture
	"""
	
	texCoords = np.array(
		[   [ 0, 0 ],
			[ 1, 0 ],
			[ 1, 1 ],
			[ 0, 1 ] ],
		np.double)
	
	def __init__(self, x, y, width, height):
		"""
		This should only be called by subclasses.
		"""
		self.size = width, height
		self.setUpLayout()
		
		# Make a texture object for ourselves
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
	
	def setUpLayout(self):		
		"""
		Set up the Pango red tape needed to create a layout
		"""
		self.surface = cairo.ImageSurface(
			cairo.FORMAT_ARGB32, self.size[0], self.size[1])
		self.cairoCtx = cairo.Context(self.surface)
		self.pangoCtx = pangocairo.CairoContext(self.cairoCtx)
		self.layout = self.pangoCtx.create_layout()
	
	def sizeChanged(self):
		"""
		(Re)initialize things that depend on the size of the rectangle
		"""
		# Request the texture to be the smallest valid size that we will fit
		# into
		texWidth = nextPowerOf2(self.size[0])
		texHeight = nextPowerOf2(self.size[1])
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexImage2D(
			GL_TEXTURE_2D, 0, GL_RGBA, texWidth, texHeight, 0, GL_BGRA,
			GL_UNSIGNED_INT_8_8_8_8_REV, None)
		
		# Create vertex arrays for drawing our rectangle
		self.verts = np.array(
			[   [ 0, 0 ],
				[ self.size[0], 0 ],
				[ self.size[0], self.size[1] ],
				[ 0, self.size[1] ] ],
			np.double)
		self.texMatrix = np.array(
			[   [ float(self.size[0])/texWidth, 0., 0., 0. ],
				[ 0., float(self.size[1])/texHeight, 0., 0. ],
				[ 0., 0., 1., 0, ],
				[ 0., 0., 0., 1. ] ],
			np.double)
	
	def layoutChanged(self):
		"""
		This should be called by the client after it changes self.layout.
		"""
		# Erase the cairo surface
		self.cairoCtx.set_operator(cairo.OPERATOR_CLEAR)
		self.cairoCtx.paint()
		self.cairoCtx.set_operator(cairo.OPERATOR_OVER)
		
		# Re-render the layout and copy the result into our texture
		self.pangoCtx.show_layout(self.layout)
		pixels = str(self.surface.get_data())
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexSubImage2D(
			GL_TEXTURE_2D, 0, 0, 0,
			self.size[0], self.size[1], GL_BGRA,
			GL_UNSIGNED_INT_8_8_8_8_REV, pixels)
		
		self.pangoCtx.update_layout(self.layout)
	
	def draw(self):
		glEnable(GL_BLEND)
		# For use with premultiplied alpha produced by Cairo
		glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
		
		glMatrixMode(GL_TEXTURE)
		glPushMatrix()
		glLoadMatrixd(self.texMatrix)
		
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexCoordPointerd(self.texCoords)
		glVertexPointerd(self.verts)
		glDrawArrays(GL_QUADS, 0, 4)
		
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glDisable(GL_BLEND)
	
	def xy_to_index(self, x, y):
		index = self.layout.xy_to_index(
			int(pango.SCALE * x), int(pango.SCALE * y)) [0]
		if index < 0:
			raise RuntimeError("Pango returned bad index")
		return index
	
	def setColor(self, color):
		layoutAttrs = self.layout.get_attributes() or pango.AttrList()
		layoutAttrs.insert(
			pango.AttrForeground(
				color[0]*0x100, color[1]*0x100, color[2]*0x100,
				0, len(self.layout.get_text())))
		self.layout.set_attributes(layoutAttrs)
		self.layoutChanged()

class AutosizedLayout(Layout):
	def __init__(self, x, y):
		Layout.__init__(self, x, y, 0, 0)
	
	def layoutChanged(self, sameSize=False):
		if not sameSize:
			# Recompute the size of the layout
			self.size = self.layout.get_pixel_size()
			# Save the text and attributes of self.layout since it will be
			# recreated in setUpLayout().
			text = self.layout.get_text()
			attrs = self.layout.get_attributes()
			self.setUpLayout()
			# Restore text and attributes to the newly-created layout
			self.layout.set_text(text)
			if attrs is not None:
				self.layout.set_attributes(attrs)
			self.sizeChanged()
		
		Layout.layoutChanged(self)

class ScrollableLayout(Layout):
	def __init__(self, x, y, width, height):
		Layout.__init__(self, x, y, width, height)
		self.sizeChanged()
		self.scrollAmount = [ 0, 0 ]

	def scroll(self, deltaX, deltaY):
		# This depends on the fact that, unlike AutosizeLayout, we do not
		# recreate our Cairo context after initialization
		self.cairoCtx.translate(-deltaX, -deltaY)
		self.scrollAmount[0] += deltaX
		self.scrollAmount[1] += deltaY
		self.layoutChanged()

	def scrollTo(self, x, y):
		self.cairoCtx.identity_matrix()
		self.cairoCtx.translate(-x, -y)
		self.scrollAmount = x, y
		self.layoutChanged()
	
	def xy_to_index(self, x, y):
		return Layout.xy_to_index(
			self, x+self.scrollAmount[0], y+self.scrollAmount[1])

# vim: set ts=4 sts=4 sw=4 ai noet :
