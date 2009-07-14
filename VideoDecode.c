#include <Python.h>
#include <xine.h>
#include <stdio.h>

static xine_t *xine;
static xine_stream_t *xine_stream;
static xine_audio_port_t *xine_audio;
static xine_video_port_t *xine_video;
static PyObject *pyFrameCb;
static PyThreadState *cbThreadState;

static void frame_cb(
	void *user_data, int format, int width, int height, double aspect,
	void *data, void *unused1, void *unused2
) {
	PyThreadState *savedState;
	PyObject *frame;
	PyObject *args;
	
	fprintf(stderr, "frame_cb called\n");
	PyEval_AcquireLock();
	fprintf(stderr, "frame_cb acquired lock\n");
	savedState = PyThreadState_Swap(cbThreadState);
	
	frame = PyString_FromStringAndSize(data, 3*width*height);
	if (frame == NULL) {} // TODO
	args = Py_BuildValue("iiidO", format, width, height, aspect, frame);
	Py_DECREF(frame);
	if (PyObject_CallObject(pyFrameCb, args) == NULL) {} // TODO
	Py_DECREF(args);
	
	if (PyErr_Occurred()) {
		PyErr_Print();
	}
	PyThreadState_Swap(savedState);
	PyEval_ReleaseLock();
}

static void
overlay_cb(void *user_data, int num_ovl, raw_overlay_t *overlays_array) {
	// Do nothing.
}

static PyObject*
VideoDecode_init(PyObject *self, PyObject *args) {
	const char *confFile;
	const char *mrl;
	raw_visual_t video_info;
	
	if (!PyArg_ParseTuple(args, "ssO", &confFile, &mrl, &pyFrameCb)) {
		return NULL;
	}
	if (!PyCallable_Check(pyFrameCb)) {
		PyErr_SetString(PyExc_TypeError, "Frame callback must be callable");
		return NULL;
	}
	Py_INCREF(pyFrameCb);
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
		PyErr_SetString(
			PyExc_RuntimeError, "Failed to open xine video driver!"
		);
		return NULL;
	}
	//xine_audio = xine_open_audio_driver(xine, NULL, NULL);
	xine_stream = xine_stream_new(xine, NULL, xine_video);
	if (!xine_open(xine_stream, mrl) ) {
		PyErr_SetString(PyExc_RuntimeError, "Failed to open MRL");
		xine_close_video_driver(xine, xine_video);
		return NULL;
	}
	
	PyEval_InitThreads();
	cbThreadState = PyThreadState_New(PyThreadState_Get()->interp);
	if (cbThreadState == NULL) {
		PyErr_SetString(PyExc_RuntimeError, "Couldn't create thread state");
		return NULL;
	}
	PyThreadState_Clear(cbThreadState);
	// TODO: check cleanup in exception-throwing code
	
	Py_RETURN_NONE;
}

static PyObject*
VideoDecode_quit(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "")) {
		return NULL;
	}
	Py_DECREF(pyFrameCb);
	PyThreadState_Delete(cbThreadState);
	xine_exit(xine);
	Py_RETURN_NONE;
}

static PyObject*
VideoDecode_start(PyObject *self, PyObject *args) {
	if (!PyArg_ParseTuple(args, "")) {
		return NULL;
	}
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

static PyMethodDef VideoDecode_methods[] = {
	{ "init", VideoDecode_init, METH_VARARGS, "" },
	{ "quit", VideoDecode_quit, METH_VARARGS, "" },
	{ "start", VideoDecode_start, METH_VARARGS, "" },
	{ "stop", VideoDecode_stop, METH_VARARGS, "" },
	{ NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initVideoDecode(void) {
	PyObject *module = Py_InitModule("VideoDecode", VideoDecode_methods);
	if (module == NULL) return;
}
