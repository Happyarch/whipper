import argparse
import os
import pty
import re
import select
import signal
import subprocess
import sys
import time
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

_LOG_DIR = os.path.join(
    os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')),
    'whipper', 'logs',
)

# Matches ANSI/VT100 escape sequences
_ANSI_RE = re.compile(rb'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def _strip_ansi(data):
    return _ANSI_RE.sub(b'', data)


def _log_path(device):
    device_tag = os.path.basename(device)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(_LOG_DIR, '%s_%s.log' % (device_tag, timestamp))


def _run(cmd, log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    master_fd, slave_fd = pty.openpty()

    with open(log_path, 'ab') as log:
        header = ('─' * 54 + '\n'
                  + '  Log: %s\n' % log_path
                  + '  Started: %s\n' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                  + '─' * 54 + '\n')
        sys.stdout.write(header)
        sys.stdout.flush()
        log.write(header.encode())

        proc = subprocess.Popen(
            cmd,
            stdout=slave_fd,
            stderr=slave_fd,
            stdin=sys.stdin.fileno(),
        )
        os.close(slave_fd)

        def drain():
            try:
                while True:
                    r, _, _ = select.select([master_fd], [], [], 0.05)
                    if not r:
                        break
                    data = os.read(master_fd, 4096)
                    if not data:
                        break
                    try:
                        os.write(sys.stdout.fileno(), data)
                    except OSError:
                        pass
                    log.write(_strip_ansi(data))
                    log.flush()
            except OSError:
                pass

        while True:
            try:
                r, _, _ = select.select([master_fd], [], [], 0.05)
            except (OSError, ValueError):
                break
            if r:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                try:
                    os.write(sys.stdout.fileno(), data)
                except OSError:
                    pass
                log.write(_strip_ansi(data))
                log.flush()
            elif proc.poll() is not None:
                drain()
                break

    os.close(master_fd)
    proc.wait()
    return proc


def main():
    parser = argparse.ArgumentParser(
        description='Run whipper cd rip in a restart loop for one drive')
    parser.add_argument('--device', required=True,
                        help='CD-DA device path (e.g. /dev/sr0)')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # --device belongs to the 'cd' parent command, not 'rip'
    cmd = ['whipper', 'cd', '--device', args.device, 'rip']

    while True:
        log_path = _log_path(args.device)
        proc = _run(cmd, log_path)
        print()
        print('─' * 54)
        print('  whipper exited (code %d). Restarting in 5 s…'
              % proc.returncode)
        print('  Log saved to: %s' % log_path)
        print('  Close this window to stop permanently.')
        print('─' * 54)
        time.sleep(5)
