VALA_SOURCES = \
	main.vala \
	Config.vala \
	BoxLayout.vala \
	Frame.vala \
	Button.vala \
	ListSelector.vala \
	MenuManager.vala \
	MainMenu.vala \
	OptionsMenu.vala \
	VideoChooserMenu.vala \
	Grid.vala \
	RectGrid.vala \
	Vector.vala

C_SOURCES = Errata.c

PACKAGES = \
	--pkg=clutter-1.0 \
	--pkg=cogl-1.0 \
	--pkg=Errata \
	--pkg=clutter-gst-0.10 \
	--pkg=gstreamer-0.10

eschers-mirror: $(C_SOURCES) $(VALA_SOURCES) Errata.vapi clutter-gst-0.10.vapi
	valac -o $@ $(C_SOURCES) $(VALA_SOURCES) -g --vapidir=. $(PACKAGES)

clutter-gst-0.10.vapi: clutter-gst-0.10/clutter-gst-0.10.gi
	vapigen --library clutter-gst-0.10 $^

CLUTTER_GST_VAPI_SOURCES = \
	clutter-gst-0.10/clutter-gst-0.10.defines \
	clutter-gst-0.10/clutter-gst-0.10.deps \
	clutter-gst-0.10/clutter-gst-0.10.excludes \
	clutter-gst-0.10/clutter-gst-0.10.files \
	clutter-gst-0.10/clutter-gst-0.10.metadata \
	clutter-gst-0.10/clutter-gst-0.10.namespace

clutter-gst-0.10/clutter-gst-0.10.gi: $(CLUTTER_GST_VAPI_SOURCES)
	vala-gen-introspect clutter-gst-0.10 clutter-gst-0.10

.PHONY: c-files
c-files: $(VALA_SOURCES)
	valac -C $^ --vapidir=. $(PACKAGES)

.PHONY: clean
clean:
	$(RM) $(patsubst %.vala,%.c,$(VALA_SOURCES))
