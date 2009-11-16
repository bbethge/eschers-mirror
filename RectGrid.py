import gobject
import clutter
from clutter import cogl
import itertools
from math import *  # math is delicious
import random
from Grid import Grid

class RectTile(clutter.Rectangle):
	__gtype_name__ = 'RectTile'

	def __init__(self, loc):
		clutter.Rectangle.__init__(self)
		self.set_reactive(True)
		self.src_loc = loc
		self.loc = loc

	def set_loc(self, loc):
		self.loc = loc

	def in_correct_place(self):
		return self.src_loc == self.loc
	
	def do_paint(self):
		x1, y1, x2, y2 = self.get_allocation_box()
		w, h = x2-x1, y2-y1
		rows = self.get_parent().rows
		cols = self.get_parent().cols

		cogl.set_source(self.get_parent().get_material())
		cogl.rectangle_with_texture_coords(
			0, 0, w, h,
			float(self.src_loc[0])/cols, float(self.src_loc[1])/rows,
			float(self.src_loc[0]+1)/cols, float(self.src_loc[1]+1)/rows)

class RectGridChildMeta(clutter.ChildMeta):
	__type_name__ = 'RectGridChildMeta'
	__gproperties__ = {
		'button-press-handler': (
			gobject.TYPE_ULONG, 'Button press handler',
			'ID of signal handler installed by grid for button press events',
			0, gobject.G_MAXULONG, 0,
			gobject.PARAM_CONSTRUCT|gobject.PARAM_READWRITE) }

	def __init__(self):
		clutter.ChildMeta.__init__(self)
		self.button_press_handler = 0
	
	def do_get_property(self, pspec):
		if pspec.name == 'button-press-handler':
			return self.button_press_handler
	
	def do_set_property(self, pspec, value):
		if pspec.name == 'button-press-handler':
			self.button_press_handler = value

class RectGrid(Grid, clutter.Container):
	__gtype_name__ = 'RectGrid'

	def __init__(self, videoFile, rows, cols):
		Grid.__init__(self, videoFile)
		self.cols = cols
		self.rows = rows
		self.children = []
		self.grabbed_tile = None

		for loc in itertools.product(range(cols), range(rows)):
			tile = RectTile(loc)
			self.add(tile)
		self.shuffle()

		self.set_reactive(True)
		self.connect('motion-event', self.__class__.on_mouse_motion)
		self.connect('button-release-event', self.__class__.on_button_release)

	def set_grabbed_tile(self, tile):
		self.grabbed_tile = tile

	def do_add(self, *children):
		for child in children:
			if child in self.children:
				raise Exception(
					"Actor %s is already a child of %s" % (child, self))
			self.children.append(child)
			child.set_parent(self)
			self.child_set_property(
				child, 'button-press-handler',
				child.connect('button-press-event', self.on_child_button_press))
			self.queue_relayout()
	
	def do_remove(self, *children):
		for child in children:
			if child not in self.children:
				raise Exception(
					"Actor %s is not a child of %s" % (child, self))
			self.children.remove(child)
			child.disconnect(
				self.child_get_property(child, 'button-press-handler'))
			self.child_set_property(child, 'button-press-handler', 0)
			child.unparent()
			self.queue_relayout()

	def do_foreach(self, func, data):
		for child in self.children:
			func(child, data)

	def do_allocate(self, box, flags):
		Grid.do_allocate(self, box, flags)
		w, h = box.size

		for child in self.children:
			child_box = clutter.ActorBox()

			if child is self.grabbed_tile:
				child_box.x1 = self.mouse_pos[0] + self.grab_offset[0]
				child_box.y1 = self.mouse_pos[1] + self.grab_offset[1]
				child_box.x2 = child_box.x1 + w/self.cols
				child_box.y2 = child_box.y1 + h/self.rows
			else:
				child_box.x1 = child.loc[0] * w / self.cols
				child_box.y1 = child.loc[1] * h / self.rows
				child_box.x2 = (child.loc[0]+1) * w / self.cols
				child_box.y2 = (child.loc[1]+1) * h / self.rows

			child.allocate(child_box, flags)

	def do_paint(self):
		for child in self.children:
			if child is not self.grabbed_tile:
				child.paint()
		if self.grabbed_tile is not None:
			self.grabbed_tile.paint()
	
	def do_pick(self, color):
		Grid.do_pick(self, color)
		for child in self.children:
			child.paint()

	def on_child_button_press(self, child, event):
		self.grabbed_tile = child
		mouse_x, mouse_y = self.transform_stage_point(event.x, event.y)
		child_x, child_y = child.get_position()
		self.grab_offset = child_x-mouse_x, child_y-mouse_y

	def on_mouse_motion(self, event):
		if self.grabbed_tile is not None:
			self.mouse_pos = self.transform_stage_point(event.x, event.y)
			self.queue_relayout()

	def on_button_release(self, event):
		if self.grabbed_tile is not None:
			self.grabbed_tile = None
			self.queue_relayout()

	def is_solved(self):
		for tile in self.children:
			if not tile.in_correct_place():
				return False
		return True
	
	def shuffle(self):
		unshuf = list(self.children)
		while len(unshuf) > 1:
			tile = unshuf.pop()
			other_tile = random.choice(unshuf)
			tile.loc, other_tile.loc = other_tile.loc, tile.loc

RectGrid.install_child_meta(RectGridChildMeta)

#class RightTriTile(Actor):
#	verts = np.array(
#		[	[-0.5, -0.5],
#			[ 0.5, -0.5],
#			[-0.5,  0.5] ],
#		np.double)
#	motionBlurSteps = 10
#	hlWidth = 0.1
#	hlTex = 0
#	hlSideVerts = np.empty((len(verts)*4,2), np.double)
#	hlSideTexCoords = np.empty_like(hlSideVerts)
#	rotMat = np.matrix(  # a matrix for rotating 90 deg ccw
#		[	[ 0., -1.],
#			[ 1.,  0.] ],
#		np.double)
#	for i in range(len(verts)):
#		nextI = (i+1) % len(verts)
#		side = verts[nextI] - verts[i]
#		side *= hlWidth / np.hypot(*side)
#		offset = side*rotMat
#		hlSideVerts[4*i] = verts[i]
#		hlSideVerts[4*i+1] = verts[i] + offset
#		hlSideVerts[4*i+2] = verts[nextI] + offset
#		hlSideVerts[4*i+3] = verts[nextI]
#		hlSideTexCoords[4*i] = [0., 0.5]
#		hlSideTexCoords[4*i+1] = [1., 0.5]
#		hlSideTexCoords[4*i+2] = [1., 0.5]
#		hlSideTexCoords[4*i+3] = [0., 0.5]
#	hlCornerVerts = []
#	hlCornerTexCoords = []
#	for i in range(len(verts)):
#		nextI = (i+1) % len(verts)
#		prevI = (i-1) % len(verts)
#		side1 = verts[i] - verts[prevI]
#		np.divide(side1, np.hypot(*side1), side1)
#		side2 = verts[nextI] - verts[i]
#		np.divide(side2, np.hypot(*side2), side2)
#		perp1 = np.array(side1 * rotMat, np.double)
#		perp2 = np.array(side2 * rotMat, np.double)
#		angle = acos(np.sum(perp1*perp2))
#		slices = int(ceil(angle/(pi/16)))
#		fanVerts = np.empty((slices+2,2), np.double)
#		fanVerts[0] = verts[i]
#		offset = hlWidth*perp1
#		miniRotMat = np.matrix(
#			[	[ cos(angle/slices), sin(angle/slices)],
#				[-sin(angle/slices), cos(angle/slices)] ],
#			np.double)
#		for n in range(slices):
#			fanVerts[n+1] = verts[i] + offset
#			offset = offset * miniRotMat
#		fanVerts[slices+1] = verts[i] + hlWidth*perp2
#		hlCornerVerts += [fanVerts]
#		hlCornerTexCoords += [
#			np.array(
#				[[0., 0.5]] + [[1., 0.5]]*(slices+1),
#				np.double)
#			]
#	totFlightTime = 0.1
#	
#	class Pose:
#		def __init__(self, *args):
#			if len(args) == 1:
#				self.pos = np.array(args[0].pos)
#				self.angle = args[0].angle
#			else:
#				self.pos = np.array(args[0])
#				self.angle = args[1]
#	
#	def __init__(self, grid, loc):
#		Actor.__init__(self, grid)
#		self.srcLoc = loc
#		self.loc = loc
#		if RightTriTile.hlTex == 0:
#			RightTriTile.hlTex = glGenTextures(1)
#			glBindTexture(GL_TEXTURE_2D, RightTriTile.hlTex)
#			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
#			texels = np.array(
#				[	[ [255, 255, 0, 255], [127, 255, 0, 0] ],
#					[ [255, 255, 0, 255], [127, 255, 0, 0] ] ],
#				np.uint8)
#			glTexImage2Dub(GL_TEXTURE_2D, 0, GL_RGBA, 0, GL_RGBA, texels)
#		self.grid.drawFixedTiles.addHandler(self.__class__.draw, self)
#		self.grid.startGrab.addHandler(self.__class__.startGrab, self)
#		self.state = 'sitting'
#	
#	def update(self, deltaT):
#		if self.state == 'flying':
#			self.flightTime += deltaT
#			self.pose = self.Pose(self.nextPose)
#			if self.flightTime < self.totFlightTime:
#				self.nextPose.pos += self.flyingVel.pos * deltaT
#				self.nextPose.angle += self.flyingVel.angle * deltaT
#			else:
#				self.endFlying()
#	
#	def startGrab(self, mousePos):
#		localX = (
#			float(mousePos[0])*self.grid.cols/self.grid.vidSize[0]-self.loc[0])
#		localY = (
#			float(mousePos[1])*self.grid.rows/self.grid.vidSize[1]-self.loc[1])
#		if (
#				0. <= localX < 1. and 0. <= localY < 1.
#				and (localX+localY < 1.) == (self.loc[2] == 0)
#		):
#			self.state = 'grabbed'
#			pose = self.locToPose(self.loc)
#			self.mouseOffset = pose.pos - mousePos
#			self.grabbedIdx = self.loc[2]
#			self.grid.endGrab.addHandler(self.__class__.endGrab, self)
#			self.grid.rotateTile.addHandler(self.__class__.rotate, self)
#			self.grid.drawFixedTiles.removeHandler(self.__class__.draw, self)
#			self.grid.drawFlyingTiles.addHandler(self.__class__.draw, self)
#	
#	def endGrab(self, mousePos):
#		self.state = 'flying'
#		self.grid.rotateTile.removeHandler(self.__class__.rotate, self)
#		self.grid.endGrab.removeHandler(self.__class__.endGrab, self)
#		targetLoc = self.grid.findTile(mousePos)
#		if targetLoc[2] == self.grabbedIdx:
#			for tile in self.grid.tiles:
#				if tile.loc == targetLoc:
#					self.swapWith(tile)
#					break
#			else:
#				raise RuntimeError("Couln't find tile at "+str(targetLoc))
#		curPos = self.mouseOffset + mousePos
#		self.startFlying(
#			self.Pose(curPos, 180*self.grabbedIdx), self.locToPose(self.loc))
#		del self.grabbedIdx
#		del self.mouseOffset
#	
#	def rotate(self, dirxn):
#		self.grabbedIdx = (self.grabbedIdx+dirxn) % 2
#		self.mouseOffset = -self.mouseOffset
#	
#	def swapWith(self, other):
#		loc = self.loc
#		#self.__setLoc(other.loc)
#		self.loc = other.loc
#		other.__setLoc(loc)
#	
#	def __setLoc(self, loc):
#		self.startFlying(self.locToPose(self.loc), self.locToPose(loc))
#		self.loc = loc
#	
#	def startFlying(self, startPose, endPose):
#		self.pose = self.Pose(np.empty(2), 0)  # This value shouldn't actually be used
#		self.nextPose = self.Pose(startPose)
#		# Awkwardly, flyingVel is a Pose object even though it is more like the
#		# time derivative of a pose.
#		self.flyingVel = self.Pose(
#			(endPose.pos-self.nextPose.pos) / self.totFlightTime,
#			(endPose.angle-self.nextPose.angle) / self.totFlightTime)
#		self.flightTime = 0.
#		if self.state == 'sitting':
#			self.grid.drawFixedTiles.removeHandler(self.__class__.draw, self)
#			self.grid.drawFlyingTiles.addHandler(self.__class__.draw, self)
#		self.state = 'flying'
#	
#	def endFlying(self):
#		self.state = 'sitting'
#		self.grid.drawFlyingTiles.removeHandler(self.__class__.draw, self)
#		self.grid.drawFixedTiles.addHandler(self.__class__.draw, self)
#		del self.flightTime
#		del self.flyingVel
#		del self.nextPose
#		del self.pose
#	
#	def locToPose(self, loc):
#		return self.Pose(
#			np.array(
#				[ (loc[0]+0.5) * self.grid.vidSize[0] / self.grid.cols,
#				  (loc[1]+0.5) * self.grid.vidSize[1] / self.grid.rows ],
#				np.double),
#			loc[2] * 180)
#	
#	def draw(self, aspect):
#		"""
#		Draw the tile.
#		aspect: aspect ratio of the video
#		"""
#		width = float(self.grid.vidSize[0])/self.grid.cols
#		height = float(self.grid.vidSize[1])/self.grid.rows
#		srcWidth = float(self.grid.srcVidSize[0])/self.grid.cols
#		srcHeight = float(self.grid.srcVidSize[1])/self.grid.rows
#		srcX = (self.srcLoc[0]+0.5)*srcWidth
#		srcY = (self.srcLoc[1]+0.5)*srcHeight
#		glMatrixMode(GL_TEXTURE)
#		glPushMatrix()
#		glTranslated(srcX, srcY, 0.)
#		glRotated(180*self.srcLoc[2], 0, 0, 1)
#		glScaled(srcWidth, srcHeight, 1.)
#		glMatrixMode(GL_MODELVIEW)
#		glBindTexture(GL_TEXTURE_2D, self.grid.vidTex)
#		glTexCoordPointerd(RightTriTile.verts)
#		glVertexPointerd(RightTriTile.verts)
#		
#		def simpleDraw(x, y, angle):
#			glPushMatrix()
#			glTranslated(x, y, 0.)
#			glRotated(angle, 0, 0, 1)
#			glScaled(width, height, 1.)
#		
#			glDrawArrays(GL_TRIANGLES, 0, 3)
#		
#			glPopMatrix()
#		
#		if self.state in [ 'flying', 'grabbed' ]:
#			glEnable(GL_BLEND)
#			if self.state == 'grabbed':
#				glColor4d(0, 0, 0, 0.8)
#				mouseX, mouseY = self.grid.getMousePos()
#				simpleDraw(
#					mouseX + self.mouseOffset[0], mouseY + self.mouseOffset[1],
#					180*self.grabbedIdx)
#			else:
#				glColor4d(0, 0, 0, 0.8/self.motionBlurSteps)
#				deltaX, deltaY = self.nextPose.pos - self.pose.pos
#				deltaAngle = self.nextPose.angle - self.pose.angle
#				for n in range(self.motionBlurSteps):
#					simpleDraw(
#						self.pose.pos[0] + n*deltaX/self.motionBlurSteps,
#						self.pose.pos[1] + n*deltaY/self.motionBlurSteps,
#						self.pose.angle + n*deltaAngle/self.motionBlurSteps)
#			glDisable(GL_BLEND)
#			glColor4d(0, 0, 0, 1)
#		else:
#			simpleDraw(
#				(self.loc[0]+0.5)*width, (self.loc[1]+0.5)*height,
#				180*self.loc[2])
#		
#		glMatrixMode(GL_TEXTURE)
#		glPopMatrix()
#		glMatrixMode(GL_MODELVIEW)
#	
#	def drawHighlight(self, aspect):
#		width = float(self.grid.vidSize[0])/self.grid.cols
#		height = float(self.grid.vidSize[1])/self.grid.rows
#		col, row, dstIdx = self.grid.tiles.inv[self]
#		dstX = (col+0.5)*width
#		dstY = (row+0.5)*height
#		glPushMatrix()
#		glTranslated(dstX, dstY, 0.)
#		glRotated(180*dstIdx, 0, 0, 1)
#		glScaled(width, height, 1.)
#		glMatrixMode(GL_TEXTURE)
#		glPushMatrix()
#		glLoadIdentity()
#		glScaled(0.5, 1., 1.)
#		glTranslated(0.5, 0., 0.)
#		
#		glEnable(GL_BLEND)
#		glBindTexture(GL_TEXTURE_2D, RightTriTile.hlTex)
#		glTexCoordPointerd(RightTriTile.hlSideTexCoords)
#		glVertexPointerd(RightTriTile.hlSideVerts)
#		glDrawArrays(GL_QUADS, 0, len(RightTriTile.hlSideVerts))
#		for i in range(len(RightTriTile.hlCornerVerts)):
#			glTexCoordPointerd(RightTriTile.hlCornerTexCoords[i])
#			glVertexPointerd(RightTriTile.hlCornerVerts[i])
#			glDrawArrays(GL_TRIANGLE_FAN, 0, len(RightTriTile.hlCornerVerts[i]))
#		glDisable(GL_BLEND)
#		
#		glPopMatrix()
#		glMatrixMode(GL_MODELVIEW)
#		glPopMatrix()

# vim: set ts=4 sts=4 sw=4 ai noet :
