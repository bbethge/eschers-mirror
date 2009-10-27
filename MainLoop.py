import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import pygame
from pygame.locals import *
import time
from Container import Container
from Signal import Signal
from Config import config

class MainLoop(Container):
	"""
	A class that has an event loop and manages a set of Actors
	"""
	def __init__(self):
		Container.__init__(self)
		self.delayFunc = None
	
	def run(self):
		"""
		Run the event loop until this Stage is done with its job
		"""
		prevTime = time.time()
		self.__done = False
		while not self.__done:
			while True:
				event = pygame.event.poll()
				if event.type == NOEVENT:
					break
				elif event.type == QUIT:
					self.quit()
					break
				elif event.type == MOUSEMOTION:
					for actor in set(self.actors):
						actor.onMouseMotion(event)
				elif event.type == MOUSEBUTTONDOWN:
					for actor in set(self.actors):
						actor.onMouseButtonDown(event)
				elif event.type == MOUSEBUTTONUP:
					for actor in set(self.actors):
						actor.onMouseButtonUp(event)
			
			curTime = time.time()
			deltaT = curTime - prevTime
			for actor in set(self.actors):
				actor.update(deltaT)
			prevTime = curTime
			
			glClear(GL_COLOR_BUFFER_BIT)
			for actor in self.actors:
				actor.draw()
			pygame.display.flip()
			if self.delayFunc is not None:
				self.delayFunc()
	
	def setDelayFunc(self, func):
		self.delayFunc = func
	
	def quit(self):
		self.__done = True

# The singleton MainLoop object
mainLoop = MainLoop()

# vim: set ts=4 sts=4 sw=4 noet :
