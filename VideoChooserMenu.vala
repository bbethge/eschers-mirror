public class VideoChooserMenu: BoxLayout {
	private Clutter.Color color;
	private ListSelector chooser;

	public VideoChooserMenu(Clutter.Color color) {
		orientation = BoxLayout.Orientation.VERTICAL;
		this.color = color;

		var file_names = new List<string>();

		// Figure out where videos are stored
		string video_dir_name;
		unowned KeyFile config = get_config();
		try {
			video_dir_name = config.get_string("default", "video_dir");
		}
		catch (KeyFileError err) {
			video_dir_name = 
				Environment.get_user_special_dir(UserDirectory.VIDEOS);
			config.set_string("default", "video_dir", video_dir_name);
			try {
				config.set_comment(
					"default", "video_dir",
					"Directory where music videos are stored"
				);
			}
			catch (KeyFileError err2) {
				// Ignore -- it's just a comment
			}
		}

		// Read the filenames from the video directory
		try {
			var video_dir = Dir.open(video_dir_name);
			while (true) {
				weak string name = video_dir.read_name();
				if (name == null) break;
				file_names.prepend(name);
			}
		}
		catch (FileError err) {
			warning(
				"Couldn't open video directory %s: %s\n",
				video_dir_name, err.message
			);
		}
		if (file_names.length() == 0) {
			warning("Couldn't find any videos in %s\n", video_dir_name);
		}

		// Sort the video filenames
		file_names.sort((CompareFunc)string.collate);

		chooser = new ListSelector(file_names);
		chooser.color = color;
		pack(chooser, false, false);
		//chooser.selected = file_names.data;

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
		go.clicked.connect(on_go_clicked);
	}

	private void on_go_clicked(Button go) {
		string filename = Path.build_filename(
			"/home/ben/Music Videos", chooser.selected, null
		);
		var grid = new RectGrid(filename, 3, 4, true);
		MenuManager? manager = get_parent() as MenuManager;
		if (manager != null) {
			var timeline = manager.transition(
				grid, MenuManager.TransitionDirection.RIGHT
			);
			timeline.completed.connect((t) => {
				grid.start();
			});
		}
		else {
			warning(
				"VideoChooserMenu: parent is %s, not MenuManager\n",
				get_parent().get_type().name()
			);
		}
	}

	//def start_video(self, timeline):
	//	filename = os.path.join(config.video_dir, self.chooser.get_selected())
	//	grid = RectGrid(filename, 3, 4)
	//	self.group.add(grid)
	//	grid.set_x(2*self.group.stage.get_width())
	//	grid.start()
}
	
// vim: set ts=4 sts=4 sw=4 ai noet :
