import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from whipper.gui import MAX_DRIVES
from whipper.gui.driveterminal import DriveTerminal

logger = logging.getLogger(__name__)


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, app, drives):
        super().__init__(application=app, title='Whipper Auto Mode')
        self.set_default_size(1000, 650)

        self._terminals = []

        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.add(notebook)

        for i, device in enumerate(drives[:MAX_DRIVES]):
            terminal = DriveTerminal(device)
            self._terminals.append(terminal)
            label = Gtk.Label()
            label.set_markup('<b>Drive %d</b>\n<small>%s</small>'
                             % (i + 1, device))
            label.set_justify(Gtk.Justification.CENTER)
            notebook.append_page(terminal, label)

        self.connect('delete-event', self._on_delete)
        self.show_all()

    def _on_delete(self, _widget, _event):
        for terminal in self._terminals:
            terminal.terminate()
        return False  # allow the window to be destroyed
