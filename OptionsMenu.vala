public class OptionsMenu: BoxLayout {
	private Clutter.Color color;

	public OptionsMenu(Clutter.Color color) {
		orientation = Orientation.VERTICAL;
		this.color = color;

		var video_dir_entry = new Clutter.Text();
		video_dir_entry.text = Config.get_config().video_dir;
		video_dir_entry.color = color;
		video_dir_entry.reactive = true;
		video_dir_entry.editable = true;
		video_dir_entry.single_line_mode = true;
		video_dir_entry.text_changed.connect((vde) => {
			Config.get_config().video_dir = vde.text;
		});
		pack(video_dir_entry, false, true);

		var back = new Button();
		back.text = "Back";
		back.color = color;
		back.clicked.connect((b) => {
			MenuManager? manager = get_parent() as MenuManager;
			if (manager != null) {
				manager.transition(
					new MainMenu(this.color),
					MenuManager.TransitionDirection.RIGHT
				);
			}
			else {
				warning("OptionsMenu: parent is not MenuManager");
			}
		});
		pack(back, false, false);
	}
}
	
// vim: set ts=4 sts=4 sw=4 ai noet :
