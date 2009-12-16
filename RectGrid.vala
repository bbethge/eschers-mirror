/**
 * Compute actual mathematical modulo operation
 */
double modulo(double x, double y) {
	return x - Math.floor(x/y)*y;
}

/*
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
*/

protected class TileInfo: Object {
	public Tile tile;
	public TileShadow shadow;
	public uint col = 0;
	public uint row = 0;
	public uint src_col = 0;
	public uint src_row = 0;
	public uint rotation_step = 0;
	public Clutter.BehaviourRotate? rotation_behaviour = null;
	public bool flipped = false;
	public bool is_flying = false;

	public TileInfo(Tile tile, TileShadow shadow) {
		this.tile = tile;
		this.shadow = shadow;
	}
}

public class RectGrid: Grid {
	private uint rows;
	private uint cols;
	private bool rotation_allowed;

	private SList<Tile> tiles = new SList<Tile>();
	private Tile? grabbed_tile = null;
	private Clutter.BehaviourRotate? grabbed_tile_rotate_behaviour;
	private float grab_offset_x;
	private float grab_offset_y;

	protected class const float MAX_TILE_ALTITUDE = 15;
	protected class const uint TILE_SNAP_TIME = 500;

	public RectGrid(
		string videoFile, uint rows, uint cols, bool rotation_allowed
	) {
		base(videoFile);

		this.cols = cols;
		this.rows = rows;
		this.rotation_allowed = rotation_allowed;

		TileVertex[] verts = new TileVertex[4];
		verts[0].x = 0; verts[0].y = 0;
		verts[1].x = 1; verts[1].y = 0;
		verts[2].x = 1; verts[2].y = 1;
		verts[3].x = 0; verts[3].y = 1;

		var shape = new TileShape();
		shape.verts = verts;

		for (uint col = 0; col < cols; ++col) {
			for (uint row = 0; row < rows; ++row) {
				var mat = Cogl.Matrix.identity();
				mat.scale(1.0f/cols, 1.0f/rows, 1);
				mat.translate(col, row, 0);

				var tile = new Tile(shape, mat, clutter_texture);
				var shadow = new TileShadow(shape);
				var tile_info = new TileInfo(tile, shadow);
				tile_info.col = col;
				tile_info.row = row;
				tile_info.src_col = col;
				tile_info.src_row = row;
				set_tile_info(tile, tile_info);

				tiles.prepend(tile);
				tile.set_parent(this);
				tile.button_press_event.connect(on_tile_button_press);

				shadow.opacity = 0x80;
				shadow.set_parent(this);
			}
		}
		shuffle();

		reactive = true;
		//motion_event.connect(on_mouse_motion);
		//button_release_event.connect(on_button_release);
	}

	protected static void set_tile_info(Tile tile, TileInfo info) {
		// We have to explicitly create a ref for the tile to hold
		info.@ref();
		tile.set_data_full("rect-grid-tile-info", info, Object.unref);
	}

	protected static TileInfo get_tile_info(Tile tile) {
		var info = tile.get_data("rect-grid-tile-info") as TileInfo;
		assert(info != null);
		return info;
	}

	public override void map() {
		base.map();
		foreach (var tile in tiles) {
			tile.map();
			var tile_info = get_tile_info(tile);
			tile_info.shadow.map();
		}
	}

	public override void unmap() {
		base.unmap();
		foreach (var tile in tiles) {
			tile.unmap();
			var tile_info = get_tile_info(tile);
			tile_info.shadow.unmap();
		}
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);
		float w, h;
		box.get_size(out w, out h);

		foreach (var tile in tiles) {
			var tile_box = Clutter.ActorBox();

			if (tile.fixed_position_set) {
				tile_box.x1 = tile.x;
				tile_box.y1 = tile.y;
			}
			else {
				var tile_info = get_tile_info(tile);
				tile_box.x1 = tile_info.col * w / cols;
				tile_box.y1 = tile_info.row * h / rows;
			}
			tile_box.x2 = tile_box.x1 + w/cols;
			tile_box.y2 = tile_box.y1 + h/rows;

			tile.allocate(tile_box, flags);

			var tile_info = get_tile_info(tile);
			tile_info.shadow.allocate(tile_box, flags);
		}
	}

	public override void paint() {
		foreach (var tile in tiles) {
			var tile_info = get_tile_info(tile);
			if (tile != grabbed_tile && !tile_info.is_flying) {
				tile.paint();
			}
		}
		foreach (var tile in tiles) {
			var tile_info = get_tile_info(tile);
			if (tile_info.is_flying) {
				tile_info.shadow.paint();
			}
		}
		foreach (var tile in tiles) {
			var tile_info = get_tile_info(tile);
			if (tile != grabbed_tile && tile_info.is_flying) {
				tile.paint();
			}
		}
		if (grabbed_tile != null) {
			grabbed_tile.paint();
		}
	}
	
	public override void pick(Clutter.Color color) {
		base.pick(color);
		foreach (var tile in tiles) {
			var tile_info = get_tile_info(tile);
			if (!tile_info.is_flying) {
				tile.paint();
			}
		}
		foreach (var tile in tiles) {
			var tile_info = get_tile_info(tile);
			if (tile_info.is_flying) {
				tile.paint();
			}
		}
	}

	protected bool on_tile_button_press(
		Clutter.Actor actor, Clutter.ButtonEvent event
	) {
		if (actor is Tile) {

			switch (event.button) {
			case 1:
				grabbed_tile = (Tile) actor;
				float mouse_x = event.x, mouse_y = event.y;
				// FIXME: bindings for transform_stage_point are broken
				//transform_stage_point(event.x, event.y, mouse_x, mouse_y);
				float child_x, child_y;
				grabbed_tile.get_position(out child_x, out child_y);
				grab_offset_x = child_x - mouse_x;
				grab_offset_y = child_y - mouse_y;

				// Allow the player to grab a flying tile
				var animation = grabbed_tile.get_animation();
				if (animation != null) {
					animation.completed();
				}

				var tile_info = get_tile_info(grabbed_tile);
				tile_info.is_flying = true;
				tile_info.shadow.animate(
					Clutter.AnimationMode.EASE_OUT_CUBIC, 250, 
					"altitude", MAX_TILE_ALTITUDE, null
				);
				return true;
				break;

			case 3:
				if (rotation_allowed) {
					if (
						(event.modifier_state & Clutter.ModifierType.SHIFT_MASK)
						!= 0
					) {
						rotate_tile((Tile)actor, -1);
					}
					else {
						rotate_tile((Tile)actor, 1);
					}
				}
				return true;
				break;
			}
		}
		return false;
	}

	protected void rotate_tile(Tile tile, int amount) {
		var tile_info = get_tile_info(tile);
		var old_rotation_step = tile_info.rotation_step;
		tile_info.rotation_step = (2+tile_info.rotation_step-amount) % 2;
		var timeline = new Clutter.Timeline(500);
		var alpha = new Clutter.Alpha.full(
			timeline, Clutter.AnimationMode.EASE_IN_OUT_QUAD
		);
		tile_info.rotation_behaviour = new Clutter.BehaviourRotate(
			alpha, Clutter.RotateAxis.Z_AXIS,
			amount > 0
				? Clutter.RotateDirection.CW
				: Clutter.RotateDirection.CCW,
			old_rotation_step * 180.0, tile_info.rotation_step * 180.0
		);
		tile_info.rotation_behaviour.set_center(
			(int)tile.width/2, (int)tile.height/2, 0
		);
		tile_info.rotation_behaviour.apply(tile);
		tile_info.rotation_behaviour.apply(tile_info.shadow);
		Signal.connect_after(
			timeline, "completed", (Callback)on_tile_rotation_completed,
			tile_info
		);
		timeline.start();
	}

	private static void on_tile_rotation_completed(
		Clutter.Timeline timeline, TileInfo tile_info
	) {
		tile_info.rotation_behaviour = null;
	}

	protected override bool motion_event(Clutter.MotionEvent event) {
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

	protected override bool button_release_event(Clutter.ButtonEvent event) {
		if (grabbed_tile != null && event.button == 1) {
			grabbed_tile.hide();
			var stage = get_stage() as Clutter.Stage;
			if (stage == null) {
				return false;
			}
			var drop_target = stage.get_actor_at_pos(
				Clutter.PickMode.REACTIVE, (int)event.x, (int)event.y
			);
			grabbed_tile.show();

			TileInfo grabbed_tile_info = get_tile_info(grabbed_tile);
			Clutter.ActorBox box;
			get_allocation_box(out box);
			float w, h;
			box.get_size(out w, out h);

			if (tiles.index(drop_target as Tile) != -1) {
				TileInfo target_tile_info = get_tile_info((Tile)drop_target);

				// swap logical positions of grabbed tile and drop target
				uint grabbed_col = grabbed_tile_info.col;
				uint grabbed_row = grabbed_tile_info.row;
				grabbed_tile_info.col = target_tile_info.col;
				grabbed_tile_info.row = target_tile_info.row;
				target_tile_info.col = grabbed_col;
				target_tile_info.row = grabbed_row;

				target_tile_info.is_flying = true;

				// Make drop target move to its new position
				var animation = drop_target.animate(
					Clutter.AnimationMode.EASE_IN_OUT_CUBIC, TILE_SNAP_TIME,
					"x", target_tile_info.col*w/cols,
					"y", target_tile_info.row*h/rows,
					null
				);
				animation.completed.connect((a) => {
					target_tile_info.is_flying = false;
				});
				var shadow_animation = target_tile_info.shadow.animate(
					Clutter.AnimationMode.EASE_IN_CUBIC, TILE_SNAP_TIME/2,
					"altitude", MAX_TILE_ALTITUDE, null
				);
				Signal.connect_after(
					shadow_animation, "completed",
					(Callback)on_target_tile_shadow_animation_completed,
					target_tile_info.shadow
				);
			}

			// Make grabbed tile move to its (new) position
			var animation = grabbed_tile.animate(
				Clutter.AnimationMode.EASE_OUT_CUBIC, TILE_SNAP_TIME,
				"x", grabbed_tile_info.col*w/cols,
				"y", grabbed_tile_info.row*h/rows,
				null
			);
			grabbed_tile_info.shadow.animate(
				Clutter.AnimationMode.EASE_OUT_CUBIC, TILE_SNAP_TIME,
				"altitude", 0.0f, null
			);
			animation.completed.connect((a) => {
				grabbed_tile_info.is_flying = false;
			});
			grabbed_tile = null;

			queue_relayout();
			return true;
		}
		return false;
	}

	private static void on_target_tile_shadow_animation_completed(
		Clutter.Animation a, TileShadow shadow
	) {
		shadow.animate(
			Clutter.AnimationMode.EASE_OUT_CUBIC,
			TILE_SNAP_TIME - TILE_SNAP_TIME/2,
			"altitude", 0.0f, null
		);
	}

	private bool on_tile_key_press(Clutter.KeyEvent event) {
		stdout.printf("key\n");
		if (grabbed_tile != null) {
			if (event.unicode_value == 'r') {
				rotate_tile(grabbed_tile, 1);
			}
			else if (event.unicode_value == 'R') {
				rotate_tile(grabbed_tile, -1);
			}
			return true;
		}
		return false;
	}

	public override bool is_solved() {
		foreach (var tile in tiles) {
			var tile_info = get_tile_info(tile);
			if (
				tile_info.col != tile_info.src_col
				|| tile_info.row != tile_info.src_row
				|| tile_info.rotation_step != 0
			) {
				return false;
			}
		}
		return true;
	}
	
	public override void shuffle() {
		for (
			weak SList<Tile> unshuffled = tiles;
			unshuffled.next != null;
			unshuffled = unshuffled.next
		) {
			Tile tile = unshuffled.data;
			int32 index = Random.int_range(1, (int32) unshuffled.length());
			Tile other_tile = unshuffled.nth_data(index);

			var tile_info = get_tile_info(tile);
			var other_tile_info = get_tile_info(other_tile);

			// swap the logical positions of tile and other tile
			uint col = tile_info.col;
			uint row = tile_info.row;
			tile_info.col = other_tile_info.col;
			tile_info.row = other_tile_info.row;
			other_tile_info.col = col;
			other_tile_info.row = row;
		}
		if (rotation_allowed) {
			foreach (var tile in tiles) {
				var tile_info = get_tile_info(tile);
				tile_info.rotation_step = Random.int_range(0, 2);
				tile.rotation_angle_z = tile_info.rotation_step * 180.0;
				tile.rotation_center_z_gravity = Clutter.Gravity.CENTER;
			}
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
