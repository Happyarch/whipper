import logging
import os
import shutil
import signal

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import GLib, Gtk, Vte

logger = logging.getLogger(__name__)


class DriveTerminal(Gtk.Box):
    """A GTK widget containing a VTE terminal running whipper-automode."""

    def __init__(self, device):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self._device = device
        self._child_pid = None

        self._terminal = Vte.Terminal()
        self._terminal.set_scroll_on_output(True)
        self._terminal.set_scroll_on_keystroke(True)

        scrollbar = Gtk.Scrollbar.new(
            Gtk.Orientation.VERTICAL,
            self._terminal.get_vadjustment(),
        )

        self.pack_start(self._terminal, True, True, 0)
        self.pack_start(scrollbar, False, False, 0)

        self.connect('realize', self._on_realize)

    def _on_realize(self, _widget):
        self._spawn()

    def _spawn(self):
        automode = shutil.which('whipper-automode')
        if automode is None:
            logger.error('whipper-automode not found in PATH; '
                         'is whipper installed?')
            return

        self._terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,                       # working directory (inherit)
            [automode, '--device', self._device],
            None,                       # environment (inherit)
            GLib.SpawnFlags.DEFAULT,
            None,                       # child setup callable
            None,                       # child setup user data
            -1,                         # timeout (-1 = default)
            None,                       # GCancellable
            self._on_spawn_done,
        )

    def _on_spawn_done(self, _terminal, pid, error):
        if error:
            logger.error('spawn failed for %s: %s', self._device, error)
            return
        self._child_pid = pid
        logger.debug('spawned whipper-automode for %s as pid %d',
                     self._device, pid)

    def connect_bell(self, callback):
        """Connect *callback* to the VTE terminal's 'bell' signal."""
        self._terminal.connect('bell', callback)

    def terminate(self):
        if self._child_pid is None:
            return
        try:
            pgid = os.getpgid(self._child_pid)
            os.killpg(pgid, signal.SIGTERM)
            logger.debug('sent SIGTERM to process group %d', pgid)
        except ProcessLookupError:
            pass
        except Exception as e:
            logger.warning('error terminating pid %d: %s', self._child_pid, e)
        self._child_pid = None
