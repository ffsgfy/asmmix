import re
import os

import fire

try:
    import procs
except ImportError:
    from . import procs


def from_file(file_in, *, ext_in=None, ext_out=None):
    path, ext = os.path.splitext(file_in)

    if ext_in is not None:
        if isinstance(ext_in, str) and ext != ext_in and ext[1:] != ext_in:
            return None
        elif ext not in ext_in and ext[1:] not in ext_in:
            return None

    if ext_out is None:
        ext_out = ext

    if isinstance(ext_out, str):
        ext_out = [ext_out]

    for ext in ext_out:
        ext = ext if ext.startswith(".") else f".{ext}"
        try:
            return procs.process_file(f"{path}{ext}")
        except FileNotFoundError:
            pass

    return None


def from_files(*files_in, ext_in=None, ext_out=None, string=True):
    files_out = []

    for path in files_in:
        path = from_file(path, ext_in=ext_in, ext_out=ext_out)
        if path is not None:
            files_out.append(path)

    return " ".join(files_out) if string else files_out


def from_string(string_in, *, ext_in=None, ext_out=None):
    string_out = re.split(r"(\S+)", string_in)

    for i, token in enumerate(string_out):
        if token and not token.isspace():  # non-files won't get opened
            token = from_file(token, ext_in=ext_in, ext_out=ext_out)
            if token is not None:
                string_out[i] = token

    return "".join(string_out)


if __name__ == "__main__":
    fire.Fire()
