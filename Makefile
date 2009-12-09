test: test.vala Grid.vala RectGrid.vala Vector.vala Errata.c
	valac -o $@ $^ --vapidir=. --pkg=clutter-1.0 --pkg=cogl-1.0 \
		--pkg=clutter-gst-0.10 --pkg=gstreamer-0.10 \
		--pkg=InstallChildMeta --pkg=Errata -g
