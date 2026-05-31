PIPX          := pipx
XDG_DATA_HOME ?= $(HOME)/.local/share
APPLICATIONS  := $(XDG_DATA_HOME)/applications
DESKTOP_SRC   := whipper/data/whipper-gui.desktop
DESKTOP_DEST  := $(APPLICATIONS)/whipper-gui.desktop

.PHONY: install reinstall uninstall

install:
	$(PIPX) install --system-site-packages .
	install -Dm644 $(DESKTOP_SRC) $(DESKTOP_DEST)
	-update-desktop-database $(APPLICATIONS)

reinstall:
	$(PIPX) reinstall whipper
	install -Dm644 $(DESKTOP_SRC) $(DESKTOP_DEST)
	-update-desktop-database $(APPLICATIONS)

uninstall:
	$(PIPX) uninstall whipper
	rm -f $(DESKTOP_DEST)
	-update-desktop-database $(APPLICATIONS)
