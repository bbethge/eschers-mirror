class Frame: Clutter.Actor, Clutter.Container, Clutter.Scriptable {
	// A container that adds space around its single child.  If expand_child is
	// set, the child will get all the space except for optional padding.
	// Otherwise, the child gets its preferred size if possible.

	private bool _expand_child;
	[Property(
		nick="Expand child",
		blurb="When set, the child will get all space except padding, rather than its requested size"
	)]
	public bool expand_child {
		get { return _expand_child; }
		set { _expand_child = value; queue_relayout(); }
		default = false;
	}

	private float _padding;
	public float padding {
		get { return _padding; }
		set { _padding = value; queue_relayout(); }
		default = 0.0f;
	}

	protected Clutter.Actor? child = null;

	// Clutter.Container methods

	public void add_actor(Clutter.Actor new_child) {
		if (new_child != child) {
			if (child != null) {
				child.unparent();
			}
			stdout.printf("add_actor\n");
			child = new_child;
			child.set_parent(this);
			queue_relayout();
		}
	}
	
	public void remove_actor(Clutter.Actor child) {
		if (child == this.child) {
			this.child = null;
			child.unparent();
			queue_relayout();
		}
	}

	public void @foreach(Clutter.Callback callback) {
		if (child != null) {
			callback(child);
		}
	}

	public void sort_depth_order() {
		// Single child
	}

	// Clutter.Actor methods

	public override void get_preferred_width(
		float for_height, out float min_width, out float natural_width
	) {
		min_width = 0;
		natural_width = 0;
		if (child != null && child.visible) {
			float child_min_width, child_natural_width;
			child.get_preferred_width(
				for_height, out child_min_width, out child_natural_width
			);
			float child_min_height, child_natural_height;
			child.get_preferred_height(
				child_natural_width,
				out child_min_height, out child_natural_height
			);
			min_width += child_min_width;
			natural_width += child_natural_width + 2*padding;
		}
	}

	public override void get_preferred_height(
		float for_width, out float min_height, out float natural_height
	) {
		min_height = 0;
		natural_height = 0;
		if (child != null && child.visible) {
			float child_min_height, child_natural_height;
			child.get_preferred_height(
				for_width, out child_min_height, out child_natural_height
			);
			min_height = float.max(min_height, child_min_height);
			natural_height = float.max(
				natural_height, child_natural_height + 2*padding
			);
		}
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		if (child != null && child.visible) {
			float w, h;
			box.get_size(out w, out h);
			float child_w, child_h;
			if (expand_child) {
				child_w = w - 2*padding;
				child_h = h - 2*padding;
			}
			else {
				float child_pref_w, child_pref_h;
				child.get_preferred_size(
					null, null, out child_pref_w, out child_pref_h
				);
				child_w = float.min(child_pref_w, w);
				child_h = float.min(child_pref_h, h);
			}

			// Center the child's allocation box in ours
			var child_box = Clutter.ActorBox();
			child_box.x1 = w/2 - child_w/2;
			child_box.y1 = h/2 - child_h/2;
			child_box.x2 = w/2 + child_w/2;
			child_box.y2 = h/2 + child_h/2;

			child.allocate(child_box, flags);
		}
		stdout.printf("allocate %f, %f, %f, %f\n", box.x1, box.y1, box.x2, box.y2);

		base.allocate(box, flags);
	}

	public override void paint() {
		if (child != null) {
			child.paint();
		}
	}
	
	public override void pick(Clutter.Color color) {
		base.pick(color);
		if (child != null) {
			child.paint();
		}
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
