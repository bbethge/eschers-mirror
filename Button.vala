class Button: Clutter.Actor, Clutter.Container, Clutter.Scriptable {
	// A button.
	// 
	// Although it isn't designed to let you add arbitrary actors to it, I can't
	// make it work without inheriting from clutter.Container.

	public signal void clicked();

	static float padding_ratio = 1.0f/4;
		// preferred ratio of padding to child height

	private bool highlighted = false;
	protected Clutter.Actor? child = null;

	private static Clutter.Color default_color =
		Clutter.Color.from_string("#ffffffff");
	private Clutter.Color _color;
	public Clutter.Color color {
		get { return _color; }
		set {
			_color = value;
			update_child_color();
		}
		default = default_color;
	}

	public Button() {
		reactive = true;

		//self.connect('enter-event', self.__class__.on_enter)
		//self.connect('leave-event', self.__class__.on_leave)
		//self.connect('button-press-event', self.__class__.on_button_press)
	}

	// clutter.Container methods

	 public void add_actor(Clutter.Actor actor) {
		if (actor != child && actor is Clutter.Text) {
			if (child != null) {
				child.unparent();
			}
			child = actor;
			child.set_parent(this);
			queue_relayout();
		}
	}
	
	public void remove_actor(Clutter.Actor actor) {
		if (actor == child) {
			child = null;
			actor.unparent();
			queue_relayout();
		}
	}

	public void @foreach(Clutter.Callback callback) {
		if (child != null) {
			callback(child);
		}
	}

	// clutter.Actor methods

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
				child_natural_width, out child_min_height,
				out child_natural_height
			);
			min_width += child_min_width;
			natural_width += 
				child_natural_width + 2*padding_ratio*child_natural_height;
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
				natural_height, child_natural_height*(1+2*padding_ratio));
		}
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		if (child != null && child.visible) {
			// Give the child the maximum of its preferred size and our
			// allocated size
			float w, h;
			child.get_preferred_size(null, null, out w, out h);
			w = float.min(w, box.get_width());
			h = float.min(h, box.get_height());

			// Center the child's allocation box in ours
			var child_box = Clutter.ActorBox();
			child_box.x1 = box.get_width()/2 - w/2;
			child_box.y1 = box.get_height()/2 - h/2;
			child_box.x2 = box.get_width()/2 + w/2;
			child_box.y2 = box.get_height()/2 + h/2;

			child.allocate(child_box, flags);
		}

		base.allocate(box, flags);
	}

	protected void update_child_color() {
		if (child != null && child is Clutter.Text) {
			if (highlighted) {
				((Clutter.Text)child).color =
					Clutter.Color.from_string("#000000ff");
			}
			else {
				((Clutter.Text)child).color = color;
			}
		}
	}

	public void set_text(string text) {
		if (child == null) {
			add_actor(new Clutter.Text());
			update_child_color();
		}
		if (child is Clutter.Text) {
			((Clutter.Text)child).text = text;
		}
	}

	public override bool enter_event(Clutter.CrossingEvent event) {
		highlighted = true;
		update_child_color();
		return true;
	}

	public override bool leave_event(Clutter.CrossingEvent event) {
		highlighted = false;
		update_child_color();
		return true;
	}

	public override bool button_press_event(Clutter.ButtonEvent event) {
		clicked();
		return true;
	}

	public override void paint() {
		Clutter.ActorBox box;
		get_allocation_box(out box);

		float width, height;
		box.get_size(out width, out height);

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

		if (child != null) {
			child.paint();
		}
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
