public int main(string[] args) {
	Clutter.init(ref args);

	var stage = new Clutter.Stage();
		var stage_color = Clutter.Color();
		stage_color.red = 0x80;
		stage_color.green = 0x80;
		stage_color.blue = 0x80;
		stage_color.alpha = 0xff;
		stage.color = stage_color;
		stage.hide.connect((s) => { Clutter.main_quit(); });
		//var main = new MainMenu(Clutter.Color.from_string("#a0ff90ff"));
		//var menus = new MenuManager(main);
		//	stage.add(menus);
		//	menus.set_size(640, 480);
		var items = new List<string>();
		items.append("foo");
		items.append("bar");
		var list = 
			new ListSelector(items, Clutter.Color.from_string("#a0ff90ff"));
			stage.add(list);
		stage.show();

	Clutter.main();

	return 0;
}

// vim: set ts=4 sts=4 sw=4 ai noet :
