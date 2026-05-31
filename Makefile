PIPX          := pipx
PYTHON        := python3
XDG_DATA_HOME ?= $(HOME)/.local/share
GLOBAL_PREFIX ?= /usr/local

DESKTOP_SRC   := whipper/data/whipper-gui.desktop
LOCAL_APPS    := $(XDG_DATA_HOME)/applications
GLOBAL_APPS   := $(GLOBAL_PREFIX)/share/applications

.PHONY: install reinstall uninstall \
        install-global reinstall-global uninstall-global

# ── Local install (current user, via pipx) ──────────────────────────────────

install:
	$(PIPX) install --system-site-packages .
	install -Dm644 $(DESKTOP_SRC) $(LOCAL_APPS)/whipper-gui.desktop
	-update-desktop-database $(LOCAL_APPS)

reinstall:
	$(PIPX) reinstall whipper
	install -Dm644 $(DESKTOP_SRC) $(LOCAL_APPS)/whipper-gui.desktop
	-update-desktop-database $(LOCAL_APPS)

uninstall:
	$(PIPX) uninstall whipper
	rm -f $(LOCAL_APPS)/whipper-gui.desktop
	-update-desktop-database $(LOCAL_APPS)

# ── Global install (system-wide, requires sudo) ──────────────────────────────
# Installs to GLOBAL_PREFIX (default: /usr/local).
# Override with: make install-global GLOBAL_PREFIX=/usr

install-global:
	sudo $(PYTHON) -m pip install --break-system-packages --prefix=$(GLOBAL_PREFIX) .
	sudo install -Dm644 $(DESKTOP_SRC) $(GLOBAL_APPS)/whipper-gui.desktop
	-sudo update-desktop-database $(GLOBAL_APPS)

reinstall-global:
	sudo $(PYTHON) -m pip install --break-system-packages --force-reinstall --prefix=$(GLOBAL_PREFIX) .
	sudo install -Dm644 $(DESKTOP_SRC) $(GLOBAL_APPS)/whipper-gui.desktop
	-sudo update-desktop-database $(GLOBAL_APPS)

uninstall-global:
	sudo $(PYTHON) -m pip uninstall -y whipper
	sudo rm -f $(GLOBAL_APPS)/whipper-gui.desktop
	-sudo update-desktop-database $(GLOBAL_APPS)
