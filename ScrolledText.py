import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from ActorContainer import ActorContainer
from Scrollbar import Scrollbar
from Layout import ScrollableLayout

class ScrolledText(ActorContainer):
	scrollAmount = 4
	
	def __init__(self, parent, pos, size, color, markup):
		ActorContainer.__init__(self, parent)
		self.pos = pos
		self.size = size
		self.scrollbar = Scrollbar(self, pos, size[1], 1., color)
		self.scrollbar.pos = (
			self.pos[0]+self.size[0]-self.scrollbar.size[0], self.pos[1])
		self.layout = ScrollableLayout(
			pos[0], pos[1], size[0]-self.scrollbar.size[0], size[1])
		self.layout.layout.set_markup(markup)
		self.layout.layoutChanged()
		self.layoutHeight = self.layout.layout.get_pixel_size()[1]
		if self.size[1] < self.layoutHeight:
			self.scrollbar.setPageSize(float(self.size[1])/self.layoutHeight)
		self.scrollPos = 0
		self.scrollbar.scrolled.addHandler(
			self.__class__.onScrollbarScrolled, self)
	
	def draw(self):
		ActorContainer.draw(self)
		glPushMatrix()
		glTranslated(self.pos[0], self.pos[1], 0.)
		self.layout.draw()
		glPopMatrix()
	
	def die(self):
		self.scrollbar.scrolled.removeHandler(
			self.__class__.onScrollbarScrolled, self)
		ActorContainer.die(self)

	def onScrollbarScrolled(self, amount):
		dist = amount * (self.layoutHeight-self.size[1])
		self.scrollPos += dist
		self.layout.scroll(0, dist)
	
	def onMouseButtonDown(self, event):
		if (
				0 <= event.pos[0]-self.pos[0] < self.size[0]
				and 0 <= event.pos[1]-self.pos[1] < self.size[1]):
			if event.button == 5:  # Scroll down
				amount = min(
					self.layoutHeight-self.scrollPos-self.size[1],
					self.scrollAmount)
				self.scrollPos += amount
				self.layout.scroll(0, amount)
				self.scrollbar.value = (
					float(self.scrollPos) / (self.layoutHeight-self.size[1]))
			elif event.button == 4:  # Scroll up
				amount = min(self.scrollPos, self.scrollAmount)
				self.scrollPos -= amount
				self.layout.scroll(0, -amount)
				self.scrollbar.value = (
					float(self.scrollPos) / (self.layoutHeight-self.size[1]))

# vim: set ts=4 sts=4 sw=4 ai noet :
