import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import numpy as np
from Layout import AutosizedLayout
from Actor import Actor
from Signal import Signal

class Button(Actor):
	verts = np.array(
		[   [ 0.5, 0.5 ],
			[ 0., 0. ],
			[ 0., 1. ],
			[ 1., 1. ],
			[ 1., 0. ],
			[ 0., 0. ]],
		np.double)
	
	def __init__(self, parent, x, y, markup, highlight):
		Actor.__init__(self, parent)
		self.pos = x, y
		self.layout = AutosizedLayout(x, y)
		self.layout.layout.set_markup(markup)
		self.layout.layoutChanged()
		self.colors = np.array(
			[ list(highlight) + [ 0. ] ] + [ list(highlight) + [ 1. ] ] * 5,
			np.double)
		self.hovering = False
		parent.drawOverlays.addHandler(self.__class__.draw, self)
		parent.mouseMotion.addHandler(self.__class__.onMouseMotion, self)
		parent.mouseButtonDown.addHandler(
			self.__class__.onMouseButtonDown, self)
		self.clicked = Signal()
	
	def onMouseMotion(self, event):
		self.hovering = (
			0 <= event.pos[0] - self.pos[0] < self.layout.size[0]
			and 0 <= event.pos[1] - self.pos[1] < self.layout.size[1])
	
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
			print 'hovering'
			glPushMatrix()
			glScaled(self.layout.size[0], self.layout.size[1], 1.)
			glEnableClientState(GL_COLOR_ARRAY)
			glDisableClientState(GL_TEXTURE_COORD_ARRAY)
			glVertexPointerd(self.verts)
			glColorPointerd(self.colors)
			glDisable(GL_TEXTURE_2D)
			glDrawArrays(GL_TRIANGLE_FAN, 0, len(self.verts))
			glEnable(GL_TEXTURE_2D)
			glEnableClientState(GL_TEXTURE_COORD_ARRAY)
			glDisableClientState(GL_COLOR_ARRAY)
			glPopMatrix()
		self.layout.draw()
		glDisable(GL_BLEND)
		glPopMatrix()

# vim: set ts=4 sts=4 sw=4 noet :
