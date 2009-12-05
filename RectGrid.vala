protected class RectTile: Clutter.Rectangle {
	public uint src_col;
	public uint src_row;

	public RectTile(uint col, uint row) {
		reactive = true;
		src_col = col;
		src_row = row;
	}

	public override void paint() {
		Clutter.ActorBox box;
		get_allocation_box(out box);

		float w, h;
		box.get_size(out w, out h);

		weak Clutter.Actor? parent = get_parent();
		if (parent == null || !(get_parent() is RectGrid)) {
			return;
		}
		weak RectGrid grid = (RectGrid) parent;

		uint rows = grid.rows;
		uint cols = grid.cols;

		uchar alpha = get_paint_opacity();
		// FIXME: is it really OK to modify the material?
		var material = grid.get_material();
		material.set_color4ub(alpha, alpha, alpha, alpha);

		Cogl.set_source(material);
		Cogl.rectangle_with_texture_coords(
			0, 0, w, h,
			(float)src_col/cols, (float)src_row/rows,
			((float)src_col+1)/cols, ((float)src_row+1)/rows
		);
	}

	public void paint_shadow(float altitude) {
		float x, y, w, h;
		get_position(out x, out y);
		get_size(out w, out h);
		Cogl.set_source_color4ub(0, 0, 0, 0x80);
		Cogl.rectangle(x, y+altitude, x+w, y+h+altitude);
	}
}

public class RectShadow: Clutter.Rectangle {
	protected Cogl.VertexBuffer vbo = new Cogl.VertexBuffer(22);
	protected float w = 0;
	protected float h = 0;

	private float _altitude;
	public float altitude {
		get { return _altitude; }
		set { _altitude = value; recalc_vbo(); }
		default = 0;
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);

		float new_width, new_height;
		box.get_size(out new_width, out new_height);
		if (new_width == w && new_height == h) {
			return;
		}

		w = new_width;
		h = new_height;
		recalc_vbo();
	}

	protected void recalc_vbo() {
		float a = altitude;

		float[] verts = {
			0 + a, 0 + a,
			0 + a, h - a,
			w - a, 0 + a,
			w - a, h - a,

			w - a, 0 + a,
			w + a, h - a,

			w - a, 0 + a,
			w + a, 0 + a,

			w - a, 0 + a,
			w - a, 0 - a,

			0 + a, 0 + a,
			0 + a, 0 - a,

			0 + a, 0 + a,
			0 - a, 0 + a,

			0 + a, h - a,
			0 - a, h - a,

			0 + a, h - a,
			0 + a, h + a,

			w - a, h - a,
			w - a, h + a,

			w - a, h - a,
			w + a, h - a
		};

		uchar[] colors = {
			0, 0, 0, 0xff,
			0, 0, 0, 0xff,
			0, 0, 0, 0xff,
			0, 0, 0, 0xff,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0,

			0, 0, 0, 0xff,
			0, 0, 0, 0
		};

		vbo.add("gl_Vertex", 2, Cogl.AttributeType.FLOAT, false, 0, verts);
		vbo.add("gl_Color", 4, Cogl.AttributeType.UNSIGNED_BYTE, true, 0, colors);
		vbo.submit();
	}

	public override void paint() {
		Cogl.set_source_color4ub(0xff, 0, 0, 0xff);
		vbo.draw(Cogl.VerticesMode.TRIANGLE_STRIP, 0, 22);
	}
}

protected class RectGridChildMeta: Clutter.ChildMeta {

	[Property(
		nick = "Button press handler",
		blurb = "ID of signal handler installed by grid for button press events"
	)]
	public ulong button_press_handler { get; set; default = 0; }

	[Property(nick="Row", blurb="Row that the tile logically is in")]
	public uint row { get; set; }

	[Property(nick="column", blurb="Column that the tile logically is in")]
	public uint column { get; set; }

	public RectGridChildMeta(Clutter.Actor actor, Clutter.Container container) {
		Object(actor: actor, container: container);
	}
}

public class RectGrid: Grid, Clutter.Container, Clutter.Scriptable {
	// TODO: make private
	public uint rows;
	public uint cols;

	private SList<Clutter.Actor> children;
	private RectTile? grabbed_tile = null;
	private float grab_offset_x;
	private float grab_offset_y;
	private bool child_meta_installed = false;

	public RectGrid(string videoFile, uint rows, uint cols) {
		base(videoFile);

		// HACK
		if (!child_meta_installed) {
			install_child_meta(typeof(RectGrid), typeof(RectGridChildMeta));
			child_meta_installed = true;
		}

		this.cols = cols;
		this.rows = rows;

		for (uint col = 0; col < cols; ++col) {
			for (uint row = 0; row < rows; ++row) {
				var tile = new RectTile(col, row);
				add_actor(tile);
				child_set(tile, "column", col, "row", row, null);
			}
		}
		shuffle();

		reactive = true;
		motion_event.connect(on_mouse_motion);
		button_release_event.connect(on_button_release);
	}

	//public void set_grabbed_tile(weak RectTile? tile) {
	//	grabbed_tile = tile;
	//}

	public void add_actor(Clutter.Actor actor) {
		if (children.index(actor) >= 0) {
			warning(
				"Actor of type %s is already a child of this RectGrid",
				actor.get_type().name()
			);
		}
		else {
			children.append(actor);
			actor.set_parent(this);
			actor.button_press_event.connect(on_child_button_press);
			queue_relayout();
		}
	}
	
	public void remove_actor(Clutter.Actor actor) {
		if (children.index(actor) == -1) {
			warning(
				"Actor of type %s is not a child of this RectGrid",
				actor.get_type().name()
			);
		}
		else {
			children.remove(actor);
			actor.button_press_event.disconnect(on_child_button_press);
			actor.unparent();
			queue_relayout();
		}
	}

	public void @foreach(Clutter.Callback callback) {
		foreach (var child in children) {
			callback(child);
		}
	}

//	public unowned Clutter.ChildMeta get_child_meta(Clutter.Actor actor) {
//		Clutter.ChildMeta *meta =
//			actor.get_data("clutter-container-child-meta");
//		if (meta != null && meta->actor == actor) {
//			return meta;
//		}
//		return null;
//	}
//
//	public void create_child_meta(Clutter.Actor actor) {
//		RectGridChildMeta child_meta = new RectGridChildMeta(actor, this);
//		if (child_meta != null) {
//			child_meta.@ref();
//			actor.set_data_full(
//				"clutter-container-child-meta", child_meta, Object.unref
//			);
//		}
//	}
//
//	public void destroy_child_meta(Clutter.Actor actor) {
//		actor.set_data("clutter-container-child-meta", null);
//	}
//
	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);
		float w, h;
		box.get_size(out w, out h);

		foreach (var child in children) {
			var child_box = Clutter.ActorBox();

			if (child.fixed_position_set) {
				child_box.x1 = child.x;
				child_box.y1 = child.y;
			}
			else {
				uint col, row;
				child_get(child, "column", out col, "row", out row, null);
				child_box.x1 = col * w / cols;
				child_box.y1 = row * h / rows;
			}
			child_box.x2 = child_box.x1 + w/cols;
			child_box.y2 = child_box.y1 + h/rows;

			child.allocate(child_box, flags);
		}
	}

	public override void paint() {
		foreach (var child in children) {
			if (child != grabbed_tile) {
				child.paint();
			}
		}
		if (grabbed_tile != null) {
			grabbed_tile.paint_shadow(12);
			grabbed_tile.paint();
		}
	}
	
	public override void pick(Clutter.Color color) {
		base.pick(color);
		foreach (var child in children) {
			child.paint();
		}
	}

	protected bool on_child_button_press(
		Clutter.Actor child, Clutter.ButtonEvent event
	) {
		if (child is RectTile) {
			grabbed_tile = (RectTile) child;
			float mouse_x = event.x, mouse_y = event.y;
			// FIXME: bindings for transform_stage_point are broken
			//transform_stage_point(event.x, event.y, mouse_x, mouse_y);
			float child_x, child_y;
			grabbed_tile.get_position(out child_x, out child_y);
			grab_offset_x = child_x - mouse_x;
			grab_offset_y = child_y - mouse_y;
			grabbed_tile.opacity = 0x80;
			return true;
		}
		return false;
	}

	protected bool on_mouse_motion(Clutter.MotionEvent event) {
		if (grabbed_tile != null) {
			float mouse_x = event.x, mouse_y = event.y;
			// FIXME: bindings for transform_stage_point are broken
			//transform_stage_point(event.x, event.y, mouse_x, mouse_y);
			grabbed_tile.set_position(
				mouse_x + grab_offset_x, mouse_y + grab_offset_y
			);
			return true;
		}
		return false;
	}

	protected bool on_button_release(Clutter.ButtonEvent event) {
		if (grabbed_tile != null) {
			grabbed_tile.hide();
			var stage = get_stage() as Clutter.Stage;
			if (stage == null) {
				return false;
			}
			var drop_target = stage.get_actor_at_pos(
				Clutter.PickMode.REACTIVE, (int)event.x, (int)event.y
			);
			grabbed_tile.show();

			if (children.index(drop_target) != -1) {
				uint grabbed_col, grabbed_row;
				child_get(
					grabbed_tile,
					"column", out grabbed_col,
					"row", out grabbed_row,
					null
				);
				uint drop_col, drop_row;
				child_get(
					drop_target,
					"column", out drop_col,
					"row", out drop_row,
					null
				);
				child_set(
					grabbed_tile, "column", drop_col, "row", drop_row, null
				);
				child_set(
					drop_target, "column", grabbed_col, "row", grabbed_row, null
				);

				drop_target.animate(
					Clutter.AnimationMode.EASE_OUT_CUBIC, 500,
					"x", grabbed_col*width/cols,
					"y", grabbed_row*height/rows,
					null
				);
			}

			uint row, col;
			child_get(
				grabbed_tile, "column", out col, "row", out row, null
			);
			grabbed_tile.animate(
				Clutter.AnimationMode.EASE_OUT_CUBIC, 500,
				"x", col*width/cols,
				"y", row*height/rows
			);
			grabbed_tile.opacity = 0xff;
			grabbed_tile = null;

			queue_relayout();
			return true;
		}
		return false;
	}

	public override bool is_solved() {
		foreach (var child in children) {
			if (child is RectTile) {
				var tile = (RectTile) child;
				uint row, col;
				child_get(child, "column", out col, "row", out row, null);
				if (col != tile.src_col || row != tile.src_row) {
					return false;
				}
			}
		}
		return true;
	}
	
	public override void shuffle() {
		for (
			weak SList<Clutter.Actor> unshuffled = children;
			unshuffled.next != null;
			unshuffled = unshuffled.next
		) {
			weak Clutter.Actor child = unshuffled.data;
			int32 index = Random.int_range(1, (int32) unshuffled.length());
			weak Clutter.Actor other_child = unshuffled.nth_data(index);

			// swap the logical positions of child and other_child
			uint col, row;
			child_get(child, "column", out col, "row", out row, null);

			uint other_col, other_row;
			child_get(
				other_child, "column", out other_col, "row", out other_row, null
			);

			child_set(child, "column", other_col, "row", other_row, null);
			child_set(other_child, "column", col, "row", row, null);
		}
	}
}

//class RightTriTile(Actor):
//	verts = np.array(
//		[	[-0.5, -0.5],
//			[ 0.5, -0.5],
//			[-0.5,  0.5] ],
//		np.double)
//	motionBlurSteps = 10
//	hlWidth = 0.1
//	hlTex = 0
//	hlSideVerts = np.empty((len(verts)*4,2), np.double)
//	hlSideTexCoords = np.empty_like(hlSideVerts)
//	rotMat = np.matrix(  # a matrix for rotating 90 deg ccw
//		[	[ 0., -1.],
//			[ 1.,  0.] ],
//		np.double)
//	for i in range(len(verts)):
//		nextI = (i+1) % len(verts)
//		side = verts[nextI] - verts[i]
//		side *= hlWidth / np.hypot(*side)
//		offset = side*rotMat
//		hlSideVerts[4*i] = verts[i]
//		hlSideVerts[4*i+1] = verts[i] + offset
//		hlSideVerts[4*i+2] = verts[nextI] + offset
//		hlSideVerts[4*i+3] = verts[nextI]
//		hlSideTexCoords[4*i] = [0., 0.5]
//		hlSideTexCoords[4*i+1] = [1., 0.5]
//		hlSideTexCoords[4*i+2] = [1., 0.5]
//		hlSideTexCoords[4*i+3] = [0., 0.5]
//	hlCornerVerts = []
//	hlCornerTexCoords = []
//	for i in range(len(verts)):
//		nextI = (i+1) % len(verts)
//		prevI = (i-1) % len(verts)
//		side1 = verts[i] - verts[prevI]
//		np.divide(side1, np.hypot(*side1), side1)
//		side2 = verts[nextI] - verts[i]
//		np.divide(side2, np.hypot(*side2), side2)
//		perp1 = np.array(side1 * rotMat, np.double)
//		perp2 = np.array(side2 * rotMat, np.double)
//		angle = acos(np.sum(perp1*perp2))
//		slices = int(ceil(angle/(pi/16)))
//		fanVerts = np.empty((slices+2,2), np.double)
//		fanVerts[0] = verts[i]
//		offset = hlWidth*perp1
//		miniRotMat = np.matrix(
//			[	[ cos(angle/slices), sin(angle/slices)],
//				[-sin(angle/slices), cos(angle/slices)] ],
//			np.double)
//		for n in range(slices):
//			fanVerts[n+1] = verts[i] + offset
//			offset = offset * miniRotMat
//		fanVerts[slices+1] = verts[i] + hlWidth*perp2
//		hlCornerVerts += [fanVerts]
//		hlCornerTexCoords += [
//			np.array(
//				[[0., 0.5]] + [[1., 0.5]]*(slices+1),
//				np.double)
//			]
//	totFlightTime = 0.1
//	
//	class Pose:
//		def __init__(self, *args):
//			if len(args) == 1:
//				self.pos = np.array(args[0].pos)
//				self.angle = args[0].angle
//			else:
//				self.pos = np.array(args[0])
//				self.angle = args[1]
//	
//	def __init__(self, grid, loc):
//		Actor.__init__(self, grid)
//		self.srcLoc = loc
//		self.loc = loc
//		if RightTriTile.hlTex == 0:
//			RightTriTile.hlTex = glGenTextures(1)
//			glBindTexture(GL_TEXTURE_2D, RightTriTile.hlTex)
//			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
//			texels = np.array(
//				[	[ [255, 255, 0, 255], [127, 255, 0, 0] ],
//					[ [255, 255, 0, 255], [127, 255, 0, 0] ] ],
//				np.uint8)
//			glTexImage2Dub(GL_TEXTURE_2D, 0, GL_RGBA, 0, GL_RGBA, texels)
//		self.grid.drawFixedTiles.addHandler(self.__class__.draw, self)
//		self.grid.startGrab.addHandler(self.__class__.startGrab, self)
//		self.state = 'sitting'
//	
//	def update(self, deltaT):
//		if self.state == 'flying':
//			self.flightTime += deltaT
//			self.pose = self.Pose(self.nextPose)
//			if self.flightTime < self.totFlightTime:
//				self.nextPose.pos += self.flyingVel.pos * deltaT
//				self.nextPose.angle += self.flyingVel.angle * deltaT
//			else:
//				self.endFlying()
//	
//	def startGrab(self, mousePos):
//		localX = (
//			float(mousePos[0])*self.grid.cols/self.grid.vidSize[0]-self.loc[0])
//		localY = (
//			float(mousePos[1])*self.grid.rows/self.grid.vidSize[1]-self.loc[1])
//		if (
//				0. <= localX < 1. and 0. <= localY < 1.
//				and (localX+localY < 1.) == (self.loc[2] == 0)
//		):
//			self.state = 'grabbed'
//			pose = self.locToPose(self.loc)
//			self.mouseOffset = pose.pos - mousePos
//			self.grabbedIdx = self.loc[2]
//			self.grid.endGrab.addHandler(self.__class__.endGrab, self)
//			self.grid.rotateTile.addHandler(self.__class__.rotate, self)
//			self.grid.drawFixedTiles.removeHandler(self.__class__.draw, self)
//			self.grid.drawFlyingTiles.addHandler(self.__class__.draw, self)
//	
//	def endGrab(self, mousePos):
//		self.state = 'flying'
//		self.grid.rotateTile.removeHandler(self.__class__.rotate, self)
//		self.grid.endGrab.removeHandler(self.__class__.endGrab, self)
//		targetLoc = self.grid.findTile(mousePos)
//		if targetLoc[2] == self.grabbedIdx:
//			for tile in self.grid.tiles:
//				if tile.loc == targetLoc:
//					self.swapWith(tile)
//					break
//			else:
//				raise RuntimeError("Couln't find tile at "+str(targetLoc))
//		curPos = self.mouseOffset + mousePos
//		self.startFlying(
//			self.Pose(curPos, 180*self.grabbedIdx), self.locToPose(self.loc))
//		del self.grabbedIdx
//		del self.mouseOffset
//	
//	def rotate(self, dirxn):
//		self.grabbedIdx = (self.grabbedIdx+dirxn) % 2
//		self.mouseOffset = -self.mouseOffset
//	
//	def swapWith(self, other):
//		loc = self.loc
//		#self.__setLoc(other.loc)
//		self.loc = other.loc
//		other.__setLoc(loc)
//	
//	def __setLoc(self, loc):
//		self.startFlying(self.locToPose(self.loc), self.locToPose(loc))
//		self.loc = loc
//	
//	def startFlying(self, startPose, endPose):
//		self.pose = self.Pose(np.empty(2), 0)  # This value shouldn't actually be used
//		self.nextPose = self.Pose(startPose)
//		# Awkwardly, flyingVel is a Pose object even though it is more like the
//		# time derivative of a pose.
//		self.flyingVel = self.Pose(
//			(endPose.pos-self.nextPose.pos) / self.totFlightTime,
//			(endPose.angle-self.nextPose.angle) / self.totFlightTime)
//		self.flightTime = 0.
//		if self.state == 'sitting':
//			self.grid.drawFixedTiles.removeHandler(self.__class__.draw, self)
//			self.grid.drawFlyingTiles.addHandler(self.__class__.draw, self)
//		self.state = 'flying'
//	
//	def endFlying(self):
//		self.state = 'sitting'
//		self.grid.drawFlyingTiles.removeHandler(self.__class__.draw, self)
//		self.grid.drawFixedTiles.addHandler(self.__class__.draw, self)
//		del self.flightTime
//		del self.flyingVel
//		del self.nextPose
//		del self.pose
//	
//	def locToPose(self, loc):
//		return self.Pose(
//			np.array(
//				[ (loc[0]+0.5) * self.grid.vidSize[0] / self.grid.cols,
//				  (loc[1]+0.5) * self.grid.vidSize[1] / self.grid.rows ],
//				np.double),
//			loc[2] * 180)
//	
//	def draw(self, aspect):
//		"""
//		Draw the tile.
//		aspect: aspect ratio of the video
//		"""
//		width = float(self.grid.vidSize[0])/self.grid.cols
//		height = float(self.grid.vidSize[1])/self.grid.rows
//		srcWidth = float(self.grid.srcVidSize[0])/self.grid.cols
//		srcHeight = float(self.grid.srcVidSize[1])/self.grid.rows
//		srcX = (self.srcLoc[0]+0.5)*srcWidth
//		srcY = (self.srcLoc[1]+0.5)*srcHeight
//		glMatrixMode(GL_TEXTURE)
//		glPushMatrix()
//		glTranslated(srcX, srcY, 0.)
//		glRotated(180*self.srcLoc[2], 0, 0, 1)
//		glScaled(srcWidth, srcHeight, 1.)
//		glMatrixMode(GL_MODELVIEW)
//		glBindTexture(GL_TEXTURE_2D, self.grid.vidTex)
//		glTexCoordPointerd(RightTriTile.verts)
//		glVertexPointerd(RightTriTile.verts)
//		
//		def simpleDraw(x, y, angle):
//			glPushMatrix()
//			glTranslated(x, y, 0.)
//			glRotated(angle, 0, 0, 1)
//			glScaled(width, height, 1.)
//		
//			glDrawArrays(GL_TRIANGLES, 0, 3)
//		
//			glPopMatrix()
//		
//		if self.state in [ 'flying', 'grabbed' ]:
//			glEnable(GL_BLEND)
//			if self.state == 'grabbed':
//				glColor4d(0, 0, 0, 0.8)
//				mouseX, mouseY = self.grid.getMousePos()
//				simpleDraw(
//					mouseX + self.mouseOffset[0], mouseY + self.mouseOffset[1],
//					180*self.grabbedIdx)
//			else:
//				glColor4d(0, 0, 0, 0.8/self.motionBlurSteps)
//				deltaX, deltaY = self.nextPose.pos - self.pose.pos
//				deltaAngle = self.nextPose.angle - self.pose.angle
//				for n in range(self.motionBlurSteps):
//					simpleDraw(
//						self.pose.pos[0] + n*deltaX/self.motionBlurSteps,
//						self.pose.pos[1] + n*deltaY/self.motionBlurSteps,
//						self.pose.angle + n*deltaAngle/self.motionBlurSteps)
//			glDisable(GL_BLEND)
//			glColor4d(0, 0, 0, 1)
//		else:
//			simpleDraw(
//				(self.loc[0]+0.5)*width, (self.loc[1]+0.5)*height,
//				180*self.loc[2])
//		
//		glMatrixMode(GL_TEXTURE)
//		glPopMatrix()
//		glMatrixMode(GL_MODELVIEW)
//	
//	def drawHighlight(self, aspect):
//		width = float(self.grid.vidSize[0])/self.grid.cols
//		height = float(self.grid.vidSize[1])/self.grid.rows
//		col, row, dstIdx = self.grid.tiles.inv[self]
//		dstX = (col+0.5)*width
//		dstY = (row+0.5)*height
//		glPushMatrix()
//		glTranslated(dstX, dstY, 0.)
//		glRotated(180*dstIdx, 0, 0, 1)
//		glScaled(width, height, 1.)
//		glMatrixMode(GL_TEXTURE)
//		glPushMatrix()
//		glLoadIdentity()
//		glScaled(0.5, 1., 1.)
//		glTranslated(0.5, 0., 0.)
//		
//		glEnable(GL_BLEND)
//		glBindTexture(GL_TEXTURE_2D, RightTriTile.hlTex)
//		glTexCoordPointerd(RightTriTile.hlSideTexCoords)
//		glVertexPointerd(RightTriTile.hlSideVerts)
//		glDrawArrays(GL_QUADS, 0, len(RightTriTile.hlSideVerts))
//		for i in range(len(RightTriTile.hlCornerVerts)):
//			glTexCoordPointerd(RightTriTile.hlCornerTexCoords[i])
//			glVertexPointerd(RightTriTile.hlCornerVerts[i])
//			glDrawArrays(GL_TRIANGLE_FAN, 0, len(RightTriTile.hlCornerVerts[i]))
//		glDisable(GL_BLEND)
//		
//		glPopMatrix()
//		glMatrixMode(GL_MODELVIEW)
//		glPopMatrix()

// vim: set ts=4 sts=4 sw=4 ai noet :
