#include <glib-object.h>
#include <clutter/clutter.h>

void install_child_meta(GType container_type, GType child_meta_type) {
	GTypeClass *klass = g_type_class_peek(container_type);
	ClutterContainerIface *iface = 
		(ClutterContainerIface*) g_type_interface_peek(
			klass, CLUTTER_TYPE_CONTAINER
		);
	iface->child_meta_type = child_meta_type;
}
