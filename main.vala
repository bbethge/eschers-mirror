public int main(string[] args) {
	ClutterGst.init(ref args);

	var stage = new Clutter.Stage();
		var stage_color = Clutter.Color.from_string("#808080ff");
		stage.color = stage_color;
		stage.hide.connect((s) => { Clutter.main_quit(); });
		var main = new MainMenu(Clutter.Color.from_string("#a0ff90ff"));
		var menus = new MenuManager(main);
			stage.add(menus);
			menus.set_size(640, 480);
		stage.show();

	Clutter.main();

	Config.get_config().write();

	return 0;
}

// vim: set ts=4 sts=4 sw=4 ai noet :
