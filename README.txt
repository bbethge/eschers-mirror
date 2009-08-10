This is Escher's Mirror, a pretentiously-named clone of the Atari Jaguar game
VidGrid.  (The name may change if I come up with something that sucks less.)

System Requirements
 * Python (http://python.org)
 * SDL (http://www.libsdl.org), including development files
 * pygame (http://pygame.org)
 * xine-lib 1.1.12 or later (http://www.xine-project.org/releases), including
   development files
      Note: Ubuntu (and probably all Debian-based distros) doesn't ship the raw
      video output plugin for xine-lib, so you will have to compile xine-lib
      yourself on these distros.
 * PyGTK and PyCairo (http://www.pygtk.org/downloads.html)
 * A C compiler
 * A video file

Compiling
$ python setup.py build

Running
Escher's Mirror is basically a jigsaw puzzle made from a video.  Since this is a
very early release, you will need to supply your own video (music videos are
recommended).
$ python eschers-mirror <videofile>
On UN*X, you can of course type ./eschers-mirror instead of
'python eschers-mirror'.

That's it. You get to play one puzzle, then you are back to the command line.
A friendlier and hopefully more fun interface is planned.
