#include <glib-object.h>
#include <cogl/cogl.h>
#include <clutter/clutter.h>
#include <string.h>

void errata_cogl_color_new(CoglColor *color) {
	CoglColor *initializer = cogl_color_new();
	memcpy(color, initializer, sizeof(CoglColor));
	cogl_color_free(initializer);
}

void errata_install_child_meta(GType container_type, GType child_meta_type) {
	GTypeClass *klass = g_type_class_peek(container_type);
	ClutterContainerIface *iface = 
		(ClutterContainerIface*) g_type_interface_peek(
			klass, CLUTTER_TYPE_CONTAINER
		);
	iface->child_meta_type = child_meta_type;
}
