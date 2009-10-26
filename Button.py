import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import numpy as np
from Layout import AutosizedLayout
from Actor import Actor
from Signal import Signal

class Button(Actor):
	texCoords = np.array([[0.25], [0.75]]*5, np.double)
	
	def __init__(self, parent, x, y, markup, highlight):
		Actor.__init__(self, parent)
		self.pos = x, y
		self.layout = AutosizedLayout(x, y)
		self.layout.layout.set_markup(markup)
		self.layout.layoutChanged()
		
		self.borderWidth = self.layout.size[1]/6
		
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_1D, self.texture)
		glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAX_LEVEL, 0)
		texels = np.array(
			[list(highlight)+[0], list(highlight)+[255]], np.uint8)
		glTexImage1Dub(GL_TEXTURE_1D, 0, GL_RGBA, 0, GL_RGBA, texels)
		
		bw = self.borderWidth
		self.verts = np.array(
			[   [ bw, bw ],
				[ 0., 0. ],
				[ self.layout.size[0]+bw, bw ],
				[ self.layout.size[0]+2*bw, 0. ],
				[ self.layout.size[0]+bw, self.layout.size[1]+bw ],
				[ self.layout.size[0]+2*bw, self.layout.size[1]+2*bw ],
				[ bw, self.layout.size[1]+bw ],
				[ 0., self.layout.size[1]+2*bw ],
				[ bw, bw ],
				[ 0., 0. ]],
			np.double)
	
		self.hovering = False
		parent.drawOverlays.addHandler(self.__class__.draw, self)
		parent.mouseMotion.addHandler(self.__class__.onMouseMotion, self)
		parent.mouseButtonDown.addHandler(
			self.__class__.onMouseButtonDown, self)
		self.clicked = Signal()
	
	def onMouseMotion(self, event):
		self.hovering = (
			0 <= event.pos[0]-self.pos[0] < self.layout.size[0]+2*self.borderWidth
			and 0 <= event.pos[1]-self.pos[1] < self.layout.size[1]+2*self.borderWidth)
	
	def onMouseButtonDown(self, event):
		if (
				0 <= event.pos[0] - self.pos[0] < self.layout.size[0]
				and 0 <= event.pos[1] - self.pos[1] < self.layout.size[1]):
			self.clicked.emit()
	
	def draw(self):
		glPushMatrix()
		glTranslated(self.pos[0], self.pos[1], 0.)
		glEnable(GL_BLEND)
		if self.hovering:
			glVertexPointerd(self.verts)
			glTexCoordPointerd(self.texCoords)
			glDisable(GL_TEXTURE_2D)
			glEnable(GL_TEXTURE_1D)
			glDrawArrays(GL_QUAD_STRIP, 0, len(self.verts))
			glDisable(GL_TEXTURE_1D)
			glEnable(GL_TEXTURE_2D)
		glTranslated(self.borderWidth, self.borderWidth, 0)
		self.layout.draw()
		glDisable(GL_BLEND)
		glPopMatrix()

# vim: set ts=4 sts=4 sw=4 noet :
