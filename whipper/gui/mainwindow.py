import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, GLib, Gtk

from whipper.gui import MAX_DRIVES
from whipper.gui.driveterminal import DriveTerminal

logger = logging.getLogger(__name__)

_MARKUP_NORMAL = '<b>Drive %d</b>\n<small>%s</small>'
# Alternating colours for the bell-alert flash
_MARKUP_BELL_A = ('<span foreground="#ff00ff">'
                  '<b>Drive %d</b>\n<small>%s</small></span>')
_MARKUP_BELL_B = ('<span foreground="#1a001a">'
                  '<b>Drive %d</b>\n<small>%s</small></span>')


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app, drives):
        super().__init__(application=app, title='Whipper Auto Mode')
        self.set_default_size(1000, 650)

        self._drives = drives[:MAX_DRIVES]
        self._terminals = []
        self._labels = []         # Gtk.Label per tab
        self._flash_timeouts = {} # tab_idx → GLib source id
        self._flash_states = {}   # tab_idx → bool (True = bright phase)

        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        self._notebook = notebook
        self.add(notebook)

        for i, device in enumerate(self._drives):
            terminal = DriveTerminal(device)
            self._terminals.append(terminal)

            label = Gtk.Label()
            label.set_markup(_MARKUP_NORMAL % (i + 1, device))
            label.set_justify(Gtk.Justification.CENTER)
            self._labels.append(label)

            # Wrap label in EventBox so scroll events on the tab bar are
            # captured here rather than falling through to the terminal.
            tab_box = Gtk.EventBox()
            tab_box.add(label)
            tab_box.add_events(Gdk.EventMask.SCROLL_MASK)
            tab_box.connect('scroll-event',
                            lambda _w, ev: self._on_tab_scroll(ev))
            tab_box.show_all()  # tab labels must be shown before append_page

            notebook.append_page(terminal, tab_box)
            terminal.connect_bell(lambda _t, idx=i: self._on_bell(idx))

        notebook.connect('switch-page', self._on_switch_page)
        self.connect('delete-event', self._on_delete)
        self.show_all()

        # GTK only realizes the first notebook page automatically; force all
        # other pages to realize now so their automode processes start
        # immediately instead of waiting for the user to click each tab.
        for terminal in self._terminals:
            if not terminal.get_realized():
                terminal.realize()

    # ── Tab scroll-to-switch ──────────────────────────────────────────────

    def _on_tab_scroll(self, event):
        nb = self._notebook
        if event.direction == Gdk.ScrollDirection.UP:
            nb.prev_page()
        elif event.direction == Gdk.ScrollDirection.DOWN:
            nb.next_page()
        elif event.direction == Gdk.ScrollDirection.SMOOTH:
            if event.delta_y < 0:
                nb.prev_page()
            elif event.delta_y > 0:
                nb.next_page()
        return True

    # ── Bell flash ───────────────────────────────────────────────────────

    def _on_bell(self, idx):
        if idx in self._flash_timeouts:
            return  # already flashing
        self._flash_states[idx] = True
        def tick():
            return self._flash_tick(idx)
        self._flash_timeouts[idx] = GLib.timeout_add(500, tick)

    def _flash_tick(self, idx):
        if idx not in self._flash_timeouts:
            return GLib.SOURCE_REMOVE
        device = self._drives[idx]
        markup = (_MARKUP_BELL_A if self._flash_states[idx]
                  else _MARKUP_BELL_B)
        self._labels[idx].set_markup(markup % (idx + 1, device))
        self._flash_states[idx] = not self._flash_states[idx]
        return GLib.SOURCE_CONTINUE

    def _stop_flash(self, idx):
        if idx not in self._flash_timeouts:
            return
        GLib.source_remove(self._flash_timeouts.pop(idx))
        self._flash_states.pop(idx, None)
        device = self._drives[idx]
        self._labels[idx].set_markup(_MARKUP_NORMAL % (idx + 1, device))

    def _on_switch_page(self, _nb, _page, page_num):
        self._stop_flash(page_num)

    # ── Cleanup ───────────────────────────────────────────────────────────

    def _on_delete(self, _widget, _event):
        for tid in list(self._flash_timeouts.values()):
            GLib.source_remove(tid)
        for terminal in self._terminals:
            terminal.terminate()
        return False  # allow window destroy
