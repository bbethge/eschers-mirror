import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import numpy as np
import pygame
from Actor import Actor
from Config import config
from Signal import Signal

class Scrollbar(Actor):
	
	def __init__(self, parent, pos, height, pageSize, color, initVal=0.):
		"""
		height: height of the scrollbar in pixels
		pageSize: size of the slider, as a fraction of the total length
		self.value is the current value of the scrollbar on a scale of 0 to 1.
		self.pos, self.color, and self.value can be written at any time.
		"""
		Actor.__init__(self, parent)
		self.value = initVal
		self.pos = pos
		self.size = config.window_size[0]/48, height
		self.arrowLength = self.size[0]
		self.color = color
		self.setPageSize(pageSize)
		w, h = self.size
		a = self.arrowLength
		self.verts = np.array(
			[
				[ w/2., 0. ],
				[ 0., a ],
				[ w, a ],
	
				[ w*0.4, a ],
				[ w*0.6, a ],
				[ w*0.6, h-a ],
	
				[ w*0.4, a ],
				[ w*0.6, h-a ],
				[ w*0.4, h-a ],
	
				[ 0., h-a ],
				[ w, h-a ],
				[ w/2., h ]
			], np.double)
		self.scrolled = Signal()
	
	def setPageSize(self, pageSize):
		self.sliderHeight = (
			max(self.size[0], pageSize*(self.size[1]-2*self.arrowLength)))
		self.pageSize = pageSize
		w, h = self.size
		s = self.sliderHeight
		self.sliderVerts = np.array(
			[
				[ w*0.1, w/2. ],
				[ w*0.1, s-w/2. ],
				[ w/2., 0. ],
				[ w/2., s ],
				[ w*0.9, w/2. ],
				[ w*0.9, s-w/2 ]
			], np.double)
	
	def draw(self):
		glPushMatrix()
		glTranslated(self.pos[0], self.pos[1], 0.)
		glDisableClientState(GL_TEXTURE_COORD_ARRAY)
		glDisable(GL_TEXTURE_2D)
		glColor3ub(*self.color)
		glEnable(GL_BLEND)
		glEnable(GL_POLYGON_SMOOTH)
		glVertexPointerd(self.verts)
		glDrawArrays(GL_TRIANGLES, 0, len(self.verts))
		glTranslated(
			0.,
			self.arrowLength
				+ self.value*(self.size[1]-2.*self.size[0]-self.sliderHeight),
			0.)
		glVertexPointerd(self.sliderVerts)
		glDrawArrays(GL_QUAD_STRIP, 0, len(self.sliderVerts))
		glDisable(GL_POLYGON_SMOOTH)
		glDisable(GL_BLEND)
		glEnable(GL_TEXTURE_2D)
		glEnableClientState(GL_TEXTURE_COORD_ARRAY)
		glPopMatrix()
	
	def update(self, deltaT):
		mousePos = pygame.mouse.get_pos()
		if (
				pygame.mouse.get_pressed()[0] and
				0 <= mousePos[0]-self.pos[0] < self.size[0]):
			if 0 <= mousePos[1]-self.pos[1] < self.arrowLength:
				oldVal = self.value
				self.value = max(0., self.value-self.pageSize*deltaT)
				self.scrolled.emit(self.value-oldVal)
			elif -self.arrowLength <= mousePos[1]-self.pos[1]-self.size[1] < 0:
				oldVal = self.value
				self.value = min(1., self.value+self.pageSize*deltaT)
				self.scrolled.emit(self.value-oldVal)

# vim: set ts=4 sts=4 sw=4 ai noet :
