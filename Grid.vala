public struct TileVertex {
	float x;
	float y;
	bool is_corner;
}

public class TileShape: Object {
	/**
	 * A set of control points that defines the shape of a tile via curve
	 * subdivision.
	 */
	private TileVertex[] _verts;
	public TileVertex[] verts {
		get { return _verts; }
		set {
			_verts = value;

			// Compute boundaries
			left = float.MAX;
			right = -float.MAX;
			top = float.MAX;
			bottom = -float.MAX;
			foreach (var vert in _verts) {
				if (vert.x < left) {
					left = vert.x;
				}
				if (vert.x > right) {
					right = vert.x;
				}
				if (vert.y < top) {
					top = vert.y;
				}
				if (vert.y > bottom) {
					bottom = vert.y;
				}
			}
		}
	}

	/**
	 * The boundaries of the tile after subdivision
	 */
	public float left { get; private set; }
	public float right { get; private set; }
	public float top { get; private set; }
	public float bottom { get; private set; }
}

public class Tile: Clutter.Actor {
	/**
	 * An actor that renders a tile (without shadow, etc.).  It knows which part
	 * of the video to display but not where it belongs at any particular time.
	 * The grid is responsible for telling tiles where to go and how to rotate
	 * or flip on the screen.
	 */

	private Cogl.TextureVertex[] verts;

	private TileShape shape;

	private Clutter.Texture texture;

	/**
	 * texture_matrix: gives transformation from tile shape coords to the video
	 *   texture coords.  This allows one to specify which part of the video
	 *   this tile shows.
	 */
	public Tile(
		TileShape shape, Cogl.Matrix texture_matrix, Clutter.Texture texture
	) {
		this.shape = shape;
		this.texture = texture;
		reactive = true;

		TileVertex[] shape_verts = shape.verts;

		verts = new Cogl.TextureVertex[shape_verts.length];
		unowned Cogl.Matrix m = texture_matrix;
		for (size_t i = 0; i < shape_verts.length; ++i) {
			verts[i].tx =
				m.xx*shape_verts[i].x + m.xy*shape_verts[i].y + m.xw;
			verts[i].ty =
				m.yx*shape_verts[i].x + m.yy*shape_verts[i].y + m.yw;
			verts[i].x = shape_verts[i].x;
			verts[i].y = shape_verts[i].y;
			verts[i].z = 0;
		}
	}

	public override void paint() {
		Cogl.set_source(texture.cogl_material);

		Clutter.ActorBox box;
		get_allocation_box(out box);
		float width, height;
		box.get_size(out width, out height);

		Cogl.push_matrix();
		Cogl.scale(width, height, 1);
		Cogl.polygon(verts, false);
		Cogl.pop_matrix();
	}

	public override void pick(Clutter.Color color) {
		base.pick(color);

		Cogl.set_source_color4ub(
			color.red, color.green, color.blue, color.alpha
		);

		Clutter.ActorBox box;
		get_allocation_box(out box);
		float width, height;
		box.get_size(out width, out height);

		Cogl.push_matrix();
		Cogl.scale(width, height, 1);
		Cogl.polygon(verts, false);
		Cogl.pop_matrix();
	}
}

public class TileShadow: Clutter.Actor {
	protected Cogl.VertexBuffer vbo;
	protected Cogl.VertexBufferIndices index_buffer;
	protected TileShape shape;
	protected float prev_width = 0;
	protected float prev_height = 0;

	private float _altitude;
	public float altitude {
		get { return _altitude; }
		set { _altitude = value; recalc_vbo(); }
		default = 0;
	}

	protected class Cogl.Texture texture;

	class construct {
		uchar[] tex_data = { 0, 0, 0, 0,  0, 0, 0, 0xff };
		texture = Cogl.texture_new_from_data(
			2, 1, Cogl.TextureFlags.NONE,
			Cogl.PixelFormat.RGBA_8888_PRE, Cogl.PixelFormat.ANY, 6, tex_data
		);
	}

	public TileShadow(TileShape shape) {
		this.shape = shape;
		var shape_verts = shape.verts;
		vbo = new Cogl.VertexBuffer(2*shape_verts.length);
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);

		float new_width, new_height;
		box.get_size(out new_width, out new_height);
		if (new_width == prev_width && new_height == prev_height) {
			return;
		}

		recalc_vbo();

		prev_width = new_width;
		prev_height = new_height;
	}

	protected void recalc_vbo() {
		Clutter.ActorBox box;
		get_allocation_box(out box);
		float w, h;
		box.get_size(out w, out h);

		float a = altitude;
		TileVertex[] shape_verts = shape.verts;
		uint n = shape_verts.length;
		float[,] verts = new float[2*n,2];
		float[] tex_coords = new float[2*n];

		for (uint i = 0; i < n; ++i) {
			float v1_x = shape_verts[i].x - shape_verts[(i-1)%n].x;
			float v1_y = shape_verts[i].y - shape_verts[(i-1)%n].y;
			float v1_len = Math.hypotf(v1_x, v1_y);

			float v2_x = shape_verts[(i+1)%n].x - shape_verts[i].x;
			float v2_y = shape_verts[(i+1)%n].y - shape_verts[i].y;
			float v2_len = Math.hypotf(v2_x, v2_y);

			float off_x = a * (v1_x*v2_len-v2_x*v1_len) / (v1_x*v2_y-v1_y*v2_x);
			float off_y = a * (v1_y*v2_len-v2_y*v1_len) / (v1_x*v2_y-v1_y*v2_x);

			verts[i,0] = shape_verts[i].x*w - off_x;
			verts[i,1] = shape_verts[i].y*h - off_y;
			verts[n+i,0] = shape_verts[i].x*w + off_x;
			verts[n+i,1] = shape_verts[i].y*h + off_y;

			tex_coords[i] = 0.75f;
			tex_coords[n+i] = 0.25f;
		}
		vbo.add("gl_Vertex", 2, Cogl.AttributeType.FLOAT, false, 0, verts);
		vbo.add(
			"gl_MultiTexCoord0", 1, Cogl.AttributeType.FLOAT, true, 0,
			tex_coords
		);
		vbo.submit();

		uchar[,] indices = new uchar[3*n-2,3];
		for (uint i = 0; i < n-2; ++i) {
			indices[i,0] = 0;
			indices[i,1] = (uchar)i+1;
			indices[i,2] = (uchar)i+2;
		}

		for (uint i = 0; i < n; ++i) {
			indices[n-2+2*i,0] = (uchar)i;
			indices[n-2+2*i,1] = (uchar) (n+i);
			indices[n-2+2*i,2] = (uchar) (n + (i+1)%n);

			indices[n-2+2*i+1,0] = (uchar)i;
			indices[n-2+2*i+1,1] = (uchar) (n + (i+1)%n);
			indices[n-2+2*i+1,2] = (uchar) ((i+1)%n);
		}
		index_buffer = new Cogl.VertexBufferIndices(
			Cogl.IndicesType.BYTE, indices, (int) (3*(3*n-2))
		);
	}

	public override void paint() {
		var shape_verts = shape.verts;

		Cogl.set_source_texture(texture);
		vbo.draw_elements(
			Cogl.VerticesMode.TRIANGLES, index_buffer,
			0, 2*shape_verts.length,
			0, 3*(3*shape_verts.length-2)
		);
	}
}

public abstract class Grid: Clutter.Actor {
	/**
	 * The base class for all grid types, which manage the state of a puzzle.
	 */

	protected ClutterGst.VideoTexture clutter_texture;

	public Grid(string video_file) {
		clutter_texture = new ClutterGst.VideoTexture();
		clutter_texture.sync_size = true;
		clutter_texture.size_change.connect((tex, w, h) => {
			queue_relayout();
		});
		clutter_texture.pixbuf_change.connect((tex) => {
			queue_redraw();
		});
		clutter_texture.set_filename(video_file);
	}

	public void start() {
		clutter_texture.set_playing(true);
	}

	public Cogl.Texture get_texture() {
		return clutter_texture.cogl_texture;
	}

	public Cogl.Material get_material() {
		return clutter_texture.cogl_material;
	}

	public override void get_preferred_width(
		float for_height, out float min_width, out float natural_width
	) {
		int texture_width, texture_height;
		clutter_texture.get_base_size(out texture_width, out texture_height);

		min_width = 0;
		if (for_height > 0) {
			natural_width = (float)texture_width / texture_height * for_height;
		}
		else {
			natural_width = texture_width;
		}
	}

	public override void get_preferred_height(
		float for_width, out float min_height, out float natural_height
	) {
		int texture_width, texture_height;
		clutter_texture.get_base_size(out texture_width, out texture_height);

		min_height = 0;
		natural_height = 0;
		if (for_width > 0) {
			if (texture_width == 0) {
				stderr.printf("texture_width == 0 ?!");
			}
			else {
				natural_height = 
					(float)texture_height / texture_width * for_width;
			}
		}
		else {
			natural_height = texture_height;
		}
	}

	/**
	 * Does this have all its tiles in the right place?
	 */
	public abstract bool is_solved();
	
	/**
	 * Randomize the locations of the tiles
	 */
	public abstract void shuffle();
}

// vim: set ts=4 sts=4 sw=4 ai noet :
