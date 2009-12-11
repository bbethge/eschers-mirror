[CCode (cprefix = "Cogl", lower_case_cprefix = "cogl_")]
namespace Cogl {
	public Cogl.Texture texture_new_from_data(
		uint width, uint height, Cogl.TextureFlags flags,
		Cogl.PixelFormat format, Cogl.PixelFormat internal_format,
		uint rowstride, [CCode (array_length = false)] uchar[] data
	);
	public void set_draw_buffer(Cogl.BufferTarget target, Cogl.Offscreen? offscreen);
}

namespace Errata {
	using GLib;
	public Cogl.Color cogl_color_new();
	public void install_child_meta(Type container_type, Type child_meta_type);
}
