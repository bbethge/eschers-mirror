class Button: Clutter.Actor {
	// A button.

	public signal void clicked();

	// preferred ratio of padding to label height
	private class const float PADDING_RATIO = 1.0f/4;

	// whether the button is highlighted because the pointer is hovering over it
	private bool highlighted = false;

	private Clutter.Text label = new Clutter.Text();

	/**
	 * The text displayed on the button
	 */
	public string text {
		get { return label.text; }
		set { label.text = value; }
	}

	private Clutter.Color _color;
	/**
	 * The text (and highlight) color of the button, which should contrast with
	 * black
	 */
	public Clutter.Color color {
		get { return _color; }
		set {
			_color = value;
			update_label_color();
		}
	}

	public Button() {
		reactive = true;
		label.set_parent(this);
		color = Clutter.Color.from_string("#ffffffff");
	}

	// clutter.Actor methods

	public override void map() {
		base.map();
		label.map();
	}

	public override void unmap() {
		base.unmap();
		label.unmap();
	}

	public override void get_preferred_width(
		float for_height, out float min_width, out float natural_width
	) {
		min_width = 0;
		natural_width = 0;
		if (label.visible) {
			float label_min_width, label_natural_width;
			label.get_preferred_width(
				for_height, out label_min_width, out label_natural_width
			);
			float label_min_height, label_natural_height;
			label.get_preferred_height(
				label_natural_width, out label_min_height,
				out label_natural_height
			);
			min_width += label_min_width;
			natural_width += 
				label_natural_width + 2*PADDING_RATIO*label_natural_height;
		}
	}

	public override void get_preferred_height(
		float for_width, out float min_height, out float natural_height
	) {
		min_height = 0;
		natural_height = 0;
		if (label.visible) {
			float label_min_height, label_natural_height;
			label.get_preferred_height(
				for_width, out label_min_height, out label_natural_height
			);
			min_height = float.max(min_height, label_min_height);
			natural_height = float.max(
				natural_height, label_natural_height*(1+2*PADDING_RATIO));
		}
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		if (label != null && label.visible) {
			// Give the label the maximum of its preferred size and our
			// allocated size
			float w, h;
			label.get_preferred_size(null, null, out w, out h);
			w = float.min(w, box.get_width());
			h = float.min(h, box.get_height());

			// Center the label's allocation box in ours
			var label_box = Clutter.ActorBox();
			label_box.x1 = box.get_width()/2 - w/2;
			label_box.y1 = box.get_height()/2 - h/2;
			label_box.x2 = box.get_width()/2 + w/2;
			label_box.y2 = box.get_height()/2 + h/2;

			label.allocate(label_box, flags);
		}

		base.allocate(box, flags);
	}

	protected void update_label_color() {
		if (highlighted) {
			label.color = Clutter.Color.from_string("#000000ff");
		}
		else {
			label.color = color;
		}
		queue_redraw();
	}

	public override bool enter_event(Clutter.CrossingEvent event) {
		highlighted = true;
		update_label_color();
		return true;
	}

	public override bool leave_event(Clutter.CrossingEvent event) {
		highlighted = false;
		update_label_color();
		return true;
	}

	public override bool button_press_event(Clutter.ButtonEvent event) {
		clicked();
		return true;
	}

	public override void paint() {
		// Find out our size
		Clutter.ActorBox box;
		get_allocation_box(out box);
		float width, height;
		box.get_size(out width, out height);

		// Draw a rounded rectangle for the background
		if (highlighted) {
			Cogl.set_source_color4ub(
				color.red, color.green, color.blue,
				color.alpha*get_paint_opacity()/255
			);
		}
		else {
			Cogl.set_source_color4ub(0, 0, 0, get_paint_opacity()/2);
		}
		Cogl.path_round_rectangle(0, 0, width, height, 5, 5);
		Cogl.path_fill();

		label.paint();
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
