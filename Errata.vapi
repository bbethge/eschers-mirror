[CCode (cprefix = "Cogl", lower_case_cprefix = "cogl_")]
namespace Cogl {
	public Cogl.Texture texture_new_from_data(
		uint width, uint height, Cogl.TextureFlags flags,
		Cogl.PixelFormat format, Cogl.PixelFormat internal_format,
		uint rowstride, [CCode (array_length = false)] uchar[] data
	);
}
