public int main(string[] args) {
	ClutterGst.init(ref args);

	var stage = new Clutter.Stage();
		var stage_color = Clutter.Color();
		stage_color.red = 0x80;
		stage_color.green = 0x80;
		stage_color.blue = 0x80;
		stage_color.alpha = 0xff;
		stage.color = stage_color;
		stage.hide.connect((s) => { Clutter.main_quit(); });
		var grid = new RectGrid("/home/ben/Music Videos/betika.ogv", 3, 4);
			stage.add_actor(grid);
		stage.show();

	grid.start();
	Clutter.main();

	return 0;
}

// vim: set ts=4 sts=4 sw=4 ai noet :
