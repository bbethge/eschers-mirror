#include <cogl/cogl.h>
#include <string.h>

void errata_cogl_color_new(CoglColor *color) {
	CoglColor *initializer = cogl_color_new();
	memcpy(color, initializer, sizeof(CoglColor));
	cogl_color_free(initializer);
}
