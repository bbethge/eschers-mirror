This is Escher's Mirror, a pretentiously-named clone of the Atari Jaguar game
VidGrid.  (The name may change if I come up with something that sucks less.)

System Requirements
===================
 * The Vala compiler, version > 0.7.8 (<http://www.vala-project.org/>).
   At the time of this writing, 0.7.8 is the most recent release, so you will
   need the development version.
 * Clutter 1.0, including development files (<http://www.clutter-project.org/>)
 * ClutterGst 0.10, including development files
 * A video file
On Debian-based systems, you can get Clutter and ClutterGst by installing the
packages `libclutter-1.0-dev` and `libclutter-gst-0.10-dev`.  When/if your
distro ships version > 0.7.8 of the Vala compiler, you can get it by installing
the `valac` package.

Compiling
=========
autotools still hurts my brain, so compilation uses a plain `Makefile`.  Just
run

    $ make

and hope for the best.

Running
=======
Escher's Mirror is basically a jigsaw puzzle made from a video.  Since this is a
very early release, you will need to supply your own video (music videos are
recommended).

    $ ./eschers-mirror

Controls
========

<table>
<tr><td>Left click and drag                  </td><td>Move tile      </td></tr>
<tr><td>r key or right click while dragging  </td><td>Rotate tile    </td></tr>
<tr><td>f key while dragging                 </td><td>Flip tile
                                                      (unimplemented)</td></tr>
</table>

Configuration
=============
Configuration is stored in the file `eschers-mirror` in your configuration 
directory.  On Linux this probably means `~/.config/eschers-mirror`.
For now, you have to edit this file directly to tell Escher's Mirror where to
look for videos.

Credits
=======
Files in the `clutter-gst-0.10` directory I borrowed from the Clutter git repo.
`data/background.jpg` (which is not currently used) is by [Steve Jurvetson]
(https://www.flickr.com/photos/jurvetson) from flickr. Unlike everything else,
it is under a Creative Commons Attribution license.
