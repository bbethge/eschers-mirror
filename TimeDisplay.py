#!/usr/bin/env python

import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
import pygame
from pygame.locals import *
import cairo
import pango
import pangocairo
import numpy as np
from Config import config
from Actor import Actor

class TimeDisplay(Actor):
	def __init__(self, grid, time):
		Actor.__init__(self, grid)
		timeStr = "%d:%02d" % (int(time/60), int(time%60))
		surface = cairo.ImageSurface(cairo.FORMAT_A8, config.window_size[0], config.window_size[1])
		cairoCtx = cairo.Context(surface)
		pangoCtx = pangocairo.CairoContext(cairoCtx)
		layout = pangoCtx.create_layout()
		layout.set_markup("""\
<span foreground="yellow"><span size="large">Congratulations!</span>
Your time is
<span size="72000">%s</span></span>""" % timeStr)
		layout.set_alignment(pango.ALIGN_CENTER)
		pangoCtx.show_layout(layout)
		self.size = layout.get_pixel_size()
		arrData = np.frombuffer(surface.get_data(), np.uint8)
		arrData = arrData.reshape((config.window_size[1],config.window_size[0]))
		color = np.array([255, 255, 0, 255], np.uint8)
		self.pixelData = np.tile(color, (self.size[1], self.size[0], 1))
		self.pixelData[:,:,3] = arrData[:self.size[1], :self.size[0]]
		del surface
		
		self.pos = [
			(self.grid.vidSize[0] - self.size[0])/2.,
			(self.grid.vidSize[1] - self.size[1])/2.]
	
		self.grid.drawOverlays.addHandler(self.__class__.draw, self)
		self.time = 0.
		self.state = 'sitting'
	
	def update(self, deltaT):
		if self.state == 'sitting':
			if self.time < 3.:
				self.time += deltaT
			else:
				self.state = 'falling'
				self.time = 0.
		elif self.state == 'falling':
			if self.pos[1]+self.size[1] > -self.grid.vidOrigin[1]:
				self.time += deltaT
				self.pos[1] += -1500 * self.time * deltaT
			else:
				self.die()
	
	def draw(self):
		glDisable(GL_TEXTURE_2D)
		glEnable(GL_BLEND)
		glColor4d(0., 0., 0., 0.5)
		glRectd(
			self.pos[0], self.pos[1],
			self.pos[0] + self.size[0], self.pos[1] + self.size[1])
		glRasterPos2d(self.pos[0], self.pos[1]+self.size[1])
		oldZoomX = glGetDouble(GL_ZOOM_X)
		oldZoomY = glGetDouble(GL_ZOOM_Y)
		glPixelZoom(1., -1.)
		glDrawPixels(
			self.size[0], self.size[1], GL_RGBA, GL_UNSIGNED_BYTE,
			self.pixelData)
		glPixelZoom(oldZoomX, oldZoomY)
		glDisable(GL_BLEND)
		glEnable(GL_TEXTURE_2D)

# vim: set ts=4 sts=4 sw=4 noet :
