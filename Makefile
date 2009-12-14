VALA_SOURCES = \
	main.vala \
	ListSelector.vala \
	MainMenu.vala \
	VideoChooserMenu.vala \
	Frame.vala \
	BoxLayout.vala \
	MenuManager.vala \
	Button.vala \
	Grid.vala \
	RectGrid.vala \
	Vector.vala \
	Config.vala

C_SOURCES = Errata.c

PACKAGES = \
	--pkg=clutter-1.0 \
	--pkg=cogl-1.0 \
	--pkg=Errata \
	--pkg=clutter-gst-0.10 \
	--pkg=gstreamer-0.10

eschers-mirror: $(C_SOURCES) $(VALA_SOURCES)
	valac -o $@ $^ -g --vapidir=. $(PACKAGES)

.PHONY: c-files
c-files: $(VALA_SOURCES)
	valac -C $^ --vapidir=. $(PACKAGES)

.PHONY: clean
clean:
	$(RM) $(patsubst %.vala,%.c,$(VALA_SOURCES))
