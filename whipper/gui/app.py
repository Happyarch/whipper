import logging
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from whipper.common.config import Config
from whipper.gui import MAX_DRIVES
from whipper.gui.mainwindow import MainWindow

logger = logging.getLogger(__name__)

_FALLBACK_DEVICE = '/dev/sr0'


class WhipperGuiApp(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id='io.github.whipper_team.WhipperGui')

    def do_activate(self):
        drives = self._load_drives()
        logger.info('starting GUI with %d drive(s): %s', len(drives), drives)
        MainWindow(self, drives)

    def _load_drives(self):
        conf = Config()
        drives = conf.get_gui_drives()
        if not drives:
            drives = self._detect_drives()

        if len(drives) > MAX_DRIVES:
            logger.warning('config lists %d drives; capping at %d',
                           len(drives), MAX_DRIVES)
            drives = drives[:MAX_DRIVES]

        return drives

    @staticmethod
    def _detect_drives():
        try:
            from whipper.common import drive as drive_mod
            devices = drive_mod.getAllDevicePaths()
            if devices:
                return [devices[0]]
        except Exception as e:
            logger.warning('drive detection failed: %s', e)
        return [_FALLBACK_DEVICE]


def main():
    logging.basicConfig(level=logging.INFO)
    app = WhipperGuiApp()
    sys.exit(app.run(sys.argv))
