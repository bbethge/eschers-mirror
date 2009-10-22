import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import pygame
from pygame.locals import *
import time

class Actor:
	"""
	A class for objects that behave on their own
	"""
	def __init__(self, grid):
		"""
		grid: the grid (puzzle) object that manages this object
		"""
		self.grid = grid
		grid.add(self)
	
	def update(self, deltaT):
		"""
		This is called by the grid before every frame so the object can update
		its state.
		deltaT: time in seconds since last update; zero if this is the first
		        update
		"""
		pass
	
	def die(self):
		self.grid.remove(self)

class Stage:
	"""
	A class that has an event loop and manages a set of Actors
	"""
	def __init__(self):
		self.actors = set()
		self.result = None
	
	def add(self, actor):
		self.actors.add(actor)
	
	def remove(self, actor):
		self.actors.remove(actor)
	
	def run(self):
		"""
		Run the event loop until this Stage is done with its job
		"""
		self.__done = False
		while not self.__done:
			while True:
				event = pygame.event.poll()
				if event.type == NOEVENT:
					break
				elif event.type == QUIT:
					self.quit()
					break
				else:
					self.handleEvent(event)
			glClear(GL_COLOR_BUFFER_BIT)
			self.draw()
			pygame.display.flip()
			time.sleep(0.030)
		return self.result
	
	def draw(self):
		"""
		Draw everything on the screen.  It is not necessary to clear the
		framebuffer or swap buffers.
		"""
	
	def handleEvent(self, event):
		pass
	
	def quit(self, result=None):
		self.__done = True
		self.result = result

# vim: set ts=4 sts=4 sw=4 noet :
