public class Config {
	private Json.Node root_node;
	private string filename;

	public Config(string config_filename) {
		filename = config_filename;

		var parser = new Json.Parser();
		try {
			parser.load_from_file(filename);
			root_node = parser.get_root().copy();
		}
		catch (Error err) {
			root_node = new Json.Node(Json.NodeType.OBJECT);
		}
	}

	/**
	 * Write the current configuration back to the file it was loaded from
	 */
	public void write() throws Error {
		var generator = new Json.Generator();
		generator.set_root(root_node);
		generator.pretty = true;
		generator.to_file(filename);
	}

	/**
	 * Check whether root_node is an object node and make it one if not
	 */
	private void ensure_root_node_is_object() {
		if (root_node.type != Json.NodeType.OBJECT) {
			var ob = new Json.Object();
			root_node.set_object(ob);
		}
	}

	public int get_int(string name, int @default) {
		ensure_root_node_is_object();
		weak Json.Object root_ob = root_node.get_object();
		if (root_ob.has_member(name)) {
			weak Json.Node node = root_ob.get_member(name);
			if (node.type == Json.NodeType.VALUE) {
				return node.get_int();
			}
			else {
				node.set_int(@default);
				return @default;
			}
		}
		else {
			var node = new Json.Node(Json.NodeType.VALUE);
			node.set_int(@default);
			root_ob.add_member(name, (owned)node);
			return @default;
		}
	}

	public string get_string(string name, string @default) {
		ensure_root_node_is_object();
		weak Json.Object root_ob = root_node.get_object();
		if (root_ob.has_member(name)) {
			weak Json.Node node = root_ob.get_member(name);
			if (node.type == Json.NodeType.VALUE) {
				int string_length;
				string val = node.get_string(out string_length);
				return val;
			}
			else {
				node.set_string(@default);
				return @default;
			}
		}
		else {
			var node = new Json.Node(Json.NodeType.VALUE);
			node.set_string(@default);
			root_ob.add_member(name, (owned)node);
			return @default;
		}
	}
}

// vim: set ts=4 sts=4 sw=4 ai noet :
