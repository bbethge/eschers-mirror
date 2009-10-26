import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import pygame
from pygame.locals import *
import time
from InputSource import InputSource
from Signal import Signal
from Config import config

class MainLoop(InputSource):
	"""
	A class that has an event loop and manages a set of Actors
	"""
	def __init__(self):
		InputSource.__init__(self)
		self.drawBackground = Signal()
		self.drawShadows = Signal()
		self.draw = Signal()
		self.drawOverlays = Signal()
		self.actors = set()
		self.delayFunc = None
	
	# TODO: rename to addActor
	def add(self, actor):
		self.actors.add(actor)
	
	# TODO: rename to removeActor
	def remove(self, actor):
		self.actors.remove(actor)
	
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
					self.mouseMotion.emit(event)
				elif event.type == MOUSEBUTTONDOWN:
					self.mouseButtonDown.emit(event)
				elif event.type == MOUSEBUTTONUP:
					self.mouseButtonUp.emit(event)
			
			curTime = time.time()
			deltaT = curTime - prevTime
			for actor in set(self.actors):
				actor.update(deltaT)
			prevTime = curTime
			
			glClear(GL_COLOR_BUFFER_BIT)
			self.drawBackground.emit()
			self.drawShadows.emit()
			self.draw.emit()
			self.drawOverlays.emit()
			pygame.display.flip()
			if self.delayFunc is not None:
				self.delayFunc()
	
	def setDelayFunc(self, func):
		self.delayFunc = func
	
	def quit(self):
		self.__done = True

# vim: set ts=4 sts=4 sw=4 noet :
