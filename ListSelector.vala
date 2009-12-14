protected class ListItem: Clutter.Actor {
	public signal void selected();

	// Preferred ratio of padding to label height
	private const float PADDING_RATIO = 1.0f/4;

	private Clutter.Text label;
	private bool is_highlighted = false;
	private bool is_selected = false;

	public string text {
		get { return label.text; }
		set { label.text = value; }
	}

	private Clutter.Color _color;
	public Clutter.Color color {
		get { return _color; }
		set {
			_color = value;
			update_label_color();
		}
	}

	public ListItem() {
		reactive = true;

		label = new Clutter.Text();
		label.ellipsize = Pango.EllipsizeMode.END;
		label.set_parent(this);
	}

	private void update_label_color() {
		if (is_selected) {
			label.color = Clutter.Color.from_string("#000000ff");
		}
		else {
			label.color = color;
		}
		queue_redraw();
	}

	public override bool enter_event(Clutter.CrossingEvent event) {
		is_highlighted = true;
		update_label_color();
		return true;
	}

	public override bool leave_event(Clutter.CrossingEvent event) {
		is_highlighted = false;
		update_label_color();
		return true;
	}

	public override bool button_press_event(Clutter.ButtonEvent event) {
		select();
		return true;
	}

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
		float label_min_width, label_natural_width;
		label.get_preferred_width(
			for_height, out label_min_width, out label_natural_width
		);
		float label_min_height, label_natural_height;
		label.get_preferred_height(
			label_natural_width, out label_min_height,
			out label_natural_height
		);
		min_width = label_min_width;
		natural_width = 
			label_natural_width + 2*PADDING_RATIO*label_natural_height;
	}

	public override void get_preferred_height(
		float for_width, out float min_height, out float natural_height
	) {
		float label_min_height, label_natural_height;
		label.get_preferred_height(
			for_width, out label_min_height, out label_natural_height
		);
		min_height = label_min_height;
		natural_height = label_natural_height * (1+2*PADDING_RATIO);
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);

		float box_w, box_h;
		box.get_size(out box_w, out box_h);

		float unused, label_h;
		label.get_preferred_height(box_w, out unused, out label_h);
		label_h = float.min(box_h, label_h);

		float padding = PADDING_RATIO * label_h;

		// The height given to the label is its requested height or our
		// allocated height, whichever is smaller; the width is our allocated
		// width minus padding.
		var label_box = Clutter.ActorBox();
		label_box.x1 = padding;
		label_box.y1 = box_h/2 - label_h/2;
		label_box.x2 = label_box.x1 + box_w - 2*padding;
		label_box.y2 = label_box.y1 + label_h;
		label.allocate(label_box, flags);
	}

	public override void paint() {
		Clutter.ActorBox box;
		get_allocation_box(out box);
		float width, height;
		box.get_size(out width, out height);

		// If highlighted, draw a stroked round rectangle; if selected, draw a
		// filled round rectangle.
		if (is_highlighted || is_selected) {
			Cogl.set_source_color4ub(
				color.red, color.green, color.blue,
				color.alpha*get_paint_opacity()/255
			);
			Cogl.path_round_rectangle(0, 0, width, height, 5, 5);
			if (is_selected) {
				Cogl.path_fill();
			}
			else {
				Cogl.path_stroke();
			}
		}

		label.paint();
	}

	public void select() {
		if (!is_selected) {
			is_selected = true;
			update_label_color();
			selected();
		}
	}
	
	public void deselect() {
		is_selected = false;
		update_label_color();
	}
}

class ListSelector: Clutter.Actor {
	private List<ListItem> items = new List<ListItem>();
	private weak ListItem? selected_item = null;

	private Clutter.Color _color;
	public Clutter.Color color {
		get { return _color; }
		set {
			_color = value;
			foreach (var item in items) {
				item.color = _color;
			}
		}
	}

	public ListSelector(List<string> item_names) {
		foreach (var name in item_names) {
			var new_item = new ListItem();
			new_item.text = name;
			new_item.color = color;
			new_item.selected.connect(on_item_selected);
			items.append(new_item);
			new_item.set_parent(this);
		}
	}

	public override void map() {
		base.map();
		foreach (var item in items) {
			item.map();
		}
	}

	public override void unmap() {
		base.unmap();
		foreach (var item in items) {
			item.unmap();
		}
	}

	public override void get_preferred_width(
		float for_height, out float min_width, out float natural_width
	) {
		min_width = 0;
		natural_width = 0;
		foreach (var item in items) {
			float item_min_w, item_natural_w;
			item.get_preferred_width(-1, out item_min_w, out item_natural_w);
			min_width = float.max(min_width, item_min_w);
			natural_width = float.max(natural_width, item_natural_w);
		}
	}

	public override void get_preferred_height(
		float for_width, out float min_height, out float natural_height
	) {
		min_height = 0;
		natural_height = 0;
		foreach (var item in items) {
			float item_min_h, item_natural_h;
			item.get_preferred_height(-1, out item_min_h, out item_natural_h);
			min_height += item_min_h;
			natural_height += item_natural_h;
		}
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);

		float x, y, width, height;
		box.get_origin(out x, out y);
		box.get_size(out width, out height);

		float y_off = 0;
		foreach (var item in items) {
			float unused, item_h;
			item.get_preferred_height(width, out unused, out item_h);

			var item_box = Clutter.ActorBox();
			item_box.x1 = 0;
			item_box.y1 = y_off;
			item_box.x2 = width;
			item_box.y2 = y_off + item_h;
			item.allocate(item_box, flags);
			y_off += item_h;
		}
	}

	public override void paint() {
		Clutter.ActorBox box;
		get_allocation_box(out box);
		float w, h;
		box.get_size(out w, out h);

		Cogl.set_source_color4ub(0, 0, 0, get_paint_opacity()/2);
		Cogl.path_round_rectangle(0, 0, w, h, 6, 5);
		Cogl.path_fill();

		foreach (var item in items) {
			item.paint();
		}
	}

	public override void pick(Clutter.Color color) {
		base.pick(color);
		foreach (var item in items) {
			item.paint();
		}
	}
	
	public string selected {
		get { return selected_item.text; }
		set {
			foreach (var item in items) {
				if (item.text == value) {
					item.select();
					break;
				}
			}
		}
	}

	private void on_item_selected(ListItem selected_item) {
		if (this.selected_item != null) {
			this.selected_item.deselect();
		}
		this.selected_item = selected_item;
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
