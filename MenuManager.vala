public class MenuManager: Clutter.Actor {
	public enum TransitionDirection {
		LEFT,
		RIGHT
	}

	private Clutter.Actor current;
	private Clutter.Actor? next = null;
	private Clutter.Behaviour? current_behaviour;
	private Clutter.Behaviour? next_behaviour;

	public MenuManager(Clutter.Actor initial) {
		current = initial;
		current.set_parent(this);
		current.set_anchor_point_from_gravity(Clutter.Gravity.SOUTH_EAST);
	}

	public override void allocate(
		Clutter.ActorBox box, Clutter.AllocationFlags flags
	) {
		base.allocate(box, flags);

		float w, h;
		box.get_size(out w, out h);

		// x1 and y1 are the *bottom right* corner of the child (since it has
		// south-east gravity); x2 and y2 are meaningless except that x2-x1
		// and y2-y1 are the width and height of the child.
		var child_box = Clutter.ActorBox();
		child_box.x1 = w;
		child_box.y1 = h;
		child_box.x2 = 2*w;
		child_box.y2 = 2*h;

		current.allocate(child_box, flags);
		if (next != null) {
			next.allocate(child_box, flags);
		}
	}

	public override void map() {
		base.map();
		current.map();
		if (next != null) {
			next.map();
		}
	}

	public override void unmap() {
		base.unmap();
		current.unmap();
		if (next != null) {
			next.unmap();
		}
	}

	public override void paint() {
		current.paint();
		if (next != null) {
			next.paint();
		}
	}

	public override void pick(Clutter.Color color) {
		base.pick(color);
		current.paint();
		if (next != null) {
			next.paint();
		}
	}

	public Clutter.Timeline transition(
		Clutter.Actor next, TransitionDirection direction
	) {
		this.next = next;
		next.set_parent(this);
		next.set_anchor_point_from_gravity(Clutter.Gravity.SOUTH_EAST);
		// This seems redundant, but is necessary to prevent next from being
		// flashed before the animation starts
		next.set_rotation(
			Clutter.RotateAxis.Z_AXIS,
			direction == TransitionDirection.RIGHT ? 90: 270,
			0, 0, 0
		);

		var timeline = new Clutter.Timeline(500);
		var alpha = new Clutter.Alpha.full(
			timeline, Clutter.AnimationMode.EASE_IN_OUT_QUAD
		);

		current_behaviour = new Clutter.BehaviourRotate(
			alpha, Clutter.RotateAxis.Z_AXIS,
			direction == TransitionDirection.RIGHT ?
				Clutter.RotateDirection.CCW : Clutter.RotateDirection.CW,
			0, direction == TransitionDirection.RIGHT ? 270 : 90
		);
		current_behaviour.apply(current);

		next_behaviour = new Clutter.BehaviourRotate(
			alpha, Clutter.RotateAxis.Z_AXIS,
			direction == TransitionDirection.RIGHT ?
				Clutter.RotateDirection.CCW : Clutter.RotateDirection.CW,
			direction == TransitionDirection.RIGHT ? 90 : 270, 0
		);
		next_behaviour.apply(next);

		timeline.completed.connect((t) => {
			current.unparent();
			current = this.next;
			this.next = null;
			current_behaviour = null;
			next_behaviour = null;
		});

		timeline.start();
		return timeline;
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
