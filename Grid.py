#!/usr/bin/env python

import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import pygame
from pygame.locals import *
import os
import numpy as np
import sys
from glob import glob
sys.path += glob(os.path.join('build', '*', ''))
import VideoDecode
import time
import bisect
from Config import config
from Signal import Signal
from Actor import Stage

class Grid(Stage):
	"""
	The base class for all grid types, which manage the state of a puzzle.
	
	Data members:
	vidSize: the pixel size of the video as it appears on-screen
	vidOrigin: the window coordinates of the origin (lower left) of where the 
	           video will be drawn
	vidAspect: the aspect ratio the video should be displayed at
	srcVidSize: the pixel size of the source video, which is stored in a texture
	vidTex: the texture object holding the current video frame
	"""
	def __init__(self, videoFile):
		Stage.__init__(self)
		# Set up vidTex
		self.vidTex = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.vidTex)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		
		VideoDecode.init(
			os.path.join(os.path.expanduser('~'), '.xine', 'config'),
			videoFile)
		self.vidSize = 1, 1
		self.vidAspect = 1.
		self.vidOrigin = 0, 0
		self.srcVidSize = 1, 1
		self.drawFixedTiles = Signal()
		self.drawFlyingTiles = Signal()
		self.drawOverlays = Signal()
		self.startGrab = Signal()
		self.endGrab = Signal()
		self.rotateTile = Signal()
	
	def run(self):
		"""
		Run the main event loop for the puzzle.  This will not return until the 
		puzzle is finished -- either won, lost, or aborted.
		"""
		VideoDecode.start()
		oldTime = time.time()
		done = False
		while not done and VideoDecode.isPlaying():
			width, height, aspect, data = VideoDecode.getFrame(20)
			if width != None:
				self.handleFrame((width,height), aspect, data)
			while True:
				event = pygame.event.poll()
				if event.type == NOEVENT:
					break
				if event.type == QUIT:
					done = True
					break
				self.handleEvent(event)
			curTime = time.time()
			deltaT = curTime - oldTime
			oldTime = curTime
			# Actors may remove themselves during the update, so we must iterate 
			# over a copy of self.actors.  FIXME: what if actors remove other
			# actors?  FIXME: move this to Stage somehow.
			for actor in set(self.actors):
				actor.update(deltaT)
			glClear(GL_COLOR_BUFFER_BIT)
			# What happens if there is no current texture image attached to
			# self.vidTex because we haven't received a frame yet?
			self.draw()
			self.drawOverlays.emit()
			pygame.display.flip()
		VideoDecode.stop()
		VideoDecode.quit()
	
	def handleFrame(self, size, aspect, data):
		if self.vidSize != size or self.vidAspect != aspect:
			self.handleSizeChange(size[0], size[1], aspect)
		glBindTexture(GL_TEXTURE_2D, self.vidTex)
		glTexSubImage2D(
			GL_TEXTURE_2D, 0, 0, 0, size[0], size[1],
			GL_RGB, GL_UNSIGNED_BYTE, data)
	
	def handleEvent(self, event):
		if event.type == MOUSEBUTTONDOWN:
			if event.button == 1: # left?
				self.grabTile(self.transformMousePos(*event.pos))
			elif event.button == 3: # right?
				self.rotateTile.emit(1)
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				self.releaseTile(self.transformMousePos(*event.pos))
		elif event.type == KEYDOWN:
			if event.key == K_r:
				if event.mod & KMOD_SHIFT:
					self.rotateTile.emit(-1)
				else:
					self.rotateTile.emit(1)
	
	def handleSizeChange(self, width, height, aspect):
		if aspect >= float(config.window_size[0])/config.window_size[1]:
			self.vidSize = config.window_size[0], round(config.window_size[0]/aspect)
		else:
			self.vidSize = round(config.window_size[1]*aspect), config.window_size[1]
		self.vidOrigin = [ (w-v)/2 for w, v in zip(config.window_size, self.vidSize) ]
		self.vidAspect = aspect
		self.srcVidSize = width, height
		# Find the smallest power-of-2--sized square that can contain the frame
		texSize = 1
		while texSize < max(width, height):
			texSize *= 2
		glBindTexture(GL_TEXTURE_2D, self.vidTex)
		# Set the active texture to a blank texSize*texSize square (the image 
		# will be filled in later).
		texInitializer = np.zeros((texSize,texSize,3), np.uint8)
		glTexImage2Dub(GL_TEXTURE_2D, 0, GL_RGB, 0, GL_RGB, texInitializer)
		# Set up the texture matrix to compensate for the pixel data being in
		# top-to-bottom order.
		glMatrixMode(GL_TEXTURE)
		glLoadIdentity()
		glScaled(1./texSize, -1./texSize, 1.)
		glTranslated(0., -float(height), 0.)
		# Set up the projection matrix so that the origin is at the lower left
		# corner of the video.
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(
			-self.vidOrigin[0], config.window_size[0]-self.vidOrigin[0],
			-self.vidOrigin[1], config.window_size[1]-self.vidOrigin[1],
			-1.0, 1.0)
		glMatrixMode(GL_MODELVIEW)
	
	def draw(self):
		pass
	
	def grabTile(self, pos):
		"""
		Grab the tile under the cursor
		"""
		self.startGrab.emit(pos)
	
	def releaseTile(self, pos):
		"""
		Release the currently grabbed tile
		"""
		self.endGrab.emit(pos)
		if self.isSolved():
			TimeDisplay(self, VideoDecode.getPosition())
	
	def isSolved(self):
		"""
		Does self have all its tiles in the right place?
		"""
		pass
	
	def shuffle(self):
		"""
		Randomize the locations of the tiles
		"""
		pass

	def transformMousePos(self, x, y):
		"""
		Transform window coordinates into coordinates relative to the video
		origin
		"""
		return x - self.vidOrigin[0], config.window_size[1] - self.vidOrigin[1] - y
	
	def getMousePos(self):
		"""
		Return the current mouse pointer location relative to the video origin
		"""
		return self.transformMousePos(*pygame.mouse.get_pos())

# vim: set ts=4 sts=4 sw=4 noet :
