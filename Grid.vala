public abstract class Grid: Clutter.Actor {
	// The base class for all grid types, which manage the state of a puzzle.

	protected ClutterGst.VideoTexture clutter_texture;

	public Grid(string video_file) {
		clutter_texture = new ClutterGst.VideoTexture();
		clutter_texture.sync_size = true;
		// HACK to make clutter_texture.get_preferred_{width,height} work
		clutter_texture.set_parent(this);
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

	public abstract bool is_solved();
		// Does this have all its tiles in the right place?
	
	public abstract void shuffle();
		// Randomize the locations of the tiles
}

// vim: set ts=4 sts=4 sw=4 ai noet :
