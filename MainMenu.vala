class MainMenu: BoxLayout {
	Clutter.Color color;

	public MainMenu(Clutter.Color color) {
		orientation = BoxLayout.Orientation.VERTICAL;
		this.color = color;
	
		var title = new Clutter.Text();
		title.set_markup("<span size=\"xx-large\">Escher\'s Mirror</span>");
		title.color = color;
		pack(title, true, false);

		var vbox = new BoxLayout();
		vbox.orientation = BoxLayout.Orientation.VERTICAL;
		vbox.padding = 10;
		pack(vbox, true, false);

		var start = new Button();
		start.text = "Start";
		start.color = color;
		vbox.add(start);
		start.clicked.connect((b) => {
			MenuManager? manager = get_parent() as MenuManager;
			if (manager != null) {
				manager.transition(
					new VideoChooserMenu(this.color),
					MenuManager.TransitionDirection.RIGHT
				);
			}
			else {
				warning("MainMenu: parent is not MenuManager\n");
			}
		});

		var options = new Button();
		options.text = "Options";
		options.color = color;
		vbox.add(options);
		options.clicked.connect((b) => {
			MenuManager? manager = get_parent() as MenuManager;
			if (manager != null) {
				var menu = new OptionsMenu(this.color);
				manager.transition(menu, MenuManager.TransitionDirection.LEFT);
			}
			else {
				warning("MainMenu: parent is not MenuManager\n");
			}
		});

		var quit = new Button();
		quit.text = "Quit";
		quit.color = color;
		vbox.add(quit);

		quit.clicked.connect((b) => {
			Clutter.main_quit();
		});
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
