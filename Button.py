import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import numpy as np
from Layout import AutosizedLayout
from Actor import Actor
from Signal import Signal
from MainLoop import mainLoop

class Button(Actor):
	texCoords = np.array([[0.25], [0.75]]*5, np.double)
	
	def __init__(self, parent, x, y, markup, color):
		Actor.__init__(self, parent)
		self.pos = x, y
		self.layout = AutosizedLayout(x, y)
		self.layout.layout.set_markup(markup)
		self.layout.setColor(color)
		self.layout.layoutChanged()
		
		self.borderWidth = self.layout.size[1]/6
		self.color = color
	
		self.hovering = False
		self.clicked = Signal()
	
	def contains(self, pos):
		return (
			0 <= pos[0]-self.pos[0]
				< self.layout.size[0]+2*self.borderWidth
			and 0 <= pos[1]-self.pos[1]
				< self.layout.size[1]+2*self.borderWidth)
	
	def onMouseMotion(self, event):
		nowHovering = self.contains(event.pos)
		if self.hovering and not nowHovering:
			self.layout.setColor(self.color)
		elif not self.hovering and nowHovering:
			self.layout.setColor( (0, 0, 0) )
		self.hovering = nowHovering
	
	def onMouseButtonDown(self, event):
		if self.contains(event.pos) and event.button == 1:
			self.clicked.emit()
	
	def draw(self):
		glPushMatrix()
		glTranslated(self.pos[0], self.pos[1], 0.)
		glEnable(GL_BLEND)
		glDisable(GL_TEXTURE_2D)
		if self.hovering:
			glColor4ub(self.color[0], self.color[1], self.color[2], 150)
		else:
			glColor4ub(0, 0, 0, 150)
		glRectd(
			0, 0, self.layout.size[0]+2*self.borderWidth,
			self.layout.size[1]+2*self.borderWidth)
		glEnable(GL_TEXTURE_2D)
		glTranslated(self.borderWidth, self.borderWidth, 0)
		self.layout.draw()
		glDisable(GL_BLEND)
		glPopMatrix()

# vim: set ts=4 sts=4 sw=4 noet :
