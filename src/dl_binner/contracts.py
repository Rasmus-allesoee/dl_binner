"""Standard-library byte contracts for the bounded parent, before numerical imports."""
import hashlib
import json
from pathlib import Path


def digest(path):
    """Hash file bytes incrementally without a numerical-library prerequisite."""
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    """Exclusively retain a JSON receipt, including failed-import/timeout evidence."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2,allow_nan=False)
        stream.write('\n')


def file_record(path):
    """Bind a regular file's bytes; reject links and missing artifacts."""
    path=Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'Missing or linked artifact: {path}')
    return dict(bytes=path.stat().st_size,sha256=digest(path))


def check_files(folder, entries):
    """Verify relative-path inventories, rejecting escapes and linked parents."""
    folder=Path(folder)
    for name,expected in entries.items():
        path=folder/name;relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts or not path.resolve().is_relative_to(folder.resolve()) or any(
                (folder/Path(*relative.parts[:i])).is_symlink() for i in range(1,len(relative.parts)+1)):
            raise ValueError(f'Unsafe artifact path: {name}')
        if file_record(path)!=expected:
            raise ValueError(f'Artifact bytes changed: {path}')
