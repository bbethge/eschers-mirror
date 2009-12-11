test: test.vala Errata.c Button.vala BoxLayout.vala
	valac -o $@ $^ --vapidir=. --pkg=clutter-1.0 --pkg=cogl-1.0 \
		--pkg=Errata -g
