public class Config: Object {
	private string _video_dir;  // Cached copy of last returned value
	public string video_dir {
		get {
			try {
				_video_dir = key_file.get_string("default", "video_dir");
			}
			catch (KeyFileError err) {
				_video_dir = 
					Environment.get_user_special_dir(UserDirectory.VIDEOS);
				video_dir = _video_dir;
			}
			return _video_dir;
		}
		set {
			key_file.set_string("default", "video_dir", value);
			try {
				key_file.set_comment(
					"default", "video_dir",
					" Directory where music videos are stored"
				);
			}
			catch (KeyFileError err) {
				// Ignore -- it's just a comment
			}
		}
	}

	private KeyFile key_file;

	private string get_config_filename() {
		return Path.build_filename(
			Environment.get_user_config_dir(), "eschers-mirror", null
		);
	}

	public Config() {
		key_file = new KeyFile();
		try {
			key_file.load_from_file(
				get_config_filename(), KeyFileFlags.KEEP_COMMENTS
			);
		}
		catch (KeyFileError err) {
			warning("Error in configuration file: %s\n", err.message);
		}
		catch (FileError err) {
			// Just use empty key file
		}
	}
	
	public void write() {
		size_t length;
		string data = key_file.to_data(out length);
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

	private static Config? config = null;

	public static Config get_config() {
		if (config == null) {
			config = new Config();
		}
		return config;
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
