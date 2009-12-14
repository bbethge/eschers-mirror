private KeyFile? config = null;

private string get_config_filename() {
	return Path.build_filename(
		Environment.get_user_config_dir(), "eschers-mirror", null
	);
}

public unowned KeyFile get_config() {
	if (config == null) {
		config = new KeyFile();
		try {
			config.load_from_file(
				get_config_filename(), KeyFileFlags.KEEP_COMMENTS
			);
		}
		catch (KeyFileError err) {
			warning("Error in configuration file: %s\n", err.message);
		}
		catch (FileError err) {
			// Just use empty config
		}
	}
	return config;
}
	
public void write_config() {
	if (config != null) {
		size_t length;
		string data = config.to_data(out length);
		string filename = get_config_filename();
		try {
			FileUtils.set_contents(filename, data, (ssize_t)length);
		}
		catch (FileError err) {
			warning(
				"Couldn't write configuration file %s: %s\n",
				filename, err.message
			);
		}
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
