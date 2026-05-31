import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

_LOG_DIR = os.path.join(
    os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')),
    'whipper', 'logs',
)


def _log_path(device):
    device_tag = os.path.basename(device)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(_LOG_DIR, '%s_%s.log' % (device_tag, timestamp))


def _tee(source, targets):
    """Read from source and write every chunk to all targets."""
    for chunk in iter(lambda: source.read1(4096), b''):
        for t in targets:
            try:
                t.write(chunk)
                t.flush()
            except OSError:
                pass


def _run(cmd, log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
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
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        tee_thread = threading.Thread(
            target=_tee,
            args=(proc.stdout, [sys.stdout.buffer, log]),
            daemon=True,
        )
        tee_thread.start()
        proc.wait()
        tee_thread.join()

    return proc


def main():
    parser = argparse.ArgumentParser(
        description='Run whipper cd rip in a restart loop for one drive')
    parser.add_argument('--device', required=True,
                        help='CD-DA device path (e.g. /dev/sr0)')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    cmd = ['whipper', 'cd', 'rip', '--device', args.device]

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
