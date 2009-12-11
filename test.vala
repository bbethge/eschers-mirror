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
		var layout = new BoxLayout();
			layout.set_size(300, 200);
			layout.padding = 10;
			layout.orientation = BoxLayout.Orientation.HORIZONTAL;
			var button = new Button();
				button.text = "hello";
				layout.pack(button, true, true);
			var button2 = new Button();
				button2.text = "goodbye";
				layout.pack(button2, true, false);
			stage.add_actor(layout);
		stage.show();

	Clutter.main();

	return 0;
}

// vim: set ts=4 sts=4 sw=4 ai noet :
