import logging
import os
import shutil
import subprocess
from importlib.resources import files

logger = logging.getLogger(__name__)

_DESKTOP_FILENAME = 'whipper-gui.desktop'
_APPLICATIONS_DIR = os.path.join(
    os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share')),
    'applications',
)


def ensure_desktop_entry():
    """Copy the bundled .desktop file to the user applications dir if needed."""
    dest = os.path.join(_APPLICATIONS_DIR, _DESKTOP_FILENAME)
    src = files('whipper.data').joinpath(_DESKTOP_FILENAME)

    src_text = src.read_text(encoding='utf-8')

    if os.path.exists(dest):
        try:
            if open(dest, encoding='utf-8').read() == src_text:
                logger.debug('desktop entry already up to date at %s', dest)
                return
        except OSError:
            pass

    os.makedirs(_APPLICATIONS_DIR, exist_ok=True)
    # Write via a temp file so the destination is never half-written
    tmp = dest + '.tmp'
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(src_text)
        shutil.move(tmp, dest)
        logger.info('installed desktop entry to %s', dest)
        _refresh_desktop_database()
    except OSError as e:
        logger.warning('could not install desktop entry: %s', e)
        if os.path.exists(tmp):
            os.unlink(tmp)


def _refresh_desktop_database():
    if shutil.which('update-desktop-database'):
        try:
            subprocess.run(
                ['update-desktop-database', _APPLICATIONS_DIR],
                check=False, capture_output=True,
            )
        except OSError:
            pass
