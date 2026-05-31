from whipper.command.basecommand import BaseCommand

import logging
logger = logging.getLogger(__name__)


class GUI(BaseCommand):
    summary = "launch the graphical multi-drive auto rip interface"
    description = (
        "Open the Whipper GUI.\n\n"
        "Each configured drive is shown as a tab containing a terminal\n"
        "running 'whipper cd rip' in a restart loop.  Configure drives\n"
        "in ~/.config/whipper/whipper.conf under the [gui] section:\n\n"
        "  [gui]\n"
        "  drives = /dev/sr0, /dev/sr1\n\n"
        "Pressing Ctrl+C inside a tab stops the current rip and\n"
        "automatically restarts whipper for that drive.\n"
        "Closing the window terminates all rip processes."
    )

    def do(self):
        from whipper.gui.app import main
        main()
