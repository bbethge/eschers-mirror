public class VideoChooserMenu: BoxLayout {
	private Clutter.Color color;

	public VideoChooserMenu(Clutter.Color color) {
		orientation = BoxLayout.Orientation.VERTICAL;
		this.color = color;

		var file_names = new List<string>();
		try {
			// FIXME: hard-coded path
			var video_dir = Dir.open("/home/ben/Music Videos");
			while (true) {
				weak string name = video_dir.read_name();
				if (name == null) break;
				file_names.prepend(name);
			}
		}
		catch (FileError err) {
			warning("Couldn't open video directory: %s\n", err.message);
		}
		if (file_names.length() == 0) {
			warning("Couldn't find any videos\n");
		}
		file_names.sort((CompareFunc)string.collate);

		var chooser = new ListSelector(file_names);
		chooser.color = color;
		pack(chooser, false, false);
		chooser.selected = file_names.data;

		pack(new Frame(), true, true);
		
		var hbox = new BoxLayout();
		hbox.orientation = BoxLayout.Orientation.HORIZONTAL;
		pack(hbox, false, true);

		var back = new Button();
		back.text = "Back";
		back.color = color;
		hbox.pack(back, false, false);
		back.clicked.connect((b) => {
			MenuManager? manager = get_parent() as MenuManager;
			if (manager != null) {
				manager.transition(
					new MainMenu(this.color),
					MenuManager.TransitionDirection.LEFT
				);
			}
			else {
				warning("VideoChooserMenu: parent is not MenuManager\n");
			}
		});

		hbox.pack(new Frame(), true, true);

		var go = new Button();
		go.text = "Go";
		go.color = color;
		hbox.pack(go, false, false);
		//go.connect('clicked', self.on_go_clicked)
	}

	//def start_video(self, timeline):
	//	filename = os.path.join(config.video_dir, self.chooser.get_selected())
	//	grid = RectGrid(filename, 3, 4)
	//	self.group.add(grid)
	//	grid.set_x(2*self.group.stage.get_width())
	//	grid.start()
}
	
// vim: set ts=4 sts=4 sw=4 ai noet :
