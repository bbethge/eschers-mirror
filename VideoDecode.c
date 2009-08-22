#include <Python.h>
#include <xine.h>
#include <stdio.h>
#include <string.h>
#include "SDL.h"
#include "SDL_thread.h"

static xine_t *xine;
static xine_stream_t *xine_stream;
static xine_audio_port_t *xine_audio;
static xine_video_port_t *xine_video;
static struct {
	int width, height;
	double aspect;
	Uint8 *data;
	SDL_mutex *mutex;  // Protects the above frame info
	SDL_cond *cond;  // Indicates frame has been updated
} frame = { 0, 0, 0.0, NULL };
static xine_event_queue_t *xine_event_queue;
static int playing;  // Boolean: is stream playing?
static SDL_mutex *playing_mutex;  // Protects 'playing' (is this necessary?)

static void frame_cb(
	void *user_data, int format, int width, int height, double aspect,
	void *data, void *unused1, void *unused2
) {
	SDL_LockMutex(frame.mutex);
	if (frame.width != width || frame.height != height) {
		// TODO: handle out-of-memory errors
		frame.data = realloc(frame.data, 3*width*height);
	}
	memcpy(frame.data, data, 3*width*height);
	frame.width = width;
	frame.height = height;
	frame.aspect = aspect;
	SDL_CondSignal(frame.cond);
	SDL_UnlockMutex(frame.mutex);
}

static void
overlay_cb(void *user_data, int num_ovl, raw_overlay_t *overlays_array) {
	// Do nothing.
}

static void
event_cb(void *user_data, const xine_event_t *event) {
	if (event->type == XINE_EVENT_UI_PLAYBACK_FINISHED) {
		SDL_LockMutex(playing_mutex);
		playing = 0;
		SDL_UnlockMutex(playing_mutex);
	}
}

static PyObject*
VideoDecode_init(PyObject *self, PyObject *args) {
	const char *confFile;
	const char *mrl;
	raw_visual_t video_info;
	
	if (!PyArg_ParseTuple(args, "ss", &confFile, &mrl)) {
		return NULL;
	}
	frame.mutex = SDL_CreateMutex();
	frame.cond = SDL_CreateCond();
	playing_mutex = SDL_CreateMutex();
	if (frame.mutex == NULL || frame.cond == NULL || playing_mutex == NULL){
		return PyErr_NoMemory();
	}
	if (!xine_check_version(1, 1, 12)) {
		PyErr_SetString(PyExc_RuntimeError, "Xine version is too old");
		return NULL;
	}
	xine = xine_new();
	if (xine == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "xine_new failed");
		return NULL;
	}
	xine_config_load(xine, confFile);
	xine_init(xine);
	
	video_info.user_data = NULL;
	video_info.supported_formats = XINE_VORAW_RGB;
	video_info.raw_output_cb = frame_cb;
	video_info.raw_overlay_cb = overlay_cb;
	xine_video = xine_open_video_driver(
			xine, NULL, XINE_VISUAL_TYPE_RAW, &video_info
		);
	if (xine_video == NULL) {
		xine_exit(xine);
		PyErr_SetString(
			PyExc_RuntimeError, "Failed to open xine video driver!"
		);
		return NULL;
	}
	xine_audio = xine_open_audio_driver(xine, NULL, NULL);
	if (xine_audio == NULL) {
		xine_close_video_driver(xine, xine_video);
		xine_exit(xine);
		PyErr_SetString(
			PyExc_RuntimeError, "Failed to open xine audio driver!"
		);
		return NULL;
	}
	xine_stream = xine_stream_new(xine, NULL, xine_video);
	if (!xine_open(xine_stream, mrl) ) {
		PyErr_SetString(PyExc_RuntimeError, "Failed to open MRL");
		xine_close_video_driver(xine, xine_video);
		xine_close_audio_driver(xine, xine_audio);
		xine_exit(xine);
		return NULL;
	}
	xine_event_queue = xine_event_new_queue(xine_stream);
	if (xine_event_queue == NULL) {
		xine_dispose(xine_stream);
		xine_close_video_driver(xine, xine_video);
		xine_close_audio_driver(xine, xine_audio);
		xine_exit(xine);
		return PyErr_NoMemory();
	}
	xine_event_create_listener_thread(xine_event_queue, event_cb, NULL);
	
	Py_RETURN_NONE;
}

static PyObject*
VideoDecode_quit(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "")) {
		return NULL;
	}
	xine_event_dispose_queue(xine_event_queue);
	xine_dispose(xine_stream);
	xine_close_audio_driver(xine, xine_audio);
	xine_close_video_driver(xine, xine_video);
	xine_exit(xine);
	SDL_DestroyCond(frame.cond);
	free(frame.data);
	SDL_DestroyMutex(frame.mutex);
	Py_RETURN_NONE;
}

static PyObject*
VideoDecode_start(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "")) {
		return NULL;
	}
	SDL_LockMutex(playing_mutex);
	playing = 1;
	SDL_UnlockMutex(playing_mutex);
	if (xine_play(xine_stream, 0, 0) == 0) {
		PyErr_SetString(PyExc_RuntimeError, "Failed to start playback");
		return NULL;
	}
	Py_RETURN_NONE;
}

static PyObject*
VideoDecode_stop(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "")) {
		return NULL;
	}
	xine_stop(xine_stream);
	Py_RETURN_NONE;
}

static PyObject*
VideoDecode_getFrame(PyObject *self, PyObject *args) {
	int timeout = -1;
	PyObject *result;
	if (!PyArg_ParseTuple(args, "|i", &timeout)) {
		return NULL;
	}
	SDL_LockMutex(frame.mutex);
	if (SDL_CondWaitTimeout(frame.cond, frame.mutex, timeout) == 0) {
		result = Py_BuildValue(
				"iids#", frame.width, frame.height, frame.aspect,
				frame.data, 3*frame.width*frame.height
			);
	}
	else {
		result = Py_BuildValue(
				"OOOO", Py_None, Py_None, Py_None, Py_None
			);
	}
	SDL_UnlockMutex(frame.mutex);
	return result;
}

static PyObject*
VideoDecode_getPosition(PyObject *self, PyObject *args) {
	int pos_stream, pos_time, length_time;
	xine_get_pos_length(xine_stream, &pos_stream, &pos_time, &length_time);
	return Py_BuildValue("d", pos_time/1000.0);
}

static PyObject*
VideoDecode_isPlaying(PyObject *self, PyObject *args) {
	int playing_copy;
	SDL_LockMutex(playing_mutex);
	playing_copy = playing;
	SDL_UnlockMutex(playing_mutex);
	return Py_BuildValue("i", playing_copy);
}

static PyMethodDef VideoDecode_methods[] = {
	{ "init", VideoDecode_init, METH_VARARGS, "" },
	{ "quit", VideoDecode_quit, METH_VARARGS, "" },
	{ "start", VideoDecode_start, METH_VARARGS, "" },
	{ "stop", VideoDecode_stop, METH_VARARGS, "" },
	{ "getFrame", VideoDecode_getFrame, METH_VARARGS, "" },
	{ "getPosition", VideoDecode_getPosition, METH_VARARGS, "" },
	{ "isPlaying", VideoDecode_isPlaying, METH_VARARGS, "" },
	{ NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initVideoDecode(void) {
	Py_InitModule("VideoDecode", VideoDecode_methods);
}
