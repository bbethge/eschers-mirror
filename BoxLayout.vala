protected class BoxLayoutChildMeta: Clutter.ChildMeta {
	[Property(nick="Expand", blurb="Expand to use all available space")]
	public bool expand { get; set; default = false; }

	[Property(nick="Fill", blurb="Fill all available space")]
	public bool fill { get; set; default = false; }
}

public class BoxLayout: Clutter.Actor, Clutter.Container, Clutter.Scriptable {
	public enum Orientation {
		HORIZONTAL,
		VERTICAL
	}

	private Orientation _orientation;
	public Orientation orientation {
		get { return _orientation; }
		set {
			_orientation = value;
			queue_relayout();
		}
		default = Orientation.HORIZONTAL;
	}

	private uint _padding;
	public uint padding {
		get { return _padding; }
		set {
			_padding = value;
			queue_relayout();
		}
		default = 0;
	}

	private List<Clutter.Actor> children;
	private class bool child_meta_installed = false;

	public BoxLayout() {
		// FIXME: there should be a better way to do this
		if (!child_meta_installed) {
			Errata.install_child_meta(
				typeof(BoxLayout), typeof(BoxLayoutChildMeta)
			);
			child_meta_installed = true;
		}
	}

	public void add_actor(Clutter.Actor actor) {
		if (children.index(actor) == -1) {
			children.append(actor);
			actor.set_parent(this);
			queue_relayout();
		}
		else {
			warning(
				"Actor of type %s is already a child of this %s\n",
				actor.get_type().name(), get_type().name()
			);
		}
	}

	public void remove_actor(Clutter.Actor actor) {
		if (children.index(actor) == -1) {
			warning(
				"Actor of type %s is not a child of this %s",
				actor.get_type().name(), get_type().name()
			);
		}
		else {
			children.remove(actor);
			actor.unparent();
			queue_relayout();
		}
	}

	public void @foreach(Clutter.Callback callback) {
		foreach (var child in children) {
			callback(child);
		}
	}

	public override void get_preferred_width(
		float for_height, out float min_width, out float natural_width
	) {
		min_width = 0;
		natural_width = 0;
		if (orientation == Orientation.HORIZONTAL) {
			foreach (var child in children) {
				float child_min_w, child_natural_w;
				child.get_preferred_width(
					for_height, out child_min_w, out child_natural_w
				);
				min_width += child_min_w;
				natural_width += child_natural_w;
			}
			natural_width += (children.length()-1) * padding;
		}
		else {
			foreach (var child in children) {
				float child_min_w, child_natural_w;
				child.get_preferred_width(
					-1, out child_min_w, out child_natural_w
				);
				min_width = float.max(min_width, child_min_w);
				natural_width = float.max(natural_width, child_natural_w);
			}
		}
	}

	public override void get_preferred_height(
		float for_width, out float min_height, out float natural_height
	) {
		min_height = 0;
		natural_height = 0;
		if (orientation == Orientation.HORIZONTAL) {
			foreach (var child in children) {
				float child_min_h, child_natural_h;
				child.get_preferred_height(
					-1, out child_min_h, out child_natural_h
				);
				min_height = float.max(min_height, child_min_h);
				natural_height = float.max(natural_height, child_natural_h);
			}
		}
		else {
			foreach (var child in children) {
				float child_min_h, child_natural_h;
				child.get_preferred_height(
					for_width, out child_min_h, out child_natural_h
				);
				min_height += child_min_h;
				natural_height += child_natural_h;
			}
			natural_height += (children.length()-1) * padding;
		}
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);

		float w, h;
		box.get_size(out w, out h);

		if (orientation == Orientation.HORIZONTAL) {
			float base_min_w = 0;
			float base_pref_w = 0;
			var min_widths = new float[children.length()];
			var pref_widths = new float[children.length()];
			uint num_expanded = 0;
			float actual_padding = 0;
			float[] widths;
			uint i = 0;
			for (
				weak List<Clutter.Actor> child_link = children;
				child_link != null;
				child_link = child_link.next
			) {
				float child_min_w, child_pref_w;
				child_link.data.get_preferred_width(
					h, out child_min_w, out child_pref_w
				);
				base_min_w += child_min_w;
				base_pref_w += child_pref_w;
				min_widths[i] = child_min_w;
				pref_widths[i] = child_pref_w;

				bool expand;
				child_get(child_link.data, "expand", out expand, null);
				if (expand) {
					++num_expanded;
				}
				++i;
			}
			if (w < base_pref_w) {
				widths = min_widths;
				if (children.length() > 1) {
					actual_padding = (w-base_min_w) / (children.length()-1);
				}
			}
			else if (w < base_pref_w + (children.length()-1)*padding) {
				widths = pref_widths;
				if (children.length() > 1) {
					actual_padding = (w-base_pref_w) / (children.length()-1);
				}
			}
			else {
				widths = pref_widths;
				// FIXME: is this consistent with our size request?
				actual_padding = padding;

				if (num_expanded > 0) {
					float extra_w =
						w - base_pref_w - (children.length()-1)*actual_padding;
					i = 0;
					for (
						weak List<Clutter.Actor> child_link = children;
						child_link != null;
						child_link = child_link.next
					) {
						bool expand;
						child_get(child_link.data, "expand", out expand, null);
						if (expand) {
							widths[i] += extra_w / num_expanded;
						}
						++i;
					}
				}
			}
			float x = 0;
			i = 0;
			for (
				weak List<Clutter.Actor> child_link = children;
				child_link != null;
				child_link = child_link.next
			) {
				var child_box = Clutter.ActorBox();

				bool fill;
				child_get(child_link.data, "fill", out fill, null);
				if (fill) {
					child_box.x1 = x;
					child_box.y1 = 0;
					child_box.x2 = x + widths[i];
					child_box.y2 = h;
				}
				else {
					float child_pref_w, child_pref_h;
					child_link.data.get_preferred_size(
						null, null, out child_pref_w, out child_pref_h
					);
					float child_w = float.min(widths[i], child_pref_w);
					float child_h = float.min(h, child_pref_h);
					child_box.x1 = x + widths[i]/2 - child_w/2;
					child_box.y1 = h/2 - child_h/2;
					child_box.x2 = x + widths[i]/2 + child_w/2;
					child_box.y2 = h/2 + child_h/2;
				}
				x += widths[i] + actual_padding;
				child_link.data.allocate(child_box, flags);
				++i;
			}
		}
		else {  // orientation == VERTICAL
			float base_min_h = 0;
			float base_pref_h = 0;
			var min_heights = new float[children.length()];
			var pref_heights = new float[children.length()];
			uint num_expanded = 0;
			float actual_padding = 0;
			float[] heights;
			uint i = 0;
			for (
				weak List<Clutter.Actor> child_link = children;
				child_link != null;
				child_link = child_link.next
			) {
				float child_min_h, child_pref_h;
				child_link.data.get_preferred_height(
					h, out child_min_h, out child_pref_h
				);
				base_min_h += child_min_h;
				base_pref_h += child_pref_h;
				min_heights[i] = child_min_h;
				pref_heights[i] = child_pref_h;
				bool expand;
				child_get(child_link.data, "expand", out expand, null);
				if (expand) {
					++num_expanded;
				}
				++i;
			}
			if (h < base_pref_h) {
				heights = min_heights;
				if (children.length() > 1) {
					actual_padding =
						(h-base_min_h) / (children.length()-1);
				}
			}
			else if (h < base_pref_h + (children.length()-1)*padding) {
				heights = pref_heights;
				if (children.length() > 1) {
					actual_padding = (h-base_pref_h) / (children.length()-1);
				}
			}
			else {
				heights = pref_heights;
				actual_padding = padding;
				if (num_expanded > 0) {
					float extra_h =
						h - base_pref_h - (children.length()-1)*actual_padding;
					i = 0;
					for (
						weak List<Clutter.Actor> child_link = children;
						child_link != null;
						child_link = child_link.next
					) {
						bool expand;
						child_get(child_link.data, "expand", out expand, null);
						if (expand) {
							heights[i] += extra_h / num_expanded;
						}
						++i;
					}
				}
			}
			float y = 0;
			i = 0;
			for (
				weak List<Clutter.Actor> child_link = children;
				child_link != null;
				child_link = child_link.next
			) {
				var child_box = Clutter.ActorBox();
				bool fill;
				child_get(child_link.data, "fill", out fill, null);
				if (fill) {
					child_box.x1 = 0;
					child_box.y1 = y;
					child_box.x2 = w;
					child_box.y2 = y + heights[i];
				}
				else {
					float child_pref_w, child_pref_h;
					child_link.data.get_preferred_size(
						null, null, out child_pref_w, out child_pref_h
					);
					float child_w = float.min(w, child_pref_w);
					float child_h = float.min(heights[i], child_pref_h);
					child_box.x1 = w/2 - child_w/2;
					child_box.y1 = y + heights[i]/2 - child_h/2;
					child_box.x2 = w/2 + child_w/2;
					child_box.y2 = y + heights[i]/2 + child_h/2;
				}
				y += heights[i] + actual_padding;
				child_link.data.allocate(child_box, flags);
				++i;
			}
		}
	}

	public override void paint() {
		foreach (var child in children) {
			child.paint();
		}
	}
	
	public override void pick(Clutter.Color color) {
		base.pick(color);
		foreach (var child in children) {
			child.paint();
		}
	}
	
	public void pack(Clutter.Actor child, bool expand, bool fill) {
		add_actor(child);
		child_set(child, "expand", expand, "fill", fill, null);
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
