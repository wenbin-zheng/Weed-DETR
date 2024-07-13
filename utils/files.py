

import contextlib
import glob
import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


class WorkingDirectory(contextlib.ContextDecorator):

    def __init__(self, new_dir):
        """Sets the working directory to 'new_dir' upon instantiation."""
        self.dir = new_dir  # new dir
        self.cwd = Path.cwd().resolve()  # current dir

    def __enter__(self):
        """Changes the current directory to the specified directory."""
        os.chdir(self.dir)

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa
        """Restore the current working directory on context exit."""
        os.chdir(self.cwd)


@contextmanager
def spaces_in_path(path):

    # If path has spaces, replace them with underscores
    if ' ' in str(path):
        string = isinstance(path, str)  # input type
        path = Path(path)

        # Create a temporary directory and construct the new path
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / path.name.replace(' ', '_')

            # Copy file/directory
            if path.is_dir():
                # tmp_path.mkdir(parents=True, exist_ok=True)
                shutil.copytree(path, tmp_path)
            elif path.is_file():
                tmp_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, tmp_path)

            try:
                # Yield the temporary path
                yield str(tmp_path) if string else tmp_path

            finally:
                # Copy file/directory back
                if tmp_path.is_dir():
                    shutil.copytree(tmp_path, path, dirs_exist_ok=True)
                elif tmp_path.is_file():
                    shutil.copy2(tmp_path, path)  # Copy back the file

    else:
        # If there are no spaces, just yield the original path
        yield path


def increment_path(path, exist_ok=False, sep='', mkdir=False):
    path = Path(path)  # os-agnostic
    if path.exists() and not exist_ok:
        path, suffix = (path.with_suffix(''), path.suffix) if path.is_file() else (path, '')

        # Method 1
        for n in range(2, 9999):
            p = f'{path}{sep}{n}{suffix}'  # increment path
            if not os.path.exists(p):  #
                break
        path = Path(p)

    if mkdir:
        path.mkdir(parents=True, exist_ok=True)  # make directory

    return path


def file_age(path=__file__):
    dt = (datetime.now() - datetime.fromtimestamp(Path(path).stat().st_mtime))  # delta
    return dt.days  # + dt.seconds / 86400  # fractional days


def file_date(path=__file__):
    t = datetime.fromtimestamp(Path(path).stat().st_mtime)
    return f'{t.year}-{t.month}-{t.day}'


def file_size(path):
    if isinstance(path, (str, Path)):
        mb = 1 << 20  # bytes to MiB (1024 ** 2)
        path = Path(path)
        if path.is_file():
            return path.stat().st_size / mb
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file()) / mb
    return 0.0


def get_latest_run(search_dir='.'):
    last_list = glob.glob(f'{search_dir}/**/last*.pt', recursive=True)
    return max(last_list, key=os.path.getctime) if last_list else ''