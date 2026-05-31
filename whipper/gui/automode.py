import argparse
import signal
import subprocess
import sys
import time

import logging
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Run whipper cd rip in a restart loop for one drive')
    parser.add_argument('--device', required=True,
                        help='CD-DA device path (e.g. /dev/sr0)')
    args = parser.parse_args()

    # Ignore SIGINT in this wrapper.  subprocess.Popen restores the default
    # SIGINT disposition in the child (restore_signals=True by default), so
    # pressing Ctrl+C kills whipper but this loop continues.
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    cmd = ['whipper', 'cd', 'rip', '--device', args.device]

    while True:
        proc = subprocess.run(cmd)
        print()
        print('─' * 54)
        print('  whipper exited (code %d). Restarting in 5 s…'
              % proc.returncode)
        print('  Close this window to stop permanently.')
        print('─' * 54)
        time.sleep(5)
