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
		[   [ 0, 1 ],
			[ 1, 1 ],
			[ 1, 0 ],
			[ 0, 0 ] ],
		np.double)
	
	def __init__(self, x, y, width, height):
		self.pos = x, y
		self.size = width, height
		self.scrollAmount = [ 0, 0 ]
		
		# Make a texture object for ourselves
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		
		# Request the texture to be the smallest valid size that we will fit
		# into
		texWidth = nextPowerOf2(width)
		texHeight = nextPowerOf2(height)
		glTexImage2D(
			GL_TEXTURE_2D, 0, GL_RGBA, texWidth, texHeight, 0, GL_BGRA,
			GL_UNSIGNED_INT_8_8_8_8_REV, None)
		
		# Set up the Pango red tape needed to render a layout to memory
		self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
		self.cairoCtx = cairo.Context(self.surface)
		self.pangoCtx = pangocairo.CairoContext(self.cairoCtx)
		self.layout = self.pangoCtx.create_layout()
		
		# Create vertex arrays for drawing our rectangle
		self.verts = np.array(
			[   [ x, y ],
				[ x+width, y ],
				[ x+width, y+height ],
				[ x, y+height ] ],
			np.double)
		self.texMatrix = np.array(
			[   [ float(width)/texWidth, 0., 0., 0. ],
				[ 0., float(height)/texHeight, 0., 0. ],
				[ 0., 0., 1., 0, ],
				[ 0., 0., 0., 1. ] ],
			np.double)
	
	def layoutChanged(self):
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
		
		glTexCoordPointerd(self.texCoords)
		glVertexPointerd(self.verts)
		glDrawArrays(GL_QUADS, 0, 4)
		
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glDisable(GL_BLEND)
	
	def scroll(self, deltaX, deltaY):
		self.cairoCtx.translate(-deltaX, deltaY)
		self.scrollAmount[0] += deltaX
		self.scrollAmount[1] += deltaY
		self.layoutChanged()
	
	def xy_to_index(self, x, y):
		index = self.layout.xy_to_index(
			pango.SCALE * (x+self.scrollAmount[0]),
			pango.SCALE * (y-self.scrollAmount[1])) [0]
		if index < 0:
			raise RuntimeError("Pango returned bad index")
		return index

# vim: set ts=4 sts=4 sw=4 noet :
