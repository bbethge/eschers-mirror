eschers-mirror: main.vala Errata.c ListSelector.vala MainMenu.vala VideoChooserMenu.vala Frame.vala BoxLayout.vala MenuManager.vala Button.vala
	valac -o $@ $^ --vapidir=. --pkg=clutter-1.0 --pkg=cogl-1.0 \
		--pkg=Errata -g
